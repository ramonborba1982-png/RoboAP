"""Sessão do robô no Nilo (Playwright).

ATENÇÃO: os seletores ainda NÃO foram validados no site real. Rode scripts/validar_nilo.py no
servidor e ajuste app/nilo/seletores.py antes de usar em atendimento.

Regra de segurança: com dry_run ativo, enviar_pedido devolve antes de localizar ou clicar o
botão "Enviar Pedido". Nunca clica em "Excluir Pedido" nem na lixeira.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoEnvio:
    enviado: bool
    motivo: str = ""


class SessaoNilo:
    def __init__(self, page, dry_run: bool = True):
        self.page = page
        self.dry_run = dry_run

    async def enviar_pedido(self) -> ResultadoEnvio:
        if self.dry_run:
            return ResultadoEnvio(False, "modo_teste")
        # O clique real só será implementado depois da autorização da empresa.
        return ResultadoEnvio(False, "nao_implementado")
