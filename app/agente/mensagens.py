"""Textos enviados ao cliente no WhatsApp."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ItemCatalogo:
    marca: str
    codigo: str
    descricao: str
    preco: Decimal
    unidade: str = ""  # ex.: "1 JG" (quantidade múltipla)
    disponibilidade: str = "Disponível"


def formatar_preco(valor: Decimal) -> str:
    """59.96 -> 'R$ 59,96'; 1234.5 -> 'R$ 1.234,50'."""
    inteiro, centavos = f"{valor:,.2f}".split(".")
    return f"R$ {inteiro.replace(',', '.')},{centavos}"


def _linha_item(item: ItemCatalogo) -> str:
    unidade = f" ({item.unidade})" if item.unidade else ""
    return f"{item.marca} {item.codigo} - {item.descricao}\n{formatar_preco(item.preco)}{unidade}"


def pedir_confirmacao(item: ItemCatalogo) -> str:
    return (
        "Encontrei esta peça:\n\n"
        f"*{_linha_item(item)}*\n\n"
        "Posso adicionar ao seu pedido? Responda *sim* para confirmar."
    )


def listar_opcoes(itens: list[ItemCatalogo], limite: int = 5) -> str:
    linhas = ["Encontrei estas opções:", ""]
    for numero, item in enumerate(itens[:limite], start=1):
        linhas.append(f"*{numero})* {_linha_item(item)}")
        if item.disponibilidade != "Disponível":
            linhas.append(f"({item.disponibilidade})")
        linhas.append("")
    linhas.append("Qual você prefere? Responda com o número ou a marca.")
    return "\n".join(linhas)


def perguntar_mais_pecas() -> str:
    return "Peça adicionada ao seu pedido. Precisa de mais alguma peça?"


def perguntar_entrega() -> str:
    return "Certo! O pedido é para *entrega* ou você vai *retirar*?"


def avisar_envio(entrega: bool) -> str:
    como = "será entregue pela MotoX" if entrega else "ficará separado para retirada"
    return f"Pedido enviado. Sua peça {como}. Obrigado!"
