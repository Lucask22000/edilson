from __future__ import annotations

from datetime import date, timedelta

import streamlit as st
import streamlit.components.v1 as components

from components import render_data_hint, render_empty_state, render_info_card, render_page_header, render_section_header, setup_page
from database import delete_orcamento, get_orcamento, list_orcamentos, update_orcamento_status
from models import STATUS_ORCAMENTO
from utils import build_quote_html, build_quote_pdf, build_share_links, currency, render_status_badge, safe_text


PAGE_TITLE = "Orcamentos"

setup_page(PAGE_TITLE)

render_page_header(
    "Orcamentos salvos",
    "Consulte, filtre, visualize detalhes e acompanhe o status de cada proposta emitida pela empresa.",
    eyebrow="Acompanhamento comercial",
    badge="Historico completo",
)

render_section_header("Filtros e consulta", "Refine a listagem por cliente, status e periodo para localizar um documento.")
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

render_data_hint(
    "Leitura rapida",
    "Abra um registro para revisar itens, exportar documentos, compartilhar links e atualizar o status do orcamento.",
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
    render_empty_state("Nenhum orcamento encontrado", "Ajuste os filtros ou crie um novo documento para iniciar o historico.")

orcamento_detalhe_id = st.session_state.get("orcamento_detalhe_id")
if orcamento_detalhe_id:
    detalhe = get_orcamento(orcamento_detalhe_id)
    if detalhe:
        render_section_header("Detalhes do orcamento", "Visualizacao completa do documento com resumo, itens e acoes.")
        info1, info2, info3 = st.columns(3)
        with info1:
            render_info_card(detalhe["numero"], safe_text(detalhe["cliente_nome"]), safe_text(detalhe["data_orcamento"]))
        with info2:
            render_info_card("Status", safe_text(detalhe["status"]), safe_text(detalhe["validade"]))
            st.markdown(render_status_badge(detalhe["status"]), unsafe_allow_html=True)
        with info3:
            render_info_card("Total final", currency(detalhe["total_final"]), f"{float(detalhe['metragem_total'] or 0):,.2f} m2")

        cliente_col, resumo_col = st.columns(2, gap="large")
        with cliente_col:
            with st.container(border=True):
                render_section_header("Dados do cliente")
                st.write(f"**Nome:** {detalhe['cliente_nome']}")
                st.write(f"**Telefone:** {safe_text(detalhe['cliente_telefone'])}")
                st.write(f"**Email:** {safe_text(detalhe['cliente_email'])}")
                st.write(f"**Endereco:** {safe_text(detalhe['cliente_endereco'])}")
                st.write(f"**Observacoes:** {safe_text(detalhe['cliente_observacoes'])}")
        with resumo_col:
            with st.container(border=True):
                render_section_header("Resumo financeiro")
                st.write(f"**Subtotal:** {currency(detalhe['subtotal'])}")
                if detalhe["desconto_tipo"] == "Percentual":
                    desconto_aplicado = float(detalhe["subtotal"]) * (float(detalhe["desconto_percentual"]) / 100)
                    st.write(f"**Desconto:** {detalhe['desconto_percentual']:.2f}% ({currency(desconto_aplicado)})")
                else:
                    st.write(f"**Desconto:** {currency(detalhe['desconto_valor'])}")
                st.write(f"**Taxa adicional:** {currency(detalhe['taxa_adicional'])}")
                st.write(f"**Prazo estimado:** {safe_text(detalhe['prazo_execucao'])}")
                st.write(f"**Pagamento:** {safe_text(detalhe['forma_pagamento'])}")

        render_section_header("Itens", "Itens que compoem o documento selecionado.")
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

        with st.container(border=True):
            render_section_header("Observacoes gerais")
            st.write(safe_text(detalhe["observacoes"]))

        render_section_header("Acoes", "Atualize o status, exporte arquivos ou compartilhe a proposta com o cliente.")
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

        render_section_header("Compartilhar", "Use os links diretos ou a mensagem pronta para enviar a proposta ao cliente.")
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
            st.caption("Voce pode enviar a mensagem pronta e anexar o PDF baixado.")

        with st.expander("Visualizar layout limpo para impressao", expanded=False):
            components.html(html_export, height=700, scrolling=True)
