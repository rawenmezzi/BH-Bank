"""
utils/sql_validator.py
Validation et securisation des requetes SQL generees.
"""

import re


# Mots interdits selon le role
MOTS_INTERDITS_USER = [
    "DROP", "DELETE", "UPDATE", "INSERT",
    "ALTER", "TRUNCATE", "CREATE", "REPLACE"
]

MOTS_INTERDITS_ADMIN = [
    "DROP", "TRUNCATE", "ALTER", "CREATE"
]


def valider_sql(sql: str, role: str = "utilisateur") -> tuple[bool, str]:
    """
    Verifie que la requete SQL est sure et autorisee.

    Retourne : (True, "OK") si valide
               (False, "message d erreur") si invalide
    """

    if not sql or not sql.strip():
        return False, "La requete SQL est vide."

    sql_upper = sql.strip().upper()

    # Doit commencer par SELECT
    if not sql_upper.startswith("SELECT"):
        return False, (
            "Requete non autorisee. "
            "Seules les requetes SELECT sont permises."
        )

    # Verifier les mots interdits selon le role
    if role == "administrateur":
        mots = MOTS_INTERDITS_ADMIN
    else:
        mots = MOTS_INTERDITS_USER

    for mot in mots:
        pattern = r'\b' + mot + r'\b'
        if re.search(pattern, sql_upper):
            return False, (
                f"Operation non autorisee detectee : {mot}. "
                f"Votre role '{role}' ne permet pas cette operation."
            )

    # Verifier que les tables utilisees sont connues
    tables_connues = {
        "customer", "account", "transaction",
        "balance_history", "branch", "card"
    }

    tables_utilisees = extraire_tables(sql)
    tables_inconnues = tables_utilisees - tables_connues

    if tables_inconnues:
        return False, (
            f"Tables inconnues detectees : {tables_inconnues}. "
            f"Tables disponibles : {tables_connues}"
        )

    return True, "OK"


def extraire_tables(sql: str) -> set:
    """
    Extrait les noms de tables mentionnes dans la requete SQL.
    """
    sql_lower = sql.lower()

    # Chercher apres FROM et JOIN
    pattern = r'(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
    matches = re.findall(pattern, sql_lower)

    return set(matches)


def nettoyer_sql(sql_brut: str) -> str:
    """
    Nettoie le SQL genere par le LLM.
    Supprime les balises markdown et les espaces superflus.
    """
    sql = sql_brut.strip()
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.replace("SQL:", "")
    sql = sql.replace("sql:", "")
    sql = sql.strip()
    return sql


if __name__ == "__main__":

    print("=" * 55)
    print("TESTS VALIDATEUR SQL")
    print("=" * 55)

    tests = [
        # (sql, role, attendu)
        (
            "SELECT COUNT(*) FROM customer WHERE status = 'Active'",
            "utilisateur",
            True
        ),
        (
            "DELETE FROM customer WHERE customer_id = 1",
            "utilisateur",
            False
        ),
        (
            "SELECT * FROM customer; DROP TABLE customer",
            "utilisateur",
            False
        ),
        (
            "SELECT * FROM table_inconnue",
            "utilisateur",
            False
        ),
        (
            "SELECT * FROM customer JOIN account ON account.customer_id = customer.customer_id",
            "utilisateur",
            True
        ),
    ]

    for sql, role, attendu in tests:
        ok, msg = valider_sql(sql, role)
        statut = "OK" if ok == attendu else "ECHEC"
        print(f"\n[{statut}] {sql[:50]}...")
        print(f"       Role : {role} | Valide : {ok} | Message : {msg}")