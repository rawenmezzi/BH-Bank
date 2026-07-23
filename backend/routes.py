"""
backend/routes.py
Endpoints FastAPI du système.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import tempfile

from backend.agent import executer_action_confirmee, repondre
from backend.evaluator import evaluer_question
from database.history import (
    enregistrer_question,
    lister_conversations_utilisateur,
    questions_frequentes,
    questions_recentes,
    sauvegarder_conversation,
    statistiques_globales,
)
from authentification.auth import (
    creer_token_action,
    exiger_administrateur,
    utilisateur_courant,
    verifier_token_action,
)

router = APIRouter()
TOKENS_ACTION_UTILISES: set[str] = set()


# ── Modèles Pydantic ──────────────────────────────────────────────

class QuestionRequest(BaseModel):
    question: str
    role: str = "utilisateur"


class ReponseModel(BaseModel):
    reponse: str
    sql: str
    nb_resultats: int


class ActionRequest(BaseModel):
    action_token: str
    confirmation: bool


class ValidationRequest(BaseModel):
    question: str
    sql_reference: str


class ConversationModel(BaseModel):
    id: str
    title: str = "Nouvelle analyse"
    departement: str = "Tous les départements"
    created_at: Optional[str] = None
    messages: list = []


# ══════════════════════════════════════════════════════════════════
# ENDPOINT PRINCIPAL — /ask
# ══════════════════════════════════════════════════════════════════

@router.post("/ask")
async def poser_question(
    question: str = Form(...),
    mapping_file: Optional[UploadFile] = File(default=None),
    utilisateur: dict = Depends(utilisateur_courant),
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
            role=utilisateur["role"],
        )

        if "erreur" in resultat:
            enregistrer_question(
                username=utilisateur["username"],
                role=utilisateur["role"],
                question=question,
                sql_genere=resultat.get("sql", ""),
                succes=False,
                erreur=resultat["erreur"],
            )
            return JSONResponse(
                status_code=400,
                content={
                    "erreur": resultat["erreur"],
                    "sql": resultat.get("sql", "")
                }
            )

        if resultat.get("confirmation_requise"):
            enregistrer_question(
                username=utilisateur["username"],
                role=utilisateur["role"],
                question=question,
                sql_genere=resultat.get("sql", ""),
                nb_resultats=resultat.get("nb_lignes_affectees", 0),
                succes=True,
            )
            resultat["action_token"] = creer_token_action(
                resultat["sql"],
                utilisateur["username"],
            )
            return resultat

        enregistrer_question(
            username=utilisateur["username"],
            role=utilisateur["role"],
            question=question,
            sql_genere=resultat.get("sql", ""),
            nb_resultats=resultat.get("nb_resultats", 0),
            succes=True,
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


@router.post("/execute-action")
def executer_action(
    requete: ActionRequest,
    administrateur: dict = Depends(exiger_administrateur),
):
    """Exécute une action prévisualisée après confirmation explicite."""
    if not requete.confirmation:
        raise HTTPException(
            status_code=400,
            detail="La confirmation explicite est obligatoire.",
        )

    payload = verifier_token_action(
        requete.action_token,
        administrateur["username"],
    )
    if not payload:
        raise HTTPException(
            status_code=400,
            detail="Confirmation invalide ou expirée.",
        )

    identifiant = payload["jti"]
    if identifiant in TOKENS_ACTION_UTILISES:
        raise HTTPException(
            status_code=409,
            detail="Cette action a déjà été exécutée.",
        )

    TOKENS_ACTION_UTILISES.add(identifiant)
    resultat = executer_action_confirmee(
        payload["sql"],
        administrateur["username"],
    )
    if "erreur" in resultat:
        return JSONResponse(status_code=400, content=resultat)
    return resultat


@router.post("/validate-question")
def valider_question(
    requete: ValidationRequest,
    _administrateur: dict = Depends(exiger_administrateur),
):
    """Compare une question NL2SQL à un SQL de référence."""
    try:
        resultat = evaluer_question(
            requete.question,
            requete.sql_reference,
        )
    except Exception as error:  # noqa: BLE001 - renvoyer un JSON exploitable
        return JSONResponse(
            status_code=500,
            content={"erreur": f"Échec de l'évaluation : {error}"},
        )

    if "erreur" in resultat and "conforme" not in resultat:
        return JSONResponse(status_code=400, content=resultat)
    return jsonable_encoder(resultat)


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
def lister_tables(_utilisateur: dict = Depends(utilisateur_courant)):
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


# ══════════════════════════════════════════════════════════════════
# HISTORIQUE DES QUESTIONS
# ══════════════════════════════════════════════════════════════════

@router.get("/questions/frequent")
def lister_questions_frequentes(
    limit: int = 10,
    _utilisateur: dict = Depends(utilisateur_courant),
):
    """Questions les plus posées (succès uniquement)."""
    limite = max(1, min(limit, 20))
    return {"questions": questions_frequentes(limite)}


@router.get("/questions/recent")
def lister_questions_recentes(
    limit: int = 8,
    utilisateur: dict = Depends(utilisateur_courant),
):
    """Dernières questions de l'utilisateur connecté."""
    limite = max(1, min(limit, 20))
    return {
        "questions": questions_recentes(utilisateur["username"], limite)
    }


@router.get("/questions/stats")
def stats_questions(_admin: dict = Depends(exiger_administrateur)):
    """Statistiques globales d'utilisation (admin)."""
    return statistiques_globales()


# ══════════════════════════════════════════════════════════════════
# HISTORIQUE DES DISCUSSIONS (par utilisateur)
# ══════════════════════════════════════════════════════════════════

@router.get("/conversations")
def lister_conversations(
    limit: int = 25,
    utilisateur: dict = Depends(utilisateur_courant),
):
    """Discussions sauvegardées de l'utilisateur connecté."""
    limite = max(1, min(limit, 50))
    return {
        "conversations": lister_conversations_utilisateur(
            utilisateur["username"],
            limite,
        )
    }


@router.put("/conversations/{conversation_id}")
def enregistrer_conversation(
    conversation_id: str,
    conversation: ConversationModel,
    utilisateur: dict = Depends(utilisateur_courant),
):
    """Crée ou met à jour une discussion de l'utilisateur connecté."""
    if conversation.id != conversation_id:
        raise HTTPException(status_code=400, detail="Identifiant de conversation invalide.")

    payload = conversation.model_dump()
    sauvegarder_conversation(utilisateur["username"], payload)
    return {"ok": True, "conversation": payload}