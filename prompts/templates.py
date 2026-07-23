"""
prompts/templates.py
Construction des prompts envoyes au LLM.
"""

FEW_SHOT_EXAMPLES = """
=== FEW-SHOT EXAMPLES ===

--- Relation Client ---
Q: Informations du client Mohamed Mezzi
SQL:
SELECT customer_id, first_name, last_name,
       city, profession, risk_level,
       segment, status, date_created
FROM customer
WHERE first_name LIKE '%Mohamed%'
AND last_name LIKE '%Mezzi%'
LIMIT 5

Q: Comptes et soldes associes a un client
SQL:
SELECT a.account_number, a.account_type,
       a.currency, a.balance, a.status,
       a.open_date, b.branch_name, b.city
FROM account a
JOIN branch b ON b.branch_id = a.branch_id
WHERE a.customer_id = 42
ORDER BY a.balance DESC

--- Audit ---
Q: Transactions suspectes superieures a 8000 TND en 2024
SQL:
SELECT c.first_name, c.last_name,
       t.amount, t.transaction_date,
       t.country, t.channel
FROM "transaction" t
JOIN account a ON a.account_id = t.account_id
JOIN customer c ON c.customer_id = a.customer_id
WHERE t.amount > 8000
AND strftime('%Y', t.transaction_date) = '2024'
ORDER BY t.amount DESC
LIMIT 20

Q: Transactions effectuees depuis l etranger
SQL:
SELECT c.first_name, c.last_name,
       t.amount, t.country,
       t.transaction_date, t.channel,
       t.transaction_type
FROM "transaction" t
JOIN account a ON a.account_id = t.account_id
JOIN customer c ON c.customer_id = a.customer_id
WHERE t.country != 'Tunisie'
ORDER BY t.transaction_date DESC
LIMIT 20

--- Marketing ---
Q: Clients n ayant pas effectue de transaction depuis 6 mois
SQL:
SELECT c.first_name, c.last_name, c.city,
       MAX(t.transaction_date) AS derniere_transaction
FROM customer c
JOIN account a ON a.customer_id = c.customer_id
LEFT JOIN "transaction" t ON t.account_id = a.account_id
WHERE c.status = 'Active'
GROUP BY c.customer_id
HAVING MAX(t.transaction_date) < date('now', '-6 months')
OR MAX(t.transaction_date) IS NULL
ORDER BY derniere_transaction ASC
LIMIT 20

Q: Top clients par volume de transactions en 2024
SQL:
SELECT c.first_name, c.last_name,
       c.city, c.segment,
       COUNT(t.transaction_id) AS nb_transactions,
       ROUND(SUM(t.amount), 2) AS volume_total
FROM "transaction" t
JOIN account a ON a.account_id = t.account_id
JOIN customer c ON c.customer_id = a.customer_id
WHERE strftime('%Y', t.transaction_date) = '2024'
GROUP BY c.customer_id
ORDER BY volume_total DESC
LIMIT 10

--- Direction ---
Q: Volume total des transactions par mois en 2024
SQL:
SELECT strftime('%Y-%m', transaction_date) AS mois,
       COUNT(*) AS nb_transactions,
       ROUND(SUM(amount), 2) AS volume_total
FROM "transaction"
WHERE strftime('%Y', transaction_date) = '2024'
GROUP BY mois
ORDER BY mois

Q: Performance des agences en 2024
SQL:
SELECT b.branch_name, b.city,
       COUNT(t.transaction_id) AS nb_transactions,
       ROUND(SUM(t.amount), 2) AS volume_total
FROM branch b
JOIN account a ON a.branch_id = b.branch_id
JOIN "transaction" t ON t.account_id = a.account_id
WHERE strftime('%Y', t.transaction_date) = '2024'
GROUP BY b.branch_id
ORDER BY nb_transactions DESC
LIMIT 10
"""


def prompt_sql(
    question: str,
    contexte_rag: str,
    mapping_text: str = "",
    role: str = "utilisateur",
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

    if role == "administrateur":
        permissions = """
=== PERMISSIONS ADMINISTRATEUR ===
- Pour une demande de consultation, genere SELECT.
- Pour une demande explicite de creation, modification ou suppression,
  genere respectivement INSERT, UPDATE ou DELETE.
- UPDATE et DELETE doivent toujours contenir une clause WHERE restrictive.
- Ne genere jamais DROP, ALTER, CREATE, TRUNCATE, PRAGMA ou plusieurs instructions.
- Ne modifie jamais une table si la demande est ambigue.
"""
    else:
        permissions = """
=== PERMISSIONS UTILISATEUR ===
- Genere uniquement SELECT. Toute modification est interdite.
"""

    return f"""
Tu es un expert en bases de donnees SQLite pour BH Bank.
Genere UNIQUEMENT une requete SQL valide. Aucune explication.
Aucune balise markdown. SQL brut uniquement.

=== SCHEMA DE LA BASE DE DONNEES ===
{contexte_rag}
{FEW_SHOT_EXAMPLES}
{mapping_section}
{permissions}
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
- CRITIQUE : plusieurs tables ont une colonne status. Choisis la table
  selon le SUJET de la question, jamais selon un mot isole :
    * comptes       -> account.status  (Active, Closed, Suspended)
    * clients       -> customer.status (Active, Inactive)
    * transactions  -> "transaction".status (Completed, Pending, Failed)
    * cartes        -> card.status     (Active, Blocked, Expired)
- Pour compter ou regrouper des COMPTES par statut : utilise account.status
  et la table account SEULE, sans jointure vers customer.
    CORRECT   : SELECT status, COUNT(*) FROM account GROUP BY status
    INCORRECT : SELECT c.status ... FROM customer c JOIN account a ...
- N'ajoute JAMAIS de jointure si une seule table suffit a repondre.
- SOLDE : pour un solde ou un solde moyen de comptes, utilise
  account.balance (table account SEULE). N'utilise balance_history
  que pour l'historique/evolution des soldes dans le temps.
    CORRECT   : SELECT AVG(balance) FROM account WHERE account_type = 'Épargne'
    INCORRECT : AVG(b.balance) FROM balance_history b JOIN account ...
- ACCENTS : respecte exactement les accents et la casse des valeurs
  texte du schema. Les comptes epargne s'ecrivent 'Épargne' (avec É),
  jamais 'Epargne'.
- customer.status = 'Active' pour les clients actifs.
- customer.status = 'Inactive' pour les clients inactifs.
- account.status = 'Active' pour les comptes actifs.
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