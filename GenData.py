import sys
sys.stdout.reconfigure(encoding='utf-8')
"""
BH Bank — Générateur de données simulées
Génère les 6 tables du modèle T24 en fichiers Excel cohérents
"""
 
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
 
# ─── Reproductibilité ────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)
 
# ─── Dossier de sortie ───────────────────────────────────────────────
os.makedirs("data", exist_ok=True)
 
# ─── Helpers ─────────────────────────────────────────────────────────
def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))
 
def random_dates(start, end, n):
    delta = (end - start).days
    return [start + timedelta(days=int(d)) for d in np.random.randint(0, delta, n)]
 
DATE_MIN  = datetime(2021, 1, 1)
DATE_MAX  = datetime(2024, 12, 31)
TODAY     = datetime(2024, 12, 31)
 
# ─── Données réalistes Tunisie ────────────────────────────────────────
FIRST_NAMES_M = ["Mohamed","Ahmed","Ali","Omar","Youssef","Khaled","Bilel",
                 "Sami","Nizar","Amine","Hatem","Riadh","Tarek","Walid","Hichem"]
FIRST_NAMES_F = ["Rawen","Fatma","Amira","Sana","Nadia","Rania","Ines",
                 "Meriem","Salma","Asma","Leila","Yasmine","Rim","Dorra","Hana"]
LAST_NAMES    = ["Ben Ali","Mezzi","Trabelsi","Chaabane","Hamdi","Krid","Najar",
                 "Ben Salem","Gharbi","Jebali","Karoui","Mrad","Sfar","Zouari",
                 "Belhaj","Tlili","Guesmi","Farhani","Ben Amor","Khayat"]
CITIES        = ["Tunis","Sfax","Sousse","Gabès","Bizerte","Ariana","Gafsa",
                 "Monastir","Ben Arous","Nabeul","Médenine","Kasserine","Kairouan","Mahdia"]
REGIONS       = {"Tunis":"Grand Tunis","Sfax":"Sfax","Sousse":"Sahel",
                 "Gabès":"Sud","Bizerte":"Nord","Ariana":"Grand Tunis",
                 "Gafsa":"Ouest","Monastir":"Sahel","Ben Arous":"Grand Tunis",
                 "Nabeul":"Cap Bon","Médenine":"Sud","Kasserine":"Ouest",
                 "Kairouan":"Centre","Mahdia":"Sahel"}
PROFESSIONS   = ["Ingénieur","Médecin","Enseignant","Commerçant","Avocat",
                 "Fonctionnaire","Entrepreneur","Architecte","Pharmacien","Comptable",
                 "Informaticien","Agriculteur","Retraité","Étudiant","Infirmier"]
MERCHANTS     = ["Carrefour","Monoprix","Géant","MG","Banque Postale","STEG",
                 "SONEDE","Orange TN","Ooredoo","Shell","Total","ONAS","CNSS",
                 "Pharmacie Centrale","Librairie El Kitab","Restaurant Le Baroque",
                 "Hôtel Laico","Air Tunisia","Tunisair","SNCFT"]
CATEGORIES    = ["Alimentation","Santé","Éducation","Transport","Énergie","Telecom",
                 "Hôtellerie","Vêtements","Loisirs","Services publics","Autres"]
ACCOUNT_TYPES = ["Courant","Épargne","DAT","Professionnel"]
CARD_TYPES    = ["Visa","Mastercard","CIB"]
CARD_LEVELS   = ["Classic","Gold","Platinum"]
BRANCH_NAMES  = [
    ("BH Bank Tunis Centre","Tunis"),("BH Bank Ariana","Ariana"),
    ("BH Bank Ben Arous","Ben Arous"),("BH Bank Sfax","Sfax"),
    ("BH Bank Sousse","Sousse"),("BH Bank Monastir","Monastir"),
    ("BH Bank Bizerte","Bizerte"),("BH Bank Nabeul","Nabeul"),
    ("BH Bank Gabès","Gabès"),("BH Bank Gafsa","Gafsa"),
    ("BH Bank Kairouan","Kairouan"),("BH Bank Médenine","Médenine"),
    ("BH Bank Mahdia","Mahdia"),("BH Bank Kasserine","Kasserine"),
]
 
# ═══════════════════════════════════════════════════════════════════════
# 1. BRANCH  (14 agences)
# ═══════════════════════════════════════════════════════════════════════
print("Génération de BRANCH...")
branch_data = []
for i, (name, city) in enumerate(BRANCH_NAMES, start=1):
    branch_data.append({
        "branch_id"  : i,
        "branch_name": name,
        "city"       : city,
        "region"     : REGIONS.get(city, "Autre"),
        "country"    : "Tunisie"
    })
df_branch = pd.DataFrame(branch_data)
df_branch.to_excel("data/BRANCH.xlsx", index=False, sheet_name="Sheet1")
print(f"  → {len(df_branch)} agences générées")
 
branch_ids = df_branch["branch_id"].tolist()
 
# ═══════════════════════════════════════════════════════════════════════
# 2. CUSTOMER  (300 clients)
# ═══════════════════════════════════════════════════════════════════════
print("Génération de CUSTOMER...")
N_CUSTOMERS = 300
genders     = np.random.choice(["M","F"], N_CUSTOMERS, p=[0.55, 0.45])
 
# Dates de naissance : 18 à 75 ans
bdate_start = datetime(1949, 1, 1)
bdate_end   = datetime(2006, 12, 31)
birth_dates = random_dates(bdate_start, bdate_end, N_CUSTOMERS)
 
# Date création compte : entre 2015 et 2023
cdate_start = datetime(2015, 1, 1)
cdate_end   = datetime(2023, 12, 31)
created_dates = random_dates(cdate_start, cdate_end, N_CUSTOMERS)
 
customer_data = []
for i in range(N_CUSTOMERS):
    g = genders[i]
    fname = random.choice(FIRST_NAMES_M if g == "M" else FIRST_NAMES_F)
    lname = random.choice(LAST_NAMES)
    customer_data.append({
        "customer_id" : i + 1,
        "first_name"  : fname,
        "last_name"   : lname,
        "gender"      : g,
        "birth_date"  : birth_dates[i].strftime("%Y-%m-%d"),
        "segment"     : np.random.choice(["Retail","Corporate"], p=[0.80, 0.20]),
        "country"     : "Tunisie",
        "city"        : random.choice(CITIES),
        "profession"  : random.choice(PROFESSIONS),
        "risk_level"  : np.random.choice(["Low","Medium","High"], p=[0.55, 0.35, 0.10]),
        "date_created": created_dates[i].strftime("%Y-%m-%d"),
        "status"      : np.random.choice(["Active","Inactive"], p=[0.82, 0.18])
    })
 
df_customer = pd.DataFrame(customer_data)
df_customer.to_excel("data/CUSTOMER.xlsx", index=False, sheet_name="Sheet1")
print(f"  → {len(df_customer)} clients générés")
 
customer_ids = df_customer["customer_id"].tolist()
 
# ═══════════════════════════════════════════════════════════════════════
# 3. ACCOUNT  (700 comptes)
# ═══════════════════════════════════════════════════════════════════════
print("Génération de ACCOUNT...")
N_ACCOUNTS = 700
 
# Dates d'ouverture entre 2015 et 2024
open_dates  = random_dates(datetime(2015,1,1), datetime(2024,6,30), N_ACCOUNTS)
statuses_ac = np.random.choice(["Active","Closed","Suspended"], N_ACCOUNTS, p=[0.85,0.10,0.05])
 
account_data = []
for i in range(N_ACCOUNTS):
    od = open_dates[i]
    st = statuses_ac[i]
    # close_date seulement si compte fermé
    close_date = None
    if st == "Closed":
        close_date = random_date(od, TODAY).strftime("%Y-%m-%d")
 
    account_data.append({
        "account_id"    : i + 1,
        "customer_id"   : random.choice(customer_ids),   # ← lié à CUSTOMER
        "account_number": f"BH{str(i+1).zfill(8)}",
        "account_type"  : random.choice(ACCOUNT_TYPES),
        "currency"      : np.random.choice(["TND","EUR","USD"], p=[0.85,0.10,0.05]),
        "balance"       : round(random.uniform(0, 150000), 2),
        "status"        : st,
        "open_date"     : od.strftime("%Y-%m-%d"),
        "close_date"    : close_date,
        "branch_id"     : random.choice(branch_ids)      # ← lié à BRANCH
    })
 
df_account = pd.DataFrame(account_data)
df_account.to_excel("data/ACCOUNT.xlsx", index=False, sheet_name="Sheet1")
print(f"  → {len(df_account)} comptes générés")
 
account_ids = df_account["account_id"].tolist()
 
# ═══════════════════════════════════════════════════════════════════════
# 4. TRANSACTION  (10 000 transactions)
# ═══════════════════════════════════════════════════════════════════════
print("Génération de TRANSACTION...")
N_TRANSACTIONS = 10000
 
# Dates de transaction entre 2021 et 2024
txn_dates = random_dates(DATE_MIN, DATE_MAX, N_TRANSACTIONS)
 
# Montants réalistes avec quelques anomalies (2% de transactions suspectes)
amounts = []
for _ in range(N_TRANSACTIONS):
    if random.random() < 0.02:          # 2% anomalies (montants très élevés)
        amounts.append(round(random.uniform(8000, 50000), 2))
    elif random.random() < 0.30:        # 30% petites transactions
        amounts.append(round(random.uniform(10, 200), 2))
    else:                               # 68% transactions normales
        amounts.append(round(random.uniform(200, 5000), 2))
 
transaction_data = []
for i in range(N_TRANSACTIONS):
    txn_type = np.random.choice(["Debit","Credit"], p=[0.65, 0.35])
    transaction_data.append({
        "transaction_id"  : i + 1,
        "account_id"      : random.choice(account_ids),   # ← lié à ACCOUNT
        "transaction_date": txn_dates[i].strftime("%Y-%m-%d"),
        "amount"          : amounts[i],
        "currency"        : np.random.choice(["TND","EUR","USD"], p=[0.85,0.10,0.05]),
        "transaction_type": txn_type,
        "channel"         : np.random.choice(["ATM","POS","Online","Agency"],
                                              p=[0.25,0.30,0.35,0.10]),
        "merchant_name"   : random.choice(MERCHANTS) if txn_type == "Debit" else None,
        "category"        : random.choice(CATEGORIES),
        "status"          : np.random.choice(["Completed","Pending","Failed"],
                                              p=[0.92,0.05,0.03]),
        "reference"       : f"REF{str(i+1).zfill(10)}",
        "country"         : np.random.choice(["Tunisie","France","Italie","Allemagne"],
                                              p=[0.88,0.05,0.04,0.03])
    })
 
df_transaction = pd.DataFrame(transaction_data)
df_transaction.to_excel("data/TRANSACTION.xlsx", index=False, sheet_name="Sheet1")
print(f"  → {len(df_transaction)} transactions générées")
print(f"     dont {sum(1 for a in amounts if a > 8000)} transactions suspectes (> 8000 TND)")
 
# ═══════════════════════════════════════════════════════════════════════
# 5. BALANCE_HISTORY  (10 000 enregistrements)
# ═══════════════════════════════════════════════════════════════════════
print("Génération de BALANCE_HISTORY...")
N_HISTORY = 10000
 
hist_dates = random_dates(DATE_MIN, DATE_MAX, N_HISTORY)
 
balance_history_data = []
for i in range(N_HISTORY):
    balance_history_data.append({
        "id"        : i + 1,
        "account_id": random.choice(account_ids),          # ← lié à ACCOUNT
        "date"      : hist_dates[i].strftime("%Y-%m-%d"),
        "balance"   : round(random.uniform(0, 200000), 2)  # balance ≥ 0 ✅
    })
 
df_balance = pd.DataFrame(balance_history_data)
df_balance.to_excel("data/BALANCE_HISTORY.xlsx", index=False, sheet_name="Sheet1")
print(f"  → {len(df_balance)} enregistrements d'historique générés")
 
# ═══════════════════════════════════════════════════════════════════════
# 6. CARD  (300 cartes — optionnel)
# ═══════════════════════════════════════════════════════════════════════
print("Génération de CARD...")
N_CARDS = 300
 
issue_dates  = random_dates(datetime(2018,1,1), datetime(2024,1,1), N_CARDS)
 
card_data = []
for i in range(N_CARDS):
    issue = issue_dates[i]
    expiry = issue + timedelta(days=365*3)   # validité 3 ans
    level  = random.choice(CARD_LEVELS)
    card_data.append({
        "card_id"     : i + 1,
        "account_id"  : random.choice(account_ids),        # ← lié à ACCOUNT
        "card_type"   : random.choice(CARD_TYPES),
        "card_level"  : level,
        "issue_date"  : issue.strftime("%Y-%m-%d"),
        "expiry_date" : expiry.strftime("%Y-%m-%d"),
        "status"      : np.random.choice(["Active","Blocked","Expired"],
                                          p=[0.80,0.10,0.10]),
        "limit_amount": {"Classic": 2000, "Gold": 5000, "Platinum": 15000}[level]
    })
 
df_card = pd.DataFrame(card_data)
df_card.to_excel("data/CARD.xlsx", index=False, sheet_name="Sheet1")
print(f"  → {len(df_card)} cartes générées")
 
# ═══════════════════════════════════════════════════════════════════════
# RÉSUMÉ FINAL
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "="*50)
print("✅ Génération terminée ! Fichiers créés dans /data/")
print("="*50)
print(f"  BRANCH.xlsx           → {len(df_branch):>6} lignes")
print(f"  CUSTOMER.xlsx         → {len(df_customer):>6} lignes")
print(f"  ACCOUNT.xlsx          → {len(df_account):>6} lignes")
print(f"  TRANSACTION.xlsx      → {len(df_transaction):>6} lignes")
print(f"  BALANCE_HISTORY.xlsx  → {len(df_balance):>6} lignes")
print(f"  CARD.xlsx             → {len(df_card):>6} lignes")
print(f"\n  TOTAL                 → {len(df_branch)+len(df_customer)+len(df_account)+len(df_transaction)+len(df_balance)+len(df_card):>6} lignes")
 
# ─── Vérification cohérence FK ────────────────────────────────────────
print("\n🔍 Vérification des clés étrangères...")
 
# ACCOUNT → CUSTOMER
orphans = df_account[~df_account["customer_id"].isin(customer_ids)]
print(f"  Comptes sans client valide    : {len(orphans)} {'✅' if len(orphans)==0 else '❌'}")
 
# ACCOUNT → BRANCH
orphans2 = df_account[~df_account["branch_id"].isin(branch_ids)]
print(f"  Comptes sans agence valide    : {len(orphans2)} {'✅' if len(orphans2)==0 else '❌'}")
 
# TRANSACTION → ACCOUNT
orphans3 = df_transaction[~df_transaction["account_id"].isin(account_ids)]
print(f"  Transactions sans compte      : {len(orphans3)} {'✅' if len(orphans3)==0 else '❌'}")
 
# BALANCE_HISTORY → ACCOUNT
orphans4 = df_balance[~df_balance["account_id"].isin(account_ids)]
print(f"  Historiques sans compte       : {len(orphans4)} {'✅' if len(orphans4)==0 else '❌'}")
 
# CARD → ACCOUNT
orphans5 = df_card[~df_card["account_id"].isin(account_ids)]
print(f"  Cartes sans compte            : {len(orphans5)} {'✅' if len(orphans5)==0 else '❌'}")
 
print("\n🎉 Données prêtes à charger dans SQLite !")