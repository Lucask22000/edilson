from __future__ import annotations

import html
from datetime import date, timedelta

import streamlit as st


STATUS_COLORS = {
    "Rascunho": "#9a6700",
    "Aprovado": "#1f6f43",
    "Recusado": "#b42318",
}


def configure_page(page_title: str) -> None:
    st.set_page_config(
        page_title=f"{page_title} | Orcamentos Pintura",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(180deg, #f3f6f8 0%, #fcfcfb 22%, #ffffff 100%);
                color: #15202b;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #123845 0%, #184c5d 100%);
            }
            [data-testid="stSidebar"] * {
                color: #f7fbfc;
            }
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
                color: #d8e9ee;
            }
            .block-container {
                padding-top: 2rem;
            }
            h1, h2, h3, h4, h5, h6 {
                color: #12202f;
            }
            p, li, label, .stCaption, .stMarkdown, .stText {
                color: #243241;
            }
            [data-testid="stForm"],
            [data-testid="stVerticalBlock"] > [data-testid="stContainer"] {
                color: #15202b;
            }
            [data-testid="stMetric"],
            [data-testid="stDataFrame"],
            [data-testid="stExpander"] {
                border-radius: 16px;
            }
            div[data-baseweb="input"] > div,
            div[data-baseweb="select"] > div,
            div[data-baseweb="textarea"] > div,
            [data-testid="stDateInputField"] {
                background: #ffffff;
                border: 1px solid #c8d4dc;
                border-radius: 12px;
                color: #15202b;
            }
            div[data-baseweb="input"] input,
            div[data-baseweb="textarea"] textarea,
            div[data-baseweb="select"] input {
                color: #15202b !important;
                -webkit-text-fill-color: #15202b !important;
            }
            div[data-baseweb="input"] > div:focus-within,
            div[data-baseweb="select"] > div:focus-within,
            div[data-baseweb="textarea"] > div:focus-within,
            [data-testid="stDateInputField"]:focus-within {
                border-color: #1b6f87;
                box-shadow: 0 0 0 1px #1b6f87;
            }
            .stButton > button,
            .stDownloadButton > button {
                background: #1b6f87;
                color: #ffffff;
                border: 1px solid #16596d;
                border-radius: 12px;
                font-weight: 600;
            }
            .stButton > button:hover,
            .stDownloadButton > button:hover {
                background: #16596d;
                border-color: #124b5b;
                color: #ffffff;
            }
            .stButton > button[kind="secondary"] {
                background: #eef5f7;
                color: #17313f;
                border: 1px solid #c7d5dc;
            }
            [data-testid="stAlert"] {
                border-radius: 14px;
            }
            [data-testid="stDataFrame"] {
                background: #ffffff;
                border: 1px solid #dbe4ea;
            }
            [data-testid="stTable"] {
                color: #15202b;
            }
            .hero-box {
                background: linear-gradient(135deg, #164556 0%, #287086 100%);
                color: #ffffff;
                border-radius: 18px;
                padding: 1.4rem 1.6rem;
                margin-bottom: 1rem;
                box-shadow: 0 14px 32px rgba(19, 58, 73, 0.16);
            }
            .metric-card {
                background: #ffffff;
                border: 1px solid #d9e3e8;
                border-radius: 16px;
                padding: 1rem 1.1rem;
                box-shadow: 0 10px 24px rgba(34, 52, 74, 0.07);
                min-height: 118px;
            }
            .metric-label {
                color: #52606d;
                font-size: 0.92rem;
                margin-bottom: 0.35rem;
            }
            .metric-value {
                color: #10202d;
                font-size: 1.85rem;
                font-weight: 700;
                line-height: 1.15;
                margin-bottom: 0.25rem;
            }
            .metric-help {
                color: #52606d;
                font-size: 0.85rem;
            }
            .section-card {
                background: #ffffff;
                border: 1px solid #d8e3e8;
                border-radius: 16px;
                padding: 1rem 1.1rem;
                margin-bottom: 1rem;
            }
            .status-pill {
                display: inline-block;
                border-radius: 999px;
                padding: 0.2rem 0.75rem;
                color: #ffffff;
                font-weight: 700;
                font-size: 0.85rem;
            }
            .total-box {
                background: #f4f8fb;
                border: 1px solid #d1dfe7;
                border-radius: 16px;
                padding: 1rem 1.2rem;
                color: #10202d;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(title: str, value: str, helper: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(title)}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
            <div class="metric-help">{html.escape(helper)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def currency(value: float | int | None) -> str:
    number = float(value or 0)
    formatted = f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def safe_text(value: str | None, fallback: str = "-") -> str:
    text = (value or "").strip()
    return text if text else fallback


def render_status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#4a5568")
    return f'<span class="status-pill" style="background:{color};">{html.escape(status)}</span>'


def default_validity_date() -> date:
    return date.today() + timedelta(days=7)


def init_quote_state() -> None:
    defaults = {
        "orcamento_itens_temp": [],
        "orc_cliente_id": None,
        "orc_data": date.today(),
        "orc_responsavel": "",
        "orc_status": "Rascunho",
        "orc_validade": default_validity_date(),
        "orc_observacoes": "",
        "orc_metragem_total": 0.0,
        "orc_prazo_execucao": "",
        "orc_forma_pagamento": "",
        "orc_desconto_tipo": "Nenhum",
        "orc_desconto_percentual": 0.0,
        "orc_desconto_valor": 0.0,
        "orc_taxa_adicional": 0.0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_quote_state() -> None:
    keys = [
        "orcamento_itens_temp",
        "orc_cliente_id",
        "orc_data",
        "orc_responsavel",
        "orc_status",
        "orc_validade",
        "orc_observacoes",
        "orc_metragem_total",
        "orc_prazo_execucao",
        "orc_forma_pagamento",
        "orc_desconto_tipo",
        "orc_desconto_percentual",
        "orc_desconto_valor",
        "orc_taxa_adicional",
        "item_produto_id",
        "item_quantidade",
        "item_valor_unitario",
        "item_observacoes",
    ]
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]
    init_quote_state()


def load_quote_into_state(orcamento: dict) -> None:
    st.session_state["orcamento_itens_temp"] = [
        {
            "produto_id": item["produto_id"],
            "item_nome": item["item_nome"],
            "categoria": item["categoria"],
            "unidade": item["unidade"],
            "quantidade": float(item["quantidade"]),
            "valor_unitario": float(item["valor_unitario"]),
            "subtotal": float(item["subtotal"]),
            "observacoes": item["observacoes"] or "",
        }
        for item in orcamento.get("itens", [])
    ]
    st.session_state["orc_cliente_id"] = orcamento.get("cliente_id")
    st.session_state["orc_data"] = date.today()
    st.session_state["orc_responsavel"] = orcamento.get("responsavel", "")
    st.session_state["orc_status"] = "Rascunho"
    validade = orcamento.get("validade")
    st.session_state["orc_validade"] = date.fromisoformat(validade) if validade else default_validity_date()
    st.session_state["orc_observacoes"] = orcamento.get("observacoes", "") or ""
    st.session_state["orc_metragem_total"] = float(orcamento.get("metragem_total") or 0.0)
    st.session_state["orc_prazo_execucao"] = orcamento.get("prazo_execucao", "") or ""
    st.session_state["orc_forma_pagamento"] = orcamento.get("forma_pagamento", "") or ""
    st.session_state["orc_desconto_tipo"] = orcamento.get("desconto_tipo", "Nenhum")
    st.session_state["orc_desconto_percentual"] = float(orcamento.get("desconto_percentual") or 0.0)
    st.session_state["orc_desconto_valor"] = float(orcamento.get("desconto_valor") or 0.0)
    st.session_state["orc_taxa_adicional"] = float(orcamento.get("taxa_adicional") or 0.0)


def build_quote_html(orcamento: dict) -> str:
    itens_rows = []
    for item in orcamento.get("itens", []):
        itens_rows.append(
            f"""
            <tr>
                <td>{html.escape(item.get("item_nome", ""))}</td>
                <td>{html.escape(item.get("categoria", "") or "-")}</td>
                <td>{html.escape(item.get("unidade", "") or "-")}</td>
                <td style="text-align:right;">{item.get("quantidade", 0):,.2f}</td>
                <td style="text-align:right;">{currency(item.get("valor_unitario", 0))}</td>
                <td style="text-align:right;">{currency(item.get("subtotal", 0))}</td>
            </tr>
            """
        )

    itens_html = "".join(itens_rows) or "<tr><td colspan='6'>Nenhum item cadastrado.</td></tr>"
    desconto_label = orcamento.get("desconto_tipo", "Nenhum")
    desconto_valor = float(orcamento.get("desconto_valor") or 0)
    if desconto_label == "Percentual":
        desconto_valor = float(orcamento.get("subtotal") or 0) * (float(orcamento.get("desconto_percentual") or 0) / 100)

    return f"""
    <html>
        <head>
            <meta charset="utf-8" />
            <title>{html.escape(orcamento.get("numero", "Orcamento"))}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #1f2937;
                    margin: 24px;
                }}
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    border-bottom: 2px solid #103c4a;
                    padding-bottom: 12px;
                    margin-bottom: 18px;
                }}
                .title {{
                    color: #103c4a;
                    font-size: 26px;
                    font-weight: 700;
                    margin: 0;
                }}
                .box {{
                    border: 1px solid #d1d5db;
                    border-radius: 12px;
                    padding: 14px;
                    margin-bottom: 16px;
                }}
                .grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 16px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 12px;
                }}
                th, td {{
                    border: 1px solid #d1d5db;
                    padding: 8px;
                    font-size: 13px;
                }}
                th {{
                    background: #f3f4f6;
                    text-align: left;
                }}
                .totals {{
                    margin-top: 18px;
                    width: 320px;
                    margin-left: auto;
                }}
                .totals td {{
                    border: none;
                    padding: 6px 0;
                }}
                .total-final {{
                    font-size: 18px;
                    font-weight: 700;
                    color: #103c4a;
                }}
                .print-btn {{
                    margin-bottom: 16px;
                }}
                @media print {{
                    .print-btn {{
                        display: none;
                    }}
                    body {{
                        margin: 0;
                    }}
                }}
            </style>
        </head>
        <body>
            <button class="print-btn" onclick="window.print()">Imprimir</button>
            <div class="header">
                <div>
                    <p class="title">Orcamento de Pintura</p>
                    <div>{html.escape(orcamento.get("numero", ""))}</div>
                </div>
                <div>
                    <div><strong>Data:</strong> {html.escape(orcamento.get("data_orcamento", ""))}</div>
                    <div><strong>Status:</strong> {html.escape(orcamento.get("status", ""))}</div>
                    <div><strong>Validade:</strong> {html.escape(orcamento.get("validade", "") or "-")}</div>
                </div>
            </div>

            <div class="grid">
                <div class="box">
                    <h3>Cliente</h3>
                    <div><strong>Nome:</strong> {html.escape(orcamento.get("cliente_nome", ""))}</div>
                    <div><strong>Telefone:</strong> {html.escape(orcamento.get("cliente_telefone", "") or "-")}</div>
                    <div><strong>Email:</strong> {html.escape(orcamento.get("cliente_email", "") or "-")}</div>
                    <div><strong>Endereco:</strong> {html.escape(orcamento.get("cliente_endereco", "") or "-")}</div>
                </div>
                <div class="box">
                    <h3>Detalhes</h3>
                    <div><strong>Responsavel:</strong> {html.escape(orcamento.get("responsavel", ""))}</div>
                    <div><strong>Metragem:</strong> {float(orcamento.get("metragem_total") or 0):,.2f} m2</div>
                    <div><strong>Prazo estimado:</strong> {html.escape(orcamento.get("prazo_execucao", "") or "-")}</div>
                    <div><strong>Pagamento:</strong> {html.escape(orcamento.get("forma_pagamento", "") or "-")}</div>
                </div>
            </div>

            <div class="box">
                <h3>Itens do orcamento</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th>Categoria</th>
                            <th>Unidade</th>
                            <th>Quantidade</th>
                            <th>Valor unitario</th>
                            <th>Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        {itens_html}
                    </tbody>
                </table>
            </div>

            <table class="totals">
                <tr>
                    <td>Subtotal</td>
                    <td style="text-align:right;">{currency(orcamento.get("subtotal", 0))}</td>
                </tr>
                <tr>
                    <td>Desconto ({html.escape(desconto_label)})</td>
                    <td style="text-align:right;">{currency(desconto_valor)}</td>
                </tr>
                <tr>
                    <td>Taxa adicional</td>
                    <td style="text-align:right;">{currency(orcamento.get("taxa_adicional", 0))}</td>
                </tr>
                <tr>
                    <td class="total-final">Total final</td>
                    <td class="total-final" style="text-align:right;">{currency(orcamento.get("total_final", 0))}</td>
                </tr>
            </table>

            <div class="box">
                <h3>Observacoes</h3>
                <div>{html.escape(orcamento.get("observacoes", "") or "Sem observacoes adicionais.")}</div>
            </div>
        </body>
    </html>
    """
