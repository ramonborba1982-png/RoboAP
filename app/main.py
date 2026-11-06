"""Servidor do agente. Recebe o webhook da Evolution API (via n8n ou direto)."""

import hmac
import logging

from fastapi import FastAPI, Header, HTTPException, Request

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
) -> dict:
    settings = get_settings()
    # Sem segredo configurado, o webhook fica fechado em vez de aberto.
    if not settings.webhook_secret or not hmac.compare_digest(
        x_webhook_secret or "", settings.webhook_secret
    ):
        raise HTTPException(status_code=401, detail="nao autorizado")

    payload = await request.json()
    evento = payload.get("event", "desconhecido")
    log.info("evento recebido: %s", evento)
    # Proxima etapa: identificar o cliente, enfileirar a conversa e acionar o agente.
    return {"recebido": True}
