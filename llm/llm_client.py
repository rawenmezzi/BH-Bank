"""
llm/llm_client.py

Module de communication avec l API Groq (Llama 3.3).
Modele utilise : llama-3.3-70b-versatile (gratuit)
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────
API_KEY    = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"

if not API_KEY:
    raise ValueError("GROQ_API_KEY manquante dans le fichier .env")

client = Groq(api_key=API_KEY)


# ══════════════════════════════════════════════════════════════════
# GENERER SQL
# ══════════════════════════════════════════════════════════════════

def generer_sql(prompt: str) -> str:
    """
    Envoie le prompt a Groq et retourne le SQL brut genere.
    Nettoie automatiquement les balises markdown.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un expert SQL specialise en SQLite "
                        "pour les bases de donnees bancaires. "
                        "Tu generes UNIQUEMENT du SQL brut, "
                        "sans aucune explication ni balise markdown."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=500,
        )

        sql_brut = response.choices[0].message.content.strip()

        # Nettoyer les balises markdown si presentes
        sql_brut = sql_brut.replace("```sql", "")
        sql_brut = sql_brut.replace("```", "")
        sql_brut = sql_brut.strip()

        return sql_brut

    except Exception as e:
        raise RuntimeError(f"Erreur Groq generation SQL : {e}")


# ══════════════════════════════════════════════════════════════════
# INTERPRETER RESULTAT
# ══════════════════════════════════════════════════════════════════

def interpreter(question: str, resultats: str, nombre_lignes: int) -> str:
    """
    Reformule les resultats SQL en langage naturel francais.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un analyste bancaire de BH Bank. "
                        "Reponds en francais avec 1 ou 2 phrases et 45 mots maximum. "
                        "Donne d'abord le resultat principal, puis au maximum un fait "
                        "complementaire utile. Utilise uniquement les informations "
                        "explicitement presentes dans les resultats SQL. "
                        "N'invente aucune cause, recommandation, tendance, revenu ou "
                        "valeur absente. N'ajoute ni introduction ni formule de politesse."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Question posee : {question}\n\n"
                        f"Nombre de lignes retournees : {nombre_lignes}\n\n"
                        f"Resultats de la base de donnees :\n{resultats}\n\n"
                        "Produis une synthese factuelle, precise et professionnelle."
                    )
                }
            ],
            temperature=0.1,
            max_tokens=120,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"Erreur Groq interpretation : {e}")


# ══════════════════════════════════════════════════════════════════
# TEST
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("=" * 55)
    print("TEST CONNEXION GROQ API")
    print("=" * 55)

    # Test 1 : generation SQL
    print("\nTest 1 : Generation SQL")
    prompt_test = """
Tables SQLite disponibles : customer, account, transaction
Regles : utilise UNIQUEMENT SELECT, LIMIT 20.

Question : Combien de clients actifs y a-t-il ?

REQUETE SQL :
"""
    sql = generer_sql(prompt_test)
    print(f"SQL genere :\n{sql}")

    # Test 2 : interpretation
    print("\nTest 2 : Interpretation en francais")
    reponse = interpreter(
        question="Combien de clients actifs ?",
        resultats="count(*) = 246",
        nombre_lignes=1
    )
    print(f"Reponse NL :\n{reponse}")

    print("\nGroq API fonctionne correctement !")