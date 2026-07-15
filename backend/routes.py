"""
backend/routes.py
Endpoints FastAPI du système.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import tempfile

from backend.agent import repondre
from authentification.auth import verifier_token

router = APIRouter()


# ── Modèles Pydantic ──────────────────────────────────────────────

class QuestionRequest(BaseModel):
    question: str
    role: str = "utilisateur"


class ReponseModel(BaseModel):
    reponse: str
    sql: str
    nb_resultats: int


# ══════════════════════════════════════════════════════════════════
# ENDPOINT PRINCIPAL — /ask
# ══════════════════════════════════════════════════════════════════

@router.post("/ask")
async def poser_question(
    question: str = Form(...),
    role: str = Form(default="utilisateur"),
    mapping_file: Optional[UploadFile] = File(default=None)
):
    """
    Endpoint principal.
    Reçoit une question + mapping optionnel.
    Retourne la réponse en langage naturel + SQL + données.
    """

    # Sauvegarder le fichier mapping temporairement si fourni
    mapping_path = None
    if mapping_file and mapping_file.filename:
        suffix = os.path.splitext(mapping_file.filename)[1]
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:
            contenu = await mapping_file.read()
            tmp.write(contenu)
            mapping_path = tmp.name

    try:
        resultat = repondre(
            question=question,
            mapping_file=mapping_path,
            role=role
        )

        if "erreur" in resultat:
            return JSONResponse(
                status_code=400,
                content={
                    "erreur": resultat["erreur"],
                    "sql": resultat.get("sql", "")
                }
            )

        # Convertir le DataFrame en liste de dicts
        donnees_json = resultat["donnees"].to_dict(orient="records")

        return {
            "reponse"      : resultat["reponse"],
            "sql"          : resultat["sql"],
            "donnees"      : donnees_json,
            "nb_resultats" : resultat["nb_resultats"]
        }

    finally:
        # Supprimer le fichier temporaire
        if mapping_path and os.path.exists(mapping_path):
            os.remove(mapping_path)


# ══════════════════════════════════════════════════════════════════
# ENDPOINT SANTE — /health
# ══════════════════════════════════════════════════════════════════

@router.get("/health")
def health_check():
    """Vérifie que l API fonctionne."""
    return {"status": "ok", "message": "BH Bank AI Agent operationnel"}


# ══════════════════════════════════════════════════════════════════
# ENDPOINT TABLES — /tables
# ══════════════════════════════════════════════════════════════════

@router.get("/tables")
def lister_tables():
    """Retourne la liste des tables disponibles."""
    return {
        "tables": [
            "customer",
            "account",
            "transaction",
            "balance_history",
            "branch",
            "card"
        ]
    }