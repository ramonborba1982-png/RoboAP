"""Limita as sessões simultâneas no Nilo (login permite até 5)."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager


class PoolNilo:
    def __init__(self, max_sessoes: int = 5):
        self._sem = asyncio.Semaphore(max_sessoes)

    @asynccontextmanager
    async def usar(self):
        async with self._sem:
            yield
