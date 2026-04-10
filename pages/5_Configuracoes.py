from __future__ import annotations

import base64

import streamlit as st

from components import render_data_hint, render_empty_state, render_page_header, render_section_header, setup_page
from database import get_company_info, upsert_company_info
from utils import get_logo_bytes


PAGE_TITLE = "Configuracoes"
MAX_LOGO_SIZE = 2 * 1024 * 1024

setup_page(PAGE_TITLE)

company = get_company_info()

render_page_header(
    "Configuracoes da empresa",
    "Atualize os dados institucionais, o nome do app e a identidade visual usada em toda a experiencia do sistema.",
    eyebrow="Identidade e parametros",
    badge="Branding centralizado",
)

render_section_header("Logo e identidade", "A logo aparece na sidebar, nos documentos exportados e no icone do app.")
render_data_hint("Recomendacao", "Use uma imagem quadrada em PNG com fundo transparente e tamanho maximo de 2 MB.")
logo_bytes = get_logo_bytes(company)
preview_col, helper_col = st.columns([1, 1.4], gap="large")
with preview_col:
    if logo_bytes:
        with st.container(border=True):
            st.image(logo_bytes, caption="Logo atual", use_container_width=True)
    else:
        render_empty_state("Nenhuma logo cadastrada", "Envie uma imagem para reforcar a identidade visual do sistema.")
with helper_col:
    with st.container(border=True):
        st.write("A logo sera usada na barra lateral, no HTML/PDF do orcamento e como icone do app no navegador.")
        st.caption("Sempre que possivel, prefira arquivos limpos e com boa leitura em tamanhos reduzidos.")

with st.form("form_configuracoes_empresa"):
    render_section_header("Dados principais")
    a1, a2 = st.columns(2)
    nome_fantasia = a1.text_input("Nome fantasia *", value=company.get("nome_fantasia") or "")
    razao_social = a2.text_input("Razao social", value=company.get("razao_social") or "")

    b1, b2, b3 = st.columns(3)
    cnpj = b1.text_input("CNPJ", value=company.get("cnpj") or "")
    telefone = b2.text_input("Telefone", value=company.get("telefone") or "")
    email = b3.text_input("Email", value=company.get("email") or "")

    c1, c2 = st.columns(2)
    endereco = c1.text_input("Endereco", value=company.get("endereco") or "")
    cidade_estado = c2.text_input("Cidade / Estado", value=company.get("cidade_estado") or "")

    render_section_header("Presenca digital")
    d1, d2 = st.columns(2)
    website = d1.text_input("Site", value=company.get("website") or "")
    instagram = d2.text_input("Instagram", value=company.get("instagram") or "")

    render_section_header("Nome do app")
    e1, e2 = st.columns(2)
    app_title = e1.text_input("Titulo do app", value=company.get("app_title") or company.get("nome_fantasia") or "")
    app_short_name = e2.text_input(
        "Nome curto para celular",
        value=company.get("app_short_name") or company.get("nome_fantasia") or "",
        help="Usado em atalhos e na identificacao do app.",
    )

    render_section_header("Logo")
    logo_file = st.file_uploader("Enviar nova logo", type=["png", "jpg", "jpeg"])
    remover_logo = st.checkbox("Remover logo atual")

    observacoes = st.text_area("Observacoes", value=company.get("observacoes") or "", height=120)

    salvar = st.form_submit_button("Salvar configuracoes", use_container_width=True)

    if salvar:
        if not nome_fantasia.strip():
            st.error("Informe pelo menos o nome fantasia da empresa.")
        elif not app_title.strip():
            st.error("Informe o titulo do app.")
        elif not app_short_name.strip():
            st.error("Informe o nome curto do app.")
        elif logo_file is not None and len(logo_file.getvalue()) > MAX_LOGO_SIZE:
            st.error("A logo excede o limite de 2 MB.")
        else:
            data = {
                "nome_fantasia": nome_fantasia.strip(),
                "app_title": app_title.strip(),
                "app_short_name": app_short_name.strip(),
                "razao_social": razao_social.strip(),
                "cnpj": cnpj.strip(),
                "telefone": telefone.strip(),
                "email": email.strip(),
                "endereco": endereco.strip(),
                "cidade_estado": cidade_estado.strip(),
                "website": website.strip(),
                "instagram": instagram.strip(),
                "logo_base64": company.get("logo_base64") or "",
                "logo_mime": company.get("logo_mime") or "",
                "logo_filename": company.get("logo_filename") or "",
                "observacoes": observacoes.strip(),
            }

            if remover_logo:
                data["logo_base64"] = ""
                data["logo_mime"] = ""
                data["logo_filename"] = ""
            elif logo_file is not None:
                logo_bytes = logo_file.getvalue()
                data["logo_base64"] = base64.b64encode(logo_bytes).decode("ascii")
                data["logo_mime"] = logo_file.type or "image/png"
                data["logo_filename"] = logo_file.name

            upsert_company_info(data)
            st.success("Configuracoes salvas com sucesso.")
            st.rerun()
