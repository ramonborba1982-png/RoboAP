"""Cliente da Evolution API: envia texto e consulta contatos.

A chave vem de EVOLUTION_API_KEY (variável de ambiente). Nunca é registrada em log.
"""

from __future__ import annotations

import logging

import httpx

from app.agente.numeros import apenas_digitos
from app.config import Settings

log = logging.getLogger("roboap")


class EvolutionClient:
    def __init__(self, settings: Settings, transporte: httpx.AsyncBaseTransport | None = None):
        self._base = settings.evolution_api_url.strip().rstrip("/")
        self._instancia = settings.evolution_instance.strip()
        chave = settings.evolution_api_key.strip()
        if not chave.isascii():
            # Costuma ser aspa curva ou espaço especial colado junto da chave.
            log.warning("evolution: EVOLUTION_API_KEY tem caractere invalido (nao ASCII); ignorada")
            chave = ""
        self._http = httpx.AsyncClient(
            headers={"apikey": chave},
            timeout=20,
            transport=transporte,
        )

    @property
    def configurado(self) -> bool:
        return bool(self._base and self._http.headers.get("apikey"))

    async def enviar_texto(self, numero: str, texto: str) -> bool:
        """Envia texto ao número (só dígitos com DDI). Devolve True se a Evolution aceitou."""
        if not self.configurado:
            log.warning("evolution: nao configurada, mensagem nao enviada")
            return False
        r = await self._http.post(
            f"{self._base}/message/sendText/{self._instancia}",
            json={"number": apenas_digitos(numero), "text": texto},
        )
        if r.status_code >= 300:
            log.warning("evolution: falha ao enviar (status %s)", r.status_code)
            return False
        return True
