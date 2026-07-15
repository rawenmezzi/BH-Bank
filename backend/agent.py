"""
backend/agent.py

Pipeline complet NL2SQL :
Question -> Analyse -> RAG -> Prompt -> LLM -> Validation -> SQLite -> Reponse NL
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import pandas as pd
from dotenv import load_dotenv

from analyse.analyzer    import QuestionAnalyzer
from rag.indexer         import search, INDEX_PATH
from mapping.reader      import lire_mapping
from prompts.templates   import prompt_sql, prompt_interpretation
from llm.llm_client      import generer_sql, interpreter
from utils.sql_validator import valider_sql, nettoyer_sql

load_dotenv()

# ── Config ────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, os.getenv("DB_PATH", "database/bh_bank.db"))

analyzer = QuestionAnalyzer()


# ══════════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE
# ══════════════════════════════════════════════════════════════════

def repondre(
    question: str,
    mapping_file=None,
    role: str = "utilisateur"
) -> dict:
    """
    Pipeline complet : recoit une question en NL,
    retourne la reponse + SQL + donnees brutes.

    Parametres :
        question     : question en langage naturel
        mapping_file : fichier mapping uploade (optionnel)
        role         : 'utilisateur' ou 'administrateur'

    Retourne un dict :
        {
            "reponse"      : str   <- reponse en francais
            "sql"          : str   <- requete SQL generee
            "donnees"      : df    <- DataFrame pandas
            "nb_resultats" : int   <- nombre de lignes
            "etapes"       : dict  <- details de chaque etape
        }
        ou
        {
            "erreur" : str
            "sql"    : str (si disponible)
        }
    """

    etapes = {}

    # ── ETAPE 1 : Analyse de la question ─────────────────────────
    print(f"\n[1/6] Analyse de la question...")
    analyse = analyzer.analyze(question)
    etapes["analyse"] = analyse
    print(f"      Tables detectees : {analyse['tables']}")
    print(f"      Type requete     : {analyse['type_requete']}")

    # ── ETAPE 2 : Lecture du mapping ──────────────────────────────
    print(f"[2/6] Lecture du mapping...")
    mapping_text = lire_mapping(mapping_file)
    etapes["mapping"] = mapping_text if mapping_text else "Aucun mapping fourni"
    print(f"      Mapping : {'charge' if mapping_text else 'aucun'}")

    # ── ETAPE 3 : RAG — recherche des passages pertinents ─────────
    print(f"[3/6] Recherche RAG...")

    # Enrichir la question avec les tables detectees
    question_enrichie = question
    if analyse["tables"]:
        tables_str = " ".join(analyse["tables"]).lower()
        question_enrichie = f"{question} {tables_str}"

    passages = search(question_enrichie, k=3)
    contexte = "\n\n".join(passages)
    etapes["rag_passages"] = passages
    print(f"      {len(passages)} passages recuperes")

    # ── ETAPE 4 : Construction du prompt ─────────────────────────
    print(f"[4/6] Construction du prompt...")
    prompt = prompt_sql(question, contexte, mapping_text)
    etapes["prompt_length"] = len(prompt)
    print(f"      Prompt : {len(prompt)} caracteres")

    # ── ETAPE 5 : LLM + Validation + Execution (avec retry) ──────
    print(f"[5/6] Generation SQL + Execution...")
    df     = None
    sql    = None
    prompt_courant = prompt

    for tentative in range(1, 4):
        print(f"      Tentative {tentative}/3...")

        # LLM genere le SQL
        sql_brut = generer_sql(prompt_courant)
        sql      = nettoyer_sql(sql_brut)
        print(f"      SQL : {sql[:60]}...")

        # Validation securite
        ok, message = valider_sql(sql, role)
        if not ok:
            etapes["erreur_validation"] = message
            return {"erreur": message, "sql": sql}

        # Execution sur SQLite
        df, erreur = _executer_sql(sql)

        if erreur:
            print(f"      Erreur SQL : {erreur}")
            # Renvoyer l erreur au LLM pour correction
            prompt_courant = (
                prompt_courant
                + f"\n\nERREUR SQL OBTENUE : {erreur}"
                + f"\nSQL INCORRECT : {sql}"
                + "\nCorrige la requete en tenant compte de cette erreur."
            )
            continue

        # Succes
        print(f"      Succes : {len(df)} lignes retournees")
        break

    if df is None:
        return {
            "erreur": "Impossible de generer une requete valide apres 3 tentatives.",
            "sql": sql
        }

    etapes["sql_final"]     = sql
    etapes["nb_resultats"]  = len(df)

    # ── ETAPE 6 : Interpretation en langage naturel ───────────────
    print(f"[6/6] Interpretation du resultat...")

    if df.empty:
        reponse_nl = "Aucun resultat trouve pour cette question dans la base de donnees."
    else:
        resultats_str = df.head(10).to_string(index=False)
        reponse_nl    = interpreter(question, resultats_str)

    etapes["reponse"] = reponse_nl

    print(f"      Reponse generee.")
    print(f"\n{'='*55}")
    print(f"REPONSE : {reponse_nl[:100]}...")
    print(f"{'='*55}\n")

    return {
        "reponse"      : reponse_nl,
        "sql"          : sql,
        "donnees"      : df,
        "nb_resultats" : len(df),
        "etapes"       : etapes
    }


# ══════════════════════════════════════════════════════════════════
# EXECUTION SQL INTERNE
# ══════════════════════════════════════════════════════════════════

def _executer_sql(sql: str):
    """
    Execute le SQL sur bh_bank.db.
    Retourne (DataFrame, None) si succes
    Retourne (None, message_erreur) si echec
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        df   = pd.read_sql_query(sql, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, str(e)


# ══════════════════════════════════════════════════════════════════
# TEST
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("=" * 55)
    print("TEST PIPELINE COMPLET")
    print("=" * 55)

    questions = [
        "Combien de clients actifs y a-t-il ?",
        "Quels sont les 5 clients avec le plus de transactions ?",
        "Quel est le volume total des transactions ce mois-ci ?",
    ]

    for q in questions:
        print(f"\nQUESTION : {q}")
        print("-" * 55)

        resultat = repondre(q, role="utilisateur")

        if "erreur" in resultat:
            print(f"ERREUR : {resultat['erreur']}")
        else:
            print(f"REPONSE    : {resultat['reponse']}")
            print(f"SQL        : {resultat['sql']}")
            print(f"RESULTATS  : {resultat['nb_resultats']} lignes")