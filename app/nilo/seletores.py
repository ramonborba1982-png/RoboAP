"""Seletores do Nilo em um só lugar, para ajustar sem mexer na lógica.

NÃO VALIDADOS em execução real. Vieram da leitura da página (papéis e rótulos). Rode
scripts/validar_nilo.py no servidor e corrija aqui o que falhar.
"""

import re

URL_LOGIN = "/#/login"
URL_CATALOGO = "/#/catalogo/listCatCompleto"
URL_CARRINHO = "/#/pedidos/pedidosAbertos"

CAMPO_CNPJ = re.compile(r"cnpj", re.I)
CAMPO_LOGIN = re.compile(r"login|usu[aá]rio", re.I)
CAMPO_SENHA = re.compile(r"senha", re.I)
BOTAO_ENTRAR = re.compile(r"entrar|login|acessar", re.I)

COMBO_CLIENTE = re.compile(r"cliente", re.I)
CAMPO_PESQUISAR = re.compile(r"pesquisar", re.I)
BOTAO_ADICIONAR = re.compile(r"^adicionar$", re.I)
BOTAO_CONTINUAR = re.compile(r"continuar comprando", re.I)
BOTAO_IR_CARRINHO = re.compile(r"ir para o carrinho", re.I)
ABA_APLICACAO = re.compile(r"aplica[cç][aã]o", re.I)

# Nunca clicar nestes (ações destrutivas ou sem volta). Conferido antes de qualquer clique.
PROIBIDOS = re.compile(r"excluir pedido|enviar pedido|excluir|remover|lixeira", re.I)
