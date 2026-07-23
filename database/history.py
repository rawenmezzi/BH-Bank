"""
Historique des questions posées à l'assistant.
Base SQLite dédiée (séparée de bh_bank.db).
"""

import json
import os
import sqlite3
from datetime import datetime, timezone


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_DB = os.path.join(BASE_DIR, "database", "question_history.db")


def init_history_db() -> None:
    """Crée la table si elle n'existe pas encore."""
    os.makedirs(os.path.dirname(HISTORY_DB), exist_ok=True)
    conn = sqlite3.connect(HISTORY_DB)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS question_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            question TEXT NOT NULL,
            question_norm TEXT NOT NULL,
            sql_genere TEXT,
            nb_resultats INTEGER DEFAULT 0,
            succes INTEGER NOT NULL DEFAULT 0,
            erreur TEXT,
            date_utc TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_qh_norm ON question_history(question_norm)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_qh_user_date ON question_history(username, date_utc)"
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_conversations (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT 'Nouvelle analyse',
            departement TEXT NOT NULL DEFAULT 'Tous les départements',
            messages_json TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_chat_user_updated
        ON chat_conversations(username, updated_at DESC)
        """
    )
    conn.commit()
    conn.close()


def _normaliser(question: str) -> str:
    return " ".join(question.lower().strip().split())


def enregistrer_question(
    username: str,
    role: str,
    question: str,
    sql_genere: str = "",
    nb_resultats: int = 0,
    succes: bool = False,
    erreur: str = "",
) -> None:
    """Enregistre une question et son résultat."""
    init_history_db()
    conn = sqlite3.connect(HISTORY_DB)
    conn.execute(
        """
        INSERT INTO question_history (
            username, role, question, question_norm,
            sql_genere, nb_resultats, succes, erreur, date_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            role,
            question.strip(),
            _normaliser(question),
            sql_genere or None,
            nb_resultats,
            1 if succes else 0,
            erreur or None,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def questions_frequentes(limit: int = 10) -> list[dict]:
    """Retourne les questions les plus posées (succès uniquement)."""
    init_history_db()
    conn = sqlite3.connect(HISTORY_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT
            MAX(question) AS question,
            COUNT(*) AS nb
        FROM question_history
        WHERE succes = 1
        GROUP BY question_norm
        ORDER BY nb DESC, MAX(date_utc) DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [{"question": row["question"], "nb": row["nb"]} for row in rows]


def questions_recentes(username: str, limit: int = 8) -> list[dict]:
    """Retourne les dernières questions d'un utilisateur."""
    init_history_db()
    conn = sqlite3.connect(HISTORY_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT question, date_utc, succes
        FROM question_history
        WHERE username = ?
        ORDER BY date_utc DESC
        LIMIT ?
        """,
        (username, limit),
    ).fetchall()
    conn.close()
    return [
        {
            "question": row["question"],
            "date_utc": row["date_utc"],
            "succes": bool(row["succes"]),
        }
        for row in rows
    ]


def statistiques_globales() -> dict:
    """Statistiques simples pour le tableau de bord admin."""
    init_history_db()
    conn = sqlite3.connect(HISTORY_DB)
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN succes = 1 THEN 1 ELSE 0 END) AS reussites,
            COUNT(DISTINCT username) AS utilisateurs
        FROM question_history
        """
    ).fetchone()
    conn.close()
    total = row[0] or 0
    reussites = row[1] or 0
    return {
        "total_questions": total,
        "reussites": reussites,
        "taux_reussite": round(reussites / total * 100, 1) if total else 0.0,
        "utilisateurs_actifs": row[2] or 0,
    }


def lister_conversations_utilisateur(username: str, limit: int = 25) -> list[dict]:
    """Retourne les discussions sauvegardées d'un utilisateur."""
    init_history_db()
    conn = sqlite3.connect(HISTORY_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT id, title, departement, messages_json, created_at, updated_at
        FROM chat_conversations
        WHERE username = ?
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (username, limit),
    ).fetchall()
    conn.close()

    conversations = []
    for row in rows:
        try:
            messages = json.loads(row["messages_json"] or "[]")
        except json.JSONDecodeError:
            messages = []
        conversations.append(
            {
                "id": row["id"],
                "title": row["title"],
                "departement": row["departement"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "messages": messages,
            }
        )
    return conversations


def sauvegarder_conversation(username: str, conversation: dict) -> None:
    """Crée ou met à jour une discussion complète."""
    init_history_db()
    now = datetime.now(timezone.utc).isoformat()
    messages = conversation.get("messages", [])
    conn = sqlite3.connect(HISTORY_DB)
    existant = conn.execute(
        "SELECT id FROM chat_conversations WHERE id = ? AND username = ?",
        (conversation["id"], username),
    ).fetchone()
    if existant:
        conn.execute(
            """
            UPDATE chat_conversations
            SET title = ?, departement = ?, messages_json = ?, updated_at = ?
            WHERE id = ? AND username = ?
            """,
            (
                conversation.get("title", "Nouvelle analyse"),
                conversation.get("departement", "Tous les départements"),
                json.dumps(messages, ensure_ascii=False, default=str),
                now,
                conversation["id"],
                username,
            ),
        )
    else:
        conn.execute(
            """
            INSERT INTO chat_conversations (
                id, username, title, departement,
                messages_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                conversation["id"],
                username,
                conversation.get("title", "Nouvelle analyse"),
                conversation.get("departement", "Tous les départements"),
                json.dumps(messages, ensure_ascii=False, default=str),
                conversation.get("created_at", now),
                now,
            ),
        )
    conn.commit()
    conn.close()
