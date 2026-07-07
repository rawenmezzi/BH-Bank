import os
import pandas as pd

from database.connection import engine
from database.models import Base

# ==========================================================
# Création de la base
# ==========================================================

print("=" * 60)
print("INITIALISATION DE LA BASE BH BANK")
print("=" * 60)

# Supprime toutes les tables
Base.metadata.drop_all(bind=engine)

# Recrée toutes les tables
Base.metadata.create_all(bind=engine)

print("Tables créées.\n")

# ==========================================================
# Dossier contenant les fichiers Excel
# ==========================================================

DATA_FOLDER = "data"

FILES = [
    ("BRANCH.xlsx", "branch"),
    ("CUSTOMER.xlsx", "customer"),
    ("ACCOUNT.xlsx", "account"),
    ("TRANSACTION.xlsx", "transaction"),
    ("BALANCE_HISTORY.xlsx", "balance_history"),
    ("CARD.xlsx", "card"),
]

# ==========================================================
# Import des données
# ==========================================================

for excel_file, table_name in FILES:

    file_path = os.path.join(DATA_FOLDER, excel_file)

    print(f"Import de {excel_file}...")

    if not os.path.exists(file_path):
        print(f"ERREUR : {excel_file} introuvable.\n")
        continue

    try:

        df = pd.read_excel(file_path)

        # Conversion automatique des colonnes Date
        for col in df.columns:
            if "date" in col.lower():
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Insertion dans SQLite
        df.to_sql(
            table_name,
            con=engine,
            if_exists="append",
            index=False
        )

        print(f"   {len(df)} lignes importées.")

    except Exception as e:

        print(f"Erreur lors de l'import de {excel_file}")
        print(e)

print()
print("=" * 60)
print("BASE BH BANK CRÉÉE AVEC SUCCÈS")
print("=" * 60)