from __future__ import annotations

import streamlit as st

from components import render_data_hint, render_empty_state, render_page_header, render_section_header, setup_page
from database import get_company_info, get_dashboard_metrics, get_recent_orcamentos, seed_sample_data
from utils import currency, render_metric_card, render_status_badge


PAGE_TITLE = "Painel"

setup_page(PAGE_TITLE)

company = get_company_info()
company_name = company.get("nome_fantasia") or "Empresa"

render_page_header(
    "Painel administrativo",
    f"Gestao completa da empresa {company_name} com clientes, produtos, orcamentos e documentos personalizados.",
    eyebrow="Visao geral do negocio",
    badge="Streamlit multipage",
)

metricas = get_dashboard_metrics()

col1, col2, col3 = st.columns(3)
with col1:
    render_metric_card("Produtos cadastrados", metricas["total_produtos"], "Catalogo de materiais e servicos")
with col2:
    render_metric_card("Clientes", metricas["total_clientes"], "Base de clientes ativos no sistema")
with col3:
    render_metric_card("Orcamentos", metricas["total_orcamentos"], "Documentos registrados")

col4, col5, col6 = st.columns(3)
with col4:
    render_metric_card("Valor total orcado", currency(metricas["valor_total_orcado"]), "Soma dos orcamentos salvos")
with col5:
    render_metric_card("Aprovados", metricas["orcamentos_aprovados"], "Orcamentos convertidos")
with col6:
    render_metric_card("Recusados", metricas["orcamentos_recusados"], "Orcamentos nao fechados")

render_section_header("Atalhos uteis", "Acoes rapidas para preparar o ambiente e atualizar os dados do painel.")
render_data_hint(
    "Rotina recomendada",
    "Revise indicadores, mantenha os cadastros em dia e acompanhe os ultimos orcamentos antes de abrir novas propostas.",
)
cta1, cta2, cta3 = st.columns([1, 1, 2])
with cta1:
    if st.button("Popular dados de exemplo", use_container_width=True):
        inserted = seed_sample_data()
        if inserted:
            st.success("Dados de exemplo adicionados com sucesso.")
        else:
            st.info("Os dados de exemplo ja estavam disponiveis.")
        st.rerun()
with cta2:
    if st.button("Atualizar painel", use_container_width=True):
        st.rerun()
with cta3:
    st.info("Use o menu lateral para cadastrar produtos, clientes, gerar orcamentos e atualizar as configuracoes.")

render_section_header("Ultimos orcamentos", "Historico recente para acompanhamento rapido do time comercial.")
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
    render_empty_state("Nenhum orcamento cadastrado", "Cadastre clientes e itens para comecar a emitir propostas.")
