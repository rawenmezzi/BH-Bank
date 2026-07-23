"""
main.py
Point d entrée FastAPI.
Lance le serveur avec : uvicorn main:app --reload
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from backend.routes import router
from authentification.auth import verifier_utilisateur, creer_token
from database.history import init_history_db
from rag.indexer import build_index, INDEX_PATH


# ── Application FastAPI ───────────────────────────────────────────
app = FastAPI(
    title="BH Bank AI Agent",
    description="Agent IA pour l interrogation intelligente des donnees bancaires T24",
    version="1.0.0"
)

# ── CORS (pour Streamlit) ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────
app.include_router(router, prefix="/api")


# ── Initialisation au démarrage ───────────────────────────────────
@app.on_event("startup")
async def startup():
    """Initialise l'historique et construit l'index RAG si absent."""
    init_history_db()
    if not os.path.exists(INDEX_PATH):
        print("Index RAG absent. Construction...")
        build_index()
        print("Index RAG pret.")


# ── Endpoint Login ────────────────────────────────────────────────
@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = verifier_utilisateur(form.username, form.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Identifiants incorrects"
        )
    token = creer_token(user["username"], user["role"])
    return {
        "access_token" : token,
        "token_type"   : "bearer",
        "role"         : user["role"],
        "username"     : user["username"]
    }


# ── Health check racine ───────────────────────────────────────────
@app.get("/")
def root():
    return {
        "message" : "BH Bank AI Agent",
        "status"  : "operationnel",
        "docs"    : "/docs"
    }