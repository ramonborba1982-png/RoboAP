"""Regras do pedido.

1. A busca só começa com as 3 informações: peça, veículo e ano.
2. Os resultados do catálogo são conferidos contra o ano do carro, lendo os anos
   abreviados das descrições (ex.: "2002/", "13/", "08/15").

A interpretação da conversa (extrair peça, veículo e ano do texto do cliente) fica com o
modelo de IA. Este módulo valida e decide, para que a regra seja testável.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from enum import Enum


class Compat(str, Enum):
    COMPATIVEL = "compativel"
    INCOMPATIVEL = "incompativel"
    # A descrição não diz o suficiente. Conferir na aba "Aplicação" do site antes de oferecer.
    INDETERMINADO = "indeterminado"


def _norm(texto: str) -> str:
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return sem_acento.lower().strip()


# ---------------------------------------------------------------------------
# As 3 informações obrigatórias
# ---------------------------------------------------------------------------

ANO_MINIMO = 1950


@dataclass
class PedidoInfo:
    peca: str = ""
    veiculo: str = ""
    ano: int | None = None

    def faltando(self, ano_ref: int | None = None) -> list[str]:
        ano_ref = ano_ref or date.today().year
        falta: list[str] = []
        if not self.peca.strip():
            falta.append("peca")
        if not self.veiculo.strip():
            falta.append("veiculo")
        if self.ano is None or not (ANO_MINIMO <= self.ano <= ano_ref + 1):
            falta.append("ano")
        return falta

    def completo(self, ano_ref: int | None = None) -> bool:
        return not self.faltando(ano_ref)

    def pergunta_faltante(self, ano_ref: int | None = None) -> str:
        """Pergunta ao cliente só o que ainda não foi dito."""
        nomes = {
            "peca": "a peça",
            "veiculo": "o carro (marca e modelo)",
            "ano": "o ano do carro",
        }
        partes = [nomes[f] for f in self.faltando(ano_ref)]
        if not partes:
            return ""
        if len(partes) == 1:
            lista = partes[0]
        else:
            lista = ", ".join(partes[:-1]) + " e " + partes[-1]
        return f"Para achar a peça certa, me diga {lista}, por favor."


# ---------------------------------------------------------------------------
# Compatibilidade de ano com a descrição do catálogo
# ---------------------------------------------------------------------------

# "2002/" "13/" "08/15" "93/01" "2010/2015". Não casa dentro de "208/2008" nem "712/812/814".
_ANO = re.compile(r"(?<![\d/])(\d{4}|\d{2})/(\d{4}|\d{2})?(?!\d)")
_PALAVRA = re.compile(r"[a-z0-9]+")

_MARCAS = {
    "fiat", "vw", "volkswagen", "chevrolet", "gm", "ford", "honda", "toyota", "hyundai",
    "renault", "peugeot", "citroen", "nissan", "jeep", "mitsubishi", "audi", "bmw",
    "mercedes", "mercedes-benz", "benz", "kia", "suzuki", "volvo", "land", "rover",
    "mini", "chery", "jac", "caoa", "subaru", "ram", "dodge", "chrysler", "iveco",
    "scania", "volare", "agrale",
}
_LIGACAO = {"de", "do", "da", "dos", "das", "novo", "nova"}


@dataclass(frozen=True)
class Aplicacao:
    contexto: str  # texto (normalizado) ao qual o intervalo de anos se refere
    ano_ini: int
    ano_fim: int | None  # None = de ano_ini em diante


def _ano_completo(valor: int, ano_ref: int) -> int:
    if valor >= 100:
        return valor
    return 2000 + valor if valor <= (ano_ref % 100) + 1 else 1900 + valor


def extrair_aplicacoes(descricao: str, ano_ref: int | None = None) -> list[Aplicacao]:
    """Lê os intervalos de ano da descrição e o texto a que cada um se refere.

    O ano vem depois do modelo ("A200 13/ B180 12/"). O texto depois do último ano
    ("CORSA 2002/ MONTANA") também pertence a esse último intervalo.
    """
    ano_ref = ano_ref or date.today().year
    texto = _norm(descricao)
    achados = list(_ANO.finditer(texto))
    aplicacoes: list[Aplicacao] = []
    fim_anterior = 0
    for i, m in enumerate(achados):
        ini = _ano_completo(int(m.group(1)), ano_ref)
        fim = _ano_completo(int(m.group(2)), ano_ref) if m.group(2) else None
        contexto = texto[fim_anterior : m.start()]
        if i == len(achados) - 1:
            contexto += " " + texto[m.end() :]
        aplicacoes.append(Aplicacao(contexto, ini, fim))
        fim_anterior = m.end()
    return aplicacoes


def _modelo_principal(veiculo: str) -> str:
    for token in _PALAVRA.findall(_norm(veiculo)):
        if token not in _MARCAS and token not in _LIGACAO:
            return token
    return ""


def compatibilidade(
    descricao: str, veiculo: str, ano: int, ano_ref: int | None = None
) -> Compat:
    """Diz se a descrição do catálogo atende ao veículo e ao ano do cliente."""
    modelo = _modelo_principal(veiculo)
    aplicacoes = extrair_aplicacoes(descricao, ano_ref)
    if not modelo or not aplicacoes:
        return Compat.INDETERMINADO

    achou_modelo = False
    for ap in aplicacoes:
        if modelo in _PALAVRA.findall(ap.contexto):
            achou_modelo = True
            limite = ap.ano_fim if ap.ano_fim is not None else 9999
            if ap.ano_ini <= ano <= limite:
                return Compat.COMPATIVEL
    return Compat.INCOMPATIVEL if achou_modelo else Compat.INDETERMINADO
