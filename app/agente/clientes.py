"""Identificação do cliente pelo nome do contato no WhatsApp.

Os contatos dos clientes são salvos como "<código>-<nome>", por exemplo "012478-Nome da Empresa".
O código é o mesmo que aparece no seletor de cliente do Nilo ("012478 - NOME DA EMPRESA").
"""

from __future__ import annotations

import re

# 3 a 8 dígitos no começo, seguidos de hífen, ponto ou espaço.
_CODIGO = re.compile(r"^\s*(\d{3,8})\s*[-.\s]")


def extrair_codigo_cliente(nome_contato: str) -> str | None:
    """'012478-Reinert e Borba' -> '012478'. Sem código no começo, devolve None.

    Os zeros à esquerda fazem parte do código e são mantidos. Nunca se adivinha o cliente:
    sem código, quem chama deve perguntar ou escalar para um humano.
    """
    achado = _CODIGO.match(nome_contato or "")
    return achado.group(1) if achado else None
