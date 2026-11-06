import pytest
from fastapi.testclient import TestClient

from app import config
from app.main import app

SEGREDO = "segredo-de-teste"


def evento(numero: str, da_empresa: bool = False) -> dict:
    return {
        "event": "messages.upsert",
        "data": {"key": {"remoteJid": f"{numero}@s.whatsapp.net", "fromMe": da_empresa}},
    }


@pytest.fixture
def cliente(monkeypatch):
    for nome in ("PEDIDO_DRY_RUN", "TESTE_NUMEROS_PERMITIDOS"):
        monkeypatch.delenv(nome, raising=False)
    monkeypatch.setenv("WEBHOOK_SECRET", SEGREDO)
    config.get_settings.cache_clear()
    yield TestClient(app)
    config.get_settings.cache_clear()


def cabecalho(segredo=SEGREDO):
    return {"X-Webhook-Secret": segredo}


def test_health(cliente):
    assert cliente.get("/health").json() == {"status": "ok"}


def test_sem_segredo_correto_e_recusado(cliente):
    assert cliente.post("/webhook/evolution", json=evento("5547990000001")).status_code == 401
    r = cliente.post("/webhook/evolution", json=evento("5547990000001"), headers=cabecalho("errado"))
    assert r.status_code == 401


def test_sem_segredo_configurado_o_webhook_fica_fechado(cliente, monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET", "")
    config.get_settings.cache_clear()
    r = cliente.post("/webhook/evolution", json=evento("5547990000001"), headers=cabecalho(""))
    assert r.status_code == 401


def test_em_teste_sem_lista_ninguem_e_atendido(cliente):
    r = cliente.post("/webhook/evolution", json=evento("5547990000001"), headers=cabecalho())
    assert r.json() == {"recebido": True, "ignorado": "remetente_nao_autorizado"}


def test_numero_autorizado_e_aceito(cliente, monkeypatch):
    monkeypatch.setenv("TESTE_NUMEROS_PERMITIDOS", "5547990000001")
    config.get_settings.cache_clear()
    r = cliente.post("/webhook/evolution", json=evento("5547990000001"), headers=cabecalho())
    assert r.json() == {"recebido": True}


def test_numero_fora_da_lista_e_ignorado(cliente, monkeypatch):
    monkeypatch.setenv("TESTE_NUMEROS_PERMITIDOS", "5547990000001")
    config.get_settings.cache_clear()
    r = cliente.post("/webhook/evolution", json=evento("5547988887777"), headers=cabecalho())
    assert r.json()["ignorado"] == "remetente_nao_autorizado"


def test_mensagem_da_empresa_nunca_dispara_resposta(cliente, monkeypatch):
    monkeypatch.setenv("TESTE_NUMEROS_PERMITIDOS", "5547990000001")
    config.get_settings.cache_clear()
    r = cliente.post(
        "/webhook/evolution", json=evento("5547990000001", da_empresa=True), headers=cabecalho()
    )
    assert r.json() == {"recebido": True, "ignorado": "mensagem_da_empresa"}


def test_segredo_na_url_tambem_vale(cliente):
    r = cliente.post(f"/webhook/evolution?secret={SEGREDO}", json=evento("5547990000001"))
    assert r.status_code == 200
    assert cliente.post("/webhook/evolution?secret=errado", json=evento("5547990000001")).status_code == 401


def test_estrutura_nao_vaza_valores():
    from app.main import estrutura

    caminhos = estrutura({"data": {"key": {"remoteJid": "5547990000001@s.whatsapp.net"}, "n": [1]}})
    assert "data.key.remoteJid:str" in caminhos
    assert not any("5547" in c for c in caminhos)
