"""
prompts/templates.py
Construction des prompts envoyes au LLM.
"""


def prompt_sql(
    question: str,
    contexte_rag: str,
    mapping_text: str = ""
) -> str:
    """
    Construit le prompt complet pour generer le SQL.
    Inclut : contexte RAG + mapping + regles + question.
    """

    mapping_section = ""
    if mapping_text:
        mapping_section = f"""
=== CORRESPONDANCES METIER (fichier mapping utilisateur) ===
{mapping_text}
"""

    return f"""
Tu es un expert en bases de donnees SQLite pour BH Bank.
Genere UNIQUEMENT une requete SQL valide. Aucune explication.
Aucune balise markdown. SQL brut uniquement.

=== SCHEMA DE LA BASE DE DONNEES ===
{contexte_rag}
{mapping_section}
=== REGLES SQL OBLIGATOIRES ===
- Utilise UNIQUEMENT les tables : customer, account, "transaction",
  balance_history, branch, card.
- CRITIQUE : "transaction" est un mot reserve SQLite.
  Toujours ecrire "transaction" avec des guillemets doubles.
  CORRECT   : FROM "transaction" t
  INCORRECT : FROM transaction
- Pour relier customer et transaction : passer par account.
  FROM customer c
  JOIN account a ON a.customer_id = c.customer_id
  JOIN "transaction" t ON t.account_id = a.account_id
- Ajoute toujours LIMIT 20 sauf si COUNT ou SUM.
- status = 'Active' pour les clients actifs.
- status = 'Inactive' pour les clients inactifs.
- risk_level = 'High' pour haut risque.
- amount > 8000 pour les transactions suspectes.
- Dates : date('now', '-30 days') pour les 30 derniers jours.
- Mois en cours : strftime('%Y-%m', colonne) = strftime('%Y-%m', 'now')

=== QUESTION ===
{question}

=== REQUETE SQL ===
"""


def prompt_interpretation(
    question: str,
    resultats: str
) -> str:
    """
    Construit le prompt pour reformuler le resultat en francais.
    """

    return f"""
Tu es un assistant bancaire de BH Bank.
Un employe a pose cette question : "{question}"

Voici les resultats obtenus depuis la base de donnees :
{resultats}

Redige une reponse claire et concise en francais.
Maximum 3 phrases. Cite uniquement les chiffres importants.
Sois direct et professionnel. Pas de formules de politesse.
"""