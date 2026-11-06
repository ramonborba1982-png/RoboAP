"""Regras de fechamento do pedido, definidas pela empresa.

- Filial: Joinville primeiro; se não tiver estoque, a próxima da lista.
- Pagamento: 28 dias em 1 parcela; se não existir, à vista.
- Transportadora: o cliente escolhe entrega (MotoX Joinville) ou retirada.

Quando nenhuma opção serve, as funções devolvem None e quem chama escala para um humano.
Nunca se chuta uma opção.
"""

from __future__ import annotations

import re
import unicodedata

FILIAIS_PADRAO = ("JOI", "ITJ", "CH", "SJ", "CRI")


def _norm(texto: str) -> str:
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return sem_acento.lower().strip()


def escolher_filial(
    estoque: dict[str, int],
    quantidade: int,
    ordem: tuple[str, ...] = FILIAIS_PADRAO,
) -> str | None:
    """Primeira filial da ordem com estoque suficiente. Joinville vem primeiro."""
    if quantidade < 1:
        return None
    for filial in ordem:
        if estoque.get(filial, 0) >= quantidade:
            return filial
    return None


_VINTE_E_OITO = re.compile(r"(?<!\d)28 dias")
_PARCELAS = re.compile(r"parcelas:?\s*(\d+)")
_A_VISTA = re.compile(r"\ba?\s?vista\b")


def escolher_condicao_pagamento(opcoes: list[str]) -> str | None:
    """28 dias em 1 parcela; se não houver, à vista; se também não, None."""
    normalizadas = [(o, _norm(o)) for o in opcoes]

    for original, n in normalizadas:
        if not _VINTE_E_OITO.search(n):
            continue
        parcelas = _PARCELAS.search(n)
        if parcelas is None or int(parcelas.group(1)) == 1:
            return original

    for original, n in normalizadas:
        if _A_VISTA.search(n):
            return original
    return None


def escolher_transportadora(
    opcoes: list[str],
    entrega: bool,
    filial: str = "JOI",
    modelo_retirada: str = "RETIRA-{filial}",
) -> str | None:
    """Entrega: MotoX Joinville. Retirada: a opção de retirada da filial que despacha.

    Se o pedido sai de Joinville, a retirada é RETIRA-JOI. Se a opção não existir, devolve
    None (escala para humano) em vez de escolher outra transportadora.
    """
    termo_retirada = _norm(modelo_retirada.format(filial=filial))
    for original in opcoes:
        n = _norm(original)
        if entrega and "motox" in n and "joinville" in n:
            return original
        if not entrega and termo_retirada in n:
            return original
    return None
