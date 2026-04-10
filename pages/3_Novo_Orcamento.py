from __future__ import annotations

import math
from datetime import date

import streamlit as st

from components import (
    render_data_hint,
    render_empty_state,
    render_info_card,
    render_page_header,
    render_section_header,
    setup_page,
)
from database import create_orcamento, get_next_quote_number, get_orcamento, list_clients, list_products
from models import STATUS_ORCAMENTO, TIPOS_DESCONTO
from services.calculations import calcular_subtotal_item, calcular_totais
from utils import currency, default_validity_date, init_quote_state, load_quote_into_state, reset_quote_state, validate_quote_payload


PAGE_TITLE = "Novo Orcamento"

setup_page(PAGE_TITLE)
init_quote_state()

if st.session_state.get("orcamento_duplicar_id"):
    original = get_orcamento(st.session_state["orcamento_duplicar_id"])
    if original:
        load_quote_into_state(original)
        st.success("Dados do orcamento carregados para duplicacao. Ajuste o que precisar e salve como novo.")
    del st.session_state["orcamento_duplicar_id"]

clientes = list_clients()
produtos_ativos = list_products(only_active=True)
produto_map = {produto["id"]: produto for produto in produtos_ativos}


def carregar_preco_padrao() -> None:
    produto_id = st.session_state.get("item_produto_id")
    produto = produto_map.get(produto_id)
    if produto:
        st.session_state["item_valor_unitario"] = float(produto["preco_unitario"])
        st.session_state["item_quantidade"] = 1.0


def sincronizar_desconto_com_tipo() -> None:
    desconto_tipo = st.session_state.get("orc_desconto_tipo", "Nenhum")
    if desconto_tipo == "Percentual":
        st.session_state["orc_desconto_valor"] = 0.0
    elif desconto_tipo == "Valor fixo":
        st.session_state["orc_desconto_percentual"] = 0.0
    else:
        st.session_state["orc_desconto_percentual"] = 0.0
        st.session_state["orc_desconto_valor"] = 0.0


def adicionar_item_ao_orcamento() -> None:
    produto_id = st.session_state.get("item_produto_id")
    produto_selecionado = produto_map.get(produto_id)
    quantidade = float(st.session_state.get("item_quantidade") or 0.0)
    valor_unitario = float(st.session_state.get("item_valor_unitario") or 0.0)

    if not produto_selecionado:
        st.session_state["item_feedback"] = ("error", "Selecione um item valido antes de adicionar.")
        return
    if quantidade <= 0:
        st.session_state["item_feedback"] = ("error", "A quantidade deve ser maior que zero.")
        return
    if valor_unitario < 0:
        st.session_state["item_feedback"] = ("error", "O valor unitario nao pode ser negativo.")
        return

    st.session_state["orcamento_itens_temp"].append(
        {
            "produto_id": produto_selecionado["id"],
            "item_nome": produto_selecionado["nome"],
            "categoria": produto_selecionado["categoria"],
            "unidade": produto_selecionado["unidade"],
            "quantidade": quantidade,
            "valor_unitario": valor_unitario,
            "subtotal": calcular_subtotal_item(quantidade, valor_unitario),
            "observacoes": st.session_state.get("item_observacoes", "").strip(),
        }
    )
    st.session_state["item_quantidade"] = 1.0
    st.session_state["item_valor_unitario"] = float(produto_selecionado["preco_unitario"])
    st.session_state["item_observacoes"] = ""
    st.session_state["item_feedback"] = ("success", "Item adicionado com sucesso.")


def _is_missing_value(value: object) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def _text_or_empty(value: object) -> str:
    if _is_missing_value(value):
        return ""
    return str(value)


def montar_tabela_itens(itens: list[dict]) -> list[dict]:
    return [
        {
            "_produto_id": item["produto_id"],
            "Item": item["item_nome"],
            "Categoria": item["categoria"],
            "Unidade": item["unidade"],
            "Quantidade": float(item["quantidade"]),
            "Valor unitario": float(item["valor_unitario"]),
            "Subtotal": float(item["subtotal"]),
            "Observacao": item["observacoes"] or "",
            "Excluir": False,
        }
        for item in itens
    ]


def normalizar_itens_editados(editor_rows: list[dict]) -> list[dict]:
    itens_normalizados = []
    for row in editor_rows:
        if bool(row.get("Excluir")):
            continue

        quantidade = float(row.get("Quantidade") or 0.0)
        valor_unitario = float(row.get("Valor unitario") or 0.0)

        itens_normalizados.append(
            {
                "produto_id": int(row["_produto_id"]),
                "item_nome": _text_or_empty(row.get("Item")),
                "categoria": _text_or_empty(row.get("Categoria")),
                "unidade": _text_or_empty(row.get("Unidade")),
                "quantidade": quantidade,
                "valor_unitario": valor_unitario,
                "subtotal": calcular_subtotal_item(quantidade, valor_unitario),
                "observacoes": _text_or_empty(row.get("Observacao")).strip(),
            }
        )

    return itens_normalizados


if "item_quantidade" not in st.session_state:
    st.session_state["item_quantidade"] = 1.0
if "item_valor_unitario" not in st.session_state:
    st.session_state["item_valor_unitario"] = 0.0
if "item_observacoes" not in st.session_state:
    st.session_state["item_observacoes"] = ""
if produtos_ativos and st.session_state.get("item_produto_id") not in produto_map:
    st.session_state["item_produto_id"] = produtos_ativos[0]["id"]
    carregar_preco_padrao()

render_page_header(
    "Novo orcamento",
    "Monte propostas com itens cadastrados, calculo automatico e um fluxo seguro para salvar no banco local.",
    eyebrow="Operacao comercial",
    badge="Calculo automatico",
)

if not clientes:
    st.warning("Cadastre pelo menos um cliente antes de criar um orcamento.")
    st.stop()

cliente_ids = [cliente["id"] for cliente in clientes]
if st.session_state["orc_cliente_id"] not in cliente_ids:
    st.session_state["orc_cliente_id"] = cliente_ids[0]

render_data_hint(
    "Fluxo recomendado",
    "Preencha os dados principais, adicione os itens e ajuste a propria lista antes de salvar o documento.",
)

render_section_header("Dados principais", "Informacoes gerais do documento e da execucao prevista.")
with st.container(border=True):
    numero_orcamento = get_next_quote_number()
    st.text_input("Numero do orcamento", value=numero_orcamento, disabled=True)

    cliente_opcoes = {cliente["id"]: cliente["nome"] for cliente in clientes}
    st.selectbox(
        "Cliente *",
        options=cliente_ids,
        format_func=lambda client_id: cliente_opcoes[client_id],
        key="orc_cliente_id",
    )
    st.date_input("Data do orcamento *", key="orc_data")
    st.text_input("Responsavel pelo orcamento *", key="orc_responsavel")
    st.selectbox("Status", STATUS_ORCAMENTO, key="orc_status")
    st.date_input("Validade do orcamento", key="orc_validade")
    st.number_input("Metragem total da obra (m2)", min_value=0.0, step=1.0, key="orc_metragem_total")
    st.text_input("Prazo estimado da execucao", key="orc_prazo_execucao")
    st.text_input("Forma de pagamento", key="orc_forma_pagamento")
    st.text_area("Observacoes gerais", key="orc_observacoes", height=140)

render_section_header("Adicionar item", "Selecione um item ativo do catalogo e ajuste quantidade, preco e observacoes.")
with st.container(border=True):
    if produtos_ativos:
        produto_ids = [produto["id"] for produto in produtos_ativos]
        st.selectbox(
            "Item cadastrado *",
            options=produto_ids,
            format_func=lambda produto_id: f"{produto_map[produto_id]['nome']} ({produto_map[produto_id]['unidade']})",
            key="item_produto_id",
            on_change=carregar_preco_padrao,
        )
        produto_selecionado = produto_map[st.session_state["item_produto_id"]]
        st.caption(
            f"Categoria: {produto_selecionado['categoria']} | Preco padrao: {currency(produto_selecionado['preco_unitario'])}"
        )
        i1, i2 = st.columns(2)
        i1.number_input("Quantidade *", min_value=0.0, step=1.0, key="item_quantidade")
        i2.number_input("Valor unitario *", min_value=0.0, step=1.0, format="%.2f", key="item_valor_unitario")
        st.text_area("Observacao do item", key="item_observacoes", height=90)

        subtotal_preview = calcular_subtotal_item(st.session_state["item_quantidade"], st.session_state["item_valor_unitario"])
        render_data_hint("Preview do item", f"Subtotal atual: {currency(subtotal_preview)}")

        st.button("Adicionar item ao orcamento", use_container_width=True, on_click=adicionar_item_ao_orcamento)

        item_feedback = st.session_state.pop("item_feedback", None)
        if item_feedback:
            feedback_tipo, feedback_texto = item_feedback
            if feedback_tipo == "success":
                st.success(feedback_texto)
            else:
                st.error(feedback_texto)
    else:
        render_empty_state(
            "Nenhum item ativo encontrado",
            "Cadastre produtos ou servicos ativos antes de montar um novo orcamento.",
        )

render_section_header("Itens do orcamento", "Confira os itens adicionados e remova linhas quando necessario.")
itens_temp = st.session_state["orcamento_itens_temp"]
if itens_temp:
    st.caption("Edite quantidade e valor unitario diretamente na lista. Marque `Excluir` para remover um item.")
    editor_df = st.data_editor(
        montar_tabela_itens(itens_temp),
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        disabled=["_produto_id", "Item", "Categoria", "Unidade", "Subtotal", "Observacao"],
        column_config={
            "_produto_id": None,
            "Quantidade": st.column_config.NumberColumn("Quantidade", min_value=0.01, step=1.0, format="%.2f"),
            "Valor unitario": st.column_config.NumberColumn(
                "Valor unitario", min_value=0.0, step=1.0, format="%.2f"
            ),
            "Subtotal": st.column_config.NumberColumn("Subtotal", format="%.2f"),
            "Excluir": st.column_config.CheckboxColumn("Excluir", help="Marque para remover o item da lista."),
        },
    )

    itens_editados = normalizar_itens_editados(editor_df)
    if itens_editados != itens_temp:
        st.session_state["orcamento_itens_temp"] = itens_editados
        itens_temp = itens_editados
else:
    render_empty_state("Seu rascunho ainda nao tem itens", "Adicione pelo menos um item para liberar o salvamento do documento.")

render_section_header("Calculo automatico", "Desconto e taxa adicional sao aplicados automaticamente sobre o subtotal.")
t1, t2, t3 = st.columns(3)
t1.selectbox("Tipo de desconto", TIPOS_DESCONTO, key="orc_desconto_tipo", on_change=sincronizar_desconto_com_tipo)
desconto_tipo = st.session_state["orc_desconto_tipo"]

if desconto_tipo == "Percentual":
    t2.number_input("Desconto (%)", min_value=0.0, max_value=100.0, step=1.0, key="orc_desconto_percentual")
elif desconto_tipo == "Valor fixo":
    t2.number_input("Desconto em valor", min_value=0.0, step=1.0, format="%.2f", key="orc_desconto_valor")
t3.number_input("Taxa adicional", min_value=0.0, step=1.0, format="%.2f", key="orc_taxa_adicional")

desconto_percentual = float(st.session_state["orc_desconto_percentual"]) if desconto_tipo == "Percentual" else 0.0
desconto_valor = float(st.session_state["orc_desconto_valor"]) if desconto_tipo == "Valor fixo" else 0.0

totais = calcular_totais(
    itens_temp,
    desconto_tipo=desconto_tipo,
    desconto_percentual=desconto_percentual,
    desconto_valor=desconto_valor,
    taxa_adicional=st.session_state["orc_taxa_adicional"],
)

tc1, tc2, tc3, tc4 = st.columns(4)
with tc1:
    render_info_card("Subtotal", currency(totais["subtotal"]), "Soma de todos os itens do rascunho")
with tc2:
    render_info_card("Desconto", currency(totais["desconto_aplicado"]), "Aplicado de acordo com a regra selecionada")
with tc3:
    render_info_card("Taxa adicional", currency(totais["taxa_adicional"]), "Custos extras incluidos no documento")
with tc4:
    render_info_card("Total final", currency(totais["total_final"]), "Valor final apresentado ao cliente")

s1, s2 = st.columns([1, 1])
if s1.button("Salvar orcamento", use_container_width=True, type="primary"):
    numero_orcamento = get_next_quote_number()
    payload, itens_normalizados, errors = validate_quote_payload(
        {
            "numero": numero_orcamento,
            "cliente_id": st.session_state["orc_cliente_id"],
            "data_orcamento": st.session_state["orc_data"].isoformat(),
            "responsavel": st.session_state["orc_responsavel"],
            "status": st.session_state["orc_status"],
            "subtotal": totais["subtotal"],
            "desconto_tipo": totais["desconto_tipo"],
            "desconto_percentual": totais["desconto_percentual"],
            "desconto_valor": totais["desconto_valor"],
            "taxa_adicional": totais["taxa_adicional"],
            "total_final": totais["total_final"],
            "observacoes": st.session_state["orc_observacoes"],
            "validade": st.session_state["orc_validade"].isoformat()
            if isinstance(st.session_state["orc_validade"], date)
            else default_validity_date().isoformat(),
            "metragem_total": float(st.session_state["orc_metragem_total"]),
            "prazo_execucao": st.session_state["orc_prazo_execucao"],
            "forma_pagamento": st.session_state["orc_forma_pagamento"],
        },
        itens_temp,
    )
    if errors:
        for error in errors:
            st.error(error)
    else:
        st.session_state["orcamento_itens_temp"] = itens_normalizados
        create_orcamento(payload, itens_normalizados)
        reset_quote_state()
        st.success("Orcamento salvo com sucesso.")
        st.rerun()

if s2.button("Limpar rascunho atual", use_container_width=True):
    reset_quote_state()
    st.info("Rascunho limpo.")
    st.rerun()
