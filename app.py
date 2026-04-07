from __future__ import annotations

import streamlit as st

from database import get_dashboard_metrics, get_recent_orcamentos, init_db, seed_sample_data
from utils import configure_page, currency, inject_custom_css, render_metric_card, render_status_badge


configure_page("Painel")
init_db()
inject_custom_css()

st.sidebar.title("Orcamentos de Pintura")
st.sidebar.caption("Navegue pelas paginas usando o menu lateral do Streamlit.")

st.markdown(
    """
    <div class="hero-box">
        <h1 style="margin:0 0 0.35rem 0;">Sistema de Orcamentos</h1>
        <p style="margin:0; font-size:1.02rem;">
            Controle produtos, clientes e orcamentos de forma simples, com calculo automatico e armazenamento local em SQLite.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
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

st.markdown("### Atalhos uteis")
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
    st.info("Use o menu lateral para cadastrar produtos, clientes e gerar novos orcamentos.")

st.markdown("### Ultimos orcamentos")
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
    st.info("Nenhum orcamento cadastrado ainda.")
