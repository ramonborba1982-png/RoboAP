"""Fluxo da conversa de venda, como máquina de estados.

Sequência definida pela empresa:
  1. Cliente informa peça, carro e ano.
  2. A IA busca no site e mostra a peça (ou as opções).
  3. A IA pede confirmação da peça.
  4. Cliente confirma -> a IA adiciona ao pedido e pergunta se precisa de mais alguma peça.
  5. Se sim, volta ao passo 1. Se não, a IA pergunta se é entrega ou retirada.
  6. Com a resposta, a IA envia o pedido (em modo de teste, para antes de enviar).

Quem entende o texto do cliente é o modelo de IA: ele devolve uma Intencao. Este módulo só
decide o próximo passo, para que a regra seja previsível e testável.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Estado(str, Enum):
    COLETANDO = "coletando"  # faltam peça, carro ou ano
    BUSCANDO = "buscando"  # consulta rodando no site
    ESCOLHENDO = "escolhendo"  # opções enviadas, cliente escolhe uma
    CONFIRMANDO = "confirmando"  # aguardando o "sim" para adicionar a peça
    MAIS_PECAS = "mais_pecas"  # peça adicionada, perguntou se quer mais
    ENTREGA = "entrega"  # perguntou entrega ou retirada
    CONCLUIDO = "concluido"
    ESCALADO = "escalado"  # um humano assumiu; a IA fica em silêncio


class Intencao(str, Enum):
    # O que o cliente quis dizer
    PEDIDO_COMPLETO = "pedido_completo"
    PEDIDO_INCOMPLETO = "pedido_incompleto"
    ESCOLHEU_OPCAO = "escolheu_opcao"
    CONFIRMOU = "confirmou"
    RECUSOU = "recusou"
    QUER_MAIS = "quer_mais"
    NAO_QUER_MAIS = "nao_quer_mais"
    ENTREGA = "entrega"
    RETIRADA = "retirada"
    PEDIU_HUMANO = "pediu_humano"
    NAO_ENTENDI = "nao_entendi"
    # Resultado da busca no site (evento do sistema)
    ACHOU_UMA = "achou_uma"
    ACHOU_VARIAS = "achou_varias"
    NAO_ACHOU = "nao_achou"


class Acao(str, Enum):
    PERGUNTAR_FALTANTE = "perguntar_faltante"
    BUSCAR_NO_SITE = "buscar_no_site"
    ENVIAR_OPCOES = "enviar_opcoes"
    PEDIR_CONFIRMACAO = "pedir_confirmacao"
    ADICIONAR_AO_CARRINHO = "adicionar_ao_carrinho"
    PERGUNTAR_MAIS_PECAS = "perguntar_mais_pecas"
    PERGUNTAR_ENTREGA = "perguntar_entrega"
    ENVIAR_PEDIDO = "enviar_pedido"
    REPETIR_PERGUNTA = "repetir_pergunta"
    ESCALAR_PARA_HUMANO = "escalar_para_humano"
    NENHUMA = "nenhuma"


@dataclass(frozen=True)
class Passo:
    estado: Estado
    acoes: tuple[Acao, ...]
    entrega: bool | None = None  # só preenchido ao enviar o pedido


_ESCALAR = Passo(Estado.ESCALADO, (Acao.ESCALAR_PARA_HUMANO,))


def proximo_passo(estado: Estado, intencao: Intencao) -> Passo:
    """Dado o estado atual e o que aconteceu, devolve o novo estado e o que fazer."""
    # Um humano já assumiu: a IA não responde mais.
    if estado == Estado.ESCALADO:
        return Passo(Estado.ESCALADO, (Acao.NENHUMA,))

    # Em qualquer ponto o cliente pode pedir um atendente.
    if intencao == Intencao.PEDIU_HUMANO:
        return _ESCALAR

    # Depois de concluir, um novo pedido recomeça do zero.
    if estado == Estado.CONCLUIDO:
        estado = Estado.COLETANDO

    if estado == Estado.COLETANDO:
        if intencao == Intencao.PEDIDO_COMPLETO:
            return Passo(Estado.BUSCANDO, (Acao.BUSCAR_NO_SITE,))
        if intencao == Intencao.PEDIDO_INCOMPLETO:
            return Passo(Estado.COLETANDO, (Acao.PERGUNTAR_FALTANTE,))

    elif estado == Estado.BUSCANDO:
        if intencao == Intencao.ACHOU_UMA:
            return Passo(Estado.CONFIRMANDO, (Acao.PEDIR_CONFIRMACAO,))
        if intencao == Intencao.ACHOU_VARIAS:
            return Passo(Estado.ESCOLHENDO, (Acao.ENVIAR_OPCOES,))
        if intencao == Intencao.NAO_ACHOU:
            return _ESCALAR

    elif estado == Estado.ESCOLHENDO:
        if intencao == Intencao.ESCOLHEU_OPCAO:
            return Passo(Estado.CONFIRMANDO, (Acao.PEDIR_CONFIRMACAO,))
        if intencao == Intencao.PEDIDO_COMPLETO:  # cliente trocou o pedido
            return Passo(Estado.BUSCANDO, (Acao.BUSCAR_NO_SITE,))
        if intencao == Intencao.RECUSOU:  # a IA não tem mais opções
            return _ESCALAR

    elif estado == Estado.CONFIRMANDO:
        if intencao == Intencao.CONFIRMOU:
            return Passo(
                Estado.MAIS_PECAS,
                (Acao.ADICIONAR_AO_CARRINHO, Acao.PERGUNTAR_MAIS_PECAS),
            )
        if intencao == Intencao.RECUSOU:
            return Passo(Estado.COLETANDO, (Acao.PERGUNTAR_FALTANTE,))
        if intencao == Intencao.PEDIDO_COMPLETO:  # cliente corrigiu o pedido
            return Passo(Estado.BUSCANDO, (Acao.BUSCAR_NO_SITE,))

    elif estado == Estado.MAIS_PECAS:
        if intencao == Intencao.NAO_QUER_MAIS:
            return Passo(Estado.ENTREGA, (Acao.PERGUNTAR_ENTREGA,))
        if intencao in (Intencao.QUER_MAIS, Intencao.PEDIDO_INCOMPLETO):
            return Passo(Estado.COLETANDO, (Acao.PERGUNTAR_FALTANTE,))
        if intencao == Intencao.PEDIDO_COMPLETO:  # já disse a próxima peça
            return Passo(Estado.BUSCANDO, (Acao.BUSCAR_NO_SITE,))

    elif estado == Estado.ENTREGA:
        if intencao == Intencao.ENTREGA:
            return Passo(Estado.CONCLUIDO, (Acao.ENVIAR_PEDIDO,), entrega=True)
        if intencao == Intencao.RETIRADA:
            return Passo(Estado.CONCLUIDO, (Acao.ENVIAR_PEDIDO,), entrega=False)

    # Qualquer outra coisa: repete a pergunta pendente, sem mudar de estado.
    return Passo(estado, (Acao.REPETIR_PERGUNTA,))
