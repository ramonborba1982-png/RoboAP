"""Servidor do agente. Recebe o webhook da Evolution API (via n8n ou direto)."""

import hmac
import logging

from fastapi import FastAPI, Header, HTTPException, Request

from app.agente.numeros import extrair_remetente, numero_permitido
from app.config import get_settings

log = logging.getLogger("roboap")
app = FastAPI(title="RoboAP - Vendedor IA de Pecas")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/webhook/evolution")
async def webhook_evolution(
    request: Request,
    x_webhook_secret: str | None = Header(default=None),
    secret: str | None = None,
) -> dict:
    settings = get_settings()
    # Sem segredo configurado, o webhook fica fechado em vez de aberto.
    # A Evolution Manager nem sempre permite cabeçalho: aceita o segredo também em ?secret=.
    enviado = x_webhook_secret or secret or ""
    if not settings.webhook_secret or not hmac.compare_digest(enviado, settings.webhook_secret):
        raise HTTPException(status_code=401, detail="nao autorizado")

    payload = await request.json()
    evento = payload.get("event", "desconhecido")
    log.warning("webhook: evento=%s", evento)

    remetente, enviada_pela_empresa = extrair_remetente(payload)
    # Mensagens da própria empresa (atendente ou robô) nunca disparam resposta.
    if enviada_pela_empresa:
        return {"recebido": True, "ignorado": "mensagem_da_empresa"}
    # Em teste, só os números autorizados falam com o robô.
    if remetente and not numero_permitido(
        remetente, settings.numeros_permitidos, settings.pedido_dry_run
    ):
        log.info("mensagem ignorada: remetente fora da lista de teste")
        return {"recebido": True, "ignorado": "remetente_nao_autorizado"}

    log.info("evento recebido: %s", evento)
    # Proxima etapa: identificar o cliente, enfileirar a conversa e acionar o agente.
    return {"recebido": True}
