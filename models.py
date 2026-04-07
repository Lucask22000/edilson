from dataclasses import dataclass, field
from typing import List


CATEGORIAS_PADRAO = [
    "Tintas",
    "Preparacao",
    "Ferramentas",
    "Mao de obra",
    "Acabamento",
    "Servico especializado",
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
