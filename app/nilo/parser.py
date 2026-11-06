"""Converte o texto de um card do catálogo Nilo em ItemCatalogo.

Os cards foram vistos como linhas de texto na ordem: marca, código, descrição, valor,
quantidade múltipla/unidade e etiqueta (Disponível, Indisponível, Outra Unidade). Etiquetas
como PROMOÇÃO podem aparecer no meio. O parser é tolerante: procura cada campo por padrão,
sem depender da posição exata. Cards sem preço ou sem código são descartados (None).
"""

from __future__ import annotations

import re
from decimal import Decimal

from app.agente.mensagens import ItemCatalogo

_PRECO = re.compile(r"R\$\s*([\d.]+,\d{2})")
_UNIDADE = re.compile(r"^\d+\s*[A-Za-z]{1,4}$")  # ex.: "1 JG", "2 PC"
_ETIQUETAS_DISP = ("indisponível", "indisponivel", "outra unidade", "disponível", "disponivel")
_IGNORAR = ("promoção", "promocao", "conversão", "conversao", "ficha técnica", "aplicação")


def _preco(texto: str) -> Decimal:
    return Decimal(texto.replace(".", "").replace(",", "."))


def parse_card(texto: str) -> ItemCatalogo | None:
    linhas = [l.strip() for l in texto.splitlines() if l.strip()]
    preco = None
    idx_preco = None
    for i, l in enumerate(linhas):
        m = _PRECO.search(l)
        if m:
            preco, idx_preco = _preco(m.group(1)), i
            break
    if preco is None:
        return None

    disponibilidade = "Disponível"
    unidade = ""
    for l in linhas:
        baixo = l.lower()
        if baixo in _ETIQUETAS_DISP:
            disponibilidade = l.capitalize() if baixo != "outra unidade" else "Outra Unidade"
        elif _UNIDADE.match(l):
            unidade = l

    antes = [
        l for l in linhas[:idx_preco]
        if l.lower() not in _IGNORAR and l.lower() not in _ETIQUETAS_DISP
    ]
    if len(antes) < 3:
        return None
    marca, codigo, descricao = antes[0], antes[1], " ".join(antes[2:])
    return ItemCatalogo(marca, codigo, descricao, preco, unidade, disponibilidade)
