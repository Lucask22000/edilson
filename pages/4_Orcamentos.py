from __future__ import annotations

from datetime import date, timedelta

import streamlit as st
import streamlit.components.v1 as components

from database import delete_orcamento, get_orcamento, init_db, list_orcamentos, update_orcamento_status
from models import STATUS_ORCAMENTO
from utils import (
    build_quote_html,
    build_quote_pdf,
    build_share_links,
    configure_page,
    currency,
    inject_custom_css,
    render_status_badge,
    safe_text,
)


configure_page("Orcamentos")
init_db()
inject_custom_css()

st.title("Orcamentos salvos")
st.caption("Consulte, filtre, visualize detalhes e acompanhe o status de cada orcamento.")

f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
search = f1.text_input("Pesquisar por cliente")
status = f2.selectbox("Filtrar por status", ["Todos"] + STATUS_ORCAMENTO)
filtrar_periodo = f3.checkbox("Filtrar periodo", value=False)
data_inicio = ""
data_fim = ""
if filtrar_periodo:
    data_inicio = f4.date_input("Data inicial", value=date.today() - timedelta(days=30)).isoformat()
    data_fim = st.date_input("Data final", value=date.today()).isoformat()

orcamentos = list_orcamentos(
    search=search,
    status="" if status == "Todos" else status,
    data_inicio=data_inicio,
    data_fim=data_fim,
)

if orcamentos:
    st.dataframe(
        [
            {
                "Numero": orcamento["numero"],
                "Cliente": orcamento["cliente_nome"],
                "Data": orcamento["data_orcamento"],
                "Status": orcamento["status"],
                "Total": currency(orcamento["total_final"]),
            }
            for orcamento in orcamentos
        ],
        use_container_width=True,
        hide_index=True,
    )

    options = {f"{orcamento['numero']} - {orcamento['cliente_nome']}": orcamento["id"] for orcamento in orcamentos}
    selecionado_label = st.selectbox("Selecione um orcamento", list(options.keys()))
    selecionado_id = options[selecionado_label]

    a1, a2, a3 = st.columns([1, 1, 1])
    with a1:
        if st.button("Abrir detalhes", use_container_width=True):
            st.session_state["orcamento_detalhe_id"] = selecionado_id
            st.rerun()
    with a2:
        if st.button("Duplicar orcamento", use_container_width=True):
            st.session_state["orcamento_duplicar_id"] = selecionado_id
            st.switch_page("pages/3_Novo_Orcamento.py")
    with a3:
        confirmar_exclusao = st.checkbox("Confirmar exclusao", key="confirmar_exclusao_orcamento")
        if st.button("Excluir orcamento", use_container_width=True) and confirmar_exclusao:
            delete_orcamento(selecionado_id)
            if st.session_state.get("orcamento_detalhe_id") == selecionado_id:
                del st.session_state["orcamento_detalhe_id"]
            st.success("Orcamento excluido com sucesso.")
            st.rerun()
else:
    st.info("Nenhum orcamento encontrado com os filtros atuais.")

orcamento_detalhe_id = st.session_state.get("orcamento_detalhe_id")
if orcamento_detalhe_id:
    detalhe = get_orcamento(orcamento_detalhe_id)
    if detalhe:
        st.markdown("### Detalhes do orcamento")
        info1, info2, info3 = st.columns([1.5, 1, 1])
        info1.markdown(
            f"""
            <div class="section-card">
                <h4 style="margin-top:0;">{detalhe['numero']}</h4>
                <p style="margin:0.2rem 0;"><strong>Cliente:</strong> {detalhe['cliente_nome']}</p>
                <p style="margin:0.2rem 0;"><strong>Responsavel:</strong> {detalhe['responsavel']}</p>
                <p style="margin:0.2rem 0;"><strong>Data:</strong> {detalhe['data_orcamento']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        info2.markdown(
            f"""
            <div class="section-card">
                <h4 style="margin-top:0;">Status</h4>
                {render_status_badge(detalhe['status'])}
                <p style="margin:0.8rem 0 0 0;"><strong>Validade:</strong> {safe_text(detalhe['validade'])}</p>
                <p style="margin:0.2rem 0 0 0;"><strong>Pagamento:</strong> {safe_text(detalhe['forma_pagamento'])}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        info3.markdown(
            f"""
            <div class="section-card">
                <h4 style="margin-top:0;">Total final</h4>
                <div style="font-size:1.8rem; font-weight:700; color:#103c4a;">{currency(detalhe['total_final'])}</div>
                <p style="margin:0.8rem 0 0 0;"><strong>Metragem:</strong> {float(detalhe['metragem_total'] or 0):,.2f} m2</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cliente_col, resumo_col = st.columns(2, gap="large")
        with cliente_col:
            st.markdown("#### Dados do cliente")
            st.write(f"**Nome:** {detalhe['cliente_nome']}")
            st.write(f"**Telefone:** {safe_text(detalhe['cliente_telefone'])}")
            st.write(f"**Email:** {safe_text(detalhe['cliente_email'])}")
            st.write(f"**Endereco:** {safe_text(detalhe['cliente_endereco'])}")
            st.write(f"**Observacoes:** {safe_text(detalhe['cliente_observacoes'])}")
        with resumo_col:
            st.markdown("#### Resumo financeiro")
            st.write(f"**Subtotal:** {currency(detalhe['subtotal'])}")
            if detalhe["desconto_tipo"] == "Percentual":
                desconto_aplicado = float(detalhe["subtotal"]) * (float(detalhe["desconto_percentual"]) / 100)
                st.write(
                    f"**Desconto:** {detalhe['desconto_percentual']:.2f}% ({currency(desconto_aplicado)})"
                )
            else:
                st.write(f"**Desconto:** {currency(detalhe['desconto_valor'])}")
            st.write(f"**Taxa adicional:** {currency(detalhe['taxa_adicional'])}")
            st.write(f"**Prazo estimado:** {safe_text(detalhe['prazo_execucao'])}")

        st.markdown("#### Itens")
        st.dataframe(
            [
                {
                    "Item": item["item_nome"],
                    "Categoria": item["categoria"] or "-",
                    "Unidade": item["unidade"] or "-",
                    "Quantidade": item["quantidade"],
                    "Valor unitario": currency(item["valor_unitario"]),
                    "Subtotal": currency(item["subtotal"]),
                    "Observacao": item["observacoes"] or "-",
                }
                for item in detalhe["itens"]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("#### Observacoes gerais")
        st.write(safe_text(detalhe["observacoes"]))

        st.markdown("#### Acoes")
        u1, u2, u3 = st.columns([1, 1, 1])
        novo_status = u1.selectbox(
            "Atualizar status",
            STATUS_ORCAMENTO,
            index=STATUS_ORCAMENTO.index(detalhe["status"]),
        )
        if u1.button("Salvar status", use_container_width=True):
            update_orcamento_status(orcamento_detalhe_id, novo_status)
            st.success("Status atualizado com sucesso.")
            st.rerun()

        html_export = build_quote_html(detalhe)
        pdf_export = build_quote_pdf(detalhe)
        u2.download_button(
            "Baixar PDF",
            data=pdf_export,
            file_name=f"{detalhe['numero']}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        u3.download_button(
            "Baixar HTML imprimivel",
            data=html_export,
            file_name=f"{detalhe['numero']}.html",
            mime="text/html",
            use_container_width=True,
        )

        st.markdown("#### Compartilhar")
        share_data = build_share_links(detalhe)
        share1, share2 = st.columns(2)
        with share1:
            if detalhe.get("cliente_email"):
                st.link_button("Compartilhar por e-mail", share_data["email"], use_container_width=True)
            else:
                st.caption("Cliente sem e-mail cadastrado para compartilhamento direto.")
        with share2:
            if share_data["whatsapp"]:
                st.link_button("Compartilhar no WhatsApp", share_data["whatsapp"], use_container_width=True)
            else:
                st.caption("Cliente sem telefone valido para link direto no WhatsApp.")

        with st.expander("Mensagem pronta para compartilhar", expanded=False):
            st.code(share_data["message"], language="text")
            st.caption("Dica: voce pode enviar a mensagem pronta e anexar o PDF baixado.")

        with st.expander("Visualizar layout limpo para impressao", expanded=False):
            components.html(html_export, height=700, scrolling=True)
