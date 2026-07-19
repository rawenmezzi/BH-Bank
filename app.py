"""
Interface Streamlit — BH Bank AI Agent.
"""

import base64
import html
import os
import sys

import pandas as pd
import requests
import streamlit as st


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

API_URL = os.getenv("API_URL", "http://localhost:8000")
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
SIEGE_PATH = os.path.join(BASE_DIR, "assets", "fond.png")

st.set_page_config(
    page_title="BH Bank — Intelligence bancaire",
    page_icon="🏦",
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


def inject_global_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bh-red: #E31E24;
            --bh-red-dark: #B9151A;
            --bh-red-soft: #FFF1F2;
            --bh-ink: #16181D;
            --bh-muted: #69707D;
            --bh-line: #E8E9ED;
            --bh-surface: #FFFFFF;
            --bh-bg: #F6F7F9;
            --bh-green: #16A36A;
        }

        html, body, [class*="css"] {
            font-family: Inter, "Segoe UI", Arial, sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 92% 2%, rgba(227, 30, 36, .055), transparent 22rem),
                var(--bh-bg);
            color: var(--bh-ink);
        }

        .block-container {
            max-width: 1440px;
            padding: 2rem 2.5rem 3rem;
        }

        #MainMenu, footer, header {
            visibility: hidden;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: var(--bh-surface);
            border-right: 1px solid var(--bh-line);
        }

        [data-testid="stSidebarContent"] {
            padding: 1.35rem 1rem 1.5rem;
        }

        [data-testid="stSidebar"] .stButton button {
            min-height: 2.65rem;
            justify-content: flex-start;
            padding: .55rem .8rem;
            font-size: .84rem;
            font-weight: 550;
            color: #4D535E !important;
            background: #FAFAFB !important;
            border: 1px solid transparent !important;
            box-shadow: none !important;
        }

        [data-testid="stSidebar"] .stButton button:hover {
            color: var(--bh-red) !important;
            background: var(--bh-red-soft) !important;
            border-color: #FFD5D7 !important;
            transform: translateX(2px);
        }

        [data-testid="collapsedControl"] {
            color: white !important;
            background: var(--bh-red) !important;
            border-radius: 0 10px 10px 0 !important;
            box-shadow: 0 8px 20px rgba(227, 30, 36, .24);
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

        [data-testid="stFileUploader"] section {
            padding: .7rem;
            background: #FAFAFB !important;
            border: 1px dashed #D7D9DE !important;
            border-radius: 12px;
        }

        [data-testid="stFileUploader"] section button {
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
            color: var(--bh-ink) !important;
            font-size: 1.25rem;
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
            color: var(--bh-ink);
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


def poser_question(question: str, role: str, mapping_file=None) -> dict:
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
            data={"question": question, "role": role},
            files=files,
            timeout=60,
        )
        return response.json()
    except (requests.RequestException, ValueError) as error:
        return {"erreur": f"Erreur de connexion au serveur : {error}"}


def section_title(kicker: str, title: str) -> None:
    st.markdown(
        f"""
        <div class="section-title">
            <span>{html.escape(kicker)}</span>
            <h2>{html.escape(title)}</h2>
        </div>
        """,
        unsafe_allow_html=True,
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
                        st.session_state.logged = True
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects.")

            st.markdown(
                """
                <div class="login-security">🔒 Connexion protégée · Session de 8 heures</div>
                <div class="login-demo">
                    Accès de démonstration<br>
                    <b>user / user123</b>&nbsp;&nbsp; ou &nbsp;&nbsp;<b>admin / admin123</b>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_sidebar():
    with st.sidebar:
        logo = image_to_base64(LOGO_PATH)
        st.markdown(
            f'<div class="bh-brand"><img src="data:image/png;base64,{logo}" alt="BH Bank"></div>',
            unsafe_allow_html=True,
        )

        role_label = (
            "Administrateur"
            if st.session_state.role == "administrateur"
            else "Utilisateur"
        )
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-status">
                    <span class="profile-dot"></span>Session active
                </div>
                <div class="profile-name">{html.escape(st.session_state.user)}</div>
                <div class="profile-role">{role_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="side-label">Contexte métier</div>', unsafe_allow_html=True)
        mapping_file = st.file_uploader(
            "Importer un mapping",
            type=["xlsx", "csv", "json"],
            help="Correspondances entre les termes métier et les colonnes SQL.",
            label_visibility="collapsed",
        )
        if mapping_file:
            st.markdown(
                f'<div class="mapping-ok">✓ {html.escape(mapping_file.name)}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="side-label">Questions suggérées</div>', unsafe_allow_html=True)
        examples = [
            "Nombre de clients actifs",
            "Classement par volume de transactions",
            "Clients à profil de risque élevé",
            "Opérations atypiques — 2024",
            "Volume transactionnel par canal",
            "Agence à plus fort portefeuille",
            "Solde moyen des comptes épargne",
            "Répartition débit / crédit",
        ]
        for index, example in enumerate(examples):
            if st.button(example, key=f"example_{index}", use_container_width=True):
                st.session_state.question_input = example
                st.session_state.pop("last_result", None)
                st.rerun()

        st.markdown('<div class="side-label">Compte</div>', unsafe_allow_html=True)
        if st.button("↪  Terminer la session", use_container_width=True):
            for key in [
                "user",
                "role",
                "logged",
                "question_input",
                "last_result",
            ]:
                st.session_state.pop(key, None)
            st.rerun()

    return mapping_file


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


def render_result(result: dict) -> None:
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
            with st.expander("Voir la requête SQL générée"):
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
            )
        with technical_column:
            with st.expander("Voir la requête SQL utilisée"):
                st.code(result["sql"], language="sql")
    else:
        st.info("La requête n’a retourné aucune donnée.")
        with st.expander("Voir la requête SQL utilisée"):
            st.code(result["sql"], language="sql")


def page_principale() -> None:
    inject_global_css()
    mapping_file = render_sidebar()

    st.markdown(
        """
        <div class="app-toolbar">
            <div class="toolbar-product">
                <span class="toolbar-monogram">BH</span>
                <span>Intelligence décisionnelle</span>
                <span class="toolbar-context">/ Assistant analytique</span>
            </div>
            <div class="toolbar-live">Services opérationnels</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">Intelligence bancaire</div>
            <h1>Pilotez vos décisions par la donnée.</h1>
            <p>
                Interrogez les données BH Bank en langage naturel.
                Notre assistant transforme chaque demande en analyse structurée,
                traçable et immédiatement exploitable.
            </p>
            <div class="hero-meta">
                <span>Groq Llama 3.3 — 70B</span>
                <span>Base de données BH Bank</span>
                <span>Profil {html.escape(st.session_state.role.capitalize())}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown(
            """
            <div class="main-query-card">
                <span>Nouvelle analyse</span>
                <h2>Que souhaitez-vous savoir ?</h2>
                <p>
                    Formulez votre demande comme vous la présenteriez à un analyste métier.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("question_form"):
            question = st.text_area(
                "Votre question",
                key="question_input",
                placeholder=(
                    "Ex. Identifier les clients à haut risque ayant effectué "
                    "des opérations atypiques en 2024."
                ),
                height=112,
                label_visibility="collapsed",
            )
            helper, action = st.columns([4.5, 1.2], vertical_alignment="center")
            with helper:
                st.caption("Les résultats incluent la synthèse, le SQL et les données sources.")
            with action:
                submitted = st.form_submit_button(
                    "Lancer l’analyse  →",
                    type="primary",
                    use_container_width=True,
                )

    if submitted:
        if not question.strip():
            st.warning("Formulez une question avant de lancer l’analyse.")
        else:
            with st.spinner("L’assistant analyse votre demande..."):
                st.session_state.last_result = poser_question(
                    question=question.strip(),
                    role=st.session_state.role,
                    mapping_file=mapping_file,
                )

    if "last_result" in st.session_state:
        render_result(st.session_state.last_result)

    st.markdown(
        """
        <div class="app-footer">
            <span>BH Bank · Plateforme interne d’intelligence décisionnelle</span>
            <span>Accès sécurisé · Données à usage professionnel</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


if st.session_state.get("logged"):
    page_principale()
else:
    page_login()
