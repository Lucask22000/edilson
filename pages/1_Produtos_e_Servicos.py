from __future__ import annotations

import streamlit as st

from database import (
    create_product,
    delete_product,
    get_product,
    get_product_categories,
    init_db,
    list_products,
    update_product,
)
from models import CATEGORIAS_PADRAO, UNIDADES_PADRAO
from utils import configure_page, currency, ensure_authenticated, inject_custom_css, render_sidebar_branding


PAGE_TITLE = "Produtos e Serviços"

configure_page(PAGE_TITLE)
init_db()
inject_custom_css(PAGE_TITLE)
ensure_authenticated(PAGE_TITLE)
render_sidebar_branding(PAGE_TITLE)

st.title("Produtos e serviços")
st.caption("Cadastre os itens que serão usados na montagem dos orçamentos.")


def resolve_category(choice: str, custom_value: str) -> str:
    return custom_value.strip() if choice == "Outra" else choice


def resolve_unit(choice: str, custom_value: str) -> str:
    return custom_value.strip() if choice == "Outra" else choice


with st.container(border=True):
    st.subheader("Novo item")
    with st.form("form_novo_produto", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        nome = col1.text_input("Nome do produto/serviço *")
        categoria_opcao = col2.selectbox("Categoria *", CATEGORIAS_PADRAO + ["Outra"])
        unidade_opcao = col3.selectbox("Unidade *", UNIDADES_PADRAO + ["Outra"])

        col4, col5, col6 = st.columns([1, 1, 2])
        preco_unitario = col4.number_input("Preço unitário *", min_value=0.0, step=1.0, format="%.2f")
        ativo = col5.toggle("Item ativo", value=True)
        descricao = col6.text_input("Descrição")

        categoria_custom = ""
        unidade_custom = ""
        if categoria_opcao == "Outra":
            categoria_custom = st.text_input("Informe a categoria")
        if unidade_opcao == "Outra":
            unidade_custom = st.text_input("Informe a unidade")

        submitted = st.form_submit_button("Cadastrar item", use_container_width=True)

        if submitted:
            categoria = resolve_category(categoria_opcao, categoria_custom)
            unidade = resolve_unit(unidade_opcao, unidade_custom)
            if not nome.strip() or not categoria or not unidade:
                st.error("Preencha nome, categoria e unidade para cadastrar o item.")
            else:
                create_product(
                    {
                        "nome": nome.strip(),
                        "categoria": categoria,
                        "unidade": unidade,
                        "preco_unitario": float(preco_unitario),
                        "descricao": descricao.strip(),
                        "ativo": 1 if ativo else 0,
                    }
                )
                st.success("Item cadastrado com sucesso.")
                st.rerun()

st.markdown("### Consulta de itens")
f1, f2, f3 = st.columns([2, 1, 1])
search = f1.text_input("Pesquisar por nome")
category_filter = f2.selectbox("Filtrar por categoria", ["Todas"] + get_product_categories())
status_filter = f3.selectbox("Status", ["Todos", "Ativos", "Inativos"])

only_active = None
if status_filter == "Ativos":
    only_active = True
elif status_filter == "Inativos":
    only_active = False

produtos = list_products(
    search=search,
    category="" if category_filter == "Todas" else category_filter,
    only_active=only_active,
)

if produtos:
    st.dataframe(
        [
            {
                "ID": item["id"],
                "Nome": item["nome"],
                "Categoria": item["categoria"],
                "Unidade": item["unidade"],
                "Preço unitário": currency(item["preco_unitario"]),
                "Status": "Ativo" if item["ativo"] else "Inativo",
            }
            for item in produtos
        ],
        use_container_width=True,
        hide_index=True,
    )

    options = {f"{item['id']} - {item['nome']}": item["id"] for item in produtos}
    selecionado_label = st.selectbox("Selecione um item para editar ou excluir", list(options.keys()))
    selecionado_id = options[selecionado_label]

    a1, a2, a3 = st.columns([1, 1, 2])
    with a1:
        if st.button("Carregar para edição", use_container_width=True):
            st.session_state["produto_edicao_id"] = selecionado_id
            st.rerun()
    with a2:
        confirmar = st.checkbox("Confirmar exclusão", key="confirmar_exclusao_produto")
        if st.button("Excluir item", use_container_width=True) and confirmar:
            delete_product(selecionado_id)
            st.success("Item excluído com sucesso.")
            if st.session_state.get("produto_edicao_id") == selecionado_id:
                del st.session_state["produto_edicao_id"]
            st.rerun()
    with a3:
        st.caption("A exclusão remove o item do cadastro. Orçamentos antigos preservam o histórico do item.")
else:
    st.info("Nenhum item encontrado com os filtros informados.")

produto_edicao_id = st.session_state.get("produto_edicao_id")
if produto_edicao_id:
    produto = get_product(produto_edicao_id)
    if produto:
        st.markdown("### Editar item")
        categorias_edicao = CATEGORIAS_PADRAO + ["Outra"]
        unidades_edicao = UNIDADES_PADRAO + ["Outra"]

        categoria_inicial = produto["categoria"] if produto["categoria"] in CATEGORIAS_PADRAO else "Outra"
        unidade_inicial = produto["unidade"] if produto["unidade"] in UNIDADES_PADRAO else "Outra"

        with st.form("form_editar_produto"):
            e1, e2, e3 = st.columns(3)
            nome = e1.text_input("Nome do produto/serviço *", value=produto["nome"])
            categoria_opcao = e2.selectbox(
                "Categoria *",
                categorias_edicao,
                index=categorias_edicao.index(categoria_inicial),
            )
            unidade_opcao = e3.selectbox(
                "Unidade *",
                unidades_edicao,
                index=unidades_edicao.index(unidade_inicial),
            )

            e4, e5, e6 = st.columns([1, 1, 2])
            preco_unitario = e4.number_input(
                "Preço unitário *",
                min_value=0.0,
                value=float(produto["preco_unitario"]),
                step=1.0,
                format="%.2f",
            )
            ativo = e5.toggle("Item ativo", value=bool(produto["ativo"]))
            descricao = e6.text_input("Descrição", value=produto["descricao"] or "")

            categoria_custom = ""
            unidade_custom = ""
            if categoria_opcao == "Outra":
                categoria_custom = st.text_input("Nova categoria", value=produto["categoria"])
            if unidade_opcao == "Outra":
                unidade_custom = st.text_input("Nova unidade", value=produto["unidade"])

            save_col, cancel_col = st.columns(2)
            salvar = save_col.form_submit_button("Salvar alterações", use_container_width=True)
            cancelar = cancel_col.form_submit_button("Cancelar", use_container_width=True)

            if salvar:
                categoria = resolve_category(categoria_opcao, categoria_custom)
                unidade = resolve_unit(unidade_opcao, unidade_custom)
                if not nome.strip() or not categoria or not unidade:
                    st.error("Preencha nome, categoria e unidade para salvar o item.")
                else:
                    update_product(
                        produto_edicao_id,
                        {
                            "nome": nome.strip(),
                            "categoria": categoria,
                            "unidade": unidade,
                            "preco_unitario": float(preco_unitario),
                            "descricao": descricao.strip(),
                            "ativo": 1 if ativo else 0,
                        },
                    )
                    st.success("Item atualizado com sucesso.")
                    del st.session_state["produto_edicao_id"]
                    st.rerun()
            if cancelar:
                del st.session_state["produto_edicao_id"]
                st.rerun()
