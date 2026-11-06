"""Testes das regras de pedido. As descrições são as vistas no catálogo do Nilo."""

from app.agente.regras import (
    Compat,
    PedidoInfo,
    compatibilidade,
    extrair_aplicacoes,
)

REF = 2026  # ano fixo para os testes não dependerem da data de hoje


# --- 3 informações obrigatórias -------------------------------------------------


def test_pedido_vazio_falta_tudo():
    assert PedidoInfo().faltando(REF) == ["peca", "veiculo", "ano"]


def test_so_a_peca_pergunta_carro_e_ano():
    info = PedidoInfo(peca="pastilha de freio")
    assert info.faltando(REF) == ["veiculo", "ano"]
    assert info.pergunta_faltante(REF) == (
        "Para achar a peça certa, me diga o carro (marca e modelo) e o ano do carro, por favor."
    )


def test_falta_so_o_ano():
    info = PedidoInfo(peca="pastilha", veiculo="Corsa")
    assert info.pergunta_faltante(REF) == (
        "Para achar a peça certa, me diga o ano do carro, por favor."
    )


def test_ano_absurdo_conta_como_faltando():
    assert PedidoInfo("pastilha", "Corsa", 1800).faltando(REF) == ["ano"]
    assert PedidoInfo("pastilha", "Corsa", 2040).faltando(REF) == ["ano"]


def test_pedido_completo():
    info = PedidoInfo("pastilha de freio", "Corsa", 2010)
    assert info.completo(REF)
    assert info.pergunta_faltante(REF) == ""


def test_espacos_em_branco_nao_valem():
    assert PedidoInfo("  ", "Corsa", 2010).faltando(REF) == ["peca"]


# --- leitura dos anos das descrições --------------------------------------------


def test_nao_confunde_modelo_com_ano():
    # "208/2008" é modelo, só "18/" é ano
    apps = extrair_aplicacoes("PAST. FREIO 208/2008 18/ C4 CACTUS 19/", REF)
    assert [(a.ano_ini, a.ano_fim) for a in apps] == [(2018, None), (2019, None)]


def test_modelos_com_barra_nao_viram_ano():
    apps = extrair_aplicacoes("PAST. FREIO 712/812/814/914 98/ DIANT/TRAS.", REF)
    assert [(a.ano_ini, a.ano_fim) for a in apps] == [(1998, None)]


def test_intervalos_de_dois_digitos():
    apps = extrair_aplicacoes("PAST. FREIO A/C/D-40 TDS/GMC 93/01", REF)
    assert [(a.ano_ini, a.ano_fim) for a in apps] == [(1993, 2001)]


def test_ano_de_quatro_digitos():
    apps = extrair_aplicacoes("PAST. FREIO CORSA 2002/ MONTANA (VARGA)", REF)
    assert [(a.ano_ini, a.ano_fim) for a in apps] == [(2002, None)]


def test_sem_ano_na_descricao():
    assert extrair_aplicacoes("ANTI-CHIO DE PASTILHA FREIO 200ML ORBI", REF) == []


# --- compatibilidade ------------------------------------------------------------


def test_corsa_2010_compativel():
    d = "PAST. FREIO CORSA 2002/ MONTANA (VARGA)"
    assert compatibilidade(d, "Chevrolet Corsa", 2010, REF) == Compat.COMPATIVEL


def test_corsa_1999_incompativel():
    d = "PAST. FREIO CORSA 2002/ MONTANA (VARGA)"
    assert compatibilidade(d, "Corsa", 1999, REF) == Compat.INCOMPATIVEL


def test_modelo_depois_do_ultimo_ano_tambem_vale():
    d = "PAST. FREIO CORSA 2002/ MONTANA (VARGA)"
    assert compatibilidade(d, "Montana", 2005, REF) == Compat.COMPATIVEL


def test_varios_modelos_cada_um_com_seu_ano():
    d = "PAST. FREIO A200 13/ B180 12/ CLA250 16/ TRAS*"
    assert compatibilidade(d, "Mercedes A200", 2015, REF) == Compat.COMPATIVEL
    assert compatibilidade(d, "A200", 2012, REF) == Compat.INCOMPATIVEL
    assert compatibilidade(d, "B180", 2012, REF) == Compat.COMPATIVEL
    assert compatibilidade(d, "CLA250", 2015, REF) == Compat.INCOMPATIVEL


def test_intervalo_fechado():
    d = "PAST. FREIO A4 08/15 A5 09/17 A6 11/ TRAS."
    assert compatibilidade(d, "A4", 2010, REF) == Compat.COMPATIVEL
    assert compatibilidade(d, "A4", 2016, REF) == Compat.INCOMPATIVEL
    assert compatibilidade(d, "A6", 2020, REF) == Compat.COMPATIVEL


def test_modelo_que_nao_aparece_fica_indeterminado():
    d = "PAST. FREIO A200 13/ B180 12/ CLA250 16/ TRAS*"
    assert compatibilidade(d, "Gol", 2015, REF) == Compat.INDETERMINADO


def test_descricao_sem_ano_fica_indeterminada():
    d = "ANTI-CHIO DE PASTILHA FREIO 200ML ORBI"
    assert compatibilidade(d, "Corsa", 2010, REF) == Compat.INDETERMINADO


def test_veiculo_vazio_fica_indeterminado():
    assert compatibilidade("PAST. FREIO CORSA 2002/", "", 2010, REF) == Compat.INDETERMINADO


def test_acento_e_caixa_nao_atrapalham():
    d = "PAST. FREIO CITROËN C4 CACTUS 19/"
    assert compatibilidade(d, "citroen c4 cactus", 2020, REF) == Compat.COMPATIVEL
