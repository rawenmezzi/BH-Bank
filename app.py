"""
app.py
Interface Streamlit moderne — BH Bank AI Agent
Couleurs : Rouge #C0392B | Blanc | Noir
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import requests
import pandas as pd
import base64

# ── Configuration ─────────────────────────────────────────────────
st.set_page_config(
    page_title="BH Bank — AI Agent",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://localhost:8000"

# ── Logo BH Bank (officiel) ───────────────────────────────────────
LOGO_PATH = "assets/logo.png"

# ── Photo siège BH Bank ───────────────────────────────────────────
SIEGE_PATH = "assets/fond.png"


# ══════════════════════════════════════════════════════════════════
# CSS GLOBAL
# ══════════════════════════════════════════════════════════════════

def inject_css():
    st.markdown("""
    <style>
   /* ── Supprime espace vide haut sidebar ── */
[data-testid="stSidebar"] {
    padding-top: 0 !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
    margin-top: -4rem !important;
}

[data-testid="stSidebarContent"] {
    padding-top: 0.5rem !important;
}   

    /* ================================
       BH BANK COLOR PALETTE
    ================================= */

    :root {
        --bh-red: #E31E24;
        --bh-red-dark: #C0392B;
        --bh-black: #1A1A1A;
        --bh-gray: #666666;
        --bh-border: #E5E5E5;
        --bh-background: #FAFAFA;
        --bh-white: #FFFFFF;
    }


    /* ================================
       MAIN BACKGROUND
    ================================= */

    .stApp {
        background-color: #FAFAFA;
        color: #1A1A1A;
    }


    /* ================================
       SIDEBAR
    ================================= */

    [data-testid="stSidebar"] {

        background-color: #FFFFFF !important;

        border-right: 1px solid #E5E5E5;

    }


    [data-testid="stSidebar"] * {

        color: #1A1A1A !important;

    }


    [data-testid="stSidebar"] img {

        margin-bottom: 10px;

    }



    /* ================================
       BUTTON PRIMARY
    ================================= */


    .stButton > button[kind="primary"] {

        background-color: #E31E24 !important;

        color:white !important;

        border:none !important;

        border-radius:8px !important;

        font-weight:600 !important;

        padding:0.6rem 1.5rem !important;

        transition:0.2s;

    }


    .stButton > button[kind="primary"]:hover {

        background-color:#C0392B !important;

    }



    /* ================================
       BUTTON SECONDARY
    ================================= */


    .stButton > button {

        background-color:#FFFFFF !important;

        color:#1A1A1A !important;

        border:1px solid #E5E5E5 !important;

        border-radius:8px !important;

    }



    .stButton > button:hover {

        border-color:#E31E24 !important;

        color:#E31E24 !important;

    }




    /* ================================
       INPUTS
    ================================= */


    .stTextInput input {

        background-color:white !important;

        color:#1A1A1A !important;

        border:1px solid #DADADA !important;

        border-radius:8px !important;

    }


    .stTextInput input:focus {

        border:2px solid #E31E24 !important;

    }



    /* ================================
       TITLES
    ================================= */


    h1 {

        color:#1A1A1A !important;

        border-bottom:3px solid #E31E24;

        padding-bottom:10px;

        font-weight:700;

    }


    h2,h3 {

        color:#1A1A1A !important;

    }




    /* ================================
       METRICS
    ================================= */


    [data-testid="stMetric"] {

        background:#FFFFFF;

        border:1px solid #E5E5E5;

        border-radius:12px;

        padding:20px;

        box-shadow:0px 4px 12px rgba(0,0,0,0.05);

    }


    [data-testid="stMetricValue"] {

        color:#E31E24 !important;

        font-size:2rem !important;

        font-weight:700 !important;

    }



    /* ================================
       ALERTS
    ================================= */


    .stAlert {

        background:white !important;

        color:#1A1A1A !important;

        border-left:4px solid #E31E24;

    }



    /* ================================
       EXPANDERS
    ================================= */


    .streamlit-expanderHeader {

        background:#FFFFFF !important;

        color:#1A1A1A !important;

        border:1px solid #E5E5E5 !important;

        border-radius:10px !important;

    }




    /* ================================
       FILE UPLOADER
    ================================= */

/* NOUVEAU */
[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border: 1px dashed #E31E24 !important;
    border-radius: 10px !important;
}

[data-testid="stFileUploader"] * {
    color: #1A1A1A !important;
    background: #FFFFFF !important;
}

[data-testid="stFileDropzone"] {
    background: #FFFFFF !important;
}

[data-testid="stFileDropzone"] * {
    color: #1A1A1A !important;
}




    /* ================================
       DATAFRAME
    ================================= */


    .stDataFrame {

        border:1px solid #E5E5E5 !important;

        border-radius:10px;

    }



    /* ================================
       RESPONSE CARD IA
    ================================= */


    .response-card {

        background:#FFFFFF;

        border-left:5px solid #E31E24;

        border-radius:10px;

        padding:20px;

        box-shadow:0 4px 15px rgba(0,0,0,0.08);

    }



    /* ================================
       DIVIDER
    ================================= */


    hr {

        border-color:#E31E24 !important;

        opacity:0.25;

    }



    /* Hide Streamlit menu */

   /* Hide Streamlit menu uniquement */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* ── Toggle sidebar TOUJOURS visible ── */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background-color: #E31E24 !important;
    border-radius: 0 8px 8px 0 !important;
    width: 20px !important;
    height: 60px !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    position: fixed !important;
    left: 0 !important;
    top: 50% !important;
    z-index: 9999 !important;
    box-shadow: 2px 0 8px rgba(0,0,0,0.2) !important;
}

[data-testid="collapsedControl"]:hover {
    background-color: #C0392B !important;
    width: 24px !important;
}

[data-testid="collapsedControl"] svg {
    fill: white !important;
    stroke: white !important;
}
                /* Warning texte noir */
[data-testid="stAlert"] p,
.stAlert p,
[data-baseweb="notification"] p {
    color: #1A1A1A !important;
}

[data-testid="stAlert"] {
    background: #FFF9E6 !important;
    border-left: 4px solid #E31E24 !important;
    color: #1A1A1A !important;
}


    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# CSS PAGE LOGIN
# ══════════════════════════════════════════════════════════════════
def image_to_base64(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()
def inject_login_css():

    st.markdown(f"""
    <style>


    /* ================================
       LOGIN BACKGROUND IMAGE
    ================================= */


    .stApp {{

        background-image:

        linear-gradient(

            rgba(255,255,255,0.78),

            rgba(255,255,255,0.78)

        ),

        url("data:image/png;base64,{image_to_base64(SIEGE_PATH)}");


        background-size:cover;

        background-position:center;

        background-attachment:fixed;

    }}




    /* ================================
       LOGIN CARD
    ================================= */
   .login-logo {{

    display:flex;

    justify-content:center;

    align-items:center;

    margin-top:-120px;
    margin-bottom:10px;

   }}


.login-logo img {{

    width:180px;

    height:auto;

    object-fit:contain;

 }}


    .login-card {{

        background:rgba(255,255,255,0.95);

        border:1px solid #E31E24;

        border-radius:16px;

        padding:2.5rem 2rem;

        max-width:420px;

        margin:auto;

        box-shadow:

        0 10px 40px rgba(0,0,0,0.15);

        backdrop-filter:blur(10px);

    }}




    /* TITLE */

    .login-title {{

        color:#1A1A1A;

        font-size:1.7rem;

        font-weight:700;

        text-align:center;

    }}



    .login-subtitle {{

        color:#666666;

        font-size:0.95rem;

        text-align:center;

    }}



    /* RED LINE */

    .bh-red-line {{

        height:3px;

        background:#E31E24;

        border-radius:5px;

        margin:1rem 0 1.5rem 0;

    }}
    /* Labels inputs login en noir */
    .stTextInput label,
    .stTextInput label p {{
    color: #1A1A1A !important;
    font-weight: 600 !important;
    }}



    </style>

    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# FONCTIONS API
# ══════════════════════════════════════════════════════════════════

def login_api(username: str, password: str):
    try:
        r = requests.post(
            f"{API_URL}/login",
            data={"username": username, "password": password},
            timeout=10
        )
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        st.error("Impossible de contacter le serveur FastAPI. Verifiez qu'il tourne.")
        return None


def poser_question(question: str, role: str, mapping_file=None):
    try:
        data  = {"question": question, "role": role}
        files = {}
        if mapping_file:
            files["mapping_file"] = (
                mapping_file.name,
                mapping_file.getvalue(),
                "application/octet-stream"
            )
        r = requests.post(
            f"{API_URL}/api/ask",
            data=data,
            files=files if files else None,
            timeout=60
        )
        return r.json()
    except Exception as e:
        return {"erreur": f"Erreur connexion serveur : {e}"}


# ══════════════════════════════════════════════════════════════════
# PAGE LOGIN
# ══════════════════════════════════════════════════════════════════

def page_login():
    inject_login_css()

    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:

        # ── Card ─────────────────────────────────────────────────
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        # Logo
       # Logo BH Bank dans la card
        st.markdown(
             f"""
             <div class="login-logo">
             <img src="data:image/png;base64,{image_to_base64(LOGO_PATH)}">
             </div>
              """,
              unsafe_allow_html=True
        )

        st.markdown('<div class="bh-red-line"></div>', unsafe_allow_html=True)

        st.markdown('<div class="login-title">BIENVENUE</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="login-subtitle">Interrogation intelligente des données bancaires</div>',
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Formulaire
        username = st.text_input(
            "Nom d'utilisateur",
            placeholder="Entrez votre identifiant"
        )
        password = st.text_input(
            "Mot de passe",
            type="password",
            placeholder="••••••••"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Se connecter", type="primary", use_container_width=True):
            if not username or not password:
                st.warning("Veuillez remplir tous les champs.")
            else:
                with st.spinner("Authentification..."):
                    result = login_api(username, password)
                if result:
                    st.session_state.user   = result["username"]
                    st.session_state.role   = result["role"]
                    st.session_state.logged = True
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")

        st.markdown("---")
        st.caption("Comptes de test  |  `user / user123`  ou  `admin / admin123`")

        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# PAGE PRINCIPALE
# ══════════════════════════════════════════════════════════════════

def page_principale():
    inject_css()

    # ── Sidebar ───────────────────────────────────────────────────
    with st.sidebar:

        # Logo haute qualité base64
        st.markdown(
            f"""
            <div style="
                display:flex;
                justify-content:center;
                align-items:center;
                padding:4px 0 4px 0;
            ">
                <img
                    src="data:image/png;base64,{image_to_base64(LOGO_PATH)}"
                    style="width:160px; height:auto; object-fit:contain;"
                />
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="
                height:2px;
                background:#E31E24;
                border-radius:2px;
                margin:8px 0 16px 0;
            "></div>
            """,
            unsafe_allow_html=True
        )

        # Profil utilisateur
        profil = "Administrateur" if st.session_state.role == "administrateur" else "Utilisateur"
       # NOUVEAU — avec indicateur vert
        st.markdown(
         f"""
    <div style="
        background:#f9f9f9;
        border:1px solid #e5e5e5;
        border-left:3px solid #E31E24;
        border-radius:8px;
        padding:12px 14px;
        margin-bottom:16px;
    ">
        <div style="
            display:flex;
            align-items:center;
            gap:8px;
            margin-bottom:6px;
        ">
            <span style="
                display:inline-block;
                width:9px;
                height:9px;
                background:#27AE60;
                border-radius:50%;
                box-shadow: 0 0 0 2px rgba(39,174,96,0.25);
                flex-shrink:0;
            "></span>
            <span style="
                font-size:0.72rem;
                font-weight:700;
                text-transform:uppercase;
                letter-spacing:1.5px;
                color:#999;
            ">
                Session active
            </span>
        </div>
        <div style="
            font-size:1rem;
            font-weight:700;
            color:#1A1A1A;
        ">
            {st.session_state.user}
        </div>
        <div style="
            font-size:0.82rem;
            color:#666;
            margin-top:2px;
        ">
            Profil : {profil}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

        # Upload mapping
        st.markdown(
            """
            <div style="
                font-size:0.75rem;
                font-weight:700;
                text-transform:uppercase;
                letter-spacing:1.5px;
                color:#999;
                margin-bottom:8px;
            ">
                Fichier de correspondance
            </div>
            """,
            unsafe_allow_html=True
        )
        mapping_file = st.file_uploader(
            "Format accepté : Excel, CSV, JSON",
            type=["xlsx", "csv", "json"],
            help="Fichier de mapping des termes métier vers les colonnes SQL"
        )
        if mapping_file:
            st.markdown(
                f"""
                <div style="
                    background:#fff5f5;
                    border:1px solid #E31E24;
                    border-radius:6px;
                    padding:8px 12px;
                    font-size:0.85rem;
                    color:#E31E24;
                    margin-top:6px;
                ">
                    ✓ {mapping_file.name}
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            """
            <div style="
                height:1px;
                background:#e5e5e5;
                margin:16px 0;
            "></div>
            """,
            unsafe_allow_html=True
        )

        # Requêtes types
        st.markdown(
            """
            <div style="
                font-size:0.75rem;
                font-weight:700;
                text-transform:uppercase;
                letter-spacing:1.5px;
                color:#999;
                margin-bottom:10px;
            ">
                Requêtes prédéfinies
            </div>
            """,
            unsafe_allow_html=True
        )

        exemples = [
            "Nombre de clients actifs",
            "Classement par volume de transactions",
            "Clients à profil de risque élevé",
            "Opérations atypiques — 2024",
            "Volume transactionnel par canal",
            "Agence à plus fort portefeuille",
            "Solde moyen des comptes épargne",
            "Répartition débit / crédit",
        ]
        for ex in exemples:
            if st.button(ex, use_container_width=True):
                st.session_state.q = ex
                st.rerun()

        st.markdown(
            """
            <div style="
                height:1px;
                background:#e5e5e5;
                margin:16px 0;
            "></div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Terminer la session", use_container_width=True):
            for k in ["user", "role", "logged", "q"]:
                st.session_state.pop(k, None)
            st.rerun()

    # ══════════════════════════════════════════════════════════════
    # ZONE PRINCIPALE
    # ══════════════════════════════════════════════════════════════

    # ── En-tête principal ─────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            justify-content:space-between;
            padding-bottom:16px;
            border-bottom:3px solid #E31E24;
            margin-bottom:2rem;
        ">
            <div style="display:flex; align-items:center; gap:20px;">
                <img
                    src="data:image/png;base64,{image_to_base64(LOGO_PATH)}"
                    style="width:120px; height:auto; object-fit:contain;"
                />
                <div>
                    <div style="
                        font-size:1.5rem;
                        font-weight:700;
                        color:#1A1A1A;
                        line-height:1.2;
                    ">
                        Système de Requêtage Intelligent
                    </div>
                    <div style="
                        font-size:0.88rem;
                        color:#666;
                        margin-top:4px;
                    ">
                        Interrogation des données bancaires 
                        en langage naturel
                    </div>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="
                    font-size:0.7rem;
                    text-transform:uppercase;
                    letter-spacing:1.5px;
                    color:#999;
                    margin-bottom:4px;
                ">
                    Environnement
                </div>
                <div style="
                    font-size:0.82rem;
                    color:#1A1A1A;
                    font-weight:500;
                ">
                    Moteur LLM : Groq Llama 3.3-70B
                </div>
                <div style="
                    font-size:0.82rem;
                    color:#1A1A1A;
                    font-weight:500;
                ">
                    Source : Base de données — BH Bank
                </div>
                <div style="
                    font-size:0.82rem;
                    color:#1A1A1A;
                    font-weight:500;
                ">
                    Profil : {st.session_state.role.capitalize()}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── Zone de saisie ────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            font-size:0.75rem;
            font-weight:700;
            text-transform:uppercase;
            letter-spacing:1.5px;
            color:#999;
            margin-bottom:8px;
        ">
            Saisie de la requête
        </div>
        """,
        unsafe_allow_html=True
    )

    col_input, col_btn = st.columns([5, 1])
    with col_input:
        question = st.text_input(
            label="requete",
            label_visibility="collapsed",
            value=st.session_state.get("q", ""),
            placeholder=(
                "Ex : Identifier les clients à haut risque ayant "
                "effectué des opérations atypiques en 2024"
            )
        )
    with col_btn:
        analyser = st.button(
            "Analyser",
            type="primary",
            use_container_width=True
        )

    # ── Traitement ────────────────────────────────────────────────
    if analyser and question:

        with st.spinner("Traitement en cours..."):
            resultat = poser_question(
                question     = question,
                role         = st.session_state.role,
                mapping_file = mapping_file if mapping_file else None
            )

        # Erreur
        if "erreur" in resultat:
            st.markdown(
                f"""
                <div style="
                    background:#fff5f5;
                    border-left:4px solid #E31E24;
                    border-radius:0 8px 8px 0;
                    padding:16px 20px;
                    margin-top:1.5rem;
                ">
                    <div style="
                        font-size:0.72rem;
                        font-weight:700;
                        text-transform:uppercase;
                        letter-spacing:1.5px;
                        color:#E31E24;
                        margin-bottom:6px;
                    ">
                        Erreur de traitement
                    </div>
                    <div style="color:#1A1A1A; font-size:0.95rem;">
                        {resultat['erreur']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if resultat.get("sql"):
                with st.expander("Requête SQL générée"):
                    st.code(resultat["sql"], language="sql")

        # Succès
        else:
            st.markdown("<div style='margin-top:1.5rem;'></div>",
                        unsafe_allow_html=True)

            # ── Métriques ─────────────────────────────────────────
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric(
                    "Enregistrements extraits",
                    resultat["nb_resultats"]
                )
            with col_m2:
                st.metric("Moteur d'inférence", "Llama 3.3 — 70B")
            with col_m3:
                st.metric("Source de données", " BH Bank")

            st.markdown(
                """
                <div style="
                    height:1px;
                    background:#e5e5e5;
                    margin:1.5rem 0;
                "></div>
                """,
                unsafe_allow_html=True
            )

            # ── Réponse ───────────────────────────────────────────
            st.markdown(
                f"""
                <div style="
                    background:#FFFFFF;
                    border:1px solid #e5e5e5;
                    border-left:5px solid #E31E24;
                    border-radius:0 10px 10px 0;
                    padding:20px 24px;
                    box-shadow:0 4px 16px rgba(0,0,0,0.06);
                ">
                    <div style="
                        font-size:0.72rem;
                        font-weight:700;
                        text-transform:uppercase;
                        letter-spacing:2px;
                        color:#E31E24;
                        margin-bottom:10px;
                    ">
                        Synthèse analytique
                    </div>
                    <div style="
                        color:#1A1A1A;
                        font-size:1rem;
                        line-height:1.7;
                        font-weight:400;
                    ">
                        {resultat["reponse"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <div style="
                    height:1px;
                    background:#e5e5e5;
                    margin:1.5rem 0;
                "></div>
                """,
                unsafe_allow_html=True
            )

            # ── Détails techniques ────────────────────────────────
            col_sql, col_data = st.columns(2)

            with col_sql:
                with st.expander("Requête SQL générée automatiquement"):
                    st.code(resultat["sql"], language="sql")

            with col_data:
                if resultat.get("donnees"):
                    with st.expander("Données extraites de la base "):
                        df = pd.DataFrame(resultat["donnees"])
                        st.dataframe(df, use_container_width=True)

            # ── Export ────────────────────────────────────────────
            if resultat.get("donnees"):
                df = pd.DataFrame(resultat["donnees"])
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label     = "Exporter les données (CSV)",
                    data      = csv,
                    file_name = "extraction_bh_bank.csv",
                    mime      = "text/csv"
                )

    elif analyser and not question:
        st.warning("Veuillez formuler une requête avant de lancer l'analyse.")


# ══════════════════════════════════════════════════════════════════
# POINT D ENTREE
# ══════════════════════════════════════════════════════════════════

if "logged" not in st.session_state:
    page_login()
else:
    page_principale()