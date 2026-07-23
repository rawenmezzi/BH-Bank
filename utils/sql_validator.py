"""
utils/sql_validator.py
Validation et securisation des requetes SQL generees.
"""

import re


TABLES_AUTORISEES = {
    "customer",
    "account",
    "transaction",
    "balance_history",
    "branch",
    "card",
}

OPERATIONS_ADMIN = {"SELECT", "INSERT", "UPDATE", "DELETE"}
OPERATIONS_UTILISATEUR = {"SELECT"}

# Interdites pour tous les rôles, y compris dans une seconde instruction.
OPERATIONS_DANGEREUSES = {
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "PRAGMA",
    "ATTACH",
    "DETACH",
    "VACUUM",
    "REINDEX",
    "GRANT",
    "REVOKE",
}


def valider_sql(sql: str, role: str = "utilisateur") -> tuple[bool, str]:
    """
    Verifie que la requete SQL est sure et autorisee.

    Retourne : (True, "OK") si valide
               (False, "message d erreur") si invalide
    """

    if not sql or not sql.strip():
        return False, "La requete SQL est vide."

    sql_normalise = sql.strip()
    if sql_normalise.endswith(";"):
        sql_normalise = sql_normalise[:-1].strip()

    # Une seule instruction, sans commentaires SQL.
    if ";" in sql_normalise:
        return False, "Une seule instruction SQL est autorisée."
    if re.search(r"--|/\*|\*/", sql_normalise):
        return False, "Les commentaires SQL ne sont pas autorisés."

    sql_upper = sql_normalise.upper()
    operation = type_requete_sql(sql_normalise)
    operations_permises = (
        OPERATIONS_ADMIN
        if role == "administrateur"
        else OPERATIONS_UTILISATEUR
    )

    if operation not in operations_permises:
        return False, (
            f"Opération {operation or 'inconnue'} non autorisée "
            f"pour le rôle '{role}'."
        )

    for mot in OPERATIONS_DANGEREUSES:
        if re.search(rf"\b{mot}\b", sql_upper):
            return False, f"Opération dangereuse interdite : {mot}."

    if re.search(
        r"\b(?:LOAD_EXTENSION|READFILE|WRITEFILE)\s*\(|\bSQLITE_",
        sql_upper,
    ):
        return False, "Fonction ou objet interne SQLite interdit."

    # Évite les modifications globales accidentelles.
    if operation in {"UPDATE", "DELETE"} and not re.search(
        r"\bWHERE\b", sql_upper
    ):
        return False, (
            f"Une clause WHERE est obligatoire pour toute opération {operation}."
        )

    tables_utilisees = extraire_tables(sql)
    tables_inconnues = tables_utilisees - TABLES_AUTORISEES

    if tables_inconnues:
        return False, (
            f"Tables inconnues detectees : {tables_inconnues}. "
            f"Tables disponibles : {TABLES_AUTORISEES}"
        )

    if operation in {"INSERT", "UPDATE", "DELETE"} and len(tables_utilisees) != 1:
        return False, "L'action doit cibler exactement une table autorisée."

    return True, "OK"


def extraire_tables(sql: str) -> set:
    """
    Extrait les noms de tables mentionnes dans la requete SQL.
    """
    sql_lower = sql.lower()
    pattern = (
        r"(?:from|join|into|update)\s+"
        r"(?:[\"`\[])?([a-zA-Z_][a-zA-Z0-9_]*)(?:[\"`\]])?"
    )
    return set(re.findall(pattern, sql_lower))


def type_requete_sql(sql: str) -> str:
    """Retourne le premier verbe SQL reconnu."""
    match = re.match(r"^\s*(SELECT|INSERT|UPDATE|DELETE)\b", sql, re.IGNORECASE)
    return match.group(1).upper() if match else ""


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