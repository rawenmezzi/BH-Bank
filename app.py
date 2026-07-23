"""
Interface Streamlit — BH Bank AI Agent.
"""

import base64
import html
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

API_URL = os.getenv("API_URL", "http://localhost:8000")
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
SIEGE_PATH = os.path.join(BASE_DIR, "assets", "fond.png")
QUESTIONS_PATH = os.path.join(BASE_DIR, "questions_reference.json")
DB_PATH = os.path.join(BASE_DIR, "database", "bh_bank.db")
BH_NAVY = "rgb(38, 72, 118)"

QUESTIONS_PAR_DEPARTEMENT = {
    "Tous les départements": [
        "Nombre de clients actifs",
        "Classement par volume de transactions",
        "Clients à profil de risque élevé",
        "Opérations atypiques — 2024",
        "Volume transactionnel par canal",
        "Agence à plus fort portefeuille",
        "Solde moyen des comptes épargne",
        "Répartition débit / crédit",
    ],
    "Relation Client — Agences": [
        "Profil complet d'un client",
        "Comptes et soldes associés",
        "Historique des transactions récentes",
        "Cartes bancaires du client",
        "Clients de l'agence de Tunis Centre",
    ],
    "Audit — Contrôle interne": [
        "Transactions suspectes en 2024",
        "Opérations effectuées depuis l'étranger",
        "Clients à haut risque avec grosses transactions",
        "Transactions échouées ce mois",
        "Clients avec fréquence de transactions élevée",
    ],
    "Marketing — CRM": [
        "Clients inactifs depuis 6 mois",
        "Clients premium par patrimoine",
        "Répartition Retail et Corporate par ville",
        "Clients sans carte bancaire",
        "Clients fidèles depuis plus de 2 ans",
    ],
    "Direction — Reporting": [
        "Volume transactionnel mensuel 2024",
        "Performance des agences en 2024",
        "Comptes ouverts ce mois",
        "Répartition des transactions par canal",
        "Top 10 clients par volume de transactions",
    ],
}

DEPARTEMENT_CONFIG = {
    "Tous les départements": {
        "badge": "Vue globale",
        "title": "Centre d'intelligence décisionnelle",
        "desc": "Analyse transversale sur l'ensemble des données BH Bank.",
        "gradient": "linear-gradient(135deg, #16181D 0%, #2A2D35 55%, #3D1F22 100%)",
        "kpi_label": "Indicateurs consolidés",
    },
    "Relation Client — Agences": {
        "badge": "Relation Client",
        "title": "Vision 360° Client",
        "desc": "Profils clients, comptes, cartes et suivi relationnel par agence.",
        "gradient": "linear-gradient(135deg, #16181D 0%, #1E2A3A 55%, #3D1F22 100%)",
        "kpi_label": "Indicateurs relation client",
    },
    "Audit — Contrôle interne": {
        "badge": "Audit & Conformité",
        "title": "Détection des anomalies",
        "desc": "Surveillance des opérations suspectes, risques AML et conformité.",
        "gradient": "linear-gradient(135deg, #16181D 0%, #2B2020 55%, #4A1518 100%)",
        "kpi_label": "Indicateurs de contrôle",
    },
    "Marketing — CRM": {
        "badge": "Marketing & CRM",
        "title": "Analyse commerciale",
        "desc": "Segmentation, fidélisation et opportunités commerciales.",
        "gradient": "linear-gradient(135deg, #16181D 0%, #252830 55%, #3A2228 100%)",
        "kpi_label": "Indicateurs CRM",
    },
    "Direction — Reporting": {
        "badge": "Direction Générale",
        "title": "Pilotage & reporting",
        "desc": "KPI stratégiques, performance réseau et volumes transactionnels.",
        "gradient": "linear-gradient(135deg, #121418 0%, #1F2228 50%, #2E181A 100%)",
        "kpi_label": "Indicateurs de pilotage",
    },
}

DEPARTEMENT_NAV = [
    ("Tous les départements", "Vue globale"),
    ("Relation Client — Agences", "Relation Client"),
    ("Audit — Contrôle interne", "Audit & Conformité"),
    ("Marketing — CRM", "Marketing & CRM"),
    ("Direction — Reporting", "Direction & Reporting"),
]

# --------------------------------------------------------------------------
# Contenu de la Vue globale (cockpit opérationnel BH Bank, usage employés).
# Utilisé uniquement par render_home_dashboard() et les fonctions render_home_*.
# --------------------------------------------------------------------------

_JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
_MOIS_FR = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]


def _date_francaise(moment: datetime) -> str:
    jour = _JOURS_FR[moment.weekday()].capitalize()
    mois = _MOIS_FR[moment.month - 1]
    return f"{jour} {moment.day} {mois} {moment.year}"


HOME_NETWORK_CITIES = [
    {"name": "Bizerte", "lat": 37.2744, "lon": 9.8739, "agences": 8},
    {"name": "Tunis", "lat": 36.8065, "lon": 10.1815, "agences": 42},
    {"name": "Nabeul", "lat": 36.4561, "lon": 10.7376, "agences": 10},
    {"name": "Kairouan", "lat": 35.6781, "lon": 10.0963, "agences": 9},
    {"name": "Sousse", "lat": 35.8256, "lon": 10.6369, "agences": 16},
    {"name": "Monastir", "lat": 35.7770, "lon": 10.8262, "agences": 7},
    {"name": "Sfax", "lat": 34.7406, "lon": 10.7603, "agences": 18},
    {"name": "Gabès", "lat": 33.8815, "lon": 10.0982, "agences": 6},
    {"name": "Médenine", "lat": 33.3549, "lon": 10.5055, "agences": 5},
    {"name": "Tataouine", "lat": 32.9297, "lon": 10.4518, "agences": 3},
]

HOME_DEPARTMENTS = [
    {
        "id": "Relation Client — Agences",
        "icon": "users",
        "title": "Relation Client",
        "desc": "Vision 360° des clients : profils, comptes, cartes et suivi relationnel par agence.",
    },
    {
        "id": "Audit — Contrôle interne",
        "icon": "search",
        "title": "Audit & Conformité",
        "desc": "Détection des anomalies, surveillance des risques et conformité réglementaire.",
    },
    {
        "id": "Marketing — CRM",
        "icon": "trending-up",
        "title": "Marketing & CRM",
        "desc": "Segmentation client, fidélisation et opportunités commerciales.",
    },
    {
        "id": "Direction — Reporting",
        "icon": "briefcase",
        "title": "Direction & Reporting",
        "desc": "KPI stratégiques, performance réseau et pilotage de l'activité.",
    },
]

_HOME_ICONS = {
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path>',
    "search": '<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>',
    "trending-up": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>',
    "bar-chart-2": '<line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line>',
    "credit-card": '<rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>',
    "alert-triangle": '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12" y2="17.01"></line>',
    "x-circle": '<circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line>',
    "globe": '<circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path>',
}


def _home_icon(name: str, size: int = 22) -> str:
    """Icône ligne minimaliste (jeu d'icônes maison, style Feather) en SVG inline."""
    inner = _HOME_ICONS.get(name, _HOME_ICONS["shield"])
    return (
        f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
        f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round">{inner}</svg>'
    )


st.set_page_config(
    page_title="BH Bank — Intelligence bancaire",
    page_icon=LOGO_PATH if os.path.exists(LOGO_PATH) else None,
    layout="wide",
    initial_sidebar_state="expanded",
)


def image_to_base64(path: str) -> str:
    """Retourne une image encodée, sans interrompre l'application si elle manque."""
    try:
        with open(path, "rb") as image:
            return base64.b64encode(image.read()).decode("utf-8")
    except OSError:
        return ""


@st.cache_data(show_spinner=False)
def _logo_base64() -> str:
    return image_to_base64(LOGO_PATH)


class _MappingFichier:
    """Wrapper minimal pour réutiliser un mapping uploadé entre les reruns."""

    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data

    def getvalue(self) -> bytes:
        return self._data


def _init_session_chat() -> None:
    defaults = {
        "conversations": [],
        "active_conv_id": None,
        "departement": "Tous les départements",
        "vue": "Assistant analytique",
        "conversations_loaded": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _charger_conversations_utilisateur() -> None:
    """Charge l'historique persistant depuis l'API (par compte utilisateur)."""
    if st.session_state.get("conversations_loaded"):
        return
    try:
        response = requests.get(
            f"{API_URL}/api/conversations",
            headers=_auth_headers(),
            timeout=15,
        )
        if response.ok:
            st.session_state.conversations = response.json().get("conversations", [])
        else:
            st.session_state.conversations = []
    except requests.RequestException:
        st.session_state.conversations = []
    st.session_state.conversations_loaded = True


def _persister_conversation(conv: dict) -> None:
    """Sauvegarde une discussion côté serveur (liée au compte connecté)."""
    try:
        requests.put(
            f"{API_URL}/api/conversations/{conv['id']}",
            json=conv,
            headers=_auth_headers(),
            timeout=20,
        )
    except requests.RequestException:
        pass


def _reinitialiser_vue_analyse() -> None:
    """Masque le détail d'analyse — affiche uniquement la zone de saisie."""
    st.session_state.active_conv_id = None


def _creer_conversation_question(
    question: str, resultat: dict, departement: str
) -> dict:
    """Crée une entrée d'historique unique par question posée."""
    conv_id = uuid.uuid4().hex[:10]
    titre = question[:48] + ("…" if len(question) > 48 else "")
    conv = {
        "id": conv_id,
        "title": titre,
        "departement": departement,
        "created_at": datetime.now().isoformat(),
        "messages": [
            {
                "role": "user",
                "content": question,
                "ts": datetime.now().isoformat(),
            },
            {
                "role": "assistant",
                "result": resultat,
                "ts": datetime.now().isoformat(),
            },
        ],
    }
    st.session_state.conversations.insert(0, conv)
    _persister_conversation(conv)
    return conv


def _conversation_active() -> dict | None:
    conv_id = st.session_state.get("active_conv_id")
    if not conv_id:
        return None
    for conv in st.session_state.conversations:
        if conv["id"] == conv_id:
            return conv
    return None


def _conversation_visible(departement: str) -> dict | None:
    """Retourne la conversation active seulement si elle appartient au département affiché."""
    conv = _conversation_active()
    if not conv or not conv.get("messages"):
        return None
    if (
        departement != "Tous les départements"
        and conv.get("departement") != departement
    ):
        return None
    return conv


def _ajouter_echange(question: str, resultat: dict, departement: str) -> None:
    _creer_conversation_question(question, resultat, departement)


def _get_mapping_actif(upload=None):
    if upload is not None:
        st.session_state.mapping_bytes = upload.getvalue()
        st.session_state.mapping_name = upload.name
    if st.session_state.get("mapping_bytes"):
        return _MappingFichier(
            st.session_state.get("mapping_name", "mapping"),
            st.session_state.mapping_bytes,
        )
    return None


def _formater_nombre(valeur: int) -> str:
    return f"{valeur:,}".replace(",", "\u202f")


def inject_global_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bh-red: #E31E24;
            --bh-red-dark: #B9151A;
            --bh-red-soft: #FFF1F2;
            --bh-ink: #16181D;
            --bh-navy: rgb(38, 72, 118);
            --bh-sidebar: rgb(10, 34, 64);
            --bh-muted: #69707D;
            --bh-line: #E8E9ED;
            --bh-surface: #FFFFFF;
            --bh-bg: #F6F7F9;
            --bh-green: #16A36A;
        }

        html, body, [class*="css"] {
            font-family: Inter, "Segoe UI", Arial, sans-serif;
        }

        /* Sidebar — bleu marine BH Bank */
        [data-testid="stSidebar"] {
            background: var(--bh-sidebar) !important;
            border-right: 1px solid rgb(18, 48, 82) !important;
        }

        [data-testid="stSidebarHeader"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
        }

        [data-testid="stSidebar"] > div {
            padding-top: 0 !important;
        }

        [data-testid="stSidebarContent"] {
            padding: 0 .85rem 1.5rem !important;
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"]:first-of-type {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }

        [data-testid="stSidebar"] .side-label {
            color: #6B7280 !important;
            margin-top: 1rem;
        }

        [data-testid="stSidebar"] .bh-brand {
            padding: 0 0 .75rem !important;
            margin: 0 0 .35rem !important;
            border-bottom: 1px solid rgb(18, 48, 82);
        }

        [data-testid="stSidebar"] .bh-brand img {
            width: 148px;
            filter: brightness(1.05);
        }

        [data-testid="stSidebar"] .slim-profile {
            padding: .7rem .8rem;
            background: rgb(14, 42, 76);
            border: 1px solid rgb(22, 52, 88);
            border-radius: 10px;
            margin-bottom: .25rem;
        }

        [data-testid="stSidebar"] .slim-profile-name {
            color: #F3F4F6;
            font-size: .88rem;
            font-weight: 700;
        }

        [data-testid="stSidebar"] .slim-profile-role {
            color: #9CA3AF;
            font-size: .72rem;
        }

        [data-testid="stSidebar"] .stButton > button {
            min-height: 2.45rem !important;
            justify-content: flex-start !important;
            padding: .5rem .75rem !important;
            font-size: .82rem !important;
            font-weight: 600 !important;
            color: #C5C9D2 !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            color: white !important;
            background: rgb(14, 42, 76) !important;
            border-color: rgb(22, 52, 88) !important;
            transform: none !important;
        }

        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            color: white !important;
            background: var(--bh-red) !important;
            border-color: var(--bh-red) !important;
            box-shadow: 0 4px 14px rgba(227, 30, 36, .28) !important;
        }

        [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
            background: var(--bh-red-dark) !important;
        }

        [data-testid="stSidebar"] .stRadio label {
            color: #C5C9D2 !important;
            font-size: .82rem !important;
        }

        [data-testid="stSidebar"] .stCaption {
            color: #6B7280 !important;
        }

        [data-testid="stSidebar"] .slim-profile {
            padding: .7rem .8rem;
            background: rgb(14, 42, 76);
            border: 1px solid rgb(22, 52, 88);
            border-radius: 10px;
            margin-bottom: .25rem;
        }

        [data-testid="stSidebar"] .slim-profile-name {
            color: #F3F4F6;
            font-size: .88rem;
            font-weight: 700;
        }

        [data-testid="stSidebar"] .slim-profile-role {
            color: #9CA3AF;
            font-size: .72rem;
        }

        [data-testid="collapsedControl"] {
            color: white !important;
            background: var(--bh-red) !important;
            border-radius: 0 8px 8px 0 !important;
        }

        .block-container {
            max-width: 100%;
            padding: 1.25rem 1.5rem 2rem;
        }

        .stApp {
            background: #F0F1F4;
            color: var(--bh-ink);
        }

        #MainMenu, footer, header {
            visibility: hidden;
        }

        /* Inputs */
        .stTextInput input, .stTextArea textarea {
            color: var(--bh-ink) !important;
            background: white !important;
            border: 1px solid #DDE0E5 !important;
            border-radius: 12px !important;
            box-shadow: 0 1px 2px rgba(22, 24, 29, .03);
        }

        .stTextInput input {
            min-height: 3rem;
        }

        .stTextArea textarea {
            padding: 1rem !important;
            line-height: 1.55;
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: var(--bh-red) !important;
            box-shadow: 0 0 0 3px rgba(227, 30, 36, .10) !important;
        }

        .stTextInput label, .stTextArea label, .stFileUploader label {
            color: var(--bh-ink) !important;
            font-weight: 650 !important;
        }

        /* Buttons */
        .stButton button, .stDownloadButton button {
            min-height: 3rem;
            border-radius: 11px !important;
            font-weight: 700 !important;
            transition: all .18s ease;
        }

        .stButton button[kind="primary"] {
            color: white !important;
            background: linear-gradient(135deg, var(--bh-red), var(--bh-red-dark)) !important;
            border: 0 !important;
            box-shadow: 0 8px 20px rgba(227, 30, 36, .22) !important;
        }

        .stButton button[kind="primary"]:hover {
            box-shadow: 0 10px 24px rgba(227, 30, 36, .30) !important;
            transform: translateY(-1px);
        }

        .stDownloadButton button {
            color: var(--bh-red) !important;
            background: white !important;
            border: 1px solid #F1B7BA !important;
        }

        .stDownloadButton button:hover {
            color: white !important;
            background: var(--bh-red) !important;
            border-color: var(--bh-red) !important;
        }

        /* Native components */
        [data-testid="stMetric"] {
            min-height: 130px;
            padding: 1.15rem 1.25rem;
            background: white;
            border: 1px solid var(--bh-line);
            border-radius: 16px;
            box-shadow: 0 6px 22px rgba(22, 24, 29, .045);
        }

        [data-testid="stMetricLabel"] {
            color: var(--bh-muted);
        }

        [data-testid="stMetricValue"] {
            color: var(--bh-ink);
            font-size: 1.65rem;
            font-weight: 750;
        }

        [data-testid="stExpander"] {
            overflow: hidden;
            background: white;
            border: 1px solid var(--bh-line);
            border-radius: 14px;
            box-shadow: 0 4px 18px rgba(22, 24, 29, .035);
        }

        [data-testid="stVerticalBlockBorderWrapper"]:not(:has(.composer-anchor)) [data-testid="stFileUploader"] section {
            padding: .7rem;
            background: #FAFAFB !important;
            border: 1px dashed #D7D9DE !important;
            border-radius: 12px;
        }

        div[data-testid="column"]:not(:has(.composer-plus-marker)) [data-testid="stFileUploader"] section button {
            color: var(--bh-red) !important;
            background: white !important;
            border-color: #F1B7BA !important;
        }

        [data-testid="stAlert"] {
            color: var(--bh-ink) !important;
            background: white !important;
            border: 1px solid var(--bh-line) !important;
            border-left: 4px solid var(--bh-red) !important;
            border-radius: 12px !important;
        }

        .stDataFrame {
            overflow: hidden;
            border: 1px solid var(--bh-line);
            border-radius: 14px;
        }

        /* Custom components */
        .app-toolbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.1rem;
            padding: .75rem 1rem;
            background: rgba(255, 255, 255, .92);
            border: 1px solid var(--bh-line);
            border-radius: 13px;
            box-shadow: 0 4px 16px rgba(22, 24, 29, .035);
            backdrop-filter: blur(12px);
        }

        .toolbar-product {
            display: flex;
            align-items: center;
            gap: .7rem;
            color: var(--bh-ink);
            font-size: .8rem;
            font-weight: 750;
        }

        .toolbar-monogram {
            display: grid;
            width: 30px;
            height: 30px;
            place-items: center;
            color: white;
            background: var(--bh-red);
            border-radius: 8px;
            font-size: .67rem;
            font-weight: 900;
            letter-spacing: -.03em;
        }

        .toolbar-context {
            color: #9297A1;
            font-size: .72rem;
            font-weight: 600;
        }

        .toolbar-live {
            display: flex;
            align-items: center;
            gap: .45rem;
            color: #4E5560;
            font-size: .7rem;
            font-weight: 650;
        }

        .toolbar-live::before {
            content: "";
            width: 7px;
            height: 7px;
            background: var(--bh-green);
            border-radius: 50%;
            box-shadow: 0 0 0 3px rgba(22, 163, 106, .10);
        }

        .bh-brand {
            display: flex;
            justify-content: center;
            padding: .2rem 0 .8rem;
        }

        .bh-brand img {
            width: 174px;
            height: auto;
        }

        .side-label {
            margin: 1.2rem 0 .55rem;
            color: #9297A1;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .13em;
            text-transform: uppercase;
        }

        .profile-card {
            padding: .9rem 1rem;
            background: linear-gradient(145deg, #202329, #121418);
            border-radius: 14px;
            box-shadow: 0 10px 24px rgba(22, 24, 29, .14);
        }

        .profile-status {
            display: flex;
            align-items: center;
            gap: .45rem;
            margin-bottom: .55rem;
            color: #B9BDC5;
            font-size: .66rem;
            font-weight: 750;
            letter-spacing: .1em;
            text-transform: uppercase;
        }

        .profile-dot {
            width: 8px;
            height: 8px;
            background: var(--bh-green);
            border-radius: 50%;
            box-shadow: 0 0 0 3px rgba(22, 163, 106, .16);
        }

        .profile-name {
            color: white;
            font-size: 1rem;
            font-weight: 750;
        }

        .profile-role {
            margin-top: .15rem;
            color: #A8ADB7;
            font-size: .78rem;
        }

        .mapping-ok {
            margin-top: .5rem;
            padding: .55rem .7rem;
            color: #166A48;
            background: #ECF9F3;
            border: 1px solid #BCE9D4;
            border-radius: 9px;
            font-size: .78rem;
            font-weight: 650;
        }

        .freq-badge {
            display: inline-block;
            margin-left: .35rem;
            padding: .12rem .42rem;
            color: #7B5000;
            background: #FFF4D6;
            border-radius: 999px;
            font-size: .62rem;
            font-weight: 800;
        }

        .recent-ok {
            color: #16A36A;
            font-size: .55rem;
        }

        .recent-ko {
            color: #E31E24;
            font-size: .55rem;
        }

        .hero {
            position: relative;
            overflow: hidden;
            min-height: 210px;
            padding: 2rem 2.2rem;
            background: linear-gradient(128deg, #191B20 0%, #262A31 62%, #3A2022 100%);
            border-radius: 22px;
            box-shadow: 0 18px 42px rgba(22, 24, 29, .14);
        }

        .hero::after {
            content: "";
            position: absolute;
            top: -90px;
            right: -70px;
            width: 280px;
            height: 280px;
            background: var(--bh-red);
            border-radius: 50%;
            opacity: .17;
        }

        .hero-eyebrow {
            display: inline-flex;
            align-items: center;
            gap: .45rem;
            position: relative;
            z-index: 1;
            padding: .38rem .65rem;
            color: #FFBFC1;
            background: rgba(227, 30, 36, .14);
            border: 1px solid rgba(255, 142, 146, .18);
            border-radius: 999px;
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .1em;
            text-transform: uppercase;
        }

        .hero h1 {
            position: relative;
            z-index: 1;
            max-width: 700px;
            margin: 1rem 0 .55rem;
            color: white !important;
            font-size: clamp(1.75rem, 3vw, 2.65rem);
            line-height: 1.12;
            letter-spacing: -.035em;
        }

        .hero p {
            position: relative;
            z-index: 1;
            max-width: 680px;
            margin: 0;
            color: #C3C7CE;
            font-size: .97rem;
            line-height: 1.6;
        }

        .hero-meta {
            position: relative;
            z-index: 1;
            display: flex;
            flex-wrap: wrap;
            gap: 1.2rem;
            margin-top: 1.35rem;
            color: #E8E9EC;
            font-size: .75rem;
        }

        .hero-meta span::before {
            content: "•";
            margin-right: .45rem;
            color: var(--bh-red);
            font-size: 1.1rem;
        }

        .main-query-card {
            margin-bottom: .15rem;
        }

        .main-query-card span {
            color: var(--bh-red);
            font-size: .68rem;
            font-weight: 850;
            letter-spacing: .13em;
            text-transform: uppercase;
        }

        .main-query-card h2 {
            margin: .25rem 0 .35rem;
            color: var(--bh-ink) !important;
            font-size: 1.3rem;
            letter-spacing: -.02em;
        }

        .main-query-card p {
            margin: 0 0 .9rem;
            color: var(--bh-muted);
            font-size: .82rem;
        }

        .section-title {
            margin: 1.8rem 0 .85rem;
        }

        .section-title span {
            color: var(--bh-red);
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .13em;
            text-transform: uppercase;
        }

        .section-title h2 {
            margin: .2rem 0 0;
            color: var(--bh-navy) !important;
            font-size: 1.15rem;
            font-weight: 600;
            letter-spacing: -.015em;
        }

        .query-shell {
            margin-bottom: -1rem;
            padding: 1rem 1.15rem .1rem;
            background: white;
            border: 1px solid var(--bh-line);
            border-radius: 17px 17px 0 0;
            box-shadow: 0 8px 28px rgba(22, 24, 29, .05);
        }

        .query-hint {
            color: var(--bh-muted);
            font-size: .8rem;
        }

        .result-head {
            display: flex;
            align-items: center;
            gap: .6rem;
            margin: 2rem 0 .85rem;
            color: var(--bh-ink);
            font-size: 1.2rem;
            font-weight: 750;
        }

        .result-head::before {
            content: "";
            width: 5px;
            height: 24px;
            background: var(--bh-red);
            border-radius: 99px;
        }

        .answer-card {
            position: relative;
            overflow: hidden;
            margin-top: 1rem;
            padding: 1.45rem 1.6rem 1.5rem;
            background: white;
            border: 1px solid var(--bh-line);
            border-radius: 17px;
            box-shadow: 0 9px 30px rgba(22, 24, 29, .055);
        }

        .answer-card::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 5px;
            background: var(--bh-red);
        }

        .answer-label {
            margin-bottom: .65rem;
            color: var(--bh-red);
            font-size: .68rem;
            font-weight: 850;
            letter-spacing: .13em;
            text-transform: uppercase;
        }

        .answer-text {
            color: #292C32;
            font-size: 1rem;
            line-height: 1.75;
        }

        .result-meta {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 1.45rem 0 .65rem;
        }

        .result-meta-title {
            color: var(--bh-ink);
            font-size: 1rem;
            font-weight: 750;
        }

        .result-meta-count {
            padding: .32rem .58rem;
            color: #676D77;
            background: #F0F1F3;
            border-radius: 999px;
            font-size: .68rem;
            font-weight: 750;
        }

        .error-card {
            margin-top: 1.25rem;
            padding: 1rem 1.15rem;
            color: #751D21;
            background: var(--bh-red-soft);
            border: 1px solid #F5C5C8;
            border-left: 5px solid var(--bh-red);
            border-radius: 12px;
        }

        .admin-action-card {
            margin-top: 1.25rem;
            padding: 1.25rem 1.4rem;
            color: #4D3510;
            background: #FFFAED;
            border: 1px solid #F0D899;
            border-left: 5px solid #D89A13;
            border-radius: 14px;
        }

        .admin-action-title {
            margin-bottom: .45rem;
            color: #7B5000;
            font-size: .72rem;
            font-weight: 850;
            letter-spacing: .11em;
            text-transform: uppercase;
        }

        .admin-success-card {
            margin-top: 1.25rem;
            padding: 1.1rem 1.3rem;
            color: #135C3F;
            background: #ECF9F3;
            border: 1px solid #BCE9D4;
            border-left: 5px solid var(--bh-green);
            border-radius: 14px;
        }

        .validation-status {
            padding: 1rem 1.15rem;
            border-radius: 13px;
            font-weight: 700;
        }

        .validation-ok {
            color: #135C3F;
            background: #ECF9F3;
            border: 1px solid #BCE9D4;
        }

        .validation-ko {
            color: #751D21;
            background: var(--bh-red-soft);
            border: 1px solid #F5C5C8;
        }

        .kpi-dashboard-wrap {
            margin: 0 0 1.75rem;
            padding: 1.15rem 1.25rem 1rem;
            background: var(--bh-surface);
            border: 2px solid var(--bh-red);
            border-radius: 14px;
            box-shadow: 0 4px 16px rgba(227, 30, 36, .08);
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.kpi-dashboard-title) {
            margin-bottom: 1.75rem !important;
            background: var(--bh-surface) !important;
            border: 2px solid var(--bh-red) !important;
            border-radius: 14px !important;
            box-shadow: 0 4px 16px rgba(227, 30, 36, .08) !important;
        }

        .kpi-dashboard-title {
            margin: 0 0 .85rem;
            font-size: .72rem;
            font-weight: 700;
            letter-spacing: .08em;
            text-transform: uppercase;
            color: var(--bh-red);
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.kpi-dashboard-title) [data-testid="stMetric"] {
            background: #FAFAFB;
            border: 1px solid var(--bh-line);
            border-radius: 10px;
            padding: .65rem .75rem;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.kpi-dashboard-title) [data-testid="stMetricLabel"] {
            font-size: .72rem !important;
            font-weight: 650 !important;
            color: var(--bh-muted) !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.kpi-dashboard-title) [data-testid="stMetricValue"] {
            font-size: 1.55rem !important;
            font-weight: 750 !important;
            color: var(--bh-ink) !important;
        }

        /* Workspace layout */
        .workspace-shell {
            gap: 0 !important;
        }

        /* Panneau historique — carreau blanc sur toute la colonne droite */
        div[data-testid="column"]:has(.history-column-anchor) {
            background: white !important;
            border: 1px solid #E4E6EA !important;
            border-radius: 14px !important;
            padding: 1rem !important;
            min-height: calc(100vh - 4rem) !important;
            box-shadow: 0 2px 12px rgba(22, 24, 29, .05) !important;
        }

        div[data-testid="column"]:has(.history-column-anchor) > div {
            height: 100%;
        }

        div[data-testid="column"]:has(.history-column-anchor) [data-testid="stVerticalBlockBorderWrapper"]:not(:has(.history-scroll-anchor)) {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            min-height: unset !important;
        }

        div[data-testid="column"]:has(.history-column-anchor) .history-panel-title {
            color: var(--bh-navy) !important;
            font-size: .85rem;
            font-weight: 600;
            margin-bottom: .75rem;
            padding-bottom: .65rem;
            border-bottom: 1px solid #ECEEF2;
        }

        div[data-testid="column"]:has(.history-column-anchor) [data-testid="stVerticalBlockBorderWrapper"]:has(.history-scroll-anchor) {
            flex: 1 !important;
            min-height: 240px !important;
            max-height: calc(100vh - 13rem) !important;
            margin-bottom: .75rem !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.history-scroll-anchor)::-webkit-scrollbar {
            width: 7px;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.history-scroll-anchor)::-webkit-scrollbar-track {
            background: #F0F1F3;
            border-radius: 4px;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.history-scroll-anchor)::-webkit-scrollbar-thumb {
            background: #C4C8D0;
            border-radius: 4px;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.history-scroll-anchor)::-webkit-scrollbar-thumb:hover {
            background: var(--bh-red);
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.history-scroll-anchor) [data-testid="stVerticalBlock"] {
            padding: .5rem .65rem !important;
        }

        .history-empty {
            padding: 2rem .75rem;
            color: #9AA0AA;
            font-size: .8rem;
            line-height: 1.55;
            text-align: center;
        }

        div[data-testid="column"]:has(.history-column-anchor) [data-testid="stVerticalBlockBorderWrapper"]:has(.history-scroll-anchor) .stButton > button {
            min-height: auto !important;
            padding: .6rem .7rem !important;
            font-size: .76rem !important;
            font-weight: 600 !important;
            text-align: left !important;
            border-radius: 8px !important;
            margin-bottom: .3rem !important;
            color: #16181D !important;
            background: #FFFFFF !important;
            border: 1px solid #E4E6EA !important;
            box-shadow: none !important;
        }

        div[data-testid="column"]:has(.history-column-anchor) [data-testid="stVerticalBlockBorderWrapper"]:has(.history-scroll-anchor) .stButton > button[kind="primary"] {
            color: white !important;
            background: var(--bh-red) !important;
            border: 1px solid var(--bh-red) !important;
            border-left: 3px solid var(--bh-red-dark) !important;
            box-shadow: 0 2px 8px rgba(227, 30, 36, .18) !important;
        }

        div[data-testid="column"]:has(.history-column-anchor) [data-testid="stVerticalBlockBorderWrapper"]:has(.history-new-anchor) .stButton > button {
            min-height: 2.5rem !important;
            color: var(--bh-ink) !important;
            background: white !important;
            border: 1px solid #D4D8DE !important;
            border-radius: 10px !important;
            font-size: .8rem !important;
            font-weight: 650 !important;
            box-shadow: 0 1px 3px rgba(22, 24, 29, .05) !important;
        }

        div[data-testid="column"]:has(.history-column-anchor) [data-testid="stVerticalBlockBorderWrapper"]:has(.history-new-anchor) .stButton > button:hover {
            color: var(--bh-red) !important;
            border-color: #F1B7BA !important;
            background: var(--bh-red-soft) !important;
        }

        .main-workspace {
            padding-right: .5rem;
        }

        .title-navy {
            color: var(--bh-navy) !important;
        }

        .page-topbar-title {
            margin: 0;
            font-size: 1.12rem;
            font-weight: 600;
            line-height: 1.3;
        }

        .dept-page-title {
            margin: .5rem 0 .25rem;
            font-size: 1.28rem;
            font-weight: 600;
            line-height: 1.25;
        }

        .section-title-navy {
            margin: .2rem 0 0;
            font-size: 1.15rem;
            font-weight: 600;
            letter-spacing: -.015em;
        }

        .page-topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: .9rem;
            margin-bottom: 1.25rem;
            padding: 1.05rem 1.3rem;
            background: linear-gradient(120deg, rgb(10,34,64) 0%, #1c3f68 100%);
            border: none;
            border-radius: 18px;
            box-shadow: 0 10px 28px rgba(10,34,64,.18);
        }

        .page-topbar-left {
            display: flex;
            align-items: center;
            gap: .9rem;
        }

        .page-topbar-avatar {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 42px;
            height: 42px;
            flex-shrink: 0;
            color: rgb(10,34,64);
            background: #FFFFFF;
            border-radius: 12px;
            font-size: .95rem;
            font-weight: 800;
        }

        .page-topbar-title {
            margin: 0;
            color: #FFFFFF !important;
            font-size: 1.05rem;
            font-weight: 750;
            line-height: 1.3;
        }

        .page-topbar p {
            margin: .2rem 0 0;
            color: rgba(255,255,255,.72);
            font-size: .8rem;
        }

        .page-topbar-status {
            display: flex;
            align-items: center;
            gap: .5rem;
            padding: .4rem .8rem;
            color: rgba(255,255,255,.9);
            background: rgba(255,255,255,.1);
            border: 1px solid rgba(255,255,255,.16);
            border-radius: 999px;
            font-size: .75rem;
            font-weight: 600;
            white-space: nowrap;
        }

        .page-topbar-dot {
            width: 7px;
            height: 7px;
            background: #3DDC84;
            border-radius: 50%;
            box-shadow: 0 0 0 3px rgba(61,220,132,.22);
        }

        .dept-page-header {
            margin-bottom: 1.1rem;
            padding: 1.1rem 1.25rem;
            background: white;
            border: 1px solid var(--bh-line);
            border-left: 4px solid var(--bh-red);
            border-radius: 12px;
        }

        .dept-page-header .dept-badge {
            color: var(--bh-red);
            background: var(--bh-red-soft);
            border: none;
            font-size: .62rem;
            font-weight: 800;
            letter-spacing: .1em;
            text-transform: uppercase;
            padding: .25rem .55rem;
            border-radius: 4px;
        }

        .dept-page-header h1 {
            margin: .5rem 0 .25rem;
            color: var(--bh-navy) !important;
            font-size: 1.28rem;
            font-weight: 600;
        }

        .dept-page-header p {
            margin: 0;
            color: var(--bh-muted);
            font-size: .84rem;
            line-height: 1.5;
        }

        .kpi-red-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: .75rem;
            margin-bottom: 1.25rem;
        }

        @media (max-width: 1100px) {
            .kpi-red-grid { grid-template-columns: repeat(2, 1fr); }
        }

        .kpi-red-card {
            padding: 1rem 1.1rem;
            background: linear-gradient(135deg, var(--bh-red) 0%, var(--bh-red-dark) 100%);
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(227, 30, 36, .22);
        }

        .kpi-red-label {
            color: rgba(255, 255, 255, .82);
            font-size: .72rem;
            font-weight: 500;
            letter-spacing: .02em;
        }

        .kpi-red-value {
            margin-top: .35rem;
            color: white;
            font-size: 1.65rem;
            font-weight: 650;
            letter-spacing: -.02em;
            line-height: 1.1;
        }

        .kpi-red-sub {
            margin-top: .3rem;
            color: rgba(255, 255, 255, .65);
            font-size: .64rem;
            font-weight: 500;
        }

        .suggestions-panel {
            margin-bottom: 1.1rem;
            padding: 1rem 1.1rem;
            background: white;
            border: 1px solid var(--bh-line);
            border-radius: 12px;
        }

        .suggestions-label {
            margin-bottom: .75rem;
            color: var(--bh-muted);
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .1em;
            text-transform: uppercase;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.suggestions-anchor) {
            margin-bottom: 1rem !important;
            background: white !important;
            border: 1px solid var(--bh-line) !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 8px rgba(22, 24, 29, .03) !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.suggestions-anchor) .stButton > button {
            min-height: 2.15rem !important;
            max-height: 2.15rem !important;
            padding: .3rem .75rem !important;
            color: #3D424B !important;
            background: #F6F7F9 !important;
            border: 1px solid #E4E6EA !important;
            border-radius: 999px !important;
            font-size: .73rem !important;
            font-weight: 600 !important;
            text-align: center !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            box-shadow: none !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.suggestions-anchor) .stButton > button:hover {
            color: var(--bh-red) !important;
            background: var(--bh-red-soft) !important;
            border-color: #FFD5D7 !important;
        }

        /* Barre de saisie unifiée — style pill (inspiré ChatGPT) */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) {
            position: relative !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) > div > div[data-testid="stVerticalBlock"] {
            position: relative !important;
            gap: 0 !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) form[data-testid="stForm"] {
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
        }

        .composer-bar-row {
            display: none !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) [data-testid="stVerticalBlock"]:has(.composer-bar-row) > div[data-testid="stHorizontalBlock"] {
            align-items: center !important;
            gap: .45rem !important;
            margin: 0 !important;
            padding: .35rem .45rem .35rem .45rem !important;
            background: #FFFFFF !important;
            border: 1px solid #D4D8DE !important;
            border-radius: 999px !important;
            box-shadow: 0 2px 12px rgba(22, 24, 29, .07) !important;
        }

        [data-testid="stVerticalBlock"]:has(.composer-bar-row) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child {
            flex: 0 0 42px !important;
            width: 42px !important;
            min-width: 42px !important;
            max-width: 42px !important;
        }

        [data-testid="stVerticalBlock"]:has(.composer-bar-row) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {
            flex: 1 1 0 !important;
            width: auto !important;
            min-width: 0 !important;
            padding: 0 !important;
        }

        [data-testid="stVerticalBlock"]:has(.composer-bar-row) > div[data-testid="stHorizontalBlock"] {
            align-items: center !important;
            min-height: 42px !important;
        }

        [data-testid="stVerticalBlock"]:has(.composer-bar-row) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            align-self: center !important;
            display: flex !important;
            align-items: center !important;
            margin-top: 0 !important;
            margin-bottom: 0 !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }

        [data-testid="stVerticalBlock"]:has(.composer-bar-row) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child [data-testid="stVerticalBlock"] {
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            justify-content: center !important;
        }

        [data-testid="stVerticalBlock"]:has(.composer-bar-row) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child form {
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) form [data-testid="stHorizontalBlock"] {
            align-items: center !important;
            gap: .35rem !important;
            margin: 0 !important;
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        .composer-plus-marker {
            display: none !important;
        }

        a.composer-plus-link,
        a.composer-plus-link:link,
        a.composer-plus-link:visited,
        .st-key-composer_plus_btn button[data-testid="stBaseButton-tertiary"],
        .st-key-composer_plus_btn button[data-testid="stBaseButton-secondary"],
        div[data-testid="column"]:has(.composer-plus-marker) .stButton > button {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            flex-shrink: 0 !important;
            width: 42px !important;
            height: 42px !important;
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            border: 2.5px solid #6B7280 !important;
            border-radius: 10px !important;
            color: #16181D !important;
            font-size: 1.45rem !important;
            font-weight: 800 !important;
            line-height: 1 !important;
            text-decoration: none !important;
            box-shadow: 0 2px 8px rgba(22, 24, 29, .15) !important;
            cursor: pointer !important;
            box-sizing: border-box !important;
        }

        a.composer-plus-link:hover,
        a.composer-plus-link:active,
        a.composer-plus-link:focus,
        .st-key-composer_plus_btn button[data-testid="stBaseButton-tertiary"]:hover,
        .st-key-composer_plus_btn button[data-testid="stBaseButton-secondary"]:hover,
        div[data-testid="column"]:has(.composer-plus-marker) .stButton > button:hover {
            background: #F3F4F6 !important;
            background-color: #F3F4F6 !important;
            border-color: #4B5563 !important;
            color: #16181D !important;
            text-decoration: none !important;
            outline: none !important;
        }

        /* Colonne + : largeur fixe, aucun widget Streamlit sombre */
        div[data-testid="column"]:has(.composer-plus-marker) {
            flex: 0 0 42px !important;
            width: 42px !important;
            min-width: 42px !important;
            max-width: 42px !important;
            height: 42px !important;
            padding: 0 !important;
            overflow: visible !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            align-self: center !important;
        }

        div[data-testid="column"]:has(.composer-plus-marker) [data-testid="stVerticalBlock"] {
            width: 42px !important;
            height: 42px !important;
            min-height: 42px !important;
            max-height: 42px !important;
            margin: 0 !important;
            padding: 0 !important;
            gap: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
        }

        div[data-testid="column"]:has(.composer-plus-marker) [data-testid="stElementContainer"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        .st-key-composer_plus_btn {
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transform: translate(3px, -3px) !important;
        }

        div[data-testid="column"]:has(.composer-plus-marker) [data-testid="stMarkdownContainer"]:has(.composer-plus-marker) {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        div[data-testid="column"]:has(.composer-plus-marker) .stButton {
            width: 42px !important;
            height: 42px !important;
            min-width: 42px !important;
            min-height: 42px !important;
            max-width: 42px !important;
            max-height: 42px !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) form [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {
            display: flex !important;
            align-items: center !important;
            align-self: center !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) form [data-testid="column"]:nth-child(2) {
            padding-left: 0 !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) form [data-testid="stTextInput"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) form [data-testid="stTextInput"] > div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) form [data-testid="stTextInput"] > div > div {
            min-height: 42px !important;
            height: 42px !important;
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) form input {
            min-height: 42px !important;
            height: 42px !important;
            max-height: 42px !important;
            padding: .6rem .75rem !important;
            font-size: .88rem !important;
            border: none !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) form input:focus {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) form [data-testid="stTextInput"] > div {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) form .stButton {
            margin: 0 !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) form .stButton > button[kind="primary"] {
            width: 38px !important;
            height: 38px !important;
            min-height: 38px !important;
            max-height: 38px !important;
            padding: 0 !important;
            margin: 0 !important;
            border-radius: 50% !important;
            font-size: 1.05rem !important;
            line-height: 1 !important;
            box-shadow: none !important;
        }

        .composer-mapping-hint {
            margin-top: .55rem;
            color: #166A48;
            font-size: .72rem;
            font-weight: 600;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.composer-anchor) form input::placeholder {
            color: #6B7280 !important;
            opacity: 1 !important;
            font-size: .9rem !important;
        }

        /* Boutons zone principale — fond clair, texte lisible */
        [data-testid="stMain"] .stButton > button[kind="secondary"],
        [data-testid="stMain"] .stButton > button:not([kind="primary"]) {
            min-height: 2.55rem !important;
            padding: .55rem .85rem !important;
            color: #16181D !important;
            background: #FFFFFF !important;
            border: 1px solid #D4D8DE !important;
            border-radius: 8px !important;
            font-size: .8rem !important;
            font-weight: 600 !important;
            line-height: 1.35 !important;
            white-space: normal !important;
            text-align: left !important;
            box-shadow: 0 1px 3px rgba(22, 24, 29, .05) !important;
        }

        [data-testid="stMain"] .stButton > button[kind="secondary"]:hover,
        [data-testid="stMain"] .stButton > button:not([kind="primary"]):hover {
            color: var(--bh-red) !important;
            background: var(--bh-red-soft) !important;
            border-color: #F1B7BA !important;
            transform: none !important;
        }

        [data-testid="stMain"] .stButton > button[kind="primary"] {
            min-height: 2.65rem !important;
            font-size: .85rem !important;
            border-radius: 8px !important;
        }

        .analysis-thread {
            margin: .5rem 0 1rem;
        }

        .analysis-entry {
            margin-bottom: 1.25rem;
            background: white;
            border: 1px solid var(--bh-line);
            border-radius: 12px;
            overflow: hidden;
        }

        .analysis-question {
            padding: .75rem 1rem;
            background: #F6F7F9;
            border-bottom: 1px solid var(--bh-line);
        }

        .analysis-question-tag {
            display: inline-block;
            margin-bottom: .3rem;
            padding: .15rem .45rem;
            color: var(--bh-red);
            background: var(--bh-red-soft);
            border-radius: 4px;
            font-size: .62rem;
            font-weight: 800;
            letter-spacing: .08em;
            text-transform: uppercase;
        }

        .analysis-question-text {
            margin: 0;
            color: var(--bh-ink);
            font-size: .88rem;
            font-weight: 600;
            line-height: 1.45;
        }

        .analysis-response {
            padding: .85rem 1rem 1rem;
        }

        .composer-card {
            padding: 1.15rem 1.2rem 1.2rem;
            background: white;
            border: 1px solid var(--bh-line);
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(22, 24, 29, .04);
        }

        .composer-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: .75rem;
        }

        .composer-title {
            color: var(--bh-ink);
            font-size: .92rem;
            font-weight: 750;
        }

        .composer-subtitle {
            margin: -.35rem 0 .75rem;
            color: var(--bh-muted);
            font-size: .78rem;
            line-height: 1.45;
        }

        [data-testid="stForm"] textarea {
            min-height: 110px !important;
            padding: .85rem 1rem !important;
            font-size: .88rem !important;
            line-height: 1.55 !important;
            border-radius: 10px !important;
            border-color: #D4D8DE !important;
            background: #FAFBFC !important;
        }

        [data-testid="stForm"] textarea:focus {
            background: white !important;
            border-color: var(--bh-red) !important;
        }

        [data-testid="stMain"] [data-testid="stExpander"] {
            margin-top: .65rem;
            border: 1px solid #ECEEF2 !important;
            border-radius: 10px !important;
            box-shadow: none !important;
        }

        div[data-testid="column"]:not(:has(.upload-anchor)) [data-testid="stFileUploader"] section {
            padding: .5rem .65rem !important;
            background: #FAFBFC !important;
            border: 1px dashed #D4D8DE !important;
            border-radius: 8px !important;
        }

        div[data-testid="column"]:not(:has(.upload-anchor)) [data-testid="stFileUploader"] section button {
            min-height: 2.2rem !important;
            padding: .35rem .75rem !important;
            color: var(--bh-red) !important;
            background: white !important;
            border: 1px solid #F1B7BA !important;
            font-size: .78rem !important;
            box-shadow: none !important;
        }

        div[data-testid="column"]:not(:has(.upload-anchor)) [data-testid="stFileUploader"] small {
            color: var(--bh-muted) !important;
        }

        .mapping-badge {
            display: inline-flex;
            align-items: center;
            gap: .35rem;
            padding: .25rem .5rem;
            color: #166A48;
            background: #ECF9F3;
            border: 1px solid #BCE9D4;
            border-radius: 6px;
            font-size: .66rem;
            font-weight: 650;
        }

        .chat-thread {
            margin: .5rem 0 1rem;
        }

        .app-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 3rem;
            padding-top: 1rem;
            color: #969BA4;
            border-top: 1px solid var(--bh-line);
            font-size: .68rem;
            font-weight: 600;
        }

        [data-testid="stFileUploader"] label[data-testid="stWidgetLabel"] {
            font-size: .78rem !important;
        }

        /* Titres page principale — secours si st.html conserve les classes */
        [data-testid="stMain"] .title-navy,
        [data-testid="stMain"] .dept-page-title,
        [data-testid="stMain"] .section-title-navy,
        [data-testid="stMain"] .history-panel-title {
            color: var(--bh-navy) !important;
            -webkit-text-fill-color: var(--bh-navy) !important;
        }

        @media (max-width: 800px) {
            .block-container {
                padding: 1rem 1rem 2rem;
            }

            .hero {
                min-height: auto;
                padding: 1.5rem;
                border-radius: 16px;
            }

            .hero-meta {
                gap: .5rem;
                flex-direction: column;
            }

            .toolbar-context,
            .app-footer span:last-child {
                display: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_login_css() -> None:
    background = image_to_base64(SIEGE_PATH)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                linear-gradient(
                    105deg,
                    rgba(8, 10, 13, .96) 0%,
                    rgba(14, 16, 20, .90) 44%,
                    rgba(18, 20, 24, .78) 100%
                ),
                url("data:image/png;base64,{background}") center/cover fixed;
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background:
                radial-gradient(circle at 78% 20%, rgba(227, 30, 36, .16), transparent 27rem),
                linear-gradient(180deg, transparent 65%, rgba(0, 0, 0, .24));
        }}

        .block-container {{
            position: relative;
            z-index: 1;
            max-width: 1280px;
            padding: 4.5vh 2.5rem 2rem;
        }}

        [data-testid="stVerticalBlockBorderWrapper"] {{
            padding: 1.65rem 1.8rem 1.4rem;
            background: rgba(255, 255, 255, .985);
            border: 1px solid rgba(255, 255, 255, .88) !important;
            border-radius: 20px;
            box-shadow:
                0 30px 80px rgba(0, 0, 0, .38),
                0 1px 0 rgba(255, 255, 255, .9) inset;
            backdrop-filter: blur(22px);
        }}

        .login-topbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10vh;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, .13);
        }}

        .login-topbar-brand {{
            color: white;
            font-size: .77rem;
            font-weight: 750;
            letter-spacing: .11em;
            text-transform: uppercase;
        }}

        .login-topbar-security {{
            display: flex;
            align-items: center;
            gap: .5rem;
            color: rgba(255, 255, 255, .72);
            font-size: .72rem;
            font-weight: 600;
        }}

        .login-topbar-security::before {{
            content: "";
            width: 7px;
            height: 7px;
            background: #25C783;
            border-radius: 50%;
            box-shadow: 0 0 0 4px rgba(37, 199, 131, .12);
        }}

        .login-intro {{
            max-width: 590px;
            padding: 2.5rem 2.5rem 2rem 0;
        }}

        .login-intro-kicker {{
            display: inline-block;
            margin-bottom: 1rem;
            padding: .42rem .7rem;
            color: #FFBFC1;
            background: rgba(227, 30, 36, .14);
            border: 1px solid rgba(255, 140, 144, .22);
            border-radius: 999px;
            font-size: .67rem;
            font-weight: 850;
            letter-spacing: .13em;
            text-transform: uppercase;
        }}

        .login-intro h1 {{
            max-width: 580px;
            margin: 0 0 1rem;
            color: #FFFFFF !important;
            font-size: clamp(2.45rem, 4vw, 4.25rem);
            line-height: 1.03;
            letter-spacing: -.055em;
        }}

        .login-intro p {{
            max-width: 530px;
            margin: 0;
            color: rgba(255, 255, 255, .76);
            font-size: 1rem;
            line-height: 1.7;
        }}

        .login-features {{
            display: flex;
            flex-wrap: wrap;
            gap: .65rem 1.2rem;
            margin-top: 1.65rem;
        }}

        .login-feature {{
            color: rgba(255, 255, 255, .88);
            font-size: .76rem;
            font-weight: 600;
        }}

        .login-feature::before {{
            content: "✓";
            margin-right: .45rem;
            color: #FF6469;
            font-weight: 850;
        }}

        .login-logo {{
            display: flex;
            justify-content: center;
            padding: 0 0 .45rem;
        }}

        .login-logo img {{
            width: 172px;
            height: auto;
        }}

        .login-kicker {{
            margin-top: .5rem;
            color: var(--bh-red);
            font-size: .68rem;
            font-weight: 850;
            letter-spacing: .14em;
            text-align: center;
            text-transform: uppercase;
        }}

        .login-title {{
            margin: .35rem 0 .3rem;
            color: #16181D !important;
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: -.035em;
            text-align: center;
        }}

        .login-subtitle {{
            margin: 0 auto 1.25rem;
            max-width: 350px;
            color: var(--bh-muted);
            font-size: .88rem;
            line-height: 1.55;
            text-align: center;
        }}

        .login-security {{
            margin-top: .9rem;
            color: #8B9099;
            font-size: .72rem;
            text-align: center;
        }}

        .login-demo {{
            margin-top: .8rem;
            padding: .7rem .8rem;
            color: #656B75;
            background: #F7F7F9;
            border: 1px solid #ECEDEF;
            border-radius: 10px;
            font-size: .72rem;
            line-height: 1.55;
            text-align: center;
        }}

        [data-testid="stForm"] {{
            border: 0 !important;
        }}

        [data-testid="stForm"] .stTextInput label,
        [data-testid="stForm"] .stTextInput label p {{
            color: #25282E !important;
            font-size: .82rem !important;
            font-weight: 700 !important;
        }}

        [data-testid="stForm"] .stTextInput input {{
            color: #17191D !important;
            background: #F9FAFB !important;
            border: 1px solid #D9DCE1 !important;
        }}

        [data-testid="stForm"] .stTextInput input::placeholder {{
            color: #969BA5 !important;
            opacity: 1 !important;
        }}

        @media (max-width: 900px) {{
            .block-container {{
                padding: 1.25rem;
            }}

            .login-topbar {{
                margin-bottom: 2rem;
            }}

            .login-intro {{
                padding: 1rem 0 2rem;
                text-align: center;
            }}

            .login-intro h1,
            .login-intro p {{
                margin-left: auto;
                margin-right: auto;
            }}

            .login-features {{
                justify-content: center;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def login_api(username: str, password: str):
    try:
        response = requests.post(
            f"{API_URL}/login",
            data={"username": username, "password": password},
            timeout=10,
        )
        return response.json() if response.status_code == 200 else None
    except requests.RequestException:
        st.error("Impossible de contacter le serveur FastAPI. Vérifiez qu'il est démarré.")
        return None


def _auth_headers() -> dict:
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"}


def _lire_reponse_api(response: requests.Response) -> dict:
    try:
        contenu = response.json()
    except ValueError:
        return {"erreur": "Le serveur a retourné une réponse invalide."}

    if response.ok:
        return contenu
    return {
        "erreur": contenu.get("erreur")
        or contenu.get("detail")
        or "La requête a échoué.",
        "sql": contenu.get("sql", ""),
    }


def poser_question(question: str, mapping_file=None) -> dict:
    try:
        files = None
        if mapping_file:
            files = {
                "mapping_file": (
                    mapping_file.name,
                    mapping_file.getvalue(),
                    "application/octet-stream",
                )
            }

        response = requests.post(
            f"{API_URL}/api/ask",
            data={"question": question},
            files=files,
            headers=_auth_headers(),
            timeout=60,
        )
        return _lire_reponse_api(response)
    except requests.RequestException as error:
        return {"erreur": f"Erreur de connexion au serveur : {error}"}


def confirmer_action(action_token: str) -> dict:
    try:
        response = requests.post(
            f"{API_URL}/api/execute-action",
            json={"action_token": action_token, "confirmation": True},
            headers=_auth_headers(),
            timeout=30,
        )
        return _lire_reponse_api(response)
    except requests.RequestException as error:
        return {"erreur": f"Erreur de connexion au serveur : {error}"}


def valider_question_api(question: str, sql_reference: str) -> dict:
    try:
        response = requests.post(
            f"{API_URL}/api/validate-question",
            json={
                "question": question,
                "sql_reference": sql_reference,
            },
            headers=_auth_headers(),
            timeout=120,
        )
        return _lire_reponse_api(response)
    except requests.RequestException as error:
        return {"erreur": f"Erreur de connexion au serveur : {error}"}


def fetch_questions_frequentes(limit: int = 8) -> list[dict]:
    try:
        response = requests.get(
            f"{API_URL}/api/questions/frequent",
            params={"limit": limit},
            headers=_auth_headers(),
            timeout=10,
        )
        if response.ok:
            return response.json().get("questions", [])
    except requests.RequestException:
        pass
    return []


def fetch_questions_recentes(limit: int = 6) -> list[dict]:
    try:
        response = requests.get(
            f"{API_URL}/api/questions/recent",
            params={"limit": limit},
            headers=_auth_headers(),
            timeout=10,
        )
        if response.ok:
            return response.json().get("questions", [])
    except requests.RequestException:
        pass
    return []


def fetch_stats_questions() -> dict:
    try:
        response = requests.get(
            f"{API_URL}/api/questions/stats",
            headers=_auth_headers(),
            timeout=10,
        )
        if response.ok:
            return response.json()
    except requests.RequestException:
        pass
    return {}


@st.cache_data(ttl=300)
def _charger_kpi_dashboard() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM customer WHERE status = 'Active'")
    clients_actifs = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM account WHERE status = 'Active'")
    comptes_actifs = cur.fetchone()[0]
    cur.execute(
        'SELECT COUNT(*) FROM "transaction" '
        "WHERE strftime('%Y', transaction_date) = '2024'"
    )
    transactions_2024 = cur.fetchone()[0]
    cur.execute(
        'SELECT COUNT(*) FROM "transaction" '
        "WHERE amount > 8000 AND strftime('%Y', transaction_date) = '2024'"
    )
    transactions_suspectes_2024 = cur.fetchone()[0]
    conn.close()
    ratio_suspectes = (
        round(transactions_suspectes_2024 * 100.0 / transactions_2024, 1)
        if transactions_2024
        else 0.0
    )
    ratio_comptes = (
        round(comptes_actifs / clients_actifs, 2)
        if clients_actifs
        else 0.0
    )
    return {
        "clients_actifs": clients_actifs,
        "comptes_actifs": comptes_actifs,
        "transactions_2024": transactions_2024,
        "transactions_suspectes_2024": transactions_suspectes_2024,
        "ratio_suspectes": ratio_suspectes,
        "ratio_comptes": ratio_comptes,
    }


def afficher_kpi_automatiques(departement: str) -> None:
    kpi = _charger_kpi_dashboard()
    st.markdown(
        f"""
        <div class="kpi-red-grid">
            <div class="kpi-red-card">
                <div class="kpi-red-label">Clients actifs</div>
                <div class="kpi-red-value">{_formater_nombre(kpi['clients_actifs'])}</div>
            </div>
            <div class="kpi-red-card">
                <div class="kpi-red-label">Comptes actifs</div>
                <div class="kpi-red-value">{_formater_nombre(kpi['comptes_actifs'])}</div>
                <div class="kpi-red-sub">{kpi['ratio_comptes']} compte(s) / client</div>
            </div>
            <div class="kpi-red-card">
                <div class="kpi-red-label">Transactions 2024</div>
                <div class="kpi-red-value">{_formater_nombre(kpi['transactions_2024'])}</div>
            </div>
            <div class="kpi-red-card">
                <div class="kpi-red-label">Opérations suspectes</div>
                <div class="kpi-red-value">{_formater_nombre(kpi['transactions_suspectes_2024'])}</div>
                <div class="kpi-red-sub">{kpi['ratio_suspectes']}% du volume 2024</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _lancer_question(question: str, mapping_file, departement: str) -> None:
    question = question.strip()
    if not question:
        return
    with st.spinner("Analyse en cours…"):
        resultat = poser_question(question, mapping_file)
    _ajouter_echange(question, resultat, departement)
    # IMPORTANT:
    # Ne pas modifier st.session_state.question_input après l'instanciation du
    # widget Streamlit (sinon erreur StreamlitAPIException).


def _select_suggestion(question: str, key_prefix: str) -> None:
    if st.button(
        question,
        key=f"sugg_{key_prefix}_{hash(question) & 0xFFFF}",
        use_container_width=True,
    ):
        st.session_state.pending_question = question


def _render_html(body: str) -> None:
    """Rendu HTML direct (st.html) — styles inline conservés."""
    st.html(body)


def render_department_header(departement: str) -> None:
    config = DEPARTEMENT_CONFIG.get(
        departement, DEPARTEMENT_CONFIG["Tous les départements"]
    )
    _render_html(
        f"""
        <div class="dept-page-header">
            <span class="dept-badge">{html.escape(config['badge'])}</span>
            <div class="dept-page-title" style="color:{BH_NAVY};margin:.5rem 0 .25rem;font-size:1.28rem;font-weight:600;line-height:1.25;">
                {html.escape(config['title'])}
            </div>
            <p style="margin:0;color:#69707D;font-size:.84rem;line-height:1.5;">{html.escape(config['desc'])}</p>
        </div>
        """
    )


def render_page_topbar(departement: str) -> None:
    config = DEPARTEMENT_CONFIG.get(
        departement, DEPARTEMENT_CONFIG["Tous les départements"]
    )
    utilisateur = st.session_state.user
    role_label = (
        "Administrateur"
        if st.session_state.role == "administrateur"
        else "Utilisateur"
    )
    initiale = utilisateur[:1].upper() if utilisateur else "?"
    _render_html(
        f"""
        <div class="page-topbar">
            <div class="page-topbar-left">
                <div class="page-topbar-avatar">{html.escape(initiale)}</div>
                <div>
                    <div class="page-topbar-title">{html.escape(config['title'])}</div>
                    <p>{html.escape(config['desc'])}</p>
                </div>
            </div>
            <div class="page-topbar-status">
                <span class="page-topbar-dot"></span>
                {html.escape(utilisateur)} · {role_label}
            </div>
        </div>
        """
    )


def render_suggestions(departement: str) -> None:
    examples = QUESTIONS_PAR_DEPARTEMENT.get(
        departement,
        QUESTIONS_PAR_DEPARTEMENT["Tous les départements"],
    )
    with st.container(border=True):
        st.markdown(
            '<div class="suggestions-anchor"></div>'
            '<div class="suggestions-label">Suggestions de requêtes</div>',
            unsafe_allow_html=True,
        )
        per_row = 3
        for row_start in range(0, len(examples), per_row):
            row_items = examples[row_start : row_start + per_row]
            cols = st.columns(len(row_items))
            for index, example in enumerate(row_items):
                with cols[index]:
                    _select_suggestion(example, f"{row_start}_{index}")


def inject_composer_plus_override() -> None:
    """CSS injecté après le widget pour écraser le thème sombre Streamlit 1.59."""
    st.markdown(
        """
        <style>
        .st-key-composer_plus_btn button[data-testid="stBaseButton-tertiary"],
        .st-key-composer_plus_btn button[data-testid="stBaseButton-secondary"] {
            all: unset !important;
            box-sizing: border-box !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 42px !important;
            height: 42px !important;
            min-width: 42px !important;
            min-height: 42px !important;
            max-width: 42px !important;
            max-height: 42px !important;
            padding: 0 !important;
            margin: 0 !important;
            background: #FFFFFF !important;
            background-color: #FFFFFF !important;
            background-image: none !important;
            border: 2.5px solid #6B7280 !important;
            border-radius: 10px !important;
            color: #16181D !important;
            font-size: 1.45rem !important;
            font-weight: 800 !important;
            line-height: 1 !important;
            box-shadow: 0 2px 8px rgba(22, 24, 29, .15) !important;
            cursor: pointer !important;
        }
        .st-key-composer_plus_btn button[data-testid="stBaseButton-tertiary"]:hover,
        .st-key-composer_plus_btn button[data-testid="stBaseButton-secondary"]:hover {
            background: #F3F4F6 !important;
            background-color: #F3F4F6 !important;
            border-color: #4B5563 !important;
            color: #16181D !important;
        }

        .st-key-composer_plus_btn,
        .st-key-composer_plus_btn [data-testid="stElementContainer"],
        .st-key-composer_plus_btn [data-testid="stVerticalBlockBorderWrapper"] {
            margin: 0 !important;
            padding: 0 !important;
            transform: translate(8px, -8px) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.dialog("Joindre un mapping")
def _dialog_mapping() -> None:
    st.markdown("Formats acceptés : **XLSX**, **CSV**, **JSON**.")
    st.file_uploader(
        "Fichier mapping",
        type=["xlsx", "csv", "json"],
        key="mapping_upload",
    )


def render_composer() -> tuple[str, bool, object]:
    """Barre de saisie unifiée : + upload et question sur la même ligne."""
    mapping_nom = st.session_state.get("mapping_name")
    question = ""
    submitted = False

    st.markdown('<div class="composer-bar-row"></div>', unsafe_allow_html=True)

    plus_col, main_col = st.columns(
        [1, 24],
        gap="small",
        vertical_alignment="center",
    )

    with plus_col:
        st.markdown('<span class="composer-plus-marker"></span>', unsafe_allow_html=True)
        if st.button(
            "+",
            key="composer_plus_btn",
            help="Joindre un fichier mapping (XLSX, CSV, JSON)",
            type="tertiary",
        ):
            _dialog_mapping()

    with main_col:
        with st.form("question_form", clear_on_submit=False):
            input_col, send_col = st.columns(
                [0.92, 0.08],
                gap="small",
                vertical_alignment="center",
            )
            with input_col:
                question = st.text_input(
                    "Votre question",
                    key="question_input",
                    placeholder="Posez votre question en langage naturel…",
                    label_visibility="collapsed",
                )
            with send_col:
                submitted = st.form_submit_button(
                    ">",
                    type="primary",
                    use_container_width=True,
                )

    inject_composer_plus_override()

    upload = st.session_state.get("mapping_upload")

    if mapping_nom:
        st.markdown(
            f'<div class="composer-mapping-hint">Mapping actif : '
            f"{html.escape(mapping_nom)}</div>",
            unsafe_allow_html=True,
        )

    return question, submitted, upload


def render_analysis_thread(departement: str) -> None:
    conv = _conversation_visible(departement)
    if not conv:
        return

    user_msg = next(
        (m for m in conv["messages"] if m["role"] == "user"),
        None,
    )
    assistant_msg = next(
        (m for m in conv["messages"] if m["role"] == "assistant"),
        None,
    )
    if not user_msg:
        return

    st.markdown(
        f"""
        <div class="analysis-entry">
            <div class="analysis-question">
                <span class="analysis-question-tag">Question</span>
                <p class="analysis-question-text">
                    {html.escape(user_msg['content'])}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if assistant_msg and assistant_msg.get("result"):
        with st.container(border=True):
            render_result(
                assistant_msg["result"],
                widget_key=f"{conv['id']}_result",
            )


def render_history_panel(departement: str) -> None:
    conversations = [
        c
        for c in st.session_state.get("conversations", [])
        if c.get("messages")
    ]
    if departement != "Tous les départements":
        conversations = [
            c for c in conversations if c.get("departement") == departement
        ]

    _render_html(
        f'<div class="history-panel-title" style="color:{BH_NAVY};font-size:.85rem;font-weight:600;margin-bottom:.75rem;padding-bottom:.65rem;border-bottom:1px solid #ECEEF2;">Historique des analyses</div>'
    )

    with st.container(height=400, border=False):
        st.markdown('<div class="history-scroll-anchor"></div>', unsafe_allow_html=True)
        if not conversations:
            st.markdown(
                '<div class="history-empty">Aucune analyse enregistrée<br>'
                "pour ce département.</div>",
                unsafe_allow_html=True,
            )
        else:
            for conv in conversations[:25]:
                active = conv["id"] == st.session_state.get("active_conv_id")
                titre = conv.get("title", "Analyse")
                label = f"{titre[:38]}{'…' if len(titre) > 38 else ''}"
                if st.button(
                    label,
                    key=f"hist_{conv['id']}",
                    use_container_width=True,
                    type="primary" if active else "secondary",
                ):
                    st.session_state.active_conv_id = conv["id"]
                    if conv.get("departement"):
                        st.session_state.departement = conv["departement"]
                    st.rerun()

    st.markdown('<div class="history-new-anchor"></div>', unsafe_allow_html=True)
    with st.container(border=False):
        if st.button("Nouvelle analyse", key="btn_new_conv", use_container_width=True):
            _reinitialiser_vue_analyse()
            st.rerun()


def _mettre_a_jour_dernier_resultat(resultat: dict) -> None:
    conv = _conversation_active()
    if conv and conv["messages"] and conv["messages"][-1]["role"] == "assistant":
        conv["messages"][-1]["result"] = resultat
        _persister_conversation(conv)


def section_title(kicker: str, title: str) -> None:
    _render_html(
        f"""
        <div class="section-title">
            <span style="color:#E31E24;font-size:.68rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;">{html.escape(kicker)}</span>
            <div class="section-title-navy" style="color:{BH_NAVY};margin:.2rem 0 0;font-size:1.15rem;font-weight:600;letter-spacing:-.015em;">{html.escape(title)}</div>
        </div>
        """
    )


def page_login() -> None:
    inject_global_css()
    inject_login_css()

    st.markdown(
        """
        <div class="login-topbar">
            <div class="login-topbar-brand">BH Bank · Intelligence décisionnelle</div>
            <div class="login-topbar-security">Plateforme opérationnelle et sécurisée</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    presentation, spacer, connection = st.columns([1.25, .12, .78], vertical_alignment="center")

    with presentation:
        st.markdown(
            """
            <div class="login-intro">
                <div class="login-intro-kicker">Nouvelle génération d’analyse</div>
                <h1>La donnée bancaire, simplement accessible.</h1>
                <p>
                    Interrogez les données BH Bank en langage naturel et obtenez
                    instantanément une synthèse claire, fiable et exploitable.
                </p>
                <div class="login-features">
                    <span class="login-feature">Analyse en temps réel</span>
                    <span class="login-feature">Accès contrôlé</span>
                    <span class="login-feature">Données centralisées</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with connection:
        with st.container(border=True):
            logo = image_to_base64(LOGO_PATH)
            st.markdown(
                f"""
                <div class="login-logo">
                    <img src="data:image/png;base64,{logo}" alt="BH Bank">
                </div>
                <div class="login-kicker">Espace sécurisé</div>
                <div class="login-title">Connexion</div>
                <div class="login-subtitle">
                    Identifiez-vous pour accéder à votre espace d’analyse.
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("login_form"):
                username = st.text_input(
                    "Identifiant",
                    placeholder="Entrez votre identifiant",
                )
                password = st.text_input(
                    "Mot de passe",
                    type="password",
                    placeholder="••••••••",
                )
                submitted = st.form_submit_button(
                    "Se connecter",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:
                if not username or not password:
                    st.warning("Veuillez renseigner votre identifiant et votre mot de passe.")
                else:
                    with st.spinner("Connexion sécurisée..."):
                        result = login_api(username, password)
                    if result:
                        st.session_state.user = result["username"]
                        st.session_state.role = result["role"]
                        st.session_state.token = result["access_token"]
                        st.session_state.logged = True
                        st.session_state.conversations_loaded = False
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects.")

            st.markdown(
                """
                <div class="login-security">Connexion protégée · Session de 8 heures</div>
                <div class="login-demo">
                    Accès de démonstration<br>
                    <b>user / user123</b>&nbsp;&nbsp; ou &nbsp;&nbsp;<b>admin / admin123</b>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_sidebar() -> str:
    """Sidebar sombre : logo BH, navigation par département, admin."""
    _init_session_chat()
    if "departement" not in st.session_state:
        st.session_state.departement = "Tous les départements"

    with st.sidebar:
        logo = _logo_base64()
        if logo:
            _render_html(
                f'<div class="bh-brand" style="padding:0 0 .75rem;margin:0 0 .35rem;border-bottom:1px solid rgb(18,48,82);">'
                f'<img src="data:image/png;base64,{logo}" alt="BH Bank" style="width:148px;filter:brightness(1.05);display:block;">'
                f"</div>"
            )

        role_label = (
            "Administrateur"
            if st.session_state.role == "administrateur"
            else "Utilisateur"
        )
        st.markdown(
            f"""
            <div class="slim-profile">
                <div class="slim-profile-name">{html.escape(st.session_state.user)}</div>
                <div class="slim-profile-role">{role_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="side-label">Espaces métier</div>',
            unsafe_allow_html=True,
        )
        for dept_id, nav_label in DEPARTEMENT_NAV:
            active = st.session_state.departement == dept_id
            if st.button(
                nav_label,
                key=f"nav_{dept_id}",
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                st.session_state.departement = dept_id
                conv = _conversation_active()
                if (
                    conv
                    and dept_id != "Tous les départements"
                    and conv.get("departement") != dept_id
                ):
                    _reinitialiser_vue_analyse()
                st.rerun()

        vue = "Assistant analytique"
        if st.session_state.role == "administrateur":
            st.markdown(
                '<div class="side-label">Administration</div>',
                unsafe_allow_html=True,
            )
            if st.button(
                "Centre de validation",
                key="nav_validation",
                use_container_width=True,
                type="primary" if st.session_state.get("vue") == "Centre de validation" else "secondary",
            ):
                st.session_state.vue = "Centre de validation"
                st.rerun()
            if st.button(
                "Assistant analytique",
                key="nav_assistant",
                use_container_width=True,
                type="primary" if st.session_state.get("vue") != "Centre de validation" else "secondary",
            ):
                st.session_state.vue = "Assistant analytique"
                st.rerun()
            vue = st.session_state.get("vue", "Assistant analytique")

        st.markdown('<div class="side-label">Session</div>', unsafe_allow_html=True)
        if st.button("Déconnexion", key="btn_logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                st.session_state.pop(key, None)
            st.rerun()

    return vue


def render_auto_visualization(dataframe: pd.DataFrame) -> None:
    """Affiche un graphique seulement quand deux colonnes s'y prêtent clairement."""
    if dataframe.empty or len(dataframe.columns) != 2 or len(dataframe) > 30:
        return

    numeric_columns = dataframe.select_dtypes(include="number").columns.tolist()
    if len(numeric_columns) != 1:
        return

    value_column = numeric_columns[0]
    label_column = next(
        column for column in dataframe.columns if column != value_column
    )
    chart_data = dataframe[[label_column, value_column]].dropna()

    if chart_data.empty or chart_data[label_column].nunique() < 2:
        return

    st.markdown(
        """
        <div class="result-meta">
            <div class="result-meta-title">Visualisation</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.bar_chart(
        chart_data.set_index(label_column)[value_column],
        color="#E31E24",
        use_container_width=True,
    )


def render_result(result: dict, widget_key: str = "result") -> None:
    if result.get("confirmation_requise"):
        operation = html.escape(str(result.get("type_action", "ACTION")))
        lignes = result.get("nb_lignes_affectees", 0)
        st.markdown(
            f"""
            <div class="admin-action-card">
                <div class="admin-action-title">Confirmation administrateur requise</div>
                <b>Action {operation}</b> — {lignes} ligne(s) seraient affectée(s).<br>
                Aucune modification n’a encore été appliquée à la base.
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander(
            "Contrôler la requête avant exécution",
            expanded=True,
            key=f"{widget_key}_confirm_exp",
        ):
            st.code(result["sql"], language="sql")

        confirmation_key = f"{widget_key}_confirm_" + result["action_token"][-12:]
        confirmation = st.checkbox(
            "J’ai vérifié la requête et je confirme cette modification irréversible.",
            key=confirmation_key,
        )
        if st.button(
            "Confirmer et exécuter",
            type="primary",
            disabled=not confirmation,
            key=f"{widget_key}_confirm_btn",
        ):
            with st.spinner("Exécution sécurisée de l'action..."):
                _mettre_a_jour_dernier_resultat(confirmer_action(result["action_token"]))
            st.session_state.pop(confirmation_key, None)
            st.rerun()
        return

    if result.get("action_executee"):
        st.markdown(
            f"""
            <div class="admin-success-card">
                <b>Modification enregistrée.</b><br>
                {html.escape(str(result["reponse"]))}
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("Requête exécutée", key=f"{widget_key}_done_sql"):
            st.code(result["sql"], language="sql")
        return

    if "erreur" in result:
        st.markdown(
            f"""
            <div class="error-card">
                <b>La requête n'a pas pu être traitée.</b><br>
                {html.escape(str(result["erreur"]))}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if result.get("sql"):
            with st.expander(
                "Voir la requête SQL générée",
                key=f"{widget_key}_err_sql",
            ):
                st.code(result["sql"], language="sql")
        return

    st.markdown(
        f"""
        <div class="answer-card">
            <div class="answer-label">Synthèse analytique</div>
            <div class="answer-text">{html.escape(str(result["reponse"]))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    data = result.get("donnees") or []
    if data:
        dataframe = pd.DataFrame(data)
        render_auto_visualization(dataframe)

        row_count = result.get("nb_resultats", len(dataframe))
        st.markdown(
            f"""
            <div class="result-meta">
                <div class="result-meta-title">Résultats détaillés</div>
                <div class="result-meta-count">{row_count} ligne(s)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True,
            height=min(430, 38 + len(dataframe) * 35),
        )

        export_column, technical_column = st.columns([1, 1.6])
        with export_column:
            st.download_button(
                "↓  Exporter les données en CSV",
                data=dataframe.to_csv(index=False).encode("utf-8"),
                file_name="extraction_bh_bank.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"{widget_key}_csv",
            )
        with technical_column:
            with st.expander(
                "Voir la requête SQL utilisée",
                key=f"{widget_key}_sql",
            ):
                st.code(result["sql"], language="sql")
    else:
        st.info("La requête n’a retourné aucune donnée.")
        with st.expander(
            "Voir la requête SQL utilisée",
            key=f"{widget_key}_sql_empty",
        ):
            st.code(result["sql"], language="sql")


@st.cache_data
def charger_questions_reference() -> list[dict]:
    try:
        with open(QUESTIONS_PATH, "r", encoding="utf-8") as fichier:
            return json.load(fichier)
    except (OSError, json.JSONDecodeError):
        return []


# ==========================================================================
# Vue globale — Dashboard institutionnel BH Bank
# (departement == "Tous les départements")
#
# Ces fonctions ne touchent à rien d'autre que le contenu affiché pour la
# Vue globale : pas de champ de question, pas de suggestions, pas
# d'historique. La sidebar, l'auth, les départements et le backend restent
# strictement inchangés.
# ==========================================================================


def inject_home_css() -> None:
    """Styles dédiés au dashboard institutionnel — préfixe .home- pour ne
    jamais entrer en conflit avec le CSS existant des départements."""
    st.markdown(
        """
        <style>
        html { scroll-behavior: smooth; }

        @keyframes home-fade-up {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .home-section {
            margin: 0 0 1.9rem;
            animation: home-fade-up .55s ease both;
        }

        .home-section-head {
            margin-bottom: 1rem;
        }

        .home-section-eyebrow {
            display: inline-block;
            color: var(--bh-red);
            font-size: .68rem;
            font-weight: 800;
            letter-spacing: .1em;
            text-transform: uppercase;
        }

        .home-section-title {
            margin: .3rem 0 0;
            color: var(--bh-navy);
            font-size: 1.15rem;
            font-weight: 700;
        }

        /* ---- En-tête personnalisé (remplace le hero institutionnel) ---- */
        .home-greeting {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: .9rem;
            padding: 1.3rem 1.5rem;
            background: linear-gradient(120deg, rgb(10,34,64) 0%, #1c3f68 100%);
            border-radius: 18px;
            box-shadow: 0 10px 28px rgba(10,34,64,.18);
            animation: home-fade-up .5s ease both;
        }

        .home-greeting-left {
            display: flex;
            align-items: center;
            gap: .9rem;
        }

        .home-greeting-avatar {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 46px;
            height: 46px;
            flex-shrink: 0;
            color: rgb(10,34,64);
            background: #FFFFFF;
            border-radius: 12px;
            font-size: 1.05rem;
            font-weight: 800;
        }

        .home-greeting-hello {
            color: #FFFFFF;
            font-size: 1.05rem;
            font-weight: 750;
        }

        .home-greeting-date {
            margin-top: .15rem;
            color: rgba(255,255,255,.72);
            font-size: .78rem;
        }

        .home-greeting-status {
            display: flex;
            align-items: center;
            gap: .5rem;
            padding: .4rem .8rem;
            color: rgba(255,255,255,.9);
            background: rgba(255,255,255,.1);
            border: 1px solid rgba(255,255,255,.16);
            border-radius: 999px;
            font-size: .75rem;
            font-weight: 600;
        }

        .home-status-dot {
            width: 7px;
            height: 7px;
            background: #3DDC84;
            border-radius: 50%;
            box-shadow: 0 0 0 3px rgba(61,220,132,.22);
        }

        /* ---- KPI consolidés (style Fabric / Power BI) ---- */
        .home-kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: .8rem;
        }

        .home-kpi-card {
            padding: 1.1rem 1.2rem;
            background: #FFFFFF;
            border: 1px solid var(--bh-line);
            border-radius: 16px;
            box-shadow: 0 6px 16px rgba(22,24,29,.05);
            transition: transform .2s ease, box-shadow .2s ease;
        }

        .home-kpi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 26px rgba(22,24,29,.09);
        }

        .home-kpi-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
            margin-bottom: .65rem;
            color: var(--bh-navy);
            background: #EEF1F5;
            border-radius: 10px;
        }

        .home-kpi-icon-alert {
            color: var(--bh-red);
            background: var(--bh-red-soft);
        }

        .home-kpi-value {
            color: var(--bh-navy);
            font-size: 1.55rem;
            font-weight: 800;
            letter-spacing: -.01em;
        }

        .home-kpi-value-alert {
            color: var(--bh-red);
        }

        .home-kpi-label {
            margin-top: .2rem;
            color: var(--bh-muted);
            font-size: .78rem;
            font-weight: 650;
        }

        .home-kpi-sub {
            margin-top: .25rem;
            color: #9AA0AC;
            font-size: .7rem;
        }

        /* ---- Alertes & anomalies ---- */
        .home-alerts-card {
            background: #FFFFFF;
            border: 1px solid var(--bh-line);
            border-radius: 16px;
            box-shadow: 0 6px 16px rgba(22,24,29,.05);
            overflow: hidden;
        }

        .home-alert-row {
            display: flex;
            align-items: center;
            gap: .9rem;
            padding: .85rem 1.1rem;
            border-bottom: 1px solid var(--bh-line);
        }

        .home-alert-row:last-child {
            border-bottom: none;
        }

        .home-alert-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
            flex-shrink: 0;
            border-radius: 10px;
        }

        .home-alert-icon-high { color: var(--bh-red); background: var(--bh-red-soft); }
        .home-alert-icon-medium { color: #B7791F; background: #FFF6E5; }
        .home-alert-icon-low { color: var(--bh-navy); background: #EEF1F5; }

        .home-alert-body { flex: 1; }

        .home-alert-label {
            color: var(--bh-ink);
            font-size: .84rem;
            font-weight: 650;
        }

        .home-alert-dept {
            margin-top: .15rem;
            color: var(--bh-muted);
            font-size: .72rem;
        }

        .home-alert-value {
            font-size: 1.1rem;
            font-weight: 800;
        }

        .home-alert-value-high { color: var(--bh-red); }
        .home-alert-value-medium { color: #B7791F; }
        .home-alert-value-low { color: var(--bh-navy); }

        /* ---- Espaces métiers (cartes + bouton natif Streamlit) ---- */
        .home-dept-marker { display: none; }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.home-dept-marker) {
            height: 100%;
            padding: 1.2rem 1.25rem 1.1rem !important;
            background: #FFFFFF !important;
            border: 1px solid var(--bh-line) !important;
            border-radius: 18px !important;
            box-shadow: 0 8px 20px rgba(22,24,29,.05) !important;
            transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.home-dept-marker):hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 34px rgba(22,24,29,.1) !important;
            border-color: rgba(227,30,36,.3) !important;
        }

        .home-dept-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 46px;
            height: 46px;
            margin-bottom: .8rem;
            color: #FFFFFF;
            background: linear-gradient(135deg, var(--bh-red), rgb(10,34,64));
            border-radius: 13px;
        }

        .home-dept-title {
            color: var(--bh-navy);
            font-size: .98rem;
            font-weight: 750;
        }

        .home-dept-desc {
            margin: .35rem 0 .95rem;
            color: var(--bh-muted);
            font-size: .78rem;
            line-height: 1.55;
            min-height: 3.4em;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.home-dept-marker) .stButton > button[kind="secondary"] {
            color: var(--bh-red) !important;
            background: var(--bh-red-soft) !important;
            border: 1px solid #F1B7BA !important;
            font-weight: 700 !important;
        }

        [data-testid="stVerticalBlockBorderWrapper"]:has(.home-dept-marker) .stButton > button[kind="secondary"]:hover {
            color: #FFFFFF !important;
            background: var(--bh-red) !important;
            border-color: var(--bh-red) !important;
        }

        @media (max-width: 800px) {
            .home-greeting { padding: 1.1rem 1.2rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _charger_alertes_globales() -> list[dict]:
    """Anomalies et points de vigilance à l'échelle de la banque (lecture seule)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        'SELECT COUNT(*) FROM "transaction" '
        "WHERE amount > 8000 AND strftime('%Y', transaction_date) = '2024'"
    )
    suspectes = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM "transaction" WHERE status = \'Failed\'')
    echouees = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM "transaction" WHERE country != \'Tunisie\'')
    etranger = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM account WHERE status = 'Suspended'")
    comptes_suspendus = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM customer WHERE risk_level = 'High'")
    clients_risque = cur.fetchone()[0]
    conn.close()
    return [
        {
            "icon": "alert-triangle",
            "label": "Opérations suspectes (> 8 000 TND, 2024)",
            "value": suspectes,
            "level": "high",
            "dept": "Audit — Contrôle interne",
        },
        {
            "icon": "shield",
            "label": "Clients à risque élevé",
            "value": clients_risque,
            "level": "high",
            "dept": "Audit — Contrôle interne",
        },
        {
            "icon": "x-circle",
            "label": "Transactions échouées",
            "value": echouees,
            "level": "medium",
            "dept": "Audit — Contrôle interne",
        },
        {
            "icon": "globe",
            "label": "Opérations depuis l'étranger",
            "value": etranger,
            "level": "medium",
            "dept": "Audit — Contrôle interne",
        },
        {
            "icon": "lock",
            "label": "Comptes suspendus",
            "value": comptes_suspendus,
            "level": "low",
            "dept": "Relation Client — Agences",
        },
    ]


def render_home_greeting() -> None:
    """Section 1 — En-tête personnalisé (remplace le hero institutionnel)."""
    utilisateur = st.session_state.get("user", "")
    role_label = (
        "Administrateur"
        if st.session_state.get("role") == "administrateur"
        else "Utilisateur"
    )
    initiale = utilisateur[:1].upper() if utilisateur else "?"
    date_du_jour = _date_francaise(datetime.now())

    st.markdown(
        f"""
        <div class="home-greeting">
            <div class="home-greeting-left">
                <div class="home-greeting-avatar">{html.escape(initiale)}</div>
                <div>
                    <div class="home-greeting-hello">Bonjour, {html.escape(utilisateur)}</div>
                    <div class="home-greeting-date">{date_du_jour} · {role_label}</div>
                </div>
            </div>
            <div class="home-greeting-status">
                <span class="home-status-dot"></span>
                Données synchronisées
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home_kpi_overview() -> None:
    """Section 2 — KPI consolidés, tous départements confondus."""
    kpi = _charger_kpi_dashboard()
    st.markdown(
        f"""
        <div class="home-section">
            <div class="home-section-head">
                <span class="home-section-eyebrow">Temps réel</span>
                <h3 class="home-section-title">Indicateurs consolidés</h3>
            </div>
            <div class="home-kpi-grid">
                <div class="home-kpi-card">
                    <div class="home-kpi-icon">{_home_icon('users', 20)}</div>
                    <div class="home-kpi-value">{_formater_nombre(kpi['clients_actifs'])}</div>
                    <div class="home-kpi-label">Clients actifs</div>
                </div>
                <div class="home-kpi-card">
                    <div class="home-kpi-icon">{_home_icon('credit-card', 20)}</div>
                    <div class="home-kpi-value">{_formater_nombre(kpi['comptes_actifs'])}</div>
                    <div class="home-kpi-label">Comptes actifs</div>
                    <div class="home-kpi-sub">{kpi['ratio_comptes']} compte(s) / client</div>
                </div>
                <div class="home-kpi-card">
                    <div class="home-kpi-icon">{_home_icon('bar-chart-2', 20)}</div>
                    <div class="home-kpi-value">{_formater_nombre(kpi['transactions_2024'])}</div>
                    <div class="home-kpi-label">Transactions 2024</div>
                </div>
                <div class="home-kpi-card home-kpi-card-alert">
                    <div class="home-kpi-icon home-kpi-icon-alert">{_home_icon('alert-triangle', 20)}</div>
                    <div class="home-kpi-value home-kpi-value-alert">{_formater_nombre(kpi['transactions_suspectes_2024'])}</div>
                    <div class="home-kpi-label">Opérations suspectes</div>
                    <div class="home-kpi-sub">{kpi['ratio_suspectes']}% du volume 2024</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home_alerts() -> None:
    """Section 3 — Alertes et anomalies à surveiller."""
    alertes = _charger_alertes_globales()
    rows_html = "".join(
        f"""
        <div class="home-alert-row">
            <div class="home-alert-icon home-alert-icon-{item['level']}">{_home_icon(item['icon'], 18)}</div>
            <div class="home-alert-body">
                <div class="home-alert-label">{html.escape(item['label'])}</div>
                <div class="home-alert-dept">{html.escape(item['dept'])}</div>
            </div>
            <div class="home-alert-value home-alert-value-{item['level']}">{_formater_nombre(item['value'])}</div>
        </div>
        """
        for item in alertes
    )
    st.markdown(
        f"""
        <div class="home-section">
            <div class="home-section-head">
                <span class="home-section-eyebrow">Vigilance</span>
                <h3 class="home-section-title">Alertes &amp; anomalies</h3>
            </div>
            <div class="home-alerts-card">{rows_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home_network() -> None:
    """Section 7 — Réseau d'agences (carte géographique réelle, Leaflet/OSM)."""
    st.markdown(
        """
        <div class="home-section">
            <div class="home-section-head">
                <span class="home-section-eyebrow">Présence nationale</span>
                <h3 class="home-section-title">Réseau d'agences</h3>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    markers_js = ",".join(
        "{lat:%s,lon:%s,name:%s,agences:%s}"
        % (
            city["lat"],
            city["lon"],
            json.dumps(city["name"]),
            city["agences"],
        )
        for city in HOME_NETWORK_CITIES
    )

    components.html(
        f"""
        <html>
        <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <style>
            html, body {{ margin: 0; padding: 0; font-family: Inter, "Segoe UI", Arial, sans-serif; }}
            #map {{
                height: 420px;
                width: 100%;
                border-radius: 22px;
                box-shadow: 0 18px 40px rgba(10,34,64,.22);
            }}
            .bh-map-caption {{
                position: absolute;
                z-index: 500;
                top: 18px;
                left: 18px;
                max-width: 230px;
                padding: 14px 16px;
                color: #FFFFFF;
                background: rgba(10,34,64,.82);
                backdrop-filter: blur(6px);
                border: 1px solid rgba(255,255,255,.15);
                border-radius: 14px;
                font-size: .78rem;
                line-height: 1.55;
                pointer-events: none;
            }}
            .bh-map-caption strong {{
                display: block;
                margin-bottom: 4px;
                font-size: 1.35rem;
                font-weight: 800;
            }}
            .leaflet-tooltip.bh-tooltip {{
                background: #16181D;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: .72rem;
                font-weight: 650;
                padding: 5px 9px;
            }}
        </style>
        </head>
        <body>
            <div style="position:relative;">
                <div class="bh-map-caption">
                    <strong>151 agences</strong>
                    Un maillage national au service de la proximité, présent dans
                    les principales régions de Tunisie.
                </div>
                <div id="map"></div>
            </div>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
                const map = L.map('map', {{
                    zoomControl: true,
                    scrollWheelZoom: false,
                    attributionControl: false,
                }}).setView([34.6, 9.6], 6.3);

                L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                    maxZoom: 18,
                }}).addTo(map);

                const cities = [{markers_js}];
                cities.forEach((city) => {{
                    const radius = 6 + Math.min(city.agences / 4, 10);
                    const marker = L.circleMarker([city.lat, city.lon], {{
                        radius: radius,
                        fillColor: '#E31E24',
                        color: '#FFFFFF',
                        weight: 2,
                        fillOpacity: 0.9,
                    }}).addTo(map);
                    marker.bindTooltip(
                        city.name + ' — ' + city.agences + ' agence(s)',
                        {{ direction: 'top', className: 'bh-tooltip', offset: [0, -6] }}
                    );
                }});
            </script>
        </body>
        </html>
        """,
        height=430,
        scrolling=False,
    )


def render_home_departments() -> None:
    """Section 9 — Espaces métiers (cartes cliquables vers les départements)."""
    st.markdown(
        """
        <div class="home-section" id="home-departments">
            <div class="home-section-head">
                <span class="home-section-eyebrow">Explorer</span>
                <h3 class="home-section-title">Espaces métiers</h3>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(len(HOME_DEPARTMENTS), gap="medium")
    for index, dept in enumerate(HOME_DEPARTMENTS):
        with cols[index]:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="home-dept-marker"></div>
                    <div class="home-dept-icon">{_home_icon(dept['icon'])}</div>
                    <div class="home-dept-title">{html.escape(dept['title'])}</div>
                    <p class="home-dept-desc">{html.escape(dept['desc'])}</p>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Accéder",
                    key=f"home_dept_btn_{index}",
                    use_container_width=True,
                ):
                    st.session_state.departement = dept["id"]
                    conv = _conversation_active()
                    if conv and conv.get("departement") != dept["id"]:
                        _reinitialiser_vue_analyse()
                    st.rerun()


def render_home_dashboard() -> None:
    """Orchestrateur — cockpit opérationnel affiché pour la Vue globale."""
    inject_home_css()
    render_home_greeting()
    render_home_kpi_overview()
    render_home_alerts()
    render_home_network()
    render_home_departments()


def render_validation_center() -> None:
    st.markdown(
        """
        <div class="app-toolbar">
            <div class="toolbar-product">
                <span class="toolbar-monogram">BH</span>
                <span>Centre de validation NL2SQL</span>
                <span class="toolbar-context">/ Contrôle qualité</span>
            </div>
            <div class="toolbar-live">Réservé aux administrateurs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero">
            <div class="hero-eyebrow">Qualité et traçabilité</div>
            <h1>Vérifiez chaque réponse par les données.</h1>
            <p>
                Le SQL généré par le LLM est comparé à une requête de référence.
                Le contrôle signale également les nombres de la synthèse qui ne
                proviennent pas des résultats.
            </p>
            <div class="hero-meta">
                <span>Comparaison des résultats</span>
                <span>Contrôle des chiffres cités</span>
                <span>SQL entièrement visible</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    questions = charger_questions_reference()
    if not questions:
        st.error("Le fichier questions_reference.json est introuvable ou invalide.")
        return

    section_title("Jeu de référence", "Tester une question métier")
    with st.container(border=True):
        index = st.selectbox(
            "Question à vérifier",
            options=range(len(questions)),
            format_func=lambda position: questions[position]["question"],
        )
        selection = questions[index]
        resultat_precedent = st.session_state.get("validation_result")
        if (
            resultat_precedent
            and resultat_precedent.get("question") != selection["question"]
        ):
            st.session_state.pop("validation_result", None)
        with st.expander("Afficher le SQL de référence"):
            st.code(selection["sql_reference"], language="sql")

        if st.button(
            "Lancer la vérification",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("Génération et comparaison des résultats..."):
                st.session_state.validation_result = valider_question_api(
                    selection["question"],
                    selection["sql_reference"],
                )

    resultat = st.session_state.get("validation_result")
    if resultat:
        if "erreur" in resultat and "conforme" not in resultat:
            st.error(resultat["erreur"])
        else:
            conforme = resultat.get("conforme", False)
            fondee = resultat.get("reponse_fondee", False)
            classe = "validation-ok" if conforme and fondee else "validation-ko"
            titre = (
                "Validation réussie"
                if conforme and fondee
                else "Écart détecté — contrôle manuel requis"
            )
            st.markdown(
                f"""
                <div class="validation-status {classe}">
                    {titre}
                </div>
                """,
                unsafe_allow_html=True,
            )

            controle_1, controle_2 = st.columns(2)
            controle_1.metric(
                "Résultat SQL",
                "Conforme" if conforme else "Différent",
            )
            controle_2.metric(
                "Chiffres de la synthèse",
                "Traçables" if fondee else "À vérifier",
            )

            st.markdown(
                f"""
                <div class="answer-card">
                    <div class="answer-label">Réponse évaluée</div>
                    <div class="answer-text">
                        {html.escape(str(resultat.get("reponse", "")))}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            reference, genere = st.columns(2)
            with reference:
                with st.expander("SQL de référence", expanded=True):
                    st.code(resultat.get("sql_reference", ""), language="sql")
            with genere:
                with st.expander("SQL généré", expanded=True):
                    st.code(resultat.get("sql_genere", ""), language="sql")

            if resultat.get("nombres_non_traces"):
                st.warning(
                    "Nombres non retrouvés dans les données : "
                    + ", ".join(resultat["nombres_non_traces"])
                )

    section_title("Catalogue", "Questions actuellement couvertes")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Identifiant": question["id"],
                    "Question métier": question["question"],
                }
                for question in questions
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )


def _render_app_footer() -> None:
    st.markdown(
        """
        <div class="app-footer">
            <span>BH Bank · Plateforme interne d'intelligence décisionnelle</span>
            <span>Accès sécurisé · Données à usage professionnel</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_principale() -> None:
    inject_global_css()
    _init_session_chat()
    _charger_conversations_utilisateur()
    vue = render_sidebar()
    departement = st.session_state.departement

    if vue == "Centre de validation":
        render_validation_center()
        return

    if departement == "Tous les départements":
        # Vue globale = dashboard institutionnel BH Bank (pas d'assistant IA ici).
        st.markdown('<div class="main-workspace">', unsafe_allow_html=True)
        render_home_dashboard()
        st.markdown("</div>", unsafe_allow_html=True)
        _render_app_footer()
        return

    mapping_file = _get_mapping_actif()

    # Layout 3 colonnes : contenu principal | historique à droite
    main_col, hist_col = st.columns([0.74, 0.26], gap="medium")

    with main_col:
        st.markdown('<div class="main-workspace">', unsafe_allow_html=True)
        render_page_topbar(departement)
        render_department_header(departement)
        afficher_kpi_automatiques(departement)
        render_suggestions(departement)
        render_analysis_thread(departement)

        with st.container(border=False):
            st.markdown('<div class="composer-anchor"></div>', unsafe_allow_html=True)
            question, submitted, upload = render_composer()
        st.markdown("</div>", unsafe_allow_html=True)

    with hist_col:
        st.markdown('<div class="history-column-anchor"></div>', unsafe_allow_html=True)
        render_history_panel(departement)

    if upload is not None:
        mapping_file = _get_mapping_actif(upload)
    else:
        mapping_file = _get_mapping_actif()

    pending = st.session_state.pop("pending_question", None)
    if pending:
        _lancer_question(pending, mapping_file, departement)
        st.rerun()

    if submitted:
        if not question.strip():
            st.warning("Formulez une question avant de lancer l'analyse.")
        else:
            _lancer_question(question, mapping_file, departement)
            st.rerun()

    _render_app_footer()


if st.session_state.get("logged") and st.session_state.get("token"):
    page_principale()
else:
    page_login()
