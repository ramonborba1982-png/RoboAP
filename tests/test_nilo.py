import asyncio
from decimal import Decimal

from app.nilo.parser import parse_card
from app.nilo.pool import PoolNilo
from app.nilo.sessao import SessaoNilo

CARD = """FRAS-LE
PD-46
PAST. FREIO CORSA 2002/ MONTANA (VARGA)
R$ 59,96
1 JG
Disponível"""


def test_parse_basico():
    i = parse_card(CARD)
    assert (i.marca, i.codigo, i.preco, i.unidade) == ("FRAS-LE", "PD-46", Decimal("59.96"), "1 JG")
    assert "CORSA" in i.descricao and i.disponibilidade == "Disponível"


def test_outra_unidade_e_promocao():
    t = "WILLTEC\nFP884\nPROMOÇÃO\nPAST. FREIO CORSA/CELTA 12.09/ *\nR$ 1.044,50\nOutra Unidade"
    i = parse_card(t)
    assert i.preco == Decimal("1044.50") and i.disponibilidade == "Outra Unidade"
    assert "PROMOÇÃO" not in i.descricao


def test_sem_preco_descarta():
    assert parse_card("A\nB\nC") is None


def test_dry_run_nunca_envia():
    r = asyncio.run(SessaoNilo(page=None, url_base="https://x", dry_run=True).enviar_pedido())
    assert not r.enviado and r.motivo == "modo_teste"


def test_pool():
    async def go():
        async with PoolNilo(2).usar():
            return 1
    assert asyncio.run(go()) == 1


def test_cliques_destrutivos_sao_bloqueados():
    import pytest

    from app.nilo.sessao import ErroNilo

    s = SessaoNilo(page=None, url_base="https://x")
    for nome in ("Excluir Pedido", "Enviar Pedido", "lixeira"):
        with pytest.raises(ErroNilo):
            asyncio.run(s._clicar(None, nome))


def test_cards_do_texto_da_pagina():
    texto = "Resultados\n" + CARD + "\nWILLTEC\nFP884\nPAST. FREIO CORSA 12.09/\nR$ 80,00\nOutra Unidade\nrodape"
    itens = SessaoNilo._cards_do_texto(texto)
    assert [i.codigo for i in itens] == ["PD-46", "FP884"]
