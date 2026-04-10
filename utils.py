from __future__ import annotations

import base64
import html
import json
from datetime import date, timedelta
from io import BytesIO
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from database import get_company_info, get_user_by_username
from services.auth import verify_password


STATUS_COLORS = {
    "Rascunho": "#6b7280",
    "Aprovado": "#22c55e",
    "Recusado": "#ef4444",
}
AUTH_SESSION_KEY = "auth_user"
DEFAULT_APP_TITLE = "Orçamentos de Pintura"
DEFAULT_APP_SHORT_NAME = "Orçamentos"


def configure_page(page_title: str) -> None:
    st.set_page_config(
        page_title=f"{page_title} | {DEFAULT_APP_TITLE}",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def safe_text(value: str | None, fallback: str = "-") -> str:
    text = (value or "").strip()
    return text if text else fallback


def currency(value: float | int | None) -> str:
    number = float(value or 0)
    formatted = f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def get_logo_bytes(company_info: dict | None = None) -> bytes | None:
    company = company_info or get_company_info()
    logo_base64 = (company.get("logo_base64") or "").strip()
    if not logo_base64:
        return None
    try:
        return base64.b64decode(logo_base64)
    except Exception:
        return None


def get_logo_data_uri(company_info: dict | None = None) -> str:
    company = company_info or get_company_info()
    logo_base64 = (company.get("logo_base64") or "").strip()
    logo_mime = safe_text(company.get("logo_mime"), "image/png")
    if not logo_base64:
        return ""
    return f"data:{logo_mime};base64,{logo_base64}"


def get_app_title(company_info: dict | None = None) -> str:
    company = company_info or get_company_info()
    return safe_text(company.get("app_title") or company.get("nome_fantasia"), DEFAULT_APP_TITLE)


def get_app_short_name(company_info: dict | None = None) -> str:
    company = company_info or get_company_info()
    return safe_text(company.get("app_short_name") or company.get("nome_fantasia"), DEFAULT_APP_SHORT_NAME)


def inject_custom_css(page_title: str) -> None:
    company = get_company_info()
    full_title = f"{page_title} | {get_app_title(company)}"
    app_short_name = get_app_short_name(company)
    logo_data_uri = get_logo_data_uri(company)

    st.markdown(
        """
        <style>
            :root {
                --bg-top: #ffffff;
                --bg-bottom: #f7f9fc;
                --surface: #ffffff;
                --surface-muted: #f0f2f6;
                --surface-strong: #fff1f1;
                --border: #e3e7ef;
                --border-strong: #d4dae5;
                --text-main: #262730;
                --text-soft: #31333f;
                --text-muted: #6c7383;
                --brand: #ff4b4b;
                --brand-strong: #e03e3e;
                --brand-deep: #bf2f2f;
                --sidebar-top: #f7f9fc;
                --sidebar-bottom: #eef2f7;
                --sidebar-text: #262730;
                --sidebar-muted: #6c7383;
                --shadow-soft: 0 14px 30px rgba(31, 41, 55, 0.08);
            }
            .stApp {
                background:
                    radial-gradient(circle at top right, rgba(255, 75, 75, 0.10), transparent 28%),
                    linear-gradient(180deg, var(--bg-top) 0%, #fbfcfe 20%, var(--bg-bottom) 100%);
                color: var(--text-main);
                font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, var(--sidebar-top) 0%, var(--sidebar-bottom) 100%);
                border-right: 1px solid var(--border);
            }
            [data-testid="stSidebar"] * {
                color: var(--sidebar-text);
            }
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
                color: var(--sidebar-muted);
            }
            [data-testid="stSidebar"] [data-testid="stButton"] > button {
                background: transparent;
                border: 1px solid transparent;
                color: var(--sidebar-text);
                box-shadow: none;
            }
            [data-testid="stSidebar"] [data-testid="stButton"] > button *,
            [data-testid="stSidebar"] [data-testid="stButton"] > button p,
            [data-testid="stSidebar"] [data-testid="stButton"] > button span {
                color: var(--sidebar-text) !important;
                -webkit-text-fill-color: var(--sidebar-text) !important;
            }
            [data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
                background: rgba(255, 75, 75, 0.08);
                border-color: rgba(255, 75, 75, 0.15);
            }
            [data-testid="stSidebarNav"] {
                background: transparent;
                padding-top: 0.25rem;
            }
            [data-testid="stSidebarNav"] a {
                border-radius: 14px;
                margin-bottom: 0.25rem;
            }
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                max-width: 1400px;
            }
            h1, h2, h3, h4, h5, h6 {
                color: var(--text-main);
            }
            p, li, label, .stCaption, .stMarkdown, .stText {
                color: var(--text-soft);
            }
            [data-testid="stForm"],
            [data-testid="stVerticalBlock"] > [data-testid="stContainer"] {
                color: var(--text-main);
            }
            [data-testid="stMetric"],
            [data-testid="stDataFrame"],
            [data-testid="stExpander"],
            [data-testid="stForm"] {
                border-radius: 16px;
            }
            [data-testid="stForm"] {
                background: rgba(255, 255, 255, 0.96);
                border: 1px solid rgba(216, 219, 225, 0.95);
                padding: 1rem;
                box-shadow: var(--shadow-soft);
            }
            div[data-baseweb="input"] > div,
            div[data-baseweb="select"] > div,
            div[data-baseweb="textarea"] > div,
            [data-testid="stDateInputField"] {
                background: var(--surface);
                border: 1px solid var(--border-strong);
                border-radius: 12px;
                color: var(--text-main);
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.45);
            }
            div[data-baseweb="input"] input,
            div[data-baseweb="textarea"] textarea,
            div[data-baseweb="select"] input {
                color: var(--text-main) !important;
                -webkit-text-fill-color: var(--text-main) !important;
                font-weight: 500;
            }
            div[data-baseweb="input"] > div:focus-within,
            div[data-baseweb="select"] > div:focus-within,
            div[data-baseweb="textarea"] > div:focus-within,
            [data-testid="stDateInputField"]:focus-within {
                border-color: var(--brand);
                box-shadow: 0 0 0 2px rgba(255, 75, 75, 0.18);
            }
            .stButton > button,
            [data-testid="stFormSubmitButton"] > button,
            .stDownloadButton > button,
            [data-testid="stLinkButton"] a {
                background: linear-gradient(180deg, var(--brand) 0%, var(--brand-strong) 100%);
                color: #ffffff;
                border: 1px solid var(--brand-strong);
                border-radius: 12px;
                font-weight: 600;
                box-shadow: 0 6px 14px rgba(255, 75, 75, 0.18);
            }
            .stButton > button *,
            [data-testid="stFormSubmitButton"] > button *,
            [data-testid="stFormSubmitButton"] > button p,
            [data-testid="stFormSubmitButton"] > button span,
            [data-testid="stFormSubmitButton"] > button [data-testid="stMarkdownContainer"] p,
            .stButton > button p,
            .stButton > button span,
            .stButton > button [data-testid="stMarkdownContainer"] p,
            .stDownloadButton > button *,
            .stDownloadButton > button p,
            .stDownloadButton > button span,
            .stDownloadButton > button [data-testid="stMarkdownContainer"] p,
            [data-testid="stLinkButton"] a,
            [data-testid="stLinkButton"] a *,
            [data-testid="stLinkButton"] a p,
            [data-testid="stLinkButton"] a span,
            [data-testid="stLinkButton"] a [data-testid="stMarkdownContainer"] p {
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                text-decoration: none !important;
            }
            .stButton > button:hover,
            [data-testid="stFormSubmitButton"] > button:hover,
            .stDownloadButton > button:hover,
            [data-testid="stLinkButton"] a:hover {
                background: linear-gradient(180deg, #ff6b6b 0%, #e03e3e 100%);
                border-color: #d13737;
                color: #ffffff;
            }
            [data-testid="stFormSubmitButton"] > button:disabled,
            [data-testid="stFormSubmitButton"] > button[disabled] {
                background: linear-gradient(180deg, #ff8585 0%, #f06363 100%);
                border-color: #ea6a6a;
                color: #ffffff !important;
                opacity: 1;
            }
            [data-testid="stFormSubmitButton"] > button:disabled *,
            [data-testid="stFormSubmitButton"] > button[disabled] *,
            [data-testid="stFormSubmitButton"] > button:disabled p,
            [data-testid="stFormSubmitButton"] > button[disabled] p,
            [data-testid="stFormSubmitButton"] > button:disabled span,
            [data-testid="stFormSubmitButton"] > button[disabled] span {
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
            }
            .stButton > button[kind="secondary"],
            [data-testid="stLinkButton"] a[kind="secondary"] {
                background: var(--surface-muted);
                color: var(--text-main);
                border: 1px solid var(--border);
                box-shadow: none;
            }
            .stButton > button[kind="secondary"] *,
            .stButton > button[kind="secondary"] p,
            .stButton > button[kind="secondary"] span,
            .stButton > button[kind="secondary"] [data-testid="stMarkdownContainer"] p {
                color: var(--text-main) !important;
                -webkit-text-fill-color: var(--text-main) !important;
            }
            [data-testid="stAlert"] {
                border-radius: 14px;
                border-width: 1px;
            }
            [data-testid="stDataFrame"] {
                background: var(--surface);
                border: 1px solid var(--border);
                box-shadow: var(--shadow-soft);
            }
            [data-testid="stTable"] {
                color: var(--text-main);
            }
            [data-testid="stExpander"] {
                background: rgba(255, 255, 255, 0.96);
                border: 1px solid rgba(216, 219, 225, 0.9);
                box-shadow: var(--shadow-soft);
            }
            [data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.98);
                border: 1px solid rgba(216, 219, 225, 0.95);
                padding: 0.25rem 0.35rem;
            }
            .page-header {
                position: relative;
                overflow: hidden;
                background:
                    radial-gradient(circle at top right, rgba(255, 255, 255, 0.18), transparent 24%),
                    linear-gradient(135deg, #992d2d 0%, var(--brand-deep) 28%, var(--brand) 100%);
                color: #ffffff;
                border-radius: 24px;
                padding: 1.6rem 1.8rem;
                margin-bottom: 1.2rem;
                box-shadow: 0 18px 44px rgba(255, 75, 75, 0.22);
            }
            .page-header::after {
                content: "";
                position: absolute;
                inset: auto -60px -70px auto;
                width: 200px;
                height: 200px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.12);
            }
            .page-header__content {
                position: relative;
                z-index: 1;
            }
            .page-header__eyebrow {
                margin: 0 0 0.35rem 0;
                font-size: 0.82rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: rgba(255, 255, 255, 0.78);
            }
            .page-header__title-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
                flex-wrap: wrap;
            }
            .page-header__title-row h1 {
                margin: 0;
                color: #ffffff;
                font-size: 2rem;
                line-height: 1.1;
            }
            .page-header__description {
                margin: 0.55rem 0 0 0;
                max-width: 760px;
                color: rgba(255, 255, 255, 0.88);
                font-size: 1rem;
            }
            .page-header__badge {
                display: inline-flex;
                align-items: center;
                border-radius: 999px;
                padding: 0.45rem 0.85rem;
                background: rgba(255, 255, 255, 0.16);
                border: 1px solid rgba(255, 255, 255, 0.18);
                color: #ffffff;
                font-size: 0.82rem;
                font-weight: 700;
                backdrop-filter: blur(6px);
            }
            .section-header {
                margin: 0.2rem 0 0.75rem 0;
            }
            .section-header h3 {
                margin: 0;
                font-size: 1.1rem;
            }
            .section-header__description {
                margin: 0.25rem 0 0 0;
                color: var(--text-muted);
                font-size: 0.93rem;
            }
            .hero-box {
                background: linear-gradient(135deg, var(--brand-deep) 0%, var(--brand) 100%);
                color: #ffffff;
                border-radius: 18px;
                padding: 1.4rem 1.6rem;
                margin-bottom: 1rem;
                box-shadow: 0 16px 36px rgba(255, 75, 75, 0.22);
            }
            .metric-card {
                background: var(--surface);
                border: 1px solid rgba(216, 219, 225, 0.95);
                border-radius: 16px;
                padding: 1rem 1.1rem;
                box-shadow: var(--shadow-soft);
                min-height: 118px;
            }
            .metric-label {
                color: var(--text-muted);
                font-size: 0.92rem;
                margin-bottom: 0.35rem;
            }
            .metric-value {
                color: var(--text-main);
                font-size: 1.85rem;
                font-weight: 700;
                line-height: 1.15;
                margin-bottom: 0.25rem;
            }
            .metric-help {
                color: var(--text-muted);
                font-size: 0.85rem;
            }
            .section-card {
                background: var(--surface);
                border: 1px solid rgba(216, 219, 225, 0.95);
                border-radius: 16px;
                padding: 1rem 1.1rem;
                margin-bottom: 1rem;
                box-shadow: var(--shadow-soft);
            }
            .info-card {
                background: linear-gradient(180deg, #ffffff 0%, #fff7f7 100%);
                border: 1px solid rgba(255, 75, 75, 0.12);
                border-radius: 16px;
                padding: 1rem 1.1rem;
                box-shadow: var(--shadow-soft);
                min-height: 118px;
            }
            .info-card__title {
                color: var(--text-muted);
                font-size: 0.86rem;
                margin-bottom: 0.35rem;
            }
            .info-card__value {
                color: var(--text-main);
                font-size: 1.35rem;
                font-weight: 700;
                line-height: 1.2;
            }
            .info-card__helper {
                margin: 0.4rem 0 0 0;
                color: var(--text-muted);
                font-size: 0.84rem;
            }
            .toolbar-card {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
                flex-wrap: wrap;
                background: rgba(255, 255, 255, 0.78);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 0.8rem 1rem;
                margin-bottom: 0.8rem;
                box-shadow: var(--shadow-soft);
            }
            .toolbar-card strong {
                color: var(--text-main);
            }
            .toolbar-card span {
                color: var(--text-muted);
                font-size: 0.9rem;
            }
            .empty-state {
                text-align: center;
                padding: 1.4rem 1.2rem;
                border-radius: 18px;
                border: 1px dashed rgba(255, 75, 75, 0.25);
                background: rgba(255, 255, 255, 0.75);
                box-shadow: var(--shadow-soft);
            }
            .empty-state h4 {
                margin: 0;
            }
            .empty-state p {
                margin: 0.4rem 0 0 0;
                color: var(--text-muted);
            }
            .login-shell {
                max-width: 980px;
                margin: 3.5rem auto 0 auto;
            }
            .login-panel {
                background:
                    radial-gradient(circle at top right, rgba(255, 255, 255, 0.18), transparent 26%),
                    linear-gradient(135deg, #992d2d 0%, var(--brand-deep) 28%, var(--brand) 100%);
                border-radius: 28px;
                padding: 2rem;
                box-shadow: 0 24px 48px rgba(255, 75, 75, 0.20);
                color: #ffffff;
                min-height: 100%;
            }
            .login-panel h1 {
                color: #ffffff;
                margin: 0 0 0.5rem 0;
                font-size: 2rem;
                line-height: 1.05;
            }
            .login-panel p {
                color: rgba(255, 255, 255, 0.86);
                margin: 0;
                line-height: 1.6;
            }
            .login-panel__eyebrow {
                display: inline-block;
                margin-bottom: 0.85rem;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: rgba(255, 255, 255, 0.76);
            }
            .login-meta {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.8rem;
                margin-top: 1.35rem;
            }
            .login-meta__item {
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 16px;
                padding: 0.9rem 1rem;
            }
            .login-meta__label {
                display: block;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                color: rgba(255, 255, 255, 0.72);
                margin-bottom: 0.3rem;
            }
            .login-meta__value {
                color: #ffffff;
                font-size: 0.96rem;
                font-weight: 600;
            }
            .login-card {
                background: rgba(255, 255, 255, 0.97);
                border: 1px solid var(--border);
                border-radius: 24px;
                padding: 1.6rem;
                box-shadow: var(--shadow-soft);
            }
            .login-card label {
                color: var(--text-main) !important;
                font-weight: 600;
            }
            .login-card__header {
                margin-bottom: 1rem;
            }
            .login-card__header h3 {
                margin: 0;
                font-size: 1.3rem;
            }
            .login-card__header p {
                margin: 0.35rem 0 0 0;
                color: var(--text-muted);
            }
            .login-card [data-testid="stForm"] {
                background: transparent;
                border: none;
                box-shadow: none;
                padding: 0;
            }
            .login-card div[data-baseweb="input"] > div {
                background: #ffffff;
                border: 1px solid #cfd6e4;
            }
            .login-card div[data-baseweb="input"] input {
                color: var(--text-main) !important;
                -webkit-text-fill-color: var(--text-main) !important;
            }
            .sidebar-company-card,
            .sidebar-user-card {
                background: rgba(255, 255, 255, 0.68);
                border: 1px solid rgba(219, 202, 183, 0.95);
                border-radius: 18px;
                padding: 0.95rem 1rem;
                box-shadow: 0 12px 24px rgba(82, 89, 109, 0.08);
                margin-bottom: 0.8rem;
            }
            .sidebar-company-card h3,
            .sidebar-user-card h4 {
                margin: 0;
                color: var(--text-main);
            }
            .sidebar-company-card p,
            .sidebar-user-card p {
                margin: 0.3rem 0 0 0;
                color: var(--text-muted);
                font-size: 0.9rem;
                line-height: 1.5;
            }
            .sidebar-label {
                display: inline-block;
                margin-bottom: 0.35rem;
                color: var(--brand-strong);
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.06em;
                text-transform: uppercase;
            }
            .status-pill {
                display: inline-block;
                border-radius: 999px;
                padding: 0.2rem 0.75rem;
                color: #ffffff;
                font-weight: 700;
                font-size: 0.85rem;
            }
            .total-box {
                background: linear-gradient(180deg, #fff9f9 0%, var(--surface-strong) 100%);
                border: 1px solid rgba(255, 75, 75, 0.18);
                border-radius: 16px;
                padding: 1rem 1.2rem;
                color: var(--text-main);
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
            }
            @media (max-width: 900px) {
                .page-header {
                    padding: 1.35rem 1.1rem;
                }
                .page-header__title-row h1 {
                    font-size: 1.65rem;
                }
                .toolbar-card {
                    align-items: flex-start;
                }
                .login-shell {
                    margin-top: 1.5rem;
                }
                .login-panel,
                .login-card {
                    padding: 1.25rem;
                }
                .login-meta {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    components.html(
        f"""
        <script>
            const doc = window.parent.document;
            doc.documentElement.lang = "pt-BR";
            doc.title = {json.dumps(full_title)};

            const ensureMeta = (attr, name, content) => {{
                let tag = doc.head.querySelector(`meta[${{attr}}="${{name}}"]`);
                if (!tag) {{
                    tag = doc.createElement("meta");
                    tag.setAttribute(attr, name);
                    doc.head.appendChild(tag);
                }}
                tag.setAttribute("content", content);
            }};

            const ensureLink = (rel, href) => {{
                let tag = doc.head.querySelector(`link[rel="${{rel}}"]`);
                if (!tag) {{
                    tag = doc.createElement("link");
                    tag.setAttribute("rel", rel);
                    doc.head.appendChild(tag);
                }}
                tag.setAttribute("href", href);
            }};

            ensureMeta("name", "apple-mobile-web-app-title", {json.dumps(app_short_name)});
            ensureMeta("name", "application-name", {json.dumps(app_short_name)});
            ensureMeta("name", "theme-color", "#ff4b4b");

            const logo = {json.dumps(logo_data_uri or "")};
            if (logo) {{
                ensureLink("icon", logo);
                ensureLink("shortcut icon", logo);
                ensureLink("apple-touch-icon", logo);
            }}
        </script>
        """,
        height=0,
    )


def set_authenticated_user(user: dict) -> None:
    st.session_state[AUTH_SESSION_KEY] = {
        "id": user["id"],
        "nome": user["nome"],
        "username": user["username"],
    }


def logout() -> None:
    if AUTH_SESSION_KEY in st.session_state:
        del st.session_state[AUTH_SESSION_KEY]
    st.rerun()


def restore_sidebar_visibility() -> None:
    components.html(
        """
        <script>
            const doc = window.parent.document;
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            const collapsed = doc.querySelector('[data-testid="collapsedControl"]');
            if (sidebar) {
                sidebar.style.display = '';
                sidebar.style.visibility = 'visible';
            }
            if (collapsed) {
                collapsed.style.display = '';
                collapsed.style.visibility = 'visible';
            }
        </script>
        """,
        height=0,
    )


def ensure_authenticated(page_title: str) -> dict:
    auth_user = st.session_state.get(AUTH_SESSION_KEY)
    if auth_user:
        return auth_user

    company = get_company_info()
    logo_bytes = get_logo_bytes(company)

    company_name = safe_text(company.get("nome_fantasia"), "Empresa")
    company_phone = safe_text(company.get("telefone"), "Nao informado")
    company_email = safe_text(company.get("email"), "Nao informado")

    st.markdown(
        """
        <style>
            [data-testid="stSidebar"],
            [data-testid="collapsedControl"] {
                display: none !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    components.html(
        """
        <script>
            const doc = window.parent.document;
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            const collapsed = doc.querySelector('[data-testid="collapsedControl"]');
            if (sidebar) sidebar.style.display = 'none';
            if (collapsed) collapsed.style.display = 'none';
        </script>
        """,
        height=0,
    )

    info_col, form_col = st.columns([1.1, 0.95], gap="large")
    with info_col:
        st.markdown(
            f"""
            <section class="login-shell">
                <div class="login-panel">
                    <span class="login-panel__eyebrow">Acesso seguro</span>
                    <h1>Sistema de orcamentos</h1>
                    <p>Controle clientes, servicos e propostas comerciais com uma experiencia administrativa consistente e profissional.</p>
                    <div class="login-meta">
                        <div class="login-meta__item">
                            <span class="login-meta__label">Empresa</span>
                            <span class="login-meta__value">{html.escape(company_name)}</span>
                        </div>
                        <div class="login-meta__item">
                            <span class="login-meta__label">Pagina</span>
                            <span class="login-meta__value">{html.escape(page_title)}</span>
                        </div>
                        <div class="login-meta__item">
                            <span class="login-meta__label">Telefone</span>
                            <span class="login-meta__value">{html.escape(company_phone)}</span>
                        </div>
                        <div class="login-meta__item">
                            <span class="login-meta__label">Email</span>
                            <span class="login-meta__value">{html.escape(company_email)}</span>
                        </div>
                    </div>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
    with form_col:
        st.markdown(
            """
            <section class="login-shell">
                <div class="login-card">
                    <div class="login-card__header">
                        <h3>Entrar no sistema</h3>
                        <p>Use suas credenciais para acessar o ambiente administrativo.</p>
                    </div>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            if logo_bytes:
                st.image(logo_bytes, width=120)
            st.subheader(safe_text(company.get("nome_fantasia"), "Empresa"))
            st.caption(f"Entre para acessar a página {page_title.lower()}.")
            with st.form("form_login"):
                username = st.text_input("Login")
                password = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar", use_container_width=True)

            if submit:
                user = get_user_by_username(username)
                if not user or not verify_password(password, user["password_hash"]):
                    st.error("Login ou senha inválidos.")
                else:
                    set_authenticated_user(user)
                    st.rerun()


    st.stop()


def render_sidebar_branding(page_title: str) -> None:
    company = get_company_info()
    logo_bytes = get_logo_bytes(company)
    auth_user = st.session_state.get(AUTH_SESSION_KEY, {})

    restore_sidebar_visibility()

    with st.sidebar:
        if logo_bytes:
            st.image(logo_bytes, width=128)
        company_details = []
        if company.get("cnpj"):
            company_details.append(f"CNPJ: {company['cnpj']}")
        if company.get("telefone"):
            company_details.append(f"Tel.: {company['telefone']}")
        details_text = " | ".join(company_details) if company_details else "Sistema administrativo de orcamentos"

        st.markdown(
            f"""
            <div class="sidebar-company-card">
                <span class="sidebar-label">Empresa</span>
                <h3>{html.escape(safe_text(company.get("nome_fantasia"), "Empresa"))}</h3>
                <p>{html.escape(page_title)}</p>
                <p>{html.escape(details_text)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="sidebar-user-card">
                <span class="sidebar-label">Sessao</span>
                <h4>{html.escape(safe_text(auth_user.get("nome"), "Administrador"))}</h4>
                <p>Login: {html.escape(safe_text(auth_user.get("username"), "admin"))}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(f"**Usuário:** {safe_text(auth_user.get('nome'), 'Administrador')}")
        st.caption("Use o menu lateral para navegar entre dashboard, cadastros, orcamentos e configuracoes.")
        if st.button("Sair", use_container_width=True):
            logout()


def render_metric_card(title: str, value: str, helper: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(title)}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
            <div class="metric-help">{html.escape(helper)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#4a5568")
    return f'<span class="status-pill" style="background:{color};">{html.escape(status)}</span>'


def default_validity_date() -> date:
    return date.today() + timedelta(days=7)


def init_quote_state() -> None:
    defaults = {
        "orcamento_itens_temp": [],
        "orc_cliente_id": None,
        "orc_data": date.today(),
        "orc_responsavel": "",
        "orc_status": "Rascunho",
        "orc_validade": default_validity_date(),
        "orc_observacoes": "",
        "orc_metragem_total": 0.0,
        "orc_prazo_execucao": "",
        "orc_forma_pagamento": "",
        "orc_desconto_tipo": "Nenhum",
        "orc_desconto_percentual": 0.0,
        "orc_desconto_valor": 0.0,
        "orc_taxa_adicional": 0.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_quote_state() -> None:
    keys = [
        "orcamento_itens_temp",
        "orc_cliente_id",
        "orc_data",
        "orc_responsavel",
        "orc_status",
        "orc_validade",
        "orc_observacoes",
        "orc_metragem_total",
        "orc_prazo_execucao",
        "orc_forma_pagamento",
        "orc_desconto_tipo",
        "orc_desconto_percentual",
        "orc_desconto_valor",
        "orc_taxa_adicional",
        "item_produto_id",
        "item_quantidade",
        "item_valor_unitario",
        "item_observacoes",
    ]
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]
    init_quote_state()


def load_quote_into_state(orcamento: dict) -> None:
    st.session_state["orcamento_itens_temp"] = [
        {
            "produto_id": item["produto_id"],
            "item_nome": item["item_nome"],
            "categoria": item["categoria"],
            "unidade": item["unidade"],
            "quantidade": float(item["quantidade"]),
            "valor_unitario": float(item["valor_unitario"]),
            "subtotal": float(item["subtotal"]),
            "observacoes": item["observacoes"] or "",
        }
        for item in orcamento.get("itens", [])
    ]
    st.session_state["orc_cliente_id"] = orcamento.get("cliente_id")
    st.session_state["orc_data"] = date.today()
    st.session_state["orc_responsavel"] = orcamento.get("responsavel", "")
    st.session_state["orc_status"] = "Rascunho"
    validade = orcamento.get("validade")
    st.session_state["orc_validade"] = date.fromisoformat(validade) if validade else default_validity_date()
    st.session_state["orc_observacoes"] = orcamento.get("observacoes", "") or ""
    st.session_state["orc_metragem_total"] = float(orcamento.get("metragem_total") or 0.0)
    st.session_state["orc_prazo_execucao"] = orcamento.get("prazo_execucao", "") or ""
    st.session_state["orc_forma_pagamento"] = orcamento.get("forma_pagamento", "") or ""
    st.session_state["orc_desconto_tipo"] = orcamento.get("desconto_tipo", "Nenhum")
    st.session_state["orc_desconto_percentual"] = float(orcamento.get("desconto_percentual") or 0.0)
    st.session_state["orc_desconto_valor"] = float(orcamento.get("desconto_valor") or 0.0)
    st.session_state["orc_taxa_adicional"] = float(orcamento.get("taxa_adicional") or 0.0)


def _company_detail_lines(company: dict) -> list[str]:
    lines = [safe_text(company.get("nome_fantasia"), "Empresa")]
    if company.get("razao_social"):
        lines.append(company["razao_social"])
    if company.get("cnpj"):
        lines.append(f"CNPJ: {company['cnpj']}")

    contact_parts = []
    if company.get("telefone"):
        contact_parts.append(company["telefone"])
    if company.get("email"):
        contact_parts.append(company["email"])
    if contact_parts:
        lines.append(" | ".join(contact_parts))

    address_parts = [safe_text(company.get("endereco"), ""), safe_text(company.get("cidade_estado"), "")]
    address_line = " - ".join([part for part in address_parts if part])
    if address_line:
        lines.append(address_line)

    web_parts = []
    if company.get("website"):
        web_parts.append(company["website"])
    if company.get("instagram"):
        web_parts.append(company["instagram"])
    if web_parts:
        lines.append(" | ".join(web_parts))

    return [line for line in lines if line and line != "-"]


def _company_details_html(company: dict) -> str:
    return "<br />".join(html.escape(line) for line in _company_detail_lines(company))


def build_quote_html(orcamento: dict) -> str:
    company = get_company_info()
    logo_data_uri = get_logo_data_uri(company)
    logo_html = (
        f'<img src="{logo_data_uri}" alt="Logo da empresa" style="max-width:90px; max-height:90px; border-radius:14px;" />'
        if logo_data_uri
        else ""
    )

    itens_rows = []
    for item in orcamento.get("itens", []):
        itens_rows.append(
            f"""
            <tr>
                <td>{html.escape(item.get("item_nome", ""))}</td>
                <td>{html.escape(item.get("categoria", "") or "-")}</td>
                <td>{html.escape(item.get("unidade", "") or "-")}</td>
                <td style="text-align:right;">{item.get("quantidade", 0):,.2f}</td>
                <td style="text-align:right;">{currency(item.get("valor_unitario", 0))}</td>
                <td style="text-align:right;">{currency(item.get("subtotal", 0))}</td>
            </tr>
            """
        )

    itens_html = "".join(itens_rows) or "<tr><td colspan='6'>Nenhum item cadastrado.</td></tr>"
    desconto_label = orcamento.get("desconto_tipo", "Nenhum")
    desconto_valor = float(orcamento.get("desconto_valor") or 0)
    if desconto_label == "Percentual":
        desconto_valor = float(orcamento.get("subtotal") or 0) * (float(orcamento.get("desconto_percentual") or 0) / 100)

    return f"""
    <html lang="pt-BR">
        <head>
            <meta charset="utf-8" />
            <meta http-equiv="Content-Language" content="pt-BR" />
            <title>{html.escape(orcamento.get("numero", "Orçamento"))}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #1c1e21;
                    margin: 24px;
                }}
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    border-bottom: 2px solid #ff4b4b;
                    padding-bottom: 12px;
                    margin-bottom: 18px;
                    gap: 20px;
                }}
                .brand {{
                    display: flex;
                    gap: 14px;
                    align-items: center;
                }}
                .title {{
                    color: #ff4b4b;
                    font-size: 26px;
                    font-weight: 700;
                    margin: 0 0 6px 0;
                }}
                .company-name {{
                    color: #ff4b4b;
                    font-size: 20px;
                    font-weight: 700;
                    margin: 0 0 4px 0;
                }}
                .muted {{
                    color: #65676b;
                    line-height: 1.5;
                    font-size: 13px;
                }}
                .box {{
                    border: 1px solid #dadde1;
                    border-radius: 12px;
                    padding: 14px;
                    margin-bottom: 16px;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 16px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 12px;
                }}
                th, td {{
                    border: 1px solid #dadde1;
                    padding: 8px;
                    font-size: 13px;
                }}
                th {{
                    background: #f0f2f6;
                    text-align: left;
                }}
                .totals {{
                    margin-top: 18px;
                    width: 320px;
                    margin-left: auto;
                }}
                .totals td {{
                    border: none;
                    padding: 6px 0;
                }}
                .total-final {{
                    font-size: 18px;
                    font-weight: 700;
                    color: #ff4b4b;
                }}
                .print-btn {{
                    margin-bottom: 16px;
                }}
                @media print {{
                    .print-btn {{
                        display: none;
                    }}
                    body {{
                        margin: 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <button class="print-btn" onclick="window.print()">Imprimir</button>
            <div class="header">
                <div class="brand">
                    {logo_html}
                    <div>
                        <p class="company-name">{html.escape(safe_text(company.get("nome_fantasia"), "Empresa"))}</p>
                        <div class="muted">{_company_details_html(company)}</div>
                    </div>
                </div>
                <div>
                    <p class="title">Orçamento de Pintura</p>
                    <div><strong>Número:</strong> {html.escape(orcamento.get("numero", ""))}</div>
                    <div><strong>Data:</strong> {html.escape(orcamento.get("data_orcamento", ""))}</div>
                    <div><strong>Status:</strong> {html.escape(orcamento.get("status", ""))}</div>
                    <div><strong>Validade:</strong> {html.escape(orcamento.get("validade", "") or "-")}</div>
                </div>
            </div>

            <div class="grid">
                <div class="box">
                    <h3>Cliente</h3>
                    <div><strong>Nome:</strong> {html.escape(orcamento.get("cliente_nome", ""))}</div>
                    <div><strong>Telefone:</strong> {html.escape(orcamento.get("cliente_telefone", "") or "-")}</div>
                    <div><strong>Email:</strong> {html.escape(orcamento.get("cliente_email", "") or "-")}</div>
                    <div><strong>Endereço:</strong> {html.escape(orcamento.get("cliente_endereco", "") or "-")}</div>
                </div>
                <div class="box">
                    <h3>Detalhes</h3>
                    <div><strong>Responsável:</strong> {html.escape(orcamento.get("responsavel", ""))}</div>
                    <div><strong>Metragem:</strong> {float(orcamento.get("metragem_total") or 0):,.2f} m2</div>
                    <div><strong>Prazo estimado:</strong> {html.escape(orcamento.get("prazo_execucao", "") or "-")}</div>
                    <div><strong>Pagamento:</strong> {html.escape(orcamento.get("forma_pagamento", "") or "-")}</div>
                </div>
            </div>

            <div class="box">
                <h3>Itens do orçamento</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th>Categoria</th>
                            <th>Unidade</th>
                            <th>Quantidade</th>
                            <th>Valor unitário</th>
                            <th>Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {itens_html}
                    </tbody>
                </table>
            </div>

            <table class="totals">
                <tr>
                    <td>Subtotal</td>
                    <td style="text-align:right;">{currency(orcamento.get("subtotal", 0))}</td>
                </tr>
                <tr>
                    <td>Desconto ({html.escape(desconto_label)})</td>
                    <td style="text-align:right;">{currency(desconto_valor)}</td>
                </tr>
                <tr>
                    <td>Taxa adicional</td>
                    <td style="text-align:right;">{currency(orcamento.get("taxa_adicional", 0))}</td>
                </tr>
                <tr>
                    <td class="total-final">Total final</td>
                    <td class="total-final" style="text-align:right;">{currency(orcamento.get("total_final", 0))}</td>
                </tr>
            </table>

            <div class="box">
                <h3>Observações</h3>
                <div>{html.escape(orcamento.get("observacoes", "") or "Sem observações adicionais.")}</div>
            </div>
        </body>
    </html>
    """


def _draw_company_logo(pdf: canvas.Canvas, company: dict, x: float, top_y: float, max_width: float, max_height: float) -> None:
    logo_bytes = get_logo_bytes(company)
    if not logo_bytes:
        return

    try:
        image = ImageReader(BytesIO(logo_bytes))
        img_width, img_height = image.getSize()
        scale = min(max_width / img_width, max_height / img_height)
        draw_width = img_width * scale
        draw_height = img_height * scale
        pdf.drawImage(
            image,
            x,
            top_y - draw_height,
            width=draw_width,
            height=draw_height,
            preserveAspectRatio=True,
            mask="auto",
        )
    except Exception:
        return


def build_quote_pdf(orcamento: dict) -> bytes:
    company = get_company_info()
    company_lines = _company_detail_lines(company)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left = 40
    right = width - 40
    y = height - 45

    def draw_page_header() -> float:
        nonlocal y
        header_height = 88
        pdf.setFillColor(colors.HexColor("#FF4B4B"))
        pdf.rect(0, height - header_height, width, header_height, fill=1, stroke=0)
        pdf.setFillColor(colors.white)
        _draw_company_logo(pdf, company, left, height - 12, 56, 56)
        text_x = left + (66 if get_logo_bytes(company) else 0)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(text_x, height - 28, safe_text(company.get("nome_fantasia"), "Empresa"))
        pdf.setFont("Helvetica", 10)
        pdf.drawString(text_x, height - 44, "Orçamento de Pintura")
        pdf.drawRightString(right, height - 28, safe_text(orcamento.get("numero")))
        pdf.drawRightString(right, height - 44, safe_text(orcamento.get("data_orcamento")))
        y = height - 108
        return y

    def ensure_space(minimum: float) -> None:
        nonlocal y
        if y < minimum:
            pdf.showPage()
            draw_page_header()

    def draw_label_value(label: str, value: str, pos_x: float, pos_y: float, offset: float = 70) -> None:
        pdf.setFillColor(colors.HexColor("#3A3B3C"))
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(pos_x, pos_y, f"{label}:")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(pos_x + offset, pos_y, safe_text(value))

    def draw_wrapped_text(text: str, pos_x: float, pos_y: float, max_width: int, line_height: int = 12) -> float:
        nonlocal y
        value = safe_text(text, "")
        if not value:
            return pos_y
        words = value.split()
        lines: list[str] = []
        current = ""
        for word in words:
            test_line = f"{current} {word}".strip()
            if pdf.stringWidth(test_line, "Helvetica", 10) <= max_width:
                current = test_line
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        for line in lines:
            ensure_space(80)
            pdf.drawString(pos_x, pos_y, line)
            pos_y -= line_height
            y = pos_y
        return pos_y

    desconto_label = orcamento.get("desconto_tipo", "Nenhum")
    desconto_valor = float(orcamento.get("desconto_valor") or 0)
    if desconto_label == "Percentual":
        desconto_valor = float(orcamento.get("subtotal") or 0) * (float(orcamento.get("desconto_percentual") or 0) / 100)

    draw_page_header()

    pdf.setFillColor(colors.HexColor("#1C1E21"))
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, y, "Dados da empresa")
    y -= 18
    pdf.setFont("Helvetica", 10)
    for line in company_lines:
        ensure_space(90)
        pdf.drawString(left, y, line)
        y -= 13
    y -= 8

    ensure_space(180)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, y, "Dados do cliente")
    y -= 18
    draw_label_value("Nome", safe_text(orcamento.get("cliente_nome")), left, y)
    y -= 14
    draw_label_value("Telefone", safe_text(orcamento.get("cliente_telefone")), left, y)
    y -= 14
    draw_label_value("Email", safe_text(orcamento.get("cliente_email")), left, y)
    y -= 14
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left, y, "Endereço:")
    pdf.setFont("Helvetica", 10)
    y = draw_wrapped_text(safe_text(orcamento.get("cliente_endereco")), left + 70, y, 420)
    y -= 8

    ensure_space(170)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, y, "Dados do orçamento")
    y -= 18
    draw_label_value("Data", safe_text(orcamento.get("data_orcamento")), left, y)
    draw_label_value("Status", safe_text(orcamento.get("status")), 300, y)
    y -= 14
    draw_label_value("Responsável", safe_text(orcamento.get("responsavel")), left, y, offset=88)
    draw_label_value("Validade", safe_text(orcamento.get("validade")), 300, y)
    y -= 14
    draw_label_value("Pagamento", safe_text(orcamento.get("forma_pagamento")), left, y, offset=82)
    draw_label_value("Prazo", safe_text(orcamento.get("prazo_execucao")), 300, y)
    y -= 14
    draw_label_value("Metragem", f"{float(orcamento.get('metragem_total') or 0):,.2f} m2", left, y, offset=76)
    y -= 24

    ensure_space(180)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, y, "Itens")
    y -= 18

    header_y = y
    pdf.setFillColor(colors.HexColor("#F0F2F5"))
    pdf.rect(left, header_y - 4, right - left, 18, fill=1, stroke=0)
    pdf.setFillColor(colors.HexColor("#1C1E21"))
    pdf.setFont("Helvetica-Bold", 9)
    columns = [
        ("Item", left + 4),
        ("Qtd.", left + 215),
        ("Un.", left + 255),
        ("Vlr. unit.", left + 310),
        ("Subtotal", left + 395),
    ]
    for label, x_pos in columns:
        pdf.drawString(x_pos, header_y + 2, label)
    y -= 22

    pdf.setFont("Helvetica", 9)
    for item in orcamento.get("itens", []):
        ensure_space(90)
        item_nome = safe_text(item.get("item_nome"))
        quantidade = f"{float(item.get('quantidade') or 0):,.2f}"
        unidade = safe_text(item.get("unidade"))
        valor_unitario = currency(item.get("valor_unitario", 0))
        subtotal = currency(item.get("subtotal", 0))
        observacao = safe_text(item.get("observacoes"), "")

        name_lines = []
        current = ""
        for word in item_nome.split():
            test_line = f"{current} {word}".strip()
            if pdf.stringWidth(test_line, "Helvetica", 9) <= 200:
                current = test_line
            else:
                if current:
                    name_lines.append(current)
                current = word
        if current:
            name_lines.append(current)
        row_height = max(16, len(name_lines) * 12)
        if observacao:
            row_height += 12

        pdf.setStrokeColor(colors.HexColor("#DADDE1"))
        pdf.line(left, y - 4, right, y - 4)

        text_y = y
        for line in name_lines:
            pdf.drawString(left + 4, text_y, line)
            text_y -= 11
        if observacao:
            pdf.setFillColor(colors.HexColor("#65676B"))
            pdf.drawString(left + 4, text_y, f"Obs.: {observacao[:70]}")
            pdf.setFillColor(colors.HexColor("#1C1E21"))

        pdf.drawRightString(left + 248, y, quantidade)
        pdf.drawString(left + 258, y, unidade)
        pdf.drawRightString(left + 388, y, valor_unitario)
        pdf.drawRightString(right - 4, y, subtotal)
        y -= row_height

    y -= 10
    ensure_space(130)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawRightString(430, y, "Subtotal:")
    pdf.drawRightString(right, y, currency(orcamento.get("subtotal", 0)))
    y -= 14
    pdf.drawRightString(430, y, f"Desconto ({desconto_label}):")
    pdf.drawRightString(right, y, currency(desconto_valor))
    y -= 14
    pdf.drawRightString(430, y, "Taxa adicional:")
    pdf.drawRightString(right, y, currency(orcamento.get("taxa_adicional", 0)))
    y -= 18
    pdf.setFillColor(colors.HexColor("#FF4B4B"))
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawRightString(430, y, "Total final:")
    pdf.drawRightString(right, y, currency(orcamento.get("total_final", 0)))
    pdf.setFillColor(colors.HexColor("#1C1E21"))
    y -= 28

    ensure_space(100)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, y, "Observações")
    y -= 16
    pdf.setFont("Helvetica", 10)
    draw_wrapped_text(safe_text(orcamento.get("observacoes"), "Sem observações adicionais."), left, y, 500)

    pdf.save()
    return buffer.getvalue()


def build_share_message(orcamento: dict) -> str:
    company = get_company_info()
    company_name = safe_text(company.get("nome_fantasia"), "Empresa")
    return (
        f"{company_name}\n"
        f"Orçamento {safe_text(orcamento.get('numero'))}\n"
        f"Cliente: {safe_text(orcamento.get('cliente_nome'))}\n"
        f"Data: {safe_text(orcamento.get('data_orcamento'))}\n"
        f"Validade: {safe_text(orcamento.get('validade'))}\n"
        f"Status: {safe_text(orcamento.get('status'))}\n"
        f"Total final: {currency(orcamento.get('total_final', 0))}\n"
        f"Responsável: {safe_text(orcamento.get('responsavel'))}\n"
        f"Observações: {safe_text(orcamento.get('observacoes'), 'Sem observações adicionais.')}"
    )


def build_share_links(orcamento: dict) -> dict:
    company = get_company_info()
    company_name = safe_text(company.get("nome_fantasia"), "Empresa")
    message = build_share_message(orcamento)
    subject = quote(f"Orçamento {safe_text(orcamento.get('numero'))} - {company_name}")
    encoded_message = quote(message)
    phone_digits = "".join(char for char in safe_text(orcamento.get("cliente_telefone"), "") if char.isdigit())

    return {
        "email": f"mailto:{safe_text(orcamento.get('cliente_email'), '')}?subject={subject}&body={encoded_message}",
        "whatsapp": f"https://wa.me/{phone_digits}?text={encoded_message}" if phone_digits else "",
        "message": message,
    }
