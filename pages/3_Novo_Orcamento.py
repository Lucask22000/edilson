from __future__ import annotations

from datetime import date

import streamlit as st

from database import create_orcamento, get_next_quote_number, get_orcamento, init_db, list_clients, list_products
from models import STATUS_ORCAMENTO, TIPOS_DESCONTO
from services.calculations import calcular_subtotal_item, calcular_totais
from utils import (
    configure_page,
    currency,
    default_validity_date,
    init_quote_state,
    inject_custom_css,
    load_quote_into_state,
    reset_quote_state,
)


configure_page("Novo Orcamento")
init_db()
inject_custom_css()
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


if "item_quantidade" not in st.session_state:
    st.session_state["item_quantidade"] = 1.0
if "item_valor_unitario" not in st.session_state:
    st.session_state["item_valor_unitario"] = 0.0
if "item_observacoes" not in st.session_state:
    st.session_state["item_observacoes"] = ""
if produtos_ativos and st.session_state.get("item_produto_id") not in produto_map:
    st.session_state["item_produto_id"] = produtos_ativos[0]["id"]
    carregar_preco_padrao()

st.title("Novo orcamento")
st.caption("Monte o orcamento com itens cadastrados, calculo automatico e salvamento no banco local.")

if not clientes:
    st.warning("Cadastre pelo menos um cliente antes de criar um orcamento.")
    st.stop()

cliente_ids = [cliente["id"] for cliente in clientes]
if st.session_state["orc_cliente_id"] not in cliente_ids:
    st.session_state["orc_cliente_id"] = cliente_ids[0]

col_meta, col_itens = st.columns([1.15, 1.2], gap="large")

with col_meta:
    st.subheader("Dados principais")
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

with col_itens:
    st.subheader("Adicionar item")
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

        subtotal_preview = calcular_subtotal_item(
            st.session_state["item_quantidade"], st.session_state["item_valor_unitario"]
        )
        st.info(f"Subtotal do item: {currency(subtotal_preview)}")

        if st.button("Adicionar item ao orcamento", use_container_width=True):
            quantidade = float(st.session_state["item_quantidade"])
            valor_unitario = float(st.session_state["item_valor_unitario"])
            if quantidade <= 0:
                st.error("A quantidade deve ser maior que zero.")
            elif valor_unitario < 0:
                st.error("O valor unitario nao pode ser negativo.")
            else:
                st.session_state["orcamento_itens_temp"].append(
                    {
                        "produto_id": produto_selecionado["id"],
                        "item_nome": produto_selecionado["nome"],
                        "categoria": produto_selecionado["categoria"],
                        "unidade": produto_selecionado["unidade"],
                        "quantidade": quantidade,
                        "valor_unitario": valor_unitario,
                        "subtotal": subtotal_preview,
                        "observacoes": st.session_state["item_observacoes"].strip(),
                    }
                )
                st.session_state["item_quantidade"] = 1.0
                st.session_state["item_valor_unitario"] = float(produto_selecionado["preco_unitario"])
                st.session_state["item_observacoes"] = ""
                st.success("Item adicionado com sucesso.")
                st.rerun()
    else:
        st.warning("Nenhum produto ou servico ativo encontrado. Cadastre itens antes de montar o orcamento.")

st.markdown("### Itens do orcamento")
itens_temp = st.session_state["orcamento_itens_temp"]
if itens_temp:
    st.dataframe(
        [
            {
                "Item": item["item_nome"],
                "Categoria": item["categoria"],
                "Unidade": item["unidade"],
                "Quantidade": item["quantidade"],
                "Valor unitario": currency(item["valor_unitario"]),
                "Subtotal": currency(item["subtotal"]),
                "Observacao": item["observacoes"] or "-",
            }
            for item in itens_temp
        ],
        use_container_width=True,
        hide_index=True,
    )

    indices = list(range(len(itens_temp)))
    r1, r2 = st.columns([2, 1])
    remover_idx = r1.selectbox(
        "Selecione um item para remover",
        options=indices,
        format_func=lambda index: f"{index + 1} - {itens_temp[index]['item_nome']}",
    )
    if r2.button("Remover item", use_container_width=True):
        itens_temp.pop(remover_idx)
        st.success("Item removido do orcamento.")
        st.rerun()
else:
    st.info("Adicione pelo menos um item para salvar o orcamento.")

st.markdown("### Calculo automatico")
t1, t2, t3 = st.columns(3)
t1.selectbox("Tipo de desconto", TIPOS_DESCONTO, key="orc_desconto_tipo")
if st.session_state["orc_desconto_tipo"] == "Percentual":
    t2.number_input("Desconto (%)", min_value=0.0, max_value=100.0, step=1.0, key="orc_desconto_percentual")
    st.session_state["orc_desconto_valor"] = 0.0
elif st.session_state["orc_desconto_tipo"] == "Valor fixo":
    t2.number_input("Desconto em valor", min_value=0.0, step=1.0, format="%.2f", key="orc_desconto_valor")
    st.session_state["orc_desconto_percentual"] = 0.0
else:
    st.session_state["orc_desconto_percentual"] = 0.0
    st.session_state["orc_desconto_valor"] = 0.0
t3.number_input("Taxa adicional", min_value=0.0, step=1.0, format="%.2f", key="orc_taxa_adicional")

totais = calcular_totais(
    itens_temp,
    desconto_tipo=st.session_state["orc_desconto_tipo"],
    desconto_percentual=st.session_state["orc_desconto_percentual"],
    desconto_valor=st.session_state["orc_desconto_valor"],
    taxa_adicional=st.session_state["orc_taxa_adicional"],
)

tc1, tc2, tc3, tc4 = st.columns(4)
with tc1:
    st.markdown(f'<div class="total-box"><strong>Subtotal</strong><br>{currency(totais["subtotal"])}</div>', unsafe_allow_html=True)
with tc2:
    st.markdown(
        f'<div class="total-box"><strong>Desconto</strong><br>{currency(totais["desconto_aplicado"])}</div>',
        unsafe_allow_html=True,
    )
with tc3:
    st.markdown(
        f'<div class="total-box"><strong>Taxa adicional</strong><br>{currency(totais["taxa_adicional"])}</div>',
        unsafe_allow_html=True,
    )
with tc4:
    st.markdown(
        f'<div class="total-box"><strong>Total final</strong><br>{currency(totais["total_final"])}</div>',
        unsafe_allow_html=True,
    )

s1, s2 = st.columns([1, 1])
if s1.button("Salvar orcamento", use_container_width=True, type="primary"):
    if not st.session_state["orc_responsavel"].strip():
        st.error("Informe o nome do responsavel pelo orcamento.")
    elif not itens_temp:
        st.error("Adicione pelo menos um item antes de salvar.")
    else:
        create_orcamento(
            {
                "numero": numero_orcamento,
                "cliente_id": st.session_state["orc_cliente_id"],
                "data_orcamento": st.session_state["orc_data"].isoformat(),
                "responsavel": st.session_state["orc_responsavel"].strip(),
                "status": st.session_state["orc_status"],
                "subtotal": totais["subtotal"],
                "desconto_tipo": totais["desconto_tipo"],
                "desconto_percentual": totais["desconto_percentual"],
                "desconto_valor": totais["desconto_valor"],
                "taxa_adicional": totais["taxa_adicional"],
                "total_final": totais["total_final"],
                "observacoes": st.session_state["orc_observacoes"].strip(),
                "validade": st.session_state["orc_validade"].isoformat()
                if isinstance(st.session_state["orc_validade"], date)
                else default_validity_date().isoformat(),
                "metragem_total": float(st.session_state["orc_metragem_total"]),
                "prazo_execucao": st.session_state["orc_prazo_execucao"].strip(),
                "forma_pagamento": st.session_state["orc_forma_pagamento"].strip(),
            },
            itens_temp,
        )
        reset_quote_state()
        st.success("Orcamento salvo com sucesso.")
        st.rerun()

if s2.button("Limpar rascunho atual", use_container_width=True):
    reset_quote_state()
    st.info("Rascunho limpo.")
    st.rerun()
