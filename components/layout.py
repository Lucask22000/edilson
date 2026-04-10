from __future__ import annotations

import html

import streamlit as st

from database import init_db
from utils import (
    configure_page,
    ensure_authenticated,
    inject_custom_css,
    render_sidebar_branding,
    safe_text,
)


def setup_page(page_title: str) -> dict:
    configure_page(page_title)
    init_db()
    inject_custom_css(page_title)
    user = ensure_authenticated(page_title)
    render_sidebar_branding(page_title)
    return user


def render_page_header(
    title: str,
    description: str,
    *,
    eyebrow: str = "Gestao administrativa",
    badge: str | None = None,
) -> None:
    badge_html = (
        f'<span class="page-header__badge">{html.escape(badge)}</span>'
        if badge
        else ""
    )
    st.markdown(
        f"""
        <section class="page-header">
            <div class="page-header__content">
                <p class="page-header__eyebrow">{html.escape(eyebrow)}</p>
                <div class="page-header__title-row">
                    <h1>{html.escape(title)}</h1>
                    {badge_html}
                </div>
                <p class="page-header__description">{html.escape(description)}</p>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, description: str | None = None) -> None:
    description_html = (
        f'<p class="section-header__description">{html.escape(description)}</p>'
        if description
        else ""
    )
    st.markdown(
        f"""
        <div class="section-header">
            <h3>{html.escape(title)}</h3>
            {description_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_card(title: str, value: str, helper: str | None = None) -> None:
    helper_html = f'<p class="info-card__helper">{html.escape(helper)}</p>' if helper else ""
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-card__title">{html.escape(title)}</div>
            <div class="info-card__value">{html.escape(safe_text(value, "-"))}</div>
            {helper_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_data_hint(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="toolbar-card">
            <strong>{html.escape(title)}</strong>
            <span>{html.escape(description)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="empty-state">
            <h4>{html.escape(title)}</h4>
            <p>{html.escape(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
