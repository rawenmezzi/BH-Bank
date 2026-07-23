"""
authentification/auth.py
Gestion des utilisateurs et tokens JWT.
Utilise hashlib au lieu de bcrypt pour eviter les conflits.
"""

import os
import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "bhbank_secret_key_2025")
ALGORITHM  = "HS256"
EXPIRATION = 60 * 8  # 8 heures
ACTION_EXPIRATION = 10  # 10 minutes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

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
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRATION)
    payload = {
        "sub"  : username,
        "role" : role,
        "type" : "access",
        "exp"  : expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verifier_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        if payload.get("type") != "access":
            return None
        return {
            "username" : payload.get("sub"),
            "role"     : payload.get("role")
        }
    except JWTError:
        return None


def utilisateur_courant(token: str = Depends(oauth2_scheme)) -> dict:
    """Extrait l'identité depuis le token, jamais depuis le formulaire client."""
    utilisateur = verifier_token(token)
    if not utilisateur or not utilisateur.get("username"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session invalide ou expirée.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return utilisateur


def exiger_administrateur(
    utilisateur: dict = Depends(utilisateur_courant),
) -> dict:
    if utilisateur.get("role") != "administrateur":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cette opération est réservée aux administrateurs.",
        )
    return utilisateur


def creer_token_action(sql: str, username: str) -> str:
    """Signe le SQL prévisualisé pour empêcher sa modification côté client."""
    payload = {
        "sub": username,
        "sql": sql,
        "type": "admin_action",
        "jti": str(uuid.uuid4()),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACTION_EXPIRATION),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verifier_token_action(token: str, username: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if (
            payload.get("type") != "admin_action"
            or payload.get("sub") != username
            or not payload.get("sql")
        ):
            return None
        return payload
    except JWTError:
        return None