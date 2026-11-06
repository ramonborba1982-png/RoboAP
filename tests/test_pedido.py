from app.agente.pedido import (
    escolher_condicao_pagamento,
    escolher_filial,
    escolher_transportadora,
)

# Estoque visto no carrinho do Nilo
ESTOQUE = {"JOI": 7, "ITJ": 5, "CH": 36, "SJ": 15, "CRI": 15}

# Opções vistas na lista de condição de pagamento
CONDICOES = [
    "003 - AGLUTINACAO - PARCELAS: 1",
    "004 - PIX - PARCELAS: 1",
    "007 - 7 DIAS - PARCELAS: 1",
    "011 - 28 DIAS - PARCELAS: 1",
    "014 - 38 DIAS - PARCELAS: 1",
    "015 - 42 DIAS - PARCELAS: 1",
    "017 - 10 DIAS - PARCELAS: 1",
    "019 - 49 DIAS - PARCELAS: 1",
]


# --- filial ---------------------------------------------------------------------


def test_joinville_primeiro():
    assert escolher_filial(ESTOQUE, 1) == "JOI"


def test_joinville_sem_estoque_suficiente_vai_para_a_proxima():
    assert escolher_filial({**ESTOQUE, "JOI": 0}, 1) == "ITJ"
    assert escolher_filial(ESTOQUE, 10) == "CH"  # JOI tem 7, ITJ tem 5, CH tem 36


def test_nenhuma_filial_com_estoque():
    assert escolher_filial({"JOI": 0, "ITJ": 0}, 1) is None


def test_quantidade_invalida():
    assert escolher_filial(ESTOQUE, 0) is None


def test_filial_fora_da_lista_nao_e_usada():
    assert escolher_filial({"XYZ": 99}, 1) is None


# --- condição de pagamento -------------------------------------------------------


def test_prefere_28_dias():
    assert escolher_condicao_pagamento(CONDICOES) == "011 - 28 DIAS - PARCELAS: 1"


def test_sem_28_dias_usa_a_vista():
    opcoes = ["004 - PIX - PARCELAS: 1", "020 - A VISTA - PARCELAS: 1", "007 - 7 DIAS - PARCELAS: 1"]
    assert escolher_condicao_pagamento(opcoes) == "020 - A VISTA - PARCELAS: 1"


def test_a_vista_com_acento():
    assert escolher_condicao_pagamento(["001 - À VISTA"]) == "001 - À VISTA"


def test_28_dias_em_duas_parcelas_nao_serve():
    opcoes = ["012 - 28 DIAS - PARCELAS: 2", "020 - A VISTA - PARCELAS: 1"]
    assert escolher_condicao_pagamento(opcoes) == "020 - A VISTA - PARCELAS: 1"


def test_nao_confunde_128_dias_com_28():
    opcoes = ["030 - 128 DIAS - PARCELAS: 1", "020 - A VISTA"]
    assert escolher_condicao_pagamento(opcoes) == "020 - A VISTA"


def test_sem_28_dias_nem_a_vista():
    assert escolher_condicao_pagamento(["004 - PIX - PARCELAS: 1"]) is None


def test_lista_vazia():
    assert escolher_condicao_pagamento([]) is None


# --- transportadora --------------------------------------------------------------

TRANSPORTADORAS = [
    "000566 - MOTOX APP TECNOLOGIA LTDA (JOINVILLE)",
    "000700 - OUTRA TRANSPORTADORA LTDA",
    "000001 - RETIRA-JOI",
    "000002 - RETIRA-ITJ",
]


def test_entrega_usa_motox_joinville():
    assert (
        escolher_transportadora(TRANSPORTADORAS, entrega=True)
        == "000566 - MOTOX APP TECNOLOGIA LTDA (JOINVILLE)"
    )


def test_motox_de_outra_cidade_nao_serve():
    assert escolher_transportadora(["000567 - MOTOX APP TECNOLOGIA LTDA (ITAJAI)"], True) is None


def test_retirada_em_joinville_usa_retira_joi():
    assert escolher_transportadora(TRANSPORTADORAS, entrega=False) == "000001 - RETIRA-JOI"


def test_retirada_e_sempre_retira_joi():
    # Mesmo havendo RETIRA-ITJ na lista, por enquanto só vale RETIRA-JOI.
    assert escolher_transportadora(TRANSPORTADORAS, entrega=False) == "000001 - RETIRA-JOI"
    assert escolher_transportadora(TRANSPORTADORAS[::-1], entrega=False) == "000001 - RETIRA-JOI"


def test_retirada_sem_retira_joi_nao_chuta():
    # Só existe RETIRA-ITJ: não escolhe, devolve None para escalar.
    opcoes = [TRANSPORTADORAS[0], "000002 - RETIRA-ITJ"]
    assert escolher_transportadora(opcoes, entrega=False) is None


def test_retirada_sem_nenhuma_opcao_de_retirada_nao_chuta():
    assert escolher_transportadora(TRANSPORTADORAS[:2], entrega=False) is None


def test_entrega_nunca_escolhe_retirada():
    esperado = "000566 - MOTOX APP TECNOLOGIA LTDA (JOINVILLE)"
    assert escolher_transportadora(TRANSPORTADORAS[::-1], entrega=True) == esperado
