"""
mapping/reader.py
Lecture du fichier de mapping uploade par l utilisateur.
Formats supportes : Excel (.xlsx), CSV (.csv), JSON (.json)
"""

import pandas as pd
import json
import os


def lire_mapping(fichier=None) -> str:
    """
    Lit le fichier de mapping et retourne
    une chaine de texte de regles metier.

    Format Excel attendu :
    | terme_metier | table_sql | colonne_sql | condition        |
    | client actif | customer  | status      | = 'Active'       |
    | suspect      | transaction| amount     | > 8000           |
    """

    if fichier is None:
        return ""

    try:
        # Detecter le format
        if hasattr(fichier, "name"):
            nom = fichier.name.lower()
        else:
            nom = str(fichier).lower()

        # ── Excel ─────────────────────────────────────────────
        if nom.endswith(".xlsx") or nom.endswith(".xls"):
            df = pd.read_excel(fichier)
            return _dataframe_to_text(df)

        # ── CSV ───────────────────────────────────────────────
        elif nom.endswith(".csv"):
            df = pd.read_csv(fichier)
            return _dataframe_to_text(df)

        # ── JSON ──────────────────────────────────────────────
        elif nom.endswith(".json"):
            if hasattr(fichier, "read"):
                data = json.load(fichier)
            else:
                with open(fichier, "r", encoding="utf-8") as f:
                    data = json.load(f)
            return _json_to_text(data)

        else:
            print(f"Format non supporte : {nom}")
            return ""

    except Exception as e:
        print(f"Erreur lecture mapping : {e}")
        return ""


def _dataframe_to_text(df: pd.DataFrame) -> str:
    """
    Convertit un DataFrame mapping en texte de regles.
    """
    colonnes_requises = [
        "terme_metier",
        "table_sql",
        "colonne_sql",
        "condition"
    ]

    # Verifier que les colonnes existent
    for col in colonnes_requises:
        if col not in df.columns:
            print(f"Colonne manquante dans le mapping : {col}")
            print(f"Colonnes trouvees : {list(df.columns)}")
            return ""

    lines = []
    for _, row in df.iterrows():
        line = (
            f"'{row['terme_metier']}' correspond a "
            f"{row['table_sql']}.{row['colonne_sql']} "
            f"{row['condition']}"
        )
        lines.append(line)

    return "\n".join(lines)


def _json_to_text(data) -> str:
    """
    Convertit un JSON mapping en texte de regles.
    Format attendu : liste de dicts avec les memes cles.
    """
    lines = []
    for item in data:
        line = (
            f"'{item.get('terme_metier', '')}' correspond a "
            f"{item.get('table_sql', '')}.{item.get('colonne_sql', '')} "
            f"{item.get('condition', '')}"
        )
        lines.append(line)
    return "\n".join(lines)


if __name__ == "__main__":
    print("Test mapping avec fichier None :")
    print(repr(lire_mapping(None)))
    print("Retourne chaine vide -> OK")