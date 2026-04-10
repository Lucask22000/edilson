from __future__ import annotations

import streamlit as st

from components import render_data_hint, render_empty_state, render_page_header, render_section_header, setup_page
from database import create_client, delete_client, get_client, list_clients, update_client


PAGE_TITLE = "Clientes"

setup_page(PAGE_TITLE)

render_page_header(
    "Clientes",
    "Organize os dados de contato e historico basico dos clientes para agilizar novos orcamentos e consultas futuras.",
    eyebrow="Relacionamento comercial",
    badge="Base ativa",
)

render_section_header("Novo cliente", "Cadastre clientes residenciais e corporativos em um fluxo simples e padronizado.")
with st.container(border=True):
    with st.form("form_novo_cliente", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        nome = c1.text_input("Nome *")
        telefone = c2.text_input("Telefone")
        email = c3.text_input("Email")
        endereco = st.text_input("Endereco")
        observacoes = st.text_area("Observacoes", height=100)
        salvar = st.form_submit_button("Cadastrar cliente", use_container_width=True)

        if salvar:
            if not nome.strip():
                st.error("Informe o nome do cliente.")
            else:
                create_client(
                    {
                        "nome": nome.strip(),
                        "telefone": telefone.strip(),
                        "email": email.strip(),
                        "endereco": endereco.strip(),
                        "observacoes": observacoes.strip(),
                    }
                )
                st.success("Cliente cadastrado com sucesso.")
                st.rerun()

render_section_header("Lista de clientes", "Use a pesquisa para localizar rapidamente registros e carregar uma edicao.")
render_data_hint("Cadastro limpo", "Manter telefone e email atualizados melhora o compartilhamento de propostas.")
search = st.text_input("Pesquisar cliente por nome")
clientes = list_clients(search=search)

if clientes:
    st.dataframe(
        [
            {
                "ID": cliente["id"],
                "Nome": cliente["nome"],
                "Telefone": cliente["telefone"] or "-",
                "Email": cliente["email"] or "-",
                "Endereco": cliente["endereco"] or "-",
            }
            for cliente in clientes
        ],
        use_container_width=True,
        hide_index=True,
    )

    options = {f"{cliente['id']} - {cliente['nome']}": cliente["id"] for cliente in clientes}
    selecionado_label = st.selectbox("Selecione um cliente para editar ou excluir", list(options.keys()))
    selecionado_id = options[selecionado_label]

    a1, a2, a3 = st.columns([1, 1, 2])
    with a1:
        if st.button("Carregar cliente", use_container_width=True):
            st.session_state["cliente_edicao_id"] = selecionado_id
            st.rerun()
    with a2:
        confirmar = st.checkbox("Confirmar exclusao", key="confirmar_exclusao_cliente")
        if st.button("Excluir cliente", use_container_width=True) and confirmar:
            try:
                delete_client(selecionado_id)
                st.success("Cliente excluido com sucesso.")
                if st.session_state.get("cliente_edicao_id") == selecionado_id:
                    del st.session_state["cliente_edicao_id"]
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    with a3:
        st.caption("Clientes com orcamentos vinculados nao podem ser removidos para preservar o historico.")
else:
    render_empty_state("Nenhum cliente cadastrado", "Cadastre o primeiro cliente para liberar a criacao de orcamentos.")

cliente_edicao_id = st.session_state.get("cliente_edicao_id")
if cliente_edicao_id:
    cliente = get_client(cliente_edicao_id)
    if cliente:
        render_section_header("Editar cliente", "Atualize dados de contato sem alterar o historico dos documentos ja emitidos.")
        with st.form("form_editar_cliente"):
            e1, e2, e3 = st.columns(3)
            nome = e1.text_input("Nome *", value=cliente["nome"])
            telefone = e2.text_input("Telefone", value=cliente["telefone"] or "")
            email = e3.text_input("Email", value=cliente["email"] or "")
            endereco = st.text_input("Endereco", value=cliente["endereco"] or "")
            observacoes = st.text_area("Observacoes", value=cliente["observacoes"] or "", height=100)

            save_col, cancel_col = st.columns(2)
            salvar = save_col.form_submit_button("Salvar alteracoes", use_container_width=True)
            cancelar = cancel_col.form_submit_button("Cancelar", use_container_width=True)

            if salvar:
                if not nome.strip():
                    st.error("Informe o nome do cliente.")
                else:
                    update_client(
                        cliente_edicao_id,
                        {
                            "nome": nome.strip(),
                            "telefone": telefone.strip(),
                            "email": email.strip(),
                            "endereco": endereco.strip(),
                            "observacoes": observacoes.strip(),
                        },
                    )
                    st.success("Cliente atualizado com sucesso.")
                    del st.session_state["cliente_edicao_id"]
                    st.rerun()
            if cancelar:
                del st.session_state["cliente_edicao_id"]
                st.rerun()
