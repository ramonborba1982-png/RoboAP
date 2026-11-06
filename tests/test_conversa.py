import asyncio

from app.agente.conversa import Conversa
from app.agente.fluxo import Estado, Intencao
from app.agente.interprete import Interpretacao, analisar_json
from app.agente.regras import PedidoInfo


class Falso:
    def __init__(self, *leituras):
        self.fila = list(leituras)

    async def interpretar(self, texto, estado, pedido):
        return self.fila.pop(0)


def rodar(c, texto, numero="55479"):
    return asyncio.run(c.responder(numero, texto))


def test_pergunta_o_que_falta_e_acumula():
    c = Conversa(Falso(
        Interpretacao(Intencao.PEDIDO_INCOMPLETO, PedidoInfo(peca="pastilha de freio")),
        Interpretacao(Intencao.PEDIDO_INCOMPLETO, PedidoInfo(veiculo="Corsa")),
        Interpretacao(Intencao.PEDIDO_INCOMPLETO, PedidoInfo(ano=2008)),
    ))
    assert "carro" in rodar(c, "x")[0]
    assert "ano" in rodar(c, "x")[0]
    assert "pastilha de freio" in rodar(c, "x")[0]


def test_nao_confia_no_rotulo_do_modelo():
    # Modelo diz "completo" mas falta o ano: o código pergunta o ano.
    c = Conversa(Falso(Interpretacao(Intencao.PEDIDO_COMPLETO, PedidoInfo("pastilha", "Corsa", None))))
    assert "ano" in rodar(c, "x")[0]


def test_pedir_humano_escala_e_depois_silencia():
    c = Conversa(Falso(Interpretacao(Intencao.PEDIU_HUMANO), Interpretacao(Intencao.NAO_ENTENDI)))
    assert "atendente" in rodar(c, "quero falar com alguem")[0]
    assert c.sessao("55479").estado == Estado.ESCALADO
    assert rodar(c, "oi") == []


def test_json_invalido_vira_nao_entendi():
    assert analisar_json("lixo").intencao == Intencao.NAO_ENTENDI
    assert analisar_json('{"intencao":"inventada"}').intencao == Intencao.NAO_ENTENDI


def test_json_valido():
    i = analisar_json('```json\n{"intencao":"pedido_completo","peca":"pastilha","veiculo":"Corsa","ano":"2008"}\n```')
    assert i.intencao == Intencao.PEDIDO_COMPLETO and i.pedido.ano == 2008


def test_prompt_monta_sem_erro():
    from app.agente.interprete import montar_prompt

    assert "coletando" in montar_prompt(Estado.COLETANDO, PedidoInfo(peca="x"))
