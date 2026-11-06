"""Valida a navegação no Nilo SEM adicionar nada ao carrinho e SEM enviar pedido.

Uso (no servidor, com as variáveis NILO_* definidas):
    python scripts/validar_nilo.py 012478 "pastilha de freio corsa"

Mostra quantos cards foram lidos e salva uma foto da tela em /tmp/nilo_busca.png para ajustar
seletores. Nunca imprime senha.
"""

import asyncio
import sys

from playwright.async_api import async_playwright

from app.config import get_settings
from app.nilo.sessao import SessaoNilo


async def main(codigo: str, termo: str) -> None:
    cfg = get_settings()
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        pagina = await nav.new_page()
        s = SessaoNilo(pagina, cfg.nilo_url, dry_run=True)
        await s.entrar(cfg.nilo_cnpj, cfg.nilo_login, cfg.nilo_senha)
        print("login: ok")
        await s.escolher_cliente(codigo)
        print("cliente: ok")
        itens = await s.buscar(termo)
        print(f"cards lidos: {len(itens)}")
        for i in itens[:5]:
            print(" ", i.marca, i.codigo, i.preco, i.disponibilidade)
        await pagina.screenshot(path="/tmp/nilo_busca.png")
        await nav.close()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2]))
