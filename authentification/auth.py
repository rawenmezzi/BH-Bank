"""
authentification/auth.py
Gestion des utilisateurs et tokens JWT.
Utilise hashlib au lieu de bcrypt pour eviter les conflits.
"""

import os
import hashlib
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "bhbank_secret_key_2025")
ALGORITHM  = "HS256"
EXPIRATION = 60 * 8  # 8 heures

# ── Fonction de hashage simple ────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed

# ── Utilisateurs ──────────────────────────────────────────────────
UTILISATEURS = {
    "user": {
        "username" : "user",
        "password" : hash_password("user123"),
        "role"     : "utilisateur"
    },
    "admin": {
        "username" : "admin",
        "password" : hash_password("admin123"),
        "role"     : "administrateur"
    }
}

# ── Fonctions ─────────────────────────────────────────────────────
def verifier_utilisateur(username: str, password: str):
    user = UTILISATEURS.get(username)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user

def creer_token(username: str, role: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=EXPIRATION)
    payload = {
        "sub"  : username,
        "role" : role,
        "exp"  : expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verifier_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return {
            "username" : payload.get("sub"),
            "role"     : payload.get("role")
        }
    except JWTError:
        return None