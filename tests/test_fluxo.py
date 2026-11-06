from decimal import Decimal

from app.agente.fluxo import Acao, Estado, Intencao, proximo_passo
from app.agente.mensagens import (
    ItemCatalogo,
    avisar_envio,
    formatar_preco,
    listar_opcoes,
    pedir_confirmacao,
    perguntar_entrega,
    perguntar_mais_pecas,
)


def rodar(estado, *intencoes):
    """Aplica uma sequência de intenções e devolve (estado final, todas as ações, último passo)."""
    acoes = []
    passo = None
    for i in intencoes:
        passo = proximo_passo(estado, i)
        estado = passo.estado
        acoes.extend(passo.acoes)
    return estado, acoes, passo


# --- caminho feliz ----------------------------------------------------------------


def test_caminho_feliz_uma_peca_com_entrega():
    estado, acoes, passo = rodar(
        Estado.COLETANDO,
        Intencao.PEDIDO_COMPLETO,
        Intencao.ACHOU_UMA,
        Intencao.CONFIRMOU,
        Intencao.NAO_QUER_MAIS,
        Intencao.ENTREGA,
    )
    assert estado == Estado.CONCLUIDO
    assert acoes == [
        Acao.BUSCAR_NO_SITE,
        Acao.PEDIR_CONFIRMACAO,
        Acao.ADICIONAR_AO_CARRINHO,
        Acao.PERGUNTAR_MAIS_PECAS,
        Acao.PERGUNTAR_ENTREGA,
        Acao.ENVIAR_PEDIDO,
    ]
    assert passo.entrega is True


def test_retirada():
    _, _, passo = rodar(Estado.ENTREGA, Intencao.RETIRADA)
    assert passo.acoes == (Acao.ENVIAR_PEDIDO,)
    assert passo.entrega is False


def test_varias_opcoes_cliente_escolhe_e_confirma():
    estado, acoes, _ = rodar(
        Estado.BUSCANDO, Intencao.ACHOU_VARIAS, Intencao.ESCOLHEU_OPCAO, Intencao.CONFIRMOU
    )
    assert estado == Estado.MAIS_PECAS
    assert acoes == [
        Acao.ENVIAR_OPCOES,
        Acao.PEDIR_CONFIRMACAO,
        Acao.ADICIONAR_AO_CARRINHO,
        Acao.PERGUNTAR_MAIS_PECAS,
    ]


# --- a peça só entra no carrinho depois do "sim" -----------------------------------


def test_nao_adiciona_sem_confirmar():
    for intencao in (Intencao.NAO_ENTENDI, Intencao.QUER_MAIS, Intencao.ESCOLHEU_OPCAO):
        passo = proximo_passo(Estado.CONFIRMANDO, intencao)
        assert Acao.ADICIONAR_AO_CARRINHO not in passo.acoes
        assert passo.estado == Estado.CONFIRMANDO


def test_recusar_a_peca_volta_a_perguntar():
    passo = proximo_passo(Estado.CONFIRMANDO, Intencao.RECUSOU)
    assert passo.estado == Estado.COLETANDO
    assert passo.acoes == (Acao.PERGUNTAR_FALTANTE,)


# --- o pedido só é enviado depois de saber entrega ou retirada ---------------------


def test_nao_envia_antes_de_perguntar_a_entrega():
    estado, acoes, _ = rodar(Estado.MAIS_PECAS, Intencao.NAO_QUER_MAIS)
    assert estado == Estado.ENTREGA
    assert Acao.ENVIAR_PEDIDO not in acoes


def test_resposta_confusa_na_entrega_repete_a_pergunta():
    passo = proximo_passo(Estado.ENTREGA, Intencao.NAO_ENTENDI)
    assert passo.estado == Estado.ENTREGA
    assert passo.acoes == (Acao.REPETIR_PERGUNTA,)


# --- mais peças -------------------------------------------------------------------


def test_quer_mais_pecas_volta_para_coletar():
    passo = proximo_passo(Estado.MAIS_PECAS, Intencao.QUER_MAIS)
    assert passo.estado == Estado.COLETANDO


def test_ja_diz_a_proxima_peca_na_mesma_mensagem():
    passo = proximo_passo(Estado.MAIS_PECAS, Intencao.PEDIDO_COMPLETO)
    assert passo.estado == Estado.BUSCANDO
    assert passo.acoes == (Acao.BUSCAR_NO_SITE,)


def test_pedido_incompleto_pergunta_o_que_falta():
    passo = proximo_passo(Estado.COLETANDO, Intencao.PEDIDO_INCOMPLETO)
    assert passo.acoes == (Acao.PERGUNTAR_FALTANTE,)


# --- escalonamento ----------------------------------------------------------------


def test_peca_nao_encontrada_escala():
    passo = proximo_passo(Estado.BUSCANDO, Intencao.NAO_ACHOU)
    assert passo.estado == Estado.ESCALADO
    assert passo.acoes == (Acao.ESCALAR_PARA_HUMANO,)


def test_cliente_pede_atendente_em_qualquer_estado():
    for estado in (Estado.COLETANDO, Estado.ESCOLHENDO, Estado.CONFIRMANDO, Estado.MAIS_PECAS, Estado.ENTREGA):
        assert proximo_passo(estado, Intencao.PEDIU_HUMANO).estado == Estado.ESCALADO


def test_depois_de_escalar_a_ia_fica_em_silencio():
    for intencao in Intencao:
        passo = proximo_passo(Estado.ESCALADO, intencao)
        assert passo.estado == Estado.ESCALADO
        assert passo.acoes == (Acao.NENHUMA,)


def test_depois_de_concluir_novo_pedido_recomeca():
    passo = proximo_passo(Estado.CONCLUIDO, Intencao.PEDIDO_COMPLETO)
    assert passo.estado == Estado.BUSCANDO


# --- mensagens --------------------------------------------------------------------

ITEM = ItemCatalogo(
    marca="FRAS-LE",
    codigo="PD-46",
    descricao="PAST. FREIO CORSA 2002/ MONTANA (VARGA)",
    preco=Decimal("59.96"),
    unidade="1 JG",
)


def test_formatar_preco():
    assert formatar_preco(Decimal("59.96")) == "R$ 59,96"
    assert formatar_preco(Decimal("1234.5")) == "R$ 1.234,50"
    assert formatar_preco(Decimal("1234567.89")) == "R$ 1.234.567,89"


def test_pedido_de_confirmacao():
    texto = pedir_confirmacao(ITEM)
    assert "FRAS-LE PD-46" in texto
    assert "R$ 59,96 (1 JG)" in texto
    assert "sim" in texto


def test_listar_opcoes_numera_e_limita():
    itens = [ITEM] * 8
    texto = listar_opcoes(itens, limite=5)
    assert "*5)*" in texto
    assert "*6)*" not in texto
    assert "número ou a marca" in texto


def test_listar_opcoes_avisa_quando_nao_esta_disponivel_na_hora():
    outro = ItemCatalogo("TEXTAR", "2484801", "PAST. FREIO", Decimal("285.64"), "1 JG", "Outra Unidade")
    assert "(Outra Unidade)" in listar_opcoes([outro])


def test_perguntas_fixas():
    assert "mais alguma peça" in perguntar_mais_pecas()
    assert "entrega" in perguntar_entrega() and "retirar" in perguntar_entrega()


def test_aviso_de_envio():
    assert "MotoX" in avisar_envio(True)
    assert "retirada" in avisar_envio(False)
