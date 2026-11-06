"""Conduz a conversa de um cliente: estado + interpretação + próxima ação + mensagens.

Neste estágio a consulta ao site (Nilo) ainda não está ligada. Quando o pedido fica completo,
o robô repete o que entendeu e avisa que a consulta ao site vem na próxima etapa. O estado
permanece COLETANDO para não prometer o que ainda não faz.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.agente.fluxo import Acao, Estado, Intencao, proximo_passo
from app.agente.interprete import Interprete
from app.agente.regras import PedidoInfo


@dataclass
class Sessao:
    estado: Estado = Estado.COLETANDO
    pedido: PedidoInfo = field(default_factory=PedidoInfo)


_PERGUNTAS = {
    "peca": "Qual peça você precisa?",
    "veiculo": "Para qual carro (marca e modelo)?",
    "ano": "Qual o ano do carro?",
}


def _mesclar(atual: PedidoInfo, novo: PedidoInfo | None) -> None:
    if not novo:
        return
    atual.peca = novo.peca or atual.peca
    atual.veiculo = novo.veiculo or atual.veiculo
    atual.ano = novo.ano or atual.ano


class Conversa:
    def __init__(self, interprete: Interprete):
        self._interprete = interprete
        self._sessoes: dict[str, Sessao] = {}

    def sessao(self, numero: str) -> Sessao:
        return self._sessoes.setdefault(numero, Sessao())

    async def responder(self, numero: str, texto: str) -> list[str]:
        s = self.sessao(numero)
        leitura = await self._interprete.interpretar(texto, s.estado, s.pedido)
        _mesclar(s.pedido, leitura.pedido)

        intencao = leitura.intencao
        # Só o código decide se o pedido está completo; não confiamos no rótulo do modelo.
        if intencao in (Intencao.PEDIDO_COMPLETO, Intencao.PEDIDO_INCOMPLETO):
            intencao = (
                Intencao.PEDIDO_COMPLETO if s.pedido.completo() else Intencao.PEDIDO_INCOMPLETO
            )

        passo = proximo_passo(s.estado, intencao)
        s.estado = passo.estado
        respostas: list[str] = []
        for acao in passo.acoes:
            if acao == Acao.PERGUNTAR_FALTANTE:
                falta = s.pedido.faltando()
                respostas.append(_PERGUNTAS[falta[0]] if falta else "Pode me dizer a peça?")
            elif acao == Acao.BUSCAR_NO_SITE:
                p = s.pedido
                respostas.append(
                    f"Entendi: *{p.peca}* para *{p.veiculo} {p.ano}*. "
                    "A consulta ao site ainda será ligada na próxima etapa dos testes."
                )
                s.estado = Estado.COLETANDO
            elif acao == Acao.ESCALAR_PARA_HUMANO:
                respostas.append("Vou chamar um atendente para te ajudar. Um momento, por favor.")
            elif acao == Acao.REPETIR_PERGUNTA:
                respostas.append("Não entendi bem. Pode dizer a peça, o carro e o ano?")
        return respostas
