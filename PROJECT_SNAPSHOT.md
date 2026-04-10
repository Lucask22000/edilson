Projeto: Sistema de Orçamentos - Snapshot completo gerado em 2026-04-09 17:09:06

Cada seção abaixo mostra o caminho do arquivo original seguido pelo conteúdo completo.

----- README.md -----
# Sistema de Orçamentos para Empresa de Pintura

Projeto web para cadastro de produtos, clientes e geração de orçamentos usando Python, Streamlit e SQLite.

## Recursos principais

- Login administrativo com usuário `admin` e senha `142536`.
- Dashboard com indicadores gerais.
- Cadastro completo de produtos e serviços.
- Cadastro completo de clientes.
- Criação de orçamentos com vários itens.
- Cálculo automático de subtotal, desconto, taxa adicional e total final.
- Consulta de orçamentos com filtros por cliente, status e período.
- Visualização detalhada com exportação em PDF e HTML imprimível.
- Compartilhamento rápido por e-mail e WhatsApp com mensagem pronta.
- Página de configurações para nome da empresa, CNPJ, contatos, nome do app e logo.
- Logo aplicada na interface, nos documentos e no ícone do app quando disponível no navegador/celular.
- Banco de dados SQLite criado automaticamente ao iniciar.

## Estrutura do projeto

```text
.
|-- app.py
|-- database.py
|-- models.py
|-- requirements.txt
|-- README.md
|-- utils.py
|-- services/
|   |-- auth.py
|   `-- calculations.py
`-- pages/
    |-- 1_Produtos_e_Servicos.py
    |-- 2_Clientes.py
    |-- 3_Novo_Orcamento.py
    |-- 4_Orcamentos.py
    `-- 5_Configuracoes.py
```

## Como executar localmente

### 1. Criar ambiente virtual

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Rodar o projeto

```bash
streamlit run app.py
```

O banco `orcamentos.db` será criado automaticamente na primeira execução.

## Primeiro acesso

- Login: `admin`
- Senha: `142536`

## Como usar

1. Faça login no sistema.
2. Abra `Configurações` para cadastrar nome da empresa, CNPJ, contatos e a logo.
3. Cadastre ou ajuste produtos e serviços.
4. Cadastre clientes.
5. Abra `Novo Orçamento` para montar e salvar um orçamento.
6. Consulte os registros na página `Orçamentos`.

## Observações técnicas

- O projeto usa Streamlit, SQLite e ReportLab.
- A logo é armazenada no banco de dados.
- A geração de PDF e HTML usa automaticamente os dados cadastrados da empresa.
- Clientes com orçamentos vinculados não podem ser excluídos para preservar histórico.

----- requirements.txt -----
streamlit>=1.35,<2.0
reportlab>=4.2,<5.0

----- .gitignore -----
.venv/
__pycache__/
*.py[cod]
*.sqlite3
*.db
.DS_Store
.env
.streamlit/secrets.toml

----- app.py -----
from __future__ import annotations

import streamlit as st

from components import render_data_hint, render_empty_state, render_page_header, render_section_header, setup_page
from database import get_company_info, get_dashboard_metrics, get_recent_orcamentos, seed_sample_data
from utils import currency, render_metric_card, render_status_badge


PAGE_TITLE = "Painel"

setup_page(PAGE_TITLE)

company = get_company_info()
company_name = company.get("nome_fantasia") or "Empresa"

render_page_header(
    "Painel administrativo",
    f"Gestao completa da empresa {company_name} com clientes, produtos, orcamentos e documentos personalizados.",
    eyebrow="Visao geral do negocio",
    badge="Streamlit multipage",
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

render_section_header("Atalhos uteis", "Acoes rapidas para preparar o ambiente e atualizar os dados do painel.")
render_data_hint(
    "Rotina recomendada",
    "Revise indicadores, mantenha os cadastros em dia e acompanhe os ultimos orcamentos antes de abrir novas propostas.",
)
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
    st.info("Use o menu lateral para cadastrar produtos, clientes, gerar orcamentos e atualizar as configuracoes.")

render_section_header("Ultimos orcamentos", "Historico recente para acompanhamento rapido do time comercial.")
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
    render_empty_state("Nenhum orcamento cadastrado", "Cadastre clientes e itens para comecar a emitir propostas.")

----- database.py -----
from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

from services.auth import hash_password


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "orcamentos.db"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "142536"


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    return {column[0]: row[index] for index, column in enumerate(cursor.description)}


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = dict_factory
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def ensure_column(conn: sqlite3.Connection, table_name: str, column_name: str, definition: str) -> None:
    columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing_columns = {column["name"] for column in columns}
    if column_name not in existing_columns:
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")


def ensure_admin_user(conn: sqlite3.Connection) -> None:
    admin_user = conn.execute(
        "SELECT id FROM usuarios WHERE username = ?",
        (DEFAULT_ADMIN_USERNAME,),
    ).fetchone()
    password_hash = hash_password(DEFAULT_ADMIN_PASSWORD)

    if admin_user:
        conn.execute(
            """
            UPDATE usuarios
            SET nome = ?, password_hash = ?, ativo = 1
            WHERE id = ?
            """,
            ("Administrador", password_hash, admin_user["id"]),
        )
        return

    conn.execute(
        """
        INSERT INTO usuarios (nome, username, password_hash, ativo)
        VALUES (?, ?, ?, ?)
        """,
        ("Administrador", DEFAULT_ADMIN_USERNAME, password_hash, 1),
    )


def init_db() -> None:
    with closing(get_connection()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT NOT NULL,
                unidade TEXT NOT NULL,
                preco_unitario REAL NOT NULL DEFAULT 0 CHECK(preco_unitario >= 0),
                descricao TEXT,
                ativo INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                observacoes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS orcamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL UNIQUE,
                cliente_id INTEGER NOT NULL,
                data_orcamento TEXT NOT NULL,
                responsavel TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Rascunho',
                subtotal REAL NOT NULL DEFAULT 0 CHECK(subtotal >= 0),
                desconto_tipo TEXT NOT NULL DEFAULT 'Nenhum',
                desconto_percentual REAL NOT NULL DEFAULT 0 CHECK(desconto_percentual >= 0),
                desconto_valor REAL NOT NULL DEFAULT 0 CHECK(desconto_valor >= 0),
                taxa_adicional REAL NOT NULL DEFAULT 0 CHECK(taxa_adicional >= 0),
                total_final REAL NOT NULL DEFAULT 0 CHECK(total_final >= 0),
                observacoes TEXT,
                validade TEXT,
                metragem_total REAL NOT NULL DEFAULT 0 CHECK(metragem_total >= 0),
                prazo_execucao TEXT,
                forma_pagamento TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT
            );

            CREATE TABLE IF NOT EXISTS orcamento_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orcamento_id INTEGER NOT NULL,
                produto_id INTEGER,
                item_nome TEXT NOT NULL,
                categoria TEXT,
                unidade TEXT,
                quantidade REAL NOT NULL CHECK(quantidade >= 0),
                valor_unitario REAL NOT NULL CHECK(valor_unitario >= 0),
                subtotal REAL NOT NULL CHECK(subtotal >= 0),
                observacoes TEXT,
                FOREIGN KEY (orcamento_id) REFERENCES orcamentos(id) ON DELETE CASCADE,
                FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                ativo INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS empresa_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                nome_fantasia TEXT NOT NULL DEFAULT 'Empresa de Pintura',
                app_title TEXT NOT NULL DEFAULT 'Orçamentos de Pintura',
                app_short_name TEXT NOT NULL DEFAULT 'Orçamentos',
                razao_social TEXT,
                cnpj TEXT,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                cidade_estado TEXT,
                website TEXT,
                instagram TEXT,
                logo_base64 TEXT,
                logo_mime TEXT,
                logo_filename TEXT,
                observacoes TEXT,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        ensure_column(conn, "empresa_config", "app_title", "TEXT NOT NULL DEFAULT 'Orçamentos de Pintura'")
        ensure_column(conn, "empresa_config", "app_short_name", "TEXT NOT NULL DEFAULT 'Orçamentos'")
        ensure_column(conn, "empresa_config", "website", "TEXT")
        ensure_column(conn, "empresa_config", "instagram", "TEXT")
        ensure_column(conn, "empresa_config", "logo_base64", "TEXT")
        ensure_column(conn, "empresa_config", "logo_mime", "TEXT")
        ensure_column(conn, "empresa_config", "logo_filename", "TEXT")

        ensure_admin_user(conn)

        total_empresa = conn.execute("SELECT COUNT(*) AS total FROM empresa_config").fetchone()["total"]
        if total_empresa == 0:
            conn.execute(
                """
                INSERT INTO empresa_config (
                    id,
                    nome_fantasia,
                    app_title,
                    app_short_name,
                    razao_social,
                    cnpj,
                    telefone,
                    email,
                    endereco,
                    cidade_estado,
                    website,
                    instagram,
                    logo_base64,
                    logo_mime,
                    logo_filename,
                    observacoes
                )
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "Edilson Pinturas",
                    "Orçamentos de Pintura",
                    "Orçamentos",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "Atualize os dados da empresa na página Configurações.",
                ),
            )
        conn.commit()


def seed_sample_data() -> bool:
    with closing(get_connection()) as conn:
        total_produtos = conn.execute("SELECT COUNT(*) AS total FROM produtos").fetchone()["total"]
        total_clientes = conn.execute("SELECT COUNT(*) AS total FROM clientes").fetchone()["total"]

        inserted = False

        if total_produtos == 0:
            produtos = [
                ("Tinta acrilica premium", "Tintas", "litro", 42.5, "Tinta para ambientes internos e externos.", 1),
                ("Massa corrida", "Preparacao", "galao", 68.0, "Correcao de imperfeicoes em paredes.", 1),
                ("Selador", "Preparacao", "litro", 29.9, "Selagem para melhor aderencia da tinta.", 1),
                ("Lixa", "Ferramentas", "unidade", 3.5, "Lixa para acabamento de superficie.", 1),
                ("Fita crepe", "Ferramentas", "unidade", 9.9, "Protecao de rodapes e batentes.", 1),
                ("Rolo de pintura", "Ferramentas", "unidade", 22.0, "Rolo anti-respingo.", 1),
                ("Pincel", "Ferramentas", "unidade", 15.0, "Pincel para recortes.", 1),
                ("Diaria de pintor", "Mao de obra", "diaria", 220.0, "Profissional principal da obra.", 1),
                ("Diaria de ajudante", "Mao de obra", "diaria", 140.0, "Apoio para preparacao e limpeza.", 1),
                ("Aplicacao de textura", "Servico especializado", "m2", 28.0, "Textura decorativa por metro quadrado.", 1),
                ("Pintura interna por m2", "Servico especializado", "m2", 18.0, "Aplicacao em ambientes internos.", 1),
                ("Pintura externa por m2", "Servico especializado", "m2", 24.0, "Aplicacao em fachadas e areas externas.", 1),
            ]
            conn.executemany(
                """
                INSERT INTO produtos (nome, categoria, unidade, preco_unitario, descricao, ativo)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                produtos,
            )
            inserted = True

        if total_clientes == 0:
            clientes = [
                ("Maria Oliveira", "(65) 99999-1111", "maria@email.com", "Rua das Flores, 120", "Cliente residencial."),
                ("Construtora Horizonte", "(65) 98888-2222", "contato@horizonte.com", "Av. Central, 455", "Obras comerciais."),
                ("Carlos Mendes", "(65) 97777-3333", "carlos@email.com", "Alameda Verde, 80", "Prefere contato por WhatsApp."),
            ]
            conn.executemany(
                """
                INSERT INTO clientes (nome, telefone, email, endereco, observacoes)
                VALUES (?, ?, ?, ?, ?)
                """,
                clientes,
            )
            inserted = True

        conn.commit()
        return inserted


def list_products(search: str = "", category: str = "", only_active: bool | None = None) -> list[dict]:
    query = "SELECT * FROM produtos WHERE 1=1"
    params: list = []

    if search:
        query += " AND nome LIKE ?"
        params.append(f"%{search.strip()}%")
    if category:
        query += " AND categoria = ?"
        params.append(category)
    if only_active is True:
        query += " AND ativo = 1"
    if only_active is False:
        query += " AND ativo = 0"

    query += " ORDER BY nome"

    with closing(get_connection()) as conn:
        return conn.execute(query, params).fetchall()


def get_product(product_id: int) -> dict | None:
    with closing(get_connection()) as conn:
        return conn.execute("SELECT * FROM produtos WHERE id = ?", (product_id,)).fetchone()


def get_product_categories() -> list[str]:
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT DISTINCT categoria FROM produtos WHERE categoria IS NOT NULL AND categoria <> '' ORDER BY categoria"
        ).fetchall()
    return [row["categoria"] for row in rows]


def create_product(data: dict) -> int:
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            """
            INSERT INTO produtos (nome, categoria, unidade, preco_unitario, descricao, ativo)
            VALUES (:nome, :categoria, :unidade, :preco_unitario, :descricao, :ativo)
            """,
            data,
        )
        conn.commit()
        return cursor.lastrowid


def update_product(product_id: int, data: dict) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            """
            UPDATE produtos
            SET nome = :nome,
                categoria = :categoria,
                unidade = :unidade,
                preco_unitario = :preco_unitario,
                descricao = :descricao,
                ativo = :ativo
            WHERE id = :id
            """,
            {**data, "id": product_id},
        )
        conn.commit()


def delete_product(product_id: int) -> None:
    with closing(get_connection()) as conn:
        conn.execute("DELETE FROM produtos WHERE id = ?", (product_id,))
        conn.commit()


def list_clients(search: str = "") -> list[dict]:
    query = "SELECT * FROM clientes WHERE 1=1"
    params: list = []

    if search:
        query += " AND nome LIKE ?"
        params.append(f"%{search.strip()}%")

    query += " ORDER BY nome"

    with closing(get_connection()) as conn:
        return conn.execute(query, params).fetchall()


def get_client(client_id: int) -> dict | None:
    with closing(get_connection()) as conn:
        return conn.execute("SELECT * FROM clientes WHERE id = ?", (client_id,)).fetchone()


def create_client(data: dict) -> int:
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            """
            INSERT INTO clientes (nome, telefone, email, endereco, observacoes)
            VALUES (:nome, :telefone, :email, :endereco, :observacoes)
            """,
            data,
        )
        conn.commit()
        return cursor.lastrowid


def update_client(client_id: int, data: dict) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            """
            UPDATE clientes
            SET nome = :nome,
                telefone = :telefone,
                email = :email,
                endereco = :endereco,
                observacoes = :observacoes
            WHERE id = :id
            """,
            {**data, "id": client_id},
        )
        conn.commit()


def delete_client(client_id: int) -> None:
    try:
        with closing(get_connection()) as conn:
            conn.execute("DELETE FROM clientes WHERE id = ?", (client_id,))
            conn.commit()
    except sqlite3.IntegrityError as exc:
        raise ValueError("Nao e possivel excluir clientes vinculados a orcamentos.") from exc


def get_next_quote_number() -> str:
    today_code = date.today().strftime("%Y%m%d")
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS total FROM orcamentos WHERE numero LIKE ?",
            (f"ORC-{today_code}-%",),
        ).fetchone()
    sequence = int(row["total"]) + 1
    return f"ORC-{today_code}-{sequence:03d}"


def create_orcamento(data: dict, itens: list[dict]) -> int:
    with closing(get_connection()) as conn:
        cursor = conn.execute(
            """
            INSERT INTO orcamentos (
                numero,
                cliente_id,
                data_orcamento,
                responsavel,
                status,
                subtotal,
                desconto_tipo,
                desconto_percentual,
                desconto_valor,
                taxa_adicional,
                total_final,
                observacoes,
                validade,
                metragem_total,
                prazo_execucao,
                forma_pagamento
            )
            VALUES (
                :numero,
                :cliente_id,
                :data_orcamento,
                :responsavel,
                :status,
                :subtotal,
                :desconto_tipo,
                :desconto_percentual,
                :desconto_valor,
                :taxa_adicional,
                :total_final,
                :observacoes,
                :validade,
                :metragem_total,
                :prazo_execucao,
                :forma_pagamento
            )
            """,
            data,
        )
        orcamento_id = cursor.lastrowid

        conn.executemany(
            """
            INSERT INTO orcamento_itens (
                orcamento_id,
                produto_id,
                item_nome,
                categoria,
                unidade,
                quantidade,
                valor_unitario,
                subtotal,
                observacoes
            )
            VALUES (
                :orcamento_id,
                :produto_id,
                :item_nome,
                :categoria,
                :unidade,
                :quantidade,
                :valor_unitario,
                :subtotal,
                :observacoes
            )
            """,
            [{**item, "orcamento_id": orcamento_id} for item in itens],
        )
        conn.commit()
        return orcamento_id


def list_orcamentos(
    search: str = "",
    status: str = "",
    data_inicio: str = "",
    data_fim: str = "",
) -> list[dict]:
    query = """
        SELECT
            o.id,
            o.numero,
            o.data_orcamento,
            o.status,
            o.total_final,
            c.nome AS cliente_nome
        FROM orcamentos o
        INNER JOIN clientes c ON c.id = o.cliente_id
        WHERE 1=1
    """
    params: list = []

    if search:
        query += " AND c.nome LIKE ?"
        params.append(f"%{search.strip()}%")
    if status:
        query += " AND o.status = ?"
        params.append(status)
    if data_inicio:
        query += " AND o.data_orcamento >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND o.data_orcamento <= ?"
        params.append(data_fim)

    query += " ORDER BY o.data_orcamento DESC, o.id DESC"

    with closing(get_connection()) as conn:
        return conn.execute(query, params).fetchall()


def get_orcamento(orcamento_id: int) -> dict | None:
    with closing(get_connection()) as conn:
        orcamento = conn.execute(
            """
            SELECT
                o.*,
                c.nome AS cliente_nome,
                c.telefone AS cliente_telefone,
                c.email AS cliente_email,
                c.endereco AS cliente_endereco,
                c.observacoes AS cliente_observacoes
            FROM orcamentos o
            INNER JOIN clientes c ON c.id = o.cliente_id
            WHERE o.id = ?
            """,
            (orcamento_id,),
        ).fetchone()

        if not orcamento:
            return None

        itens = conn.execute(
            """
            SELECT *
            FROM orcamento_itens
            WHERE orcamento_id = ?
            ORDER BY id
            """,
            (orcamento_id,),
        ).fetchall()

        orcamento["itens"] = itens
        return orcamento


def update_orcamento_status(orcamento_id: int, status: str) -> None:
    with closing(get_connection()) as conn:
        conn.execute("UPDATE orcamentos SET status = ? WHERE id = ?", (status, orcamento_id))
        conn.commit()


def delete_orcamento(orcamento_id: int) -> None:
    with closing(get_connection()) as conn:
        conn.execute("DELETE FROM orcamentos WHERE id = ?", (orcamento_id,))
        conn.commit()


def get_dashboard_metrics() -> dict:
    with closing(get_connection()) as conn:
        total_produtos = conn.execute("SELECT COUNT(*) AS total FROM produtos").fetchone()["total"]
        total_clientes = conn.execute("SELECT COUNT(*) AS total FROM clientes").fetchone()["total"]
        total_orcamentos = conn.execute("SELECT COUNT(*) AS total FROM orcamentos").fetchone()["total"]
        valor_total = conn.execute("SELECT COALESCE(SUM(total_final), 0) AS total FROM orcamentos").fetchone()["total"]
        aprovados = conn.execute(
            "SELECT COUNT(*) AS total FROM orcamentos WHERE status = 'Aprovado'"
        ).fetchone()["total"]
        recusados = conn.execute(
            "SELECT COUNT(*) AS total FROM orcamentos WHERE status = 'Recusado'"
        ).fetchone()["total"]

    return {
        "total_produtos": total_produtos,
        "total_clientes": total_clientes,
        "total_orcamentos": total_orcamentos,
        "valor_total_orcado": float(valor_total or 0),
        "orcamentos_aprovados": aprovados,
        "orcamentos_recusados": recusados,
    }


def get_recent_orcamentos(limit: int = 5) -> list[dict]:
    with closing(get_connection()) as conn:
        return conn.execute(
            """
            SELECT
                o.numero,
                o.data_orcamento,
                o.status,
                o.total_final,
                c.nome AS cliente_nome
            FROM orcamentos o
            INNER JOIN clientes c ON c.id = o.cliente_id
            ORDER BY o.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def get_user_by_username(username: str) -> dict | None:
    with closing(get_connection()) as conn:
        return conn.execute(
            "SELECT * FROM usuarios WHERE username = ? AND ativo = 1",
            (username.strip(),),
        ).fetchone()


def update_user_password(user_id: int, password_hash: str) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            "UPDATE usuarios SET password_hash = ? WHERE id = ?",
            (password_hash, user_id),
        )
        conn.commit()


def get_company_info() -> dict:
    with closing(get_connection()) as conn:
        company = conn.execute("SELECT * FROM empresa_config WHERE id = 1").fetchone()
    return company or {
        "id": 1,
        "nome_fantasia": "Empresa de Pintura",
        "app_title": "Orçamentos de Pintura",
        "app_short_name": "Orçamentos",
        "razao_social": "",
        "cnpj": "",
        "telefone": "",
        "email": "",
        "endereco": "",
        "cidade_estado": "",
        "website": "",
        "instagram": "",
        "logo_base64": "",
        "logo_mime": "",
        "logo_filename": "",
        "observacoes": "",
    }


def upsert_company_info(data: dict) -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            """
            INSERT INTO empresa_config (
                id,
                nome_fantasia,
                app_title,
                app_short_name,
                razao_social,
                cnpj,
                telefone,
                email,
                endereco,
                cidade_estado,
                website,
                instagram,
                logo_base64,
                logo_mime,
                logo_filename,
                observacoes,
                updated_at
            )
            VALUES (
                1,
                :nome_fantasia,
                :app_title,
                :app_short_name,
                :razao_social,
                :cnpj,
                :telefone,
                :email,
                :endereco,
                :cidade_estado,
                :website,
                :instagram,
                :logo_base64,
                :logo_mime,
                :logo_filename,
                :observacoes,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT(id) DO UPDATE SET
                nome_fantasia = excluded.nome_fantasia,
                app_title = excluded.app_title,
                app_short_name = excluded.app_short_name,
                razao_social = excluded.razao_social,
                cnpj = excluded.cnpj,
                telefone = excluded.telefone,
                email = excluded.email,
                endereco = excluded.endereco,
                cidade_estado = excluded.cidade_estado,
                website = excluded.website,
                instagram = excluded.instagram,
                logo_base64 = excluded.logo_base64,
                logo_mime = excluded.logo_mime,
                logo_filename = excluded.logo_filename,
                observacoes = excluded.observacoes,
                updated_at = CURRENT_TIMESTAMP
            """,
            data,
        )
        conn.commit()

----- models.py -----
from dataclasses import dataclass, field
from typing import List


CATEGORIAS_PADRAO = [
    "Tintas",
    "Preparação",
    "Ferramentas",
    "Mão de obra",
    "Acabamento",
    "Serviço especializado",
]

UNIDADES_PADRAO = [
    "litro",
    "galao",
    "metro",
    "m2",
    "unidade",
    "diaria",
    "kit",
]

STATUS_ORCAMENTO = ["Rascunho", "Aprovado", "Recusado"]
TIPOS_DESCONTO = ["Nenhum", "Percentual", "Valor fixo"]


@dataclass
class Produto:
    nome: str = ""
    categoria: str = ""
    unidade: str = ""
    preco_unitario: float = 0.0
    descricao: str = ""
    ativo: bool = True


@dataclass
class Cliente:
    nome: str = ""
    telefone: str = ""
    email: str = ""
    endereco: str = ""
    observacoes: str = ""


@dataclass
class OrcamentoItem:
    produto_id: int | None = None
    item_nome: str = ""
    categoria: str = ""
    unidade: str = ""
    quantidade: float = 1.0
    valor_unitario: float = 0.0
    subtotal: float = 0.0
    observacoes: str = ""


@dataclass
class Orcamento:
    cliente_id: int | None = None
    data_orcamento: str = ""
    responsavel: str = ""
    status: str = "Rascunho"
    validade: str = ""
    observacoes: str = ""
    metragem_total: float = 0.0
    prazo_execucao: str = ""
    forma_pagamento: str = ""
    subtotal: float = 0.0
    desconto_tipo: str = "Nenhum"
    desconto_percentual: float = 0.0
    desconto_valor: float = 0.0
    taxa_adicional: float = 0.0
    total_final: float = 0.0
    itens: List[OrcamentoItem] = field(default_factory=list)

----- utils.py -----
from __future__ import annotations

import base64
import html
import json
from datetime import date, timedelta
from io import BytesIO
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from database import get_company_info, get_user_by_username
from services.auth import verify_password


STATUS_COLORS = {
    "Rascunho": "#6b7280",
    "Aprovado": "#22c55e",
    "Recusado": "#ef4444",
}
AUTH_SESSION_KEY = "auth_user"
DEFAULT_APP_TITLE = "Orçamentos de Pintura"
DEFAULT_APP_SHORT_NAME = "Orçamentos"


def configure_page(page_title: str) -> None:
    st.set_page_config(
        page_title=f"{page_title} | {DEFAULT_APP_TITLE}",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def safe_text(value: str | None, fallback: str = "-") -> str:
    text = (value or "").strip()
    return text if text else fallback


def currency(value: float | int | None) -> str:
    number = float(value or 0)
    formatted = f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def get_logo_bytes(company_info: dict | None = None) -> bytes | None:
    company = company_info or get_company_info()
    logo_base64 = (company.get("logo_base64") or "").strip()
    if not logo_base64:
        return None
    try:
        return base64.b64decode(logo_base64)
    except Exception:
        return None


def get_logo_data_uri(company_info: dict | None = None) -> str:
    company = company_info or get_company_info()
    logo_base64 = (company.get("logo_base64") or "").strip()
    logo_mime = safe_text(company.get("logo_mime"), "image/png")
    if not logo_base64:
        return ""
    return f"data:{logo_mime};base64,{logo_base64}"


def get_app_title(company_info: dict | None = None) -> str:
    company = company_info or get_company_info()
    return safe_text(company.get("app_title") or company.get("nome_fantasia"), DEFAULT_APP_TITLE)


def get_app_short_name(company_info: dict | None = None) -> str:
    company = company_info or get_company_info()
    return safe_text(company.get("app_short_name") or company.get("nome_fantasia"), DEFAULT_APP_SHORT_NAME)


def inject_custom_css(page_title: str) -> None:
    company = get_company_info()
    full_title = f"{page_title} | {get_app_title(company)}"
    app_short_name = get_app_short_name(company)
    logo_data_uri = get_logo_data_uri(company)

    st.markdown(
        """
        <style>
            :root {
                --bg-top: #ffffff;
                --bg-bottom: #f7f9fc;
                --surface: #ffffff;
                --surface-muted: #f0f2f6;
                --surface-strong: #fff1f1;
                --border: #e3e7ef;
                --border-strong: #d4dae5;
                --text-main: #262730;
                --text-soft: #31333f;
                --text-muted: #6c7383;
                --brand: #ff4b4b;
                --brand-strong: #e03e3e;
                --brand-deep: #bf2f2f;
                --sidebar-top: #f7f9fc;
                --sidebar-bottom: #eef2f7;
                --sidebar-text: #262730;
                --sidebar-muted: #6c7383;
                --shadow-soft: 0 14px 30px rgba(31, 41, 55, 0.08);
            }
            .stApp {
                background:
                    radial-gradient(circle at top right, rgba(255, 75, 75, 0.10), transparent 28%),
                    linear-gradient(180deg, var(--bg-top) 0%, #fbfcfe 20%, var(--bg-bottom) 100%);
                color: var(--text-main);
                font-family: "Trebuchet MS", "Segoe UI", sans-serif;
            }
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, var(--sidebar-top) 0%, var(--sidebar-bottom) 100%);
                border-right: 1px solid var(--border);
            }
            [data-testid="stSidebar"] * {
                color: var(--sidebar-text);
            }
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
                color: var(--sidebar-muted);
            }
            [data-testid="stSidebar"] [data-testid="stButton"] > button {
                background: transparent;
                border: 1px solid transparent;
                color: var(--sidebar-text);
                box-shadow: none;
            }
            [data-testid="stSidebar"] [data-testid="stButton"] > button *,
            [data-testid="stSidebar"] [data-testid="stButton"] > button p,
            [data-testid="stSidebar"] [data-testid="stButton"] > button span {
                color: var(--sidebar-text) !important;
                -webkit-text-fill-color: var(--sidebar-text) !important;
            }
            [data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
                background: rgba(255, 75, 75, 0.08);
                border-color: rgba(255, 75, 75, 0.15);
            }
            [data-testid="stSidebarNav"] {
                background: transparent;
                padding-top: 0.25rem;
            }
            [data-testid="stSidebarNav"] a {
                border-radius: 14px;
                margin-bottom: 0.25rem;
            }
            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                max-width: 1400px;
            }
            h1, h2, h3, h4, h5, h6 {
                color: var(--text-main);
            }
            p, li, label, .stCaption, .stMarkdown, .stText {
                color: var(--text-soft);
            }
            [data-testid="stForm"],
            [data-testid="stVerticalBlock"] > [data-testid="stContainer"] {
                color: var(--text-main);
            }
            [data-testid="stMetric"],
            [data-testid="stDataFrame"],
            [data-testid="stExpander"],
            [data-testid="stForm"] {
                border-radius: 16px;
            }
            [data-testid="stForm"] {
                background: rgba(255, 255, 255, 0.96);
                border: 1px solid rgba(216, 219, 225, 0.95);
                padding: 1rem;
                box-shadow: var(--shadow-soft);
            }
            div[data-baseweb="input"] > div,
            div[data-baseweb="select"] > div,
            div[data-baseweb="textarea"] > div,
            [data-testid="stDateInputField"] {
                background: var(--surface);
                border: 1px solid var(--border-strong);
                border-radius: 12px;
                color: var(--text-main);
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.45);
            }
            div[data-baseweb="input"] input,
            div[data-baseweb="textarea"] textarea,
            div[data-baseweb="select"] input {
                color: var(--text-main) !important;
                -webkit-text-fill-color: var(--text-main) !important;
                font-weight: 500;
            }
            div[data-baseweb="input"] > div:focus-within,
            div[data-baseweb="select"] > div:focus-within,
            div[data-baseweb="textarea"] > div:focus-within,
            [data-testid="stDateInputField"]:focus-within {
                border-color: var(--brand);
                box-shadow: 0 0 0 2px rgba(255, 75, 75, 0.18);
            }
            .stButton > button,
            .stDownloadButton > button,
            [data-testid="stLinkButton"] a {
                background: linear-gradient(180deg, var(--brand) 0%, var(--brand-strong) 100%);
                color: #ffffff;
                border: 1px solid var(--brand-strong);
                border-radius: 12px;
                font-weight: 600;
                box-shadow: 0 6px 14px rgba(255, 75, 75, 0.18);
            }
            .stButton > button *,
            .stButton > button p,
            .stButton > button span,
            .stButton > button [data-testid="stMarkdownContainer"] p,
            .stDownloadButton > button *,
            .stDownloadButton > button p,
            .stDownloadButton > button span,
            .stDownloadButton > button [data-testid="stMarkdownContainer"] p,
            [data-testid="stLinkButton"] a,
            [data-testid="stLinkButton"] a *,
            [data-testid="stLinkButton"] a p,
            [data-testid="stLinkButton"] a span,
            [data-testid="stLinkButton"] a [data-testid="stMarkdownContainer"] p {
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                text-decoration: none !important;
            }
            .stButton > button:hover,
            .stDownloadButton > button:hover,
            [data-testid="stLinkButton"] a:hover {
                background: linear-gradient(180deg, #ff6b6b 0%, #e03e3e 100%);
                border-color: #d13737;
                color: #ffffff;
            }
            .stButton > button[kind="secondary"],
            [data-testid="stLinkButton"] a[kind="secondary"] {
                background: var(--surface-muted);
                color: var(--text-main);
                border: 1px solid var(--border);
                box-shadow: none;
            }
            .stButton > button[kind="secondary"] *,
            .stButton > button[kind="secondary"] p,
            .stButton > button[kind="secondary"] span,
            .stButton > button[kind="secondary"] [data-testid="stMarkdownContainer"] p {
                color: var(--text-main) !important;
                -webkit-text-fill-color: var(--text-main) !important;
            }
            [data-testid="stAlert"] {
                border-radius: 14px;
                border-width: 1px;
            }
            [data-testid="stDataFrame"] {
                background: var(--surface);
                border: 1px solid var(--border);
                box-shadow: var(--shadow-soft);
            }
            [data-testid="stTable"] {
                color: var(--text-main);
            }
            [data-testid="stExpander"] {
                background: rgba(255, 255, 255, 0.96);
                border: 1px solid rgba(216, 219, 225, 0.9);
                box-shadow: var(--shadow-soft);
            }
            [data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.98);
                border: 1px solid rgba(216, 219, 225, 0.95);
                padding: 0.25rem 0.35rem;
            }
            .page-header {
                position: relative;
                overflow: hidden;
                background:
                    radial-gradient(circle at top right, rgba(255, 255, 255, 0.18), transparent 24%),
                    linear-gradient(135deg, #992d2d 0%, var(--brand-deep) 28%, var(--brand) 100%);
                color: #ffffff;
                border-radius: 24px;
                padding: 1.6rem 1.8rem;
                margin-bottom: 1.2rem;
                box-shadow: 0 18px 44px rgba(255, 75, 75, 0.22);
            }
            .page-header::after {
                content: "";
                position: absolute;
                inset: auto -60px -70px auto;
                width: 200px;
                height: 200px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.12);
            }
            .page-header__content {
                position: relative;
                z-index: 1;
            }
            .page-header__eyebrow {
                margin: 0 0 0.35rem 0;
                font-size: 0.82rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: rgba(255, 255, 255, 0.78);
            }
            .page-header__title-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
                flex-wrap: wrap;
            }
            .page-header__title-row h1 {
                margin: 0;
                color: #ffffff;
                font-size: 2rem;
                line-height: 1.1;
            }
            .page-header__description {
                margin: 0.55rem 0 0 0;
                max-width: 760px;
                color: rgba(255, 255, 255, 0.88);
                font-size: 1rem;
            }
            .page-header__badge {
                display: inline-flex;
                align-items: center;
                border-radius: 999px;
                padding: 0.45rem 0.85rem;
                background: rgba(255, 255, 255, 0.16);
                border: 1px solid rgba(255, 255, 255, 0.18);
                color: #ffffff;
                font-size: 0.82rem;
                font-weight: 700;
                backdrop-filter: blur(6px);
            }
            .section-header {
                margin: 0.2rem 0 0.75rem 0;
            }
            .section-header h3 {
                margin: 0;
                font-size: 1.1rem;
            }
            .section-header__description {
                margin: 0.25rem 0 0 0;
                color: var(--text-muted);
                font-size: 0.93rem;
            }
            .hero-box {
                background: linear-gradient(135deg, var(--brand-deep) 0%, var(--brand) 100%);
                color: #ffffff;
                border-radius: 18px;
                padding: 1.4rem 1.6rem;
                margin-bottom: 1rem;
                box-shadow: 0 16px 36px rgba(255, 75, 75, 0.22);
            }
            .metric-card {
                background: var(--surface);
                border: 1px solid rgba(216, 219, 225, 0.95);
                border-radius: 16px;
                padding: 1rem 1.1rem;
                box-shadow: var(--shadow-soft);
                min-height: 118px;
            }
            .metric-label {
                color: var(--text-muted);
                font-size: 0.92rem;
                margin-bottom: 0.35rem;
            }
            .metric-value {
                color: var(--text-main);
                font-size: 1.85rem;
                font-weight: 700;
                line-height: 1.15;
                margin-bottom: 0.25rem;
            }
            .metric-help {
                color: var(--text-muted);
                font-size: 0.85rem;
            }
            .section-card {
                background: var(--surface);
                border: 1px solid rgba(216, 219, 225, 0.95);
                border-radius: 16px;
                padding: 1rem 1.1rem;
                margin-bottom: 1rem;
                box-shadow: var(--shadow-soft);
            }
            .info-card {
                background: linear-gradient(180deg, #ffffff 0%, #fff7f7 100%);
                border: 1px solid rgba(255, 75, 75, 0.12);
                border-radius: 16px;
                padding: 1rem 1.1rem;
                box-shadow: var(--shadow-soft);
                min-height: 118px;
            }
            .info-card__title {
                color: var(--text-muted);
                font-size: 0.86rem;
                margin-bottom: 0.35rem;
            }
            .info-card__value {
                color: var(--text-main);
                font-size: 1.35rem;
                font-weight: 700;
                line-height: 1.2;
            }
            .info-card__helper {
                margin: 0.4rem 0 0 0;
                color: var(--text-muted);
                font-size: 0.84rem;
            }
            .toolbar-card {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
                flex-wrap: wrap;
                background: rgba(255, 255, 255, 0.78);
                border: 1px solid var(--border);
                border-radius: 16px;
                padding: 0.8rem 1rem;
                margin-bottom: 0.8rem;
                box-shadow: var(--shadow-soft);
            }
            .toolbar-card strong {
                color: var(--text-main);
            }
            .toolbar-card span {
                color: var(--text-muted);
                font-size: 0.9rem;
            }
            .empty-state {
                text-align: center;
                padding: 1.4rem 1.2rem;
                border-radius: 18px;
                border: 1px dashed rgba(255, 75, 75, 0.25);
                background: rgba(255, 255, 255, 0.75);
                box-shadow: var(--shadow-soft);
            }
            .empty-state h4 {
                margin: 0;
            }
            .empty-state p {
                margin: 0.4rem 0 0 0;
                color: var(--text-muted);
            }
            .login-shell {
                max-width: 980px;
                margin: 3.5rem auto 0 auto;
            }
            .login-panel {
                background:
                    radial-gradient(circle at top right, rgba(255, 255, 255, 0.18), transparent 26%),
                    linear-gradient(135deg, #992d2d 0%, var(--brand-deep) 28%, var(--brand) 100%);
                border-radius: 28px;
                padding: 2rem;
                box-shadow: 0 24px 48px rgba(255, 75, 75, 0.20);
                color: #ffffff;
                min-height: 100%;
            }
            .login-panel h1 {
                color: #ffffff;
                margin: 0 0 0.5rem 0;
                font-size: 2rem;
                line-height: 1.05;
            }
            .login-panel p {
                color: rgba(255, 255, 255, 0.86);
                margin: 0;
                line-height: 1.6;
            }
            .login-panel__eyebrow {
                display: inline-block;
                margin-bottom: 0.85rem;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: rgba(255, 255, 255, 0.76);
            }
            .login-meta {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.8rem;
                margin-top: 1.35rem;
            }
            .login-meta__item {
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 16px;
                padding: 0.9rem 1rem;
            }
            .login-meta__label {
                display: block;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                color: rgba(255, 255, 255, 0.72);
                margin-bottom: 0.3rem;
            }
            .login-meta__value {
                color: #ffffff;
                font-size: 0.96rem;
                font-weight: 600;
            }
            .login-card {
                background: rgba(255, 255, 255, 0.97);
                border: 1px solid var(--border);
                border-radius: 24px;
                padding: 1.6rem;
                box-shadow: var(--shadow-soft);
            }
            .login-card__header {
                margin-bottom: 1rem;
            }
            .login-card__header h3 {
                margin: 0;
                font-size: 1.3rem;
            }
            .login-card__header p {
                margin: 0.35rem 0 0 0;
                color: var(--text-muted);
            }
            .sidebar-company-card,
            .sidebar-user-card {
                background: rgba(255, 255, 255, 0.68);
                border: 1px solid rgba(219, 202, 183, 0.95);
                border-radius: 18px;
                padding: 0.95rem 1rem;
                box-shadow: 0 12px 24px rgba(82, 89, 109, 0.08);
                margin-bottom: 0.8rem;
            }
            .sidebar-company-card h3,
            .sidebar-user-card h4 {
                margin: 0;
                color: var(--text-main);
            }
            .sidebar-company-card p,
            .sidebar-user-card p {
                margin: 0.3rem 0 0 0;
                color: var(--text-muted);
                font-size: 0.9rem;
                line-height: 1.5;
            }
            .sidebar-label {
                display: inline-block;
                margin-bottom: 0.35rem;
                color: var(--brand-strong);
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.06em;
                text-transform: uppercase;
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
                background: linear-gradient(180deg, #fff9f9 0%, var(--surface-strong) 100%);
                border: 1px solid rgba(255, 75, 75, 0.18);
                border-radius: 16px;
                padding: 1rem 1.2rem;
                color: var(--text-main);
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
            }
            @media (max-width: 900px) {
                .page-header {
                    padding: 1.35rem 1.1rem;
                }
                .page-header__title-row h1 {
                    font-size: 1.65rem;
                }
                .toolbar-card {
                    align-items: flex-start;
                }
                .login-shell {
                    margin-top: 1.5rem;
                }
                .login-panel,
                .login-card {
                    padding: 1.25rem;
                }
                .login-meta {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    components.html(
        f"""
        <script>
            const doc = window.parent.document;
            doc.documentElement.lang = "pt-BR";
            doc.title = {json.dumps(full_title)};

            const ensureMeta = (attr, name, content) => {{
                let tag = doc.head.querySelector(`meta[${{attr}}="${{name}}"]`);
                if (!tag) {{
                    tag = doc.createElement("meta");
                    tag.setAttribute(attr, name);
                    doc.head.appendChild(tag);
                }}
                tag.setAttribute("content", content);
            }};

            const ensureLink = (rel, href) => {{
                let tag = doc.head.querySelector(`link[rel="${{rel}}"]`);
                if (!tag) {{
                    tag = doc.createElement("link");
                    tag.setAttribute("rel", rel);
                    doc.head.appendChild(tag);
                }}
                tag.setAttribute("href", href);
            }};

            ensureMeta("name", "apple-mobile-web-app-title", {json.dumps(app_short_name)});
            ensureMeta("name", "application-name", {json.dumps(app_short_name)});
            ensureMeta("name", "theme-color", "#ff4b4b");

            const logo = {json.dumps(logo_data_uri or "")};
            if (logo) {{
                ensureLink("icon", logo);
                ensureLink("shortcut icon", logo);
                ensureLink("apple-touch-icon", logo);
            }}
        </script>
        """,
        height=0,
    )


def set_authenticated_user(user: dict) -> None:
    st.session_state[AUTH_SESSION_KEY] = {
        "id": user["id"],
        "nome": user["nome"],
        "username": user["username"],
    }


def logout() -> None:
    if AUTH_SESSION_KEY in st.session_state:
        del st.session_state[AUTH_SESSION_KEY]
    st.rerun()


def ensure_authenticated(page_title: str) -> dict:
    auth_user = st.session_state.get(AUTH_SESSION_KEY)
    if auth_user:
        return auth_user

    company = get_company_info()
    logo_bytes = get_logo_bytes(company)

    company_name = safe_text(company.get("nome_fantasia"), "Empresa")
    company_phone = safe_text(company.get("telefone"), "Nao informado")
    company_email = safe_text(company.get("email"), "Nao informado")

    st.markdown(
        """
        <style>
            [data-testid="stSidebar"],
            [data-testid="collapsedControl"] {
                display: none !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    components.html(
        """
        <script>
            const doc = window.parent.document;
            const sidebar = doc.querySelector('[data-testid="stSidebar"]');
            const collapsed = doc.querySelector('[data-testid="collapsedControl"]');
            if (sidebar) sidebar.style.display = 'none';
            if (collapsed) collapsed.style.display = 'none';
        </script>
        """,
        height=0,
    )

    info_col, form_col = st.columns([1.1, 0.95], gap="large")
    with info_col:
        st.markdown(
            f"""
            <section class="login-shell">
                <div class="login-panel">
                    <span class="login-panel__eyebrow">Acesso seguro</span>
                    <h1>Sistema de orcamentos</h1>
                    <p>Controle clientes, servicos e propostas comerciais com uma experiencia administrativa consistente e profissional.</p>
                    <div class="login-meta">
                        <div class="login-meta__item">
                            <span class="login-meta__label">Empresa</span>
                            <span class="login-meta__value">{html.escape(company_name)}</span>
                        </div>
                        <div class="login-meta__item">
                            <span class="login-meta__label">Pagina</span>
                            <span class="login-meta__value">{html.escape(page_title)}</span>
                        </div>
                        <div class="login-meta__item">
                            <span class="login-meta__label">Telefone</span>
                            <span class="login-meta__value">{html.escape(company_phone)}</span>
                        </div>
                        <div class="login-meta__item">
                            <span class="login-meta__label">Email</span>
                            <span class="login-meta__value">{html.escape(company_email)}</span>
                        </div>
                    </div>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
    with form_col:
        st.markdown(
            """
            <section class="login-shell">
                <div class="login-card">
                    <div class="login-card__header">
                        <h3>Entrar no sistema</h3>
                        <p>Use suas credenciais para acessar o ambiente administrativo.</p>
                    </div>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        with st.container(border=True):
            if logo_bytes:
                st.image(logo_bytes, width=120)
            st.subheader(safe_text(company.get("nome_fantasia"), "Empresa"))
            st.caption(f"Entre para acessar a página {page_title.lower()}.")
            with st.form("form_login"):
                username = st.text_input("Login")
                password = st.text_input("Senha", type="password")
                submit = st.form_submit_button("Entrar", use_container_width=True)

            if submit:
                user = get_user_by_username(username)
                if not user or not verify_password(password, user["password_hash"]):
                    st.error("Login ou senha inválidos.")
                else:
                    set_authenticated_user(user)
                    st.rerun()


    st.stop()


def render_sidebar_branding(page_title: str) -> None:
    company = get_company_info()
    logo_bytes = get_logo_bytes(company)
    auth_user = st.session_state.get(AUTH_SESSION_KEY, {})

    with st.sidebar:
        if logo_bytes:
            st.image(logo_bytes, width=128)
        company_details = []
        if company.get("cnpj"):
            company_details.append(f"CNPJ: {company['cnpj']}")
        if company.get("telefone"):
            company_details.append(f"Tel.: {company['telefone']}")
        details_text = " | ".join(company_details) if company_details else "Sistema administrativo de orcamentos"

        st.markdown(
            f"""
            <div class="sidebar-company-card">
                <span class="sidebar-label">Empresa</span>
                <h3>{html.escape(safe_text(company.get("nome_fantasia"), "Empresa"))}</h3>
                <p>{html.escape(page_title)}</p>
                <p>{html.escape(details_text)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="sidebar-user-card">
                <span class="sidebar-label">Sessao</span>
                <h4>{html.escape(safe_text(auth_user.get("nome"), "Administrador"))}</h4>
                <p>Login: {html.escape(safe_text(auth_user.get("username"), "admin"))}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(f"**Usuário:** {safe_text(auth_user.get('nome'), 'Administrador')}")
        st.caption("Use o menu lateral para navegar entre dashboard, cadastros, orcamentos e configuracoes.")
        if st.button("Sair", use_container_width=True):
            logout()


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


def _company_detail_lines(company: dict) -> list[str]:
    lines = [safe_text(company.get("nome_fantasia"), "Empresa")]
    if company.get("razao_social"):
        lines.append(company["razao_social"])
    if company.get("cnpj"):
        lines.append(f"CNPJ: {company['cnpj']}")

    contact_parts = []
    if company.get("telefone"):
        contact_parts.append(company["telefone"])
    if company.get("email"):
        contact_parts.append(company["email"])
    if contact_parts:
        lines.append(" | ".join(contact_parts))

    address_parts = [safe_text(company.get("endereco"), ""), safe_text(company.get("cidade_estado"), "")]
    address_line = " - ".join([part for part in address_parts if part])
    if address_line:
        lines.append(address_line)

    web_parts = []
    if company.get("website"):
        web_parts.append(company["website"])
    if company.get("instagram"):
        web_parts.append(company["instagram"])
    if web_parts:
        lines.append(" | ".join(web_parts))

    return [line for line in lines if line and line != "-"]


def _company_details_html(company: dict) -> str:
    return "<br />".join(html.escape(line) for line in _company_detail_lines(company))


def build_quote_html(orcamento: dict) -> str:
    company = get_company_info()
    logo_data_uri = get_logo_data_uri(company)
    logo_html = (
        f'<img src="{logo_data_uri}" alt="Logo da empresa" style="max-width:90px; max-height:90px; border-radius:14px;" />'
        if logo_data_uri
        else ""
    )

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
    <html lang="pt-BR">
        <head>
            <meta charset="utf-8" />
            <meta http-equiv="Content-Language" content="pt-BR" />
            <title>{html.escape(orcamento.get("numero", "Orçamento"))}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #1c1e21;
                    margin: 24px;
                }}
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    border-bottom: 2px solid #ff4b4b;
                    padding-bottom: 12px;
                    margin-bottom: 18px;
                    gap: 20px;
                }}
                .brand {{
                    display: flex;
                    gap: 14px;
                    align-items: center;
                }}
                .title {{
                    color: #ff4b4b;
                    font-size: 26px;
                    font-weight: 700;
                    margin: 0 0 6px 0;
                }}
                .company-name {{
                    color: #ff4b4b;
                    font-size: 20px;
                    font-weight: 700;
                    margin: 0 0 4px 0;
                }}
                .muted {{
                    color: #65676b;
                    line-height: 1.5;
                    font-size: 13px;
                }}
                .box {{
                    border: 1px solid #dadde1;
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
                    border: 1px solid #dadde1;
                    padding: 8px;
                    font-size: 13px;
                }}
                th {{
                    background: #f0f2f6;
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
                    color: #ff4b4b;
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
                <div class="brand">
                    {logo_html}
                    <div>
                        <p class="company-name">{html.escape(safe_text(company.get("nome_fantasia"), "Empresa"))}</p>
                        <div class="muted">{_company_details_html(company)}</div>
                    </div>
                </div>
                <div>
                    <p class="title">Orçamento de Pintura</p>
                    <div><strong>Número:</strong> {html.escape(orcamento.get("numero", ""))}</div>
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
                    <div><strong>Endereço:</strong> {html.escape(orcamento.get("cliente_endereco", "") or "-")}</div>
                </div>
                <div class="box">
                    <h3>Detalhes</h3>
                    <div><strong>Responsável:</strong> {html.escape(orcamento.get("responsavel", ""))}</div>
                    <div><strong>Metragem:</strong> {float(orcamento.get("metragem_total") or 0):,.2f} m2</div>
                    <div><strong>Prazo estimado:</strong> {html.escape(orcamento.get("prazo_execucao", "") or "-")}</div>
                    <div><strong>Pagamento:</strong> {html.escape(orcamento.get("forma_pagamento", "") or "-")}</div>
                </div>
            </div>

            <div class="box">
                <h3>Itens do orçamento</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th>Categoria</th>
                            <th>Unidade</th>
                            <th>Quantidade</th>
                            <th>Valor unitário</th>
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
                <h3>Observações</h3>
                <div>{html.escape(orcamento.get("observacoes", "") or "Sem observações adicionais.")}</div>
            </div>
        </body>
    </html>
    """


def _draw_company_logo(pdf: canvas.Canvas, company: dict, x: float, top_y: float, max_width: float, max_height: float) -> None:
    logo_bytes = get_logo_bytes(company)
    if not logo_bytes:
        return

    try:
        image = ImageReader(BytesIO(logo_bytes))
        img_width, img_height = image.getSize()
        scale = min(max_width / img_width, max_height / img_height)
        draw_width = img_width * scale
        draw_height = img_height * scale
        pdf.drawImage(
            image,
            x,
            top_y - draw_height,
            width=draw_width,
            height=draw_height,
            preserveAspectRatio=True,
            mask="auto",
        )
    except Exception:
        return


def build_quote_pdf(orcamento: dict) -> bytes:
    company = get_company_info()
    company_lines = _company_detail_lines(company)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left = 40
    right = width - 40
    y = height - 45

    def draw_page_header() -> float:
        nonlocal y
        header_height = 88
        pdf.setFillColor(colors.HexColor("#FF4B4B"))
        pdf.rect(0, height - header_height, width, header_height, fill=1, stroke=0)
        pdf.setFillColor(colors.white)
        _draw_company_logo(pdf, company, left, height - 12, 56, 56)
        text_x = left + (66 if get_logo_bytes(company) else 0)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(text_x, height - 28, safe_text(company.get("nome_fantasia"), "Empresa"))
        pdf.setFont("Helvetica", 10)
        pdf.drawString(text_x, height - 44, "Orçamento de Pintura")
        pdf.drawRightString(right, height - 28, safe_text(orcamento.get("numero")))
        pdf.drawRightString(right, height - 44, safe_text(orcamento.get("data_orcamento")))
        y = height - 108
        return y

    def ensure_space(minimum: float) -> None:
        nonlocal y
        if y < minimum:
            pdf.showPage()
            draw_page_header()

    def draw_label_value(label: str, value: str, pos_x: float, pos_y: float, offset: float = 70) -> None:
        pdf.setFillColor(colors.HexColor("#3A3B3C"))
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(pos_x, pos_y, f"{label}:")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(pos_x + offset, pos_y, safe_text(value))

    def draw_wrapped_text(text: str, pos_x: float, pos_y: float, max_width: int, line_height: int = 12) -> float:
        nonlocal y
        value = safe_text(text, "")
        if not value:
            return pos_y
        words = value.split()
        lines: list[str] = []
        current = ""
        for word in words:
            test_line = f"{current} {word}".strip()
            if pdf.stringWidth(test_line, "Helvetica", 10) <= max_width:
                current = test_line
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        for line in lines:
            ensure_space(80)
            pdf.drawString(pos_x, pos_y, line)
            pos_y -= line_height
            y = pos_y
        return pos_y

    desconto_label = orcamento.get("desconto_tipo", "Nenhum")
    desconto_valor = float(orcamento.get("desconto_valor") or 0)
    if desconto_label == "Percentual":
        desconto_valor = float(orcamento.get("subtotal") or 0) * (float(orcamento.get("desconto_percentual") or 0) / 100)

    draw_page_header()

    pdf.setFillColor(colors.HexColor("#1C1E21"))
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, y, "Dados da empresa")
    y -= 18
    pdf.setFont("Helvetica", 10)
    for line in company_lines:
        ensure_space(90)
        pdf.drawString(left, y, line)
        y -= 13
    y -= 8

    ensure_space(180)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, y, "Dados do cliente")
    y -= 18
    draw_label_value("Nome", safe_text(orcamento.get("cliente_nome")), left, y)
    y -= 14
    draw_label_value("Telefone", safe_text(orcamento.get("cliente_telefone")), left, y)
    y -= 14
    draw_label_value("Email", safe_text(orcamento.get("cliente_email")), left, y)
    y -= 14
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(left, y, "Endereço:")
    pdf.setFont("Helvetica", 10)
    y = draw_wrapped_text(safe_text(orcamento.get("cliente_endereco")), left + 70, y, 420)
    y -= 8

    ensure_space(170)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, y, "Dados do orçamento")
    y -= 18
    draw_label_value("Data", safe_text(orcamento.get("data_orcamento")), left, y)
    draw_label_value("Status", safe_text(orcamento.get("status")), 300, y)
    y -= 14
    draw_label_value("Responsável", safe_text(orcamento.get("responsavel")), left, y, offset=88)
    draw_label_value("Validade", safe_text(orcamento.get("validade")), 300, y)
    y -= 14
    draw_label_value("Pagamento", safe_text(orcamento.get("forma_pagamento")), left, y, offset=82)
    draw_label_value("Prazo", safe_text(orcamento.get("prazo_execucao")), 300, y)
    y -= 14
    draw_label_value("Metragem", f"{float(orcamento.get('metragem_total') or 0):,.2f} m2", left, y, offset=76)
    y -= 24

    ensure_space(180)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, y, "Itens")
    y -= 18

    header_y = y
    pdf.setFillColor(colors.HexColor("#F0F2F5"))
    pdf.rect(left, header_y - 4, right - left, 18, fill=1, stroke=0)
    pdf.setFillColor(colors.HexColor("#1C1E21"))
    pdf.setFont("Helvetica-Bold", 9)
    columns = [
        ("Item", left + 4),
        ("Qtd.", left + 215),
        ("Un.", left + 255),
        ("Vlr. unit.", left + 310),
        ("Subtotal", left + 395),
    ]
    for label, x_pos in columns:
        pdf.drawString(x_pos, header_y + 2, label)
    y -= 22

    pdf.setFont("Helvetica", 9)
    for item in orcamento.get("itens", []):
        ensure_space(90)
        item_nome = safe_text(item.get("item_nome"))
        quantidade = f"{float(item.get('quantidade') or 0):,.2f}"
        unidade = safe_text(item.get("unidade"))
        valor_unitario = currency(item.get("valor_unitario", 0))
        subtotal = currency(item.get("subtotal", 0))
        observacao = safe_text(item.get("observacoes"), "")

        name_lines = []
        current = ""
        for word in item_nome.split():
            test_line = f"{current} {word}".strip()
            if pdf.stringWidth(test_line, "Helvetica", 9) <= 200:
                current = test_line
            else:
                if current:
                    name_lines.append(current)
                current = word
        if current:
            name_lines.append(current)
        row_height = max(16, len(name_lines) * 12)
        if observacao:
            row_height += 12

        pdf.setStrokeColor(colors.HexColor("#DADDE1"))
        pdf.line(left, y - 4, right, y - 4)

        text_y = y
        for line in name_lines:
            pdf.drawString(left + 4, text_y, line)
            text_y -= 11
        if observacao:
            pdf.setFillColor(colors.HexColor("#65676B"))
            pdf.drawString(left + 4, text_y, f"Obs.: {observacao[:70]}")
            pdf.setFillColor(colors.HexColor("#1C1E21"))

        pdf.drawRightString(left + 248, y, quantidade)
        pdf.drawString(left + 258, y, unidade)
        pdf.drawRightString(left + 388, y, valor_unitario)
        pdf.drawRightString(right - 4, y, subtotal)
        y -= row_height

    y -= 10
    ensure_space(130)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawRightString(430, y, "Subtotal:")
    pdf.drawRightString(right, y, currency(orcamento.get("subtotal", 0)))
    y -= 14
    pdf.drawRightString(430, y, f"Desconto ({desconto_label}):")
    pdf.drawRightString(right, y, currency(desconto_valor))
    y -= 14
    pdf.drawRightString(430, y, "Taxa adicional:")
    pdf.drawRightString(right, y, currency(orcamento.get("taxa_adicional", 0)))
    y -= 18
    pdf.setFillColor(colors.HexColor("#FF4B4B"))
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawRightString(430, y, "Total final:")
    pdf.drawRightString(right, y, currency(orcamento.get("total_final", 0)))
    pdf.setFillColor(colors.HexColor("#1C1E21"))
    y -= 28

    ensure_space(100)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(left, y, "Observações")
    y -= 16
    pdf.setFont("Helvetica", 10)
    draw_wrapped_text(safe_text(orcamento.get("observacoes"), "Sem observações adicionais."), left, y, 500)

    pdf.save()
    return buffer.getvalue()


def build_share_message(orcamento: dict) -> str:
    company = get_company_info()
    company_name = safe_text(company.get("nome_fantasia"), "Empresa")
    return (
        f"{company_name}\n"
        f"Orçamento {safe_text(orcamento.get('numero'))}\n"
        f"Cliente: {safe_text(orcamento.get('cliente_nome'))}\n"
        f"Data: {safe_text(orcamento.get('data_orcamento'))}\n"
        f"Validade: {safe_text(orcamento.get('validade'))}\n"
        f"Status: {safe_text(orcamento.get('status'))}\n"
        f"Total final: {currency(orcamento.get('total_final', 0))}\n"
        f"Responsável: {safe_text(orcamento.get('responsavel'))}\n"
        f"Observações: {safe_text(orcamento.get('observacoes'), 'Sem observações adicionais.')}"
    )


def build_share_links(orcamento: dict) -> dict:
    company = get_company_info()
    company_name = safe_text(company.get("nome_fantasia"), "Empresa")
    message = build_share_message(orcamento)
    subject = quote(f"Orçamento {safe_text(orcamento.get('numero'))} - {company_name}")
    encoded_message = quote(message)
    phone_digits = "".join(char for char in safe_text(orcamento.get("cliente_telefone"), "") if char.isdigit())

    return {
        "email": f"mailto:{safe_text(orcamento.get('cliente_email'), '')}?subject={subject}&body={encoded_message}",
        "whatsapp": f"https://wa.me/{phone_digits}?text={encoded_message}" if phone_digits else "",
        "message": message,
    }

----- services\__init__.py -----
# Pacote de servicos do sistema.

----- services\auth.py -----
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets


PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 390_000
SALT_SIZE = 16


def _b64encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_SIZE)
    digest = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${_b64encode(salt)}${_b64encode(digest)}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        scheme, iterations, salt_b64, digest_b64 = stored_hash.split("$", 3)
    except ValueError:
        return False

    if scheme != f"pbkdf2_{PBKDF2_ALGORITHM}":
        return False

    candidate = hashlib.pbkdf2_hmac(
        PBKDF2_ALGORITHM,
        password.encode("utf-8"),
        _b64decode(salt_b64),
        int(iterations),
    )
    return hmac.compare_digest(candidate, _b64decode(digest_b64))

----- services\calculations.py -----
from __future__ import annotations

from typing import Iterable


def sanitize_money(value: float | int | None) -> float:
    if value is None:
        return 0.0
    return round(float(value), 2)


def calcular_subtotal_item(quantidade: float, valor_unitario: float) -> float:
    quantidade = max(0.0, float(quantidade or 0))
    valor_unitario = max(0.0, float(valor_unitario or 0))
    return round(quantidade * valor_unitario, 2)


def calcular_totais(
    itens: Iterable[dict],
    desconto_tipo: str = "Nenhum",
    desconto_percentual: float = 0.0,
    desconto_valor: float = 0.0,
    taxa_adicional: float = 0.0,
) -> dict:
    subtotal = round(sum(sanitize_money(item.get("subtotal", 0)) for item in itens), 2)
    taxa_adicional = max(0.0, sanitize_money(taxa_adicional))

    desconto_aplicado = 0.0
    desconto_percentual = max(0.0, sanitize_money(desconto_percentual))
    desconto_valor = max(0.0, sanitize_money(desconto_valor))

    if desconto_tipo == "Percentual" and subtotal > 0:
        desconto_aplicado = round(subtotal * (desconto_percentual / 100), 2)
    elif desconto_tipo == "Valor fixo":
        desconto_aplicado = min(subtotal, desconto_valor)

    total_final = max(0.0, round(subtotal - desconto_aplicado + taxa_adicional, 2))

    return {
        "subtotal": subtotal,
        "desconto_tipo": desconto_tipo,
        "desconto_percentual": desconto_percentual if desconto_tipo == "Percentual" else 0.0,
        "desconto_valor": desconto_aplicado if desconto_tipo == "Valor fixo" else 0.0,
        "desconto_aplicado": desconto_aplicado,
        "taxa_adicional": taxa_adicional,
        "total_final": total_final,
    }

----- pages\1_Produtos_e_Servicos.py -----
from __future__ import annotations

import streamlit as st

from components import render_data_hint, render_empty_state, render_page_header, render_section_header, setup_page
from database import create_product, delete_product, get_product, get_product_categories, list_products, update_product
from models import CATEGORIAS_PADRAO, UNIDADES_PADRAO
from utils import currency


PAGE_TITLE = "Produtos e Servicos"

setup_page(PAGE_TITLE)


def resolve_category(choice: str, custom_value: str) -> str:
    return custom_value.strip() if choice == "Outra" else choice


def resolve_unit(choice: str, custom_value: str) -> str:
    return custom_value.strip() if choice == "Outra" else choice


render_page_header(
    "Produtos e servicos",
    "Mantenha o catalogo da empresa organizado para acelerar a criacao de orcamentos e padronizar os valores usados pelo time.",
    eyebrow="Base comercial",
    badge="Cadastro central",
)

render_section_header("Novo item", "Cadastre materiais, servicos e mao de obra com categoria, unidade e status.")
with st.container(border=True):
    with st.form("form_novo_produto", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        nome = col1.text_input("Nome do produto/servico *")
        categoria_opcao = col2.selectbox("Categoria *", CATEGORIAS_PADRAO + ["Outra"])
        unidade_opcao = col3.selectbox("Unidade *", UNIDADES_PADRAO + ["Outra"])

        col4, col5, col6 = st.columns([1, 1, 2])
        preco_unitario = col4.number_input("Preco unitario *", min_value=0.0, step=1.0, format="%.2f")
        ativo = col5.toggle("Item ativo", value=True)
        descricao = col6.text_input("Descricao")

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

render_section_header("Consulta de itens", "Use os filtros para localizar itens do catalogo e carregar edicoes com rapidez.")
render_data_hint("Catalogo padronizado", "Categorias consistentes facilitam filtros, comparacoes e a montagem de novos orcamentos.")
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
                "Preco unitario": currency(item["preco_unitario"]),
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
        if st.button("Carregar para edicao", use_container_width=True):
            st.session_state["produto_edicao_id"] = selecionado_id
            st.rerun()
    with a2:
        confirmar = st.checkbox("Confirmar exclusao", key="confirmar_exclusao_produto")
        if st.button("Excluir item", use_container_width=True) and confirmar:
            delete_product(selecionado_id)
            st.success("Item excluido com sucesso.")
            if st.session_state.get("produto_edicao_id") == selecionado_id:
                del st.session_state["produto_edicao_id"]
            st.rerun()
    with a3:
        st.caption("A exclusao remove o item do cadastro. Orcamentos antigos preservam o historico do item.")
else:
    render_empty_state("Nenhum item encontrado", "Ajuste os filtros ou cadastre um novo item para iniciar o catalogo.")

produto_edicao_id = st.session_state.get("produto_edicao_id")
if produto_edicao_id:
    produto = get_product(produto_edicao_id)
    if produto:
        render_section_header("Editar item", "Atualize dados comerciais sem alterar o historico de orcamentos antigos.")
        categorias_edicao = CATEGORIAS_PADRAO + ["Outra"]
        unidades_edicao = UNIDADES_PADRAO + ["Outra"]

        categoria_inicial = produto["categoria"] if produto["categoria"] in CATEGORIAS_PADRAO else "Outra"
        unidade_inicial = produto["unidade"] if produto["unidade"] in UNIDADES_PADRAO else "Outra"

        with st.form("form_editar_produto"):
            e1, e2, e3 = st.columns(3)
            nome = e1.text_input("Nome do produto/servico *", value=produto["nome"])
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
                "Preco unitario *",
                min_value=0.0,
                value=float(produto["preco_unitario"]),
                step=1.0,
                format="%.2f",
            )
            ativo = e5.toggle("Item ativo", value=bool(produto["ativo"]))
            descricao = e6.text_input("Descricao", value=produto["descricao"] or "")

            categoria_custom = ""
            unidade_custom = ""
            if categoria_opcao == "Outra":
                categoria_custom = st.text_input("Nova categoria", value=produto["categoria"])
            if unidade_opcao == "Outra":
                unidade_custom = st.text_input("Nova unidade", value=produto["unidade"])

            save_col, cancel_col = st.columns(2)
            salvar = save_col.form_submit_button("Salvar alteracoes", use_container_width=True)
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

----- pages\2_Clientes.py -----
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

----- pages\3_Novo_Orcamento.py -----
from __future__ import annotations

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
from utils import currency, default_validity_date, init_quote_state, load_quote_into_state, reset_quote_state


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
    "Preencha os dados principais, adicione os itens do servico e revise os totais antes de salvar o documento.",
)

col_meta, col_itens = st.columns([1.15, 1.2], gap="large")

with col_meta:
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

with col_itens:
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

            subtotal_preview = calcular_subtotal_item(
                st.session_state["item_quantidade"], st.session_state["item_valor_unitario"]
            )
            render_data_hint("Preview do item", f"Subtotal atual: {currency(subtotal_preview)}")

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
            render_empty_state(
                "Nenhum item ativo encontrado",
                "Cadastre produtos ou servicos ativos antes de montar um novo orcamento.",
            )

render_section_header("Itens do orcamento", "Confira os itens adicionados e remova linhas quando necessario.")
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
    render_empty_state("Seu rascunho ainda nao tem itens", "Adicione pelo menos um item para liberar o salvamento do documento.")

render_section_header("Calculo automatico", "Desconto e taxa adicional sao aplicados automaticamente sobre o subtotal.")
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

----- pages\4_Orcamentos.py -----
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

----- pages\5_Configuracoes.py -----
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
