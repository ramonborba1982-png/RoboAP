from app.agente.clientes import extrair_codigo_cliente


def test_codigo_com_hifen():
    assert extrair_codigo_cliente("012478-Reinert e Borba") == "012478"


def test_mantem_zeros_a_esquerda():
    assert extrair_codigo_cliente("008723-Dorival") == "008723"


def test_codigo_com_espacos_e_ponto():
    assert extrair_codigo_cliente("012132 - VH Auto Center") == "012132"
    assert extrair_codigo_cliente("012074. Auto Pecas") == "012074"
    assert extrair_codigo_cliente("  024742-Superpartes") == "024742"


def test_contato_sem_codigo_nao_e_adivinhado():
    assert extrair_codigo_cliente("Maria da Silva") is None
    assert extrair_codigo_cliente("") is None
    assert extrair_codigo_cliente(None) is None


def test_numero_de_telefone_nao_vira_codigo():
    assert extrair_codigo_cliente("+55 47 99123-4567") is None
    assert extrair_codigo_cliente("5547991234567") is None


def test_codigo_curto_demais_ou_no_meio_do_nome():
    assert extrair_codigo_cliente("12-Fulano") is None
    assert extrair_codigo_cliente("Loja 012478-Fulano") is None
