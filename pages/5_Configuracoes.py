from __future__ import annotations

import base64

import streamlit as st

from database import DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME, get_company_info, init_db, upsert_company_info
from utils import configure_page, ensure_authenticated, get_logo_bytes, inject_custom_css, render_sidebar_branding


PAGE_TITLE = "Configurações"
MAX_LOGO_SIZE = 2 * 1024 * 1024

configure_page(PAGE_TITLE)
init_db()
inject_custom_css(PAGE_TITLE)
ensure_authenticated(PAGE_TITLE)
render_sidebar_branding(PAGE_TITLE)

company = get_company_info()

st.title("Configurações")
st.caption("Atualize os dados da empresa, o nome do app e a logo usada na interface e nos documentos.")

info1, info2 = st.columns([1, 1])
with info1:
    st.info(f"Login padrão ativo: `{DEFAULT_ADMIN_USERNAME}`")
with info2:
    st.info(f"Senha padrão ativa: `{DEFAULT_ADMIN_PASSWORD}`")

st.markdown("### Logo e identidade")
logo_bytes = get_logo_bytes(company)
preview_col, helper_col = st.columns([1, 1.4], gap="large")
with preview_col:
    if logo_bytes:
        st.image(logo_bytes, caption="Logo atual", use_container_width=True)
    else:
        st.caption("Nenhuma logo cadastrada ainda.")
with helper_col:
    st.write("A logo será usada na barra lateral, no HTML/PDF do orçamento e como ícone do app no navegador/celular quando disponível.")
    st.caption("Recomendação: PNG quadrado com fundo transparente, até 2 MB.")

with st.form("form_configuracoes_empresa"):
    st.markdown("### Dados principais")
    a1, a2 = st.columns(2)
    nome_fantasia = a1.text_input("Nome fantasia *", value=company.get("nome_fantasia") or "")
    razao_social = a2.text_input("Razão social", value=company.get("razao_social") or "")

    b1, b2, b3 = st.columns(3)
    cnpj = b1.text_input("CNPJ", value=company.get("cnpj") or "")
    telefone = b2.text_input("Telefone", value=company.get("telefone") or "")
    email = b3.text_input("Email", value=company.get("email") or "")

    c1, c2 = st.columns(2)
    endereco = c1.text_input("Endereço", value=company.get("endereco") or "")
    cidade_estado = c2.text_input("Cidade / Estado", value=company.get("cidade_estado") or "")

    st.markdown("### Presença digital")
    d1, d2 = st.columns(2)
    website = d1.text_input("Site", value=company.get("website") or "")
    instagram = d2.text_input("Instagram", value=company.get("instagram") or "")

    st.markdown("### Nome do app")
    e1, e2 = st.columns(2)
    app_title = e1.text_input("Título do app", value=company.get("app_title") or company.get("nome_fantasia") or "")
    app_short_name = e2.text_input(
        "Nome curto para celular",
        value=company.get("app_short_name") or company.get("nome_fantasia") or "",
        help="Usado como nome curto em atalhos e identificação do app.",
    )

    st.markdown("### Logo")
    logo_file = st.file_uploader("Enviar nova logo", type=["png", "jpg", "jpeg"])
    remover_logo = st.checkbox("Remover logo atual")

    observacoes = st.text_area("Observações", value=company.get("observacoes") or "", height=120)

    salvar = st.form_submit_button("Salvar configurações", use_container_width=True)

    if salvar:
        if not nome_fantasia.strip():
            st.error("Informe pelo menos o nome fantasia da empresa.")
        elif not app_title.strip():
            st.error("Informe o título do app.")
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
            st.success("Configurações salvas com sucesso.")
            st.rerun()
