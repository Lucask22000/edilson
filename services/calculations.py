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
    desconto_percentual = min(100.0, max(0.0, sanitize_money(desconto_percentual)))
    desconto_valor = max(0.0, sanitize_money(desconto_valor))

    if desconto_tipo == "Percentual" and subtotal > 0:
        desconto_aplicado = min(subtotal, round(subtotal * (desconto_percentual / 100), 2))
    elif desconto_tipo == "Valor fixo":
        desconto_aplicado = round(min(subtotal, desconto_valor), 2)

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
