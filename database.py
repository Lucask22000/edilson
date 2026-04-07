from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "orcamentos.db"


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    return {column[0]: row[index] for index, column in enumerate(cursor.description)}


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = dict_factory
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


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
            """
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
