"""Évaluation NL2SQL contre des requêtes SQL de référence."""

import math
import re

import pandas as pd

from backend.agent import _executer_sql, repondre
from utils.sql_validator import type_requete_sql, valider_sql


def evaluer_question(question: str, sql_reference: str) -> dict:
    """Compare le résultat produit par le LLM à la source de vérité SQL."""
    ok, message = valider_sql(sql_reference, role="utilisateur")
    if not ok or type_requete_sql(sql_reference) != "SELECT":
        return {"erreur": f"SQL de référence invalide : {message}"}

    attendu, erreur = _executer_sql(sql_reference)
    if erreur:
        return {"erreur": f"Échec du SQL de référence : {erreur}"}

    genere = repondre(question, role="utilisateur")
    if "erreur" in genere:
        return {
            "question": question,
            "conforme": False,
            "erreur": genere["erreur"],
            "sql_reference": sql_reference,
            "sql_genere": genere.get("sql", ""),
        }

    obtenu = genere["donnees"]
    conforme = _signature(obtenu) == _signature(attendu)
    nombres_non_traces = _nombres_non_traces(
        genere["reponse"],
        obtenu,
        question,
        len(obtenu),
    )

    return {
        "question": question,
        "conforme": conforme,
        "reponse_fondee": not nombres_non_traces,
        "nombres_non_traces": nombres_non_traces,
        "sql_reference": sql_reference,
        "sql_genere": genere["sql"],
        "nb_lignes_reference": len(attendu),
        "nb_lignes_generees": len(obtenu),
        "reponse": genere["reponse"],
    }


def _signature(dataframe: pd.DataFrame) -> list[tuple]:
    """Normalise valeurs et ordre sans dépendre des alias de colonnes."""
    lignes = []
    for ligne in dataframe.itertuples(index=False, name=None):
        valeurs = tuple(sorted((_normaliser(valeur) for valeur in ligne), key=str))
        lignes.append(valeurs)
    return sorted(lignes, key=str)


def _normaliser(valeur):
    if pd.isna(valeur):
        return "<NULL>"
    if isinstance(valeur, float):
        if math.isfinite(valeur):
            return round(valeur, 6)
        return str(valeur)
    return str(valeur).strip()


def _nombres_non_traces(
    reponse: str,
    dataframe: pd.DataFrame,
    question: str,
    nombre_lignes: int,
) -> list[str]:
    """Repère les nombres de la synthèse absents des entrées vérifiables.

    Sont considérés comme fondés : les nombres présents dans la question,
    le nombre de lignes, les valeurs présentes dans les données et les
    totaux (somme d'une colonne numérique). Un total erroné reste signalé.
    """
    # Valeurs numériques considérées comme fondées (comparaison numérique).
    autorisees: set[float] = set()
    _ajouter_valeur(autorisees, nombre_lignes)
    for jeton in re.findall(_MOTIF_NOMBRE, _normaliser_milliers(question)):
        _ajouter_valeur(autorisees, jeton)
    for valeur in dataframe.to_numpy().flatten():
        for jeton in re.findall(_MOTIF_NOMBRE, str(valeur)):
            _ajouter_valeur(autorisees, jeton)

    # Autoriser les totaux légitimes : somme de chaque colonne numérique.
    colonnes_numeriques = dataframe.select_dtypes(include="number")
    for colonne in colonnes_numeriques.columns:
        _ajouter_valeur(autorisees, colonnes_numeriques[colonne].sum())

    non_traces = []
    for jeton in re.findall(_MOTIF_NOMBRE, _normaliser_milliers(reponse)):
        nombre = _en_float(jeton)
        if nombre is None:
            continue
        if not _valeur_couverte(nombre, jeton, autorisees):
            non_traces.append(jeton)
    return sorted(set(non_traces))


# Nombre simple, éventuellement avec décimales (virgule ou point).
_MOTIF_NOMBRE = r"(?<!\w)-?\d+(?:[.,]\d+)?"

# Espaces utilisés comme séparateurs de milliers (normal, insécable, fin).
_SEP_MILLIERS = "[ \u00a0\u202f\u2009]"

# Nombre groupé « à la française » : 70 518 ou 1 234 567,89.
_MOTIF_GROUPE = re.compile(
    rf"(?<!\d)\d{{1,3}}(?:{_SEP_MILLIERS}\d{{3}})+(?:[.,]\d+)?(?!\d)"
)


def _normaliser_milliers(texte: str) -> str:
    """Retire les séparateurs de milliers pour reconstituer les nombres entiers."""
    return _MOTIF_GROUPE.sub(
        lambda m: re.sub(_SEP_MILLIERS, "", m.group(0)),
        str(texte),
    )


def _en_float(valeur) -> float | None:
    """Convertit un jeton numérique (virgule ou point, espaces) en float."""
    texte = re.sub(_SEP_MILLIERS, "", str(valeur))
    try:
        return float(texte.replace(",", "."))
    except (TypeError, ValueError):
        return None


def _ajouter_valeur(ensemble: set[float], valeur) -> None:
    nombre = _en_float(valeur)
    if nombre is not None:
        ensemble.add(nombre)


def _valeur_couverte(nombre: float, jeton: str, autorisees: set[float]) -> bool:
    """Vrai si le nombre correspond à une valeur autorisée, arrondi d'affichage inclus."""
    decimales = len(jeton.split(",")[-1].split(".")[-1]) if (
        "," in jeton or "." in jeton
    ) else 0
    unite = 10 ** (-decimales)

    for valeur in autorisees:
        if valeur == nombre:
            return True
        if round(valeur, decimales) == round(nombre, decimales):
            return True
        # Tolère l'arrondi ET la troncature à la précision d'affichage.
        if abs(valeur - nombre) < unite:
            return True
        if abs(valeur - nombre) <= max(1e-9, abs(valeur) * 1e-6):
            return True
    return False
