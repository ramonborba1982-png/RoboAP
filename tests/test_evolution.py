import asyncio
import json

import httpx

from app.config import Settings
from app.evolution import EvolutionClient


def cliente(handler, chave="k"):
    s = Settings(evolution_api_url="https://ev.test", evolution_api_key=chave, evolution_instance="ap")
    return EvolutionClient(s, httpx.MockTransport(handler))


def test_envia_texto():
    vistos = {}

    def h(req):
        vistos["url"] = str(req.url)
        vistos["corpo"] = json.loads(req.content)
        return httpx.Response(201, json={})

    ok = asyncio.run(cliente(h).enviar_texto("5547990000001@s.whatsapp.net", "oi"))
    assert ok and vistos["url"].endswith("/message/sendText/ap")
    assert vistos["corpo"] == {"number": "5547990000001", "text": "oi"}


def test_sem_chave_nao_envia():
    assert asyncio.run(cliente(lambda r: httpx.Response(201), chave="").enviar_texto("55479", "oi")) is False


def test_falha_da_api():
    assert asyncio.run(cliente(lambda r: httpx.Response(401)).enviar_texto("55479", "oi")) is False
