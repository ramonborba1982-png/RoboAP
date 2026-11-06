"""Sessão do robô no Nilo (Playwright).

ATENÇÃO: os seletores ainda NÃO foram validados no site real. Rode scripts/validar_nilo.py no
servidor e ajuste app/nilo/seletores.py antes de usar em atendimento.

Segurança:
- Com dry_run ativo, enviar_pedido devolve antes de localizar ou clicar o botão.
- Nenhum método clica em "Excluir Pedido", lixeira ou "Enviar Pedido" (ver `_clicar`).
- O robô só escolhe o cliente pelo seletor do catálogo (nunca pelo "+" da lista de clientes).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.agente.mensagens import ItemCatalogo
from app.nilo import seletores as sel
from app.nilo.parser import parse_card


@dataclass(frozen=True)
class ResultadoEnvio:
    enviado: bool
    motivo: str = ""


class ErroNilo(Exception):
    pass


class SessaoNilo:
    def __init__(self, page, url_base: str, dry_run: bool = True):
        self.page = page
        self.url = url_base.rstrip("/")
        self.dry_run = dry_run

    # --- proteção -----------------------------------------------------------------

    async def _clicar(self, locator, nome: str) -> None:
        if sel.PROIBIDOS.search(nome) and nome != "enviar_pedido_liberado":
            raise ErroNilo(f"clique bloqueado por seguranca: {nome}")
        await locator.click()

    # --- entrada ------------------------------------------------------------------

    async def entrar(self, cnpj: str, login: str, senha: str) -> None:
        await self.page.goto(self.url + sel.URL_LOGIN)
        await self.page.get_by_label(sel.CAMPO_CNPJ).fill(cnpj)
        await self.page.get_by_label(sel.CAMPO_LOGIN).fill(login)
        await self.page.get_by_label(sel.CAMPO_SENHA).fill(senha)
        await self.page.get_by_role("button", name=sel.BOTAO_ENTRAR).click()
        await self.page.wait_for_url(lambda u: "login" not in u, timeout=20000)

    async def escolher_cliente(self, codigo: str) -> None:
        """Abre o catálogo, digita o código no seletor de cliente e escolhe a opção."""
        await self.page.goto(self.url + sel.URL_CATALOGO)
        combo = self.page.get_by_role("combobox").first
        await combo.click()
        await combo.fill(codigo)
        opcao = self.page.get_by_role("option").filter(has_text=codigo).first
        await opcao.wait_for(timeout=10000)
        await opcao.click()
        # O menu precisa fechar antes de pesquisar, senão o texto digitado se perde.
        await self.page.wait_for_timeout(500)

    async def buscar(self, termo: str) -> list[ItemCatalogo]:
        caixa = self.page.get_by_role("textbox", name=sel.CAMPO_PESQUISAR)
        await caixa.click(click_count=3)
        await caixa.fill(termo)
        await caixa.press("Enter")
        await self.page.wait_for_load_state("networkidle", timeout=20000)
        await self.page.wait_for_timeout(1500)
        texto = await self.page.locator("body").inner_text()
        return self._cards_do_texto(texto)

    @staticmethod
    def _cards_do_texto(texto: str) -> list[ItemCatalogo]:
        """Separa os cards pela linha de preço e devolve só os que o parser entende."""
        import re

        blocos = re.split(r"(?=\n[^\n]+\n[^\n]+\n[^\n]+\nR\$ )", "\n" + texto)
        itens = [parse_card(b) for b in blocos]
        return [i for i in itens if i]

    # --- fechamento ---------------------------------------------------------------

    async def enviar_pedido(self) -> ResultadoEnvio:
        if self.dry_run:
            return ResultadoEnvio(False, "modo_teste")
        # O clique real só será implementado depois da autorização da empresa.
        return ResultadoEnvio(False, "nao_implementado")
