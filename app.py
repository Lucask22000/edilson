from __future__ import annotations

import html

import streamlit as st

from database import get_company_info, get_dashboard_metrics, get_recent_orcamentos, init_db, seed_sample_data
from utils import (
    configure_page,
    currency,
    ensure_authenticated,
    inject_custom_css,
    render_metric_card,
    render_sidebar_branding,
    render_status_badge,
)


PAGE_TITLE = "Painel"

configure_page(PAGE_TITLE)
init_db()
inject_custom_css(PAGE_TITLE)
ensure_authenticated(PAGE_TITLE)
render_sidebar_branding(PAGE_TITLE)

company = get_company_info()
company_name = html.escape(company.get("nome_fantasia") or "Empresa")

st.markdown(
    f"""
    <div class="hero-box">
        <h1 style="margin:0 0 0.35rem 0;">Sistema de Orçamentos</h1>
        <p style="margin:0; font-size:1.02rem;">
            Gestão completa da empresa <strong>{company_name}</strong> com clientes, produtos, orçamentos e documentos personalizados.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

metricas = get_dashboard_metrics()

col1, col2, col3 = st.columns(3)
with col1:
    render_metric_card("Produtos cadastrados", metricas["total_produtos"], "Catálogo de materiais e serviços")
with col2:
    render_metric_card("Clientes", metricas["total_clientes"], "Base de clientes ativos no sistema")
with col3:
    render_metric_card("Orçamentos", metricas["total_orcamentos"], "Documentos registrados")

col4, col5, col6 = st.columns(3)
with col4:
    render_metric_card("Valor total orçado", currency(metricas["valor_total_orcado"]), "Soma dos orçamentos salvos")
with col5:
    render_metric_card("Aprovados", metricas["orcamentos_aprovados"], "Orçamentos convertidos")
with col6:
    render_metric_card("Recusados", metricas["orcamentos_recusados"], "Orçamentos não fechados")

st.markdown("### Atalhos úteis")
cta1, cta2, cta3 = st.columns([1, 1, 2])
with cta1:
    if st.button("Popular dados de exemplo", use_container_width=True):
        inserted = seed_sample_data()
        if inserted:
            st.success("Dados de exemplo adicionados com sucesso.")
        else:
            st.info("Os dados de exemplo já estavam disponíveis.")
        st.rerun()
with cta2:
    if st.button("Atualizar painel", use_container_width=True):
        st.rerun()
with cta3:
    st.info("Use o menu lateral para cadastrar produtos, clientes, gerar orçamentos e atualizar as configurações da empresa.")

st.markdown("### Últimos orçamentos")
recentes = get_recent_orcamentos()
if recentes:
    for orcamento in recentes:
        with st.container(border=True):
            col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
            col_a.markdown(f"**{orcamento['numero']}**  \n{orcamento['cliente_nome']}")
            col_b.write(orcamento["data_orcamento"])
            col_c.markdown(render_status_badge(orcamento["status"]), unsafe_allow_html=True)
            col_d.write(currency(orcamento["total_final"]))
else:
    st.info("Nenhum orçamento cadastrado ainda.")
