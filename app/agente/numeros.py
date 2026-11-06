"""Quem pode conversar com o robô.

Em modo de teste o robô responde só aos números da lista de teste. Sem lista, em teste, não
responde a ninguém (falha fechada). Em produção, sem lista, responde a todos os clientes.
"""

from __future__ import annotations


def apenas_digitos(valor: str) -> str:
    """'554791234567:12@s.whatsapp.net' -> '554791234567'."""
    antes_do_arroba = valor.split("@", 1)[0].split(":", 1)[0]
    return "".join(c for c in antes_do_arroba if c.isdigit())


def normalizar_numero(valor: str) -> str:
    """Iguala números brasileiros com e sem o nono dígito.

    5547991234567 (13 dígitos) e 554791234567 (12 dígitos) são o mesmo celular.
    """
    n = apenas_digitos(valor)
    if n.startswith("55") and len(n) == 13 and n[4] == "9":
        return n[:4] + n[5:]
    return n


def numero_permitido(numero: str, permitidos: tuple[str, ...], dry_run: bool) -> bool:
    alvo = normalizar_numero(numero)
    if not alvo:
        return False
    if permitidos:
        return alvo in {normalizar_numero(p) for p in permitidos}
    return not dry_run


def extrair_remetente(payload: dict) -> tuple[str, bool]:
    """Devolve (número, enviada_pela_empresa) de um evento messages.upsert da Evolution.

    Formato esperado (confirmar com um evento real):
      {"data": {"key": {"remoteJid": "5547...@s.whatsapp.net", "fromMe": false}}}
    """
    data = payload.get("data")
    if isinstance(data, list) and data:
        data = data[0]
    if not isinstance(data, dict):
        return "", False
    chave = data.get("key") or {}
    return str(chave.get("remoteJid", "")), bool(chave.get("fromMe", False))
