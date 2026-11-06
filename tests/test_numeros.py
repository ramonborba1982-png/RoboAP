from app.agente.numeros import (
    apenas_digitos,
    extrair_remetente,
    normalizar_numero,
    numero_permitido,
)


def test_jid_vira_so_digitos():
    assert apenas_digitos("554791234567@s.whatsapp.net") == "554791234567"
    assert apenas_digitos("554791234567:12@s.whatsapp.net") == "554791234567"
    assert apenas_digitos("+55 (47) 99123-4567") == "5547991234567"


def test_nono_digito_nao_atrapalha():
    com = "5547991234567"
    sem = "554791234567"
    assert normalizar_numero(com) == normalizar_numero(sem) == sem


def test_numero_fora_do_padrao_nao_e_alterado():
    assert normalizar_numero("5511912345678") == "551112345678"  # 13 dígitos com 9: igualado
    assert normalizar_numero("12345") == "12345"


def test_so_numeros_da_lista_em_teste():
    lista = ("5547990000001",)
    assert numero_permitido("554790000001@s.whatsapp.net", lista, dry_run=True)
    assert not numero_permitido("5547988887777@s.whatsapp.net", lista, dry_run=True)


def test_teste_sem_lista_nao_responde_a_ninguem():
    assert not numero_permitido("5547990000001", (), dry_run=True)


def test_producao_sem_lista_responde_a_todos():
    assert numero_permitido("5547990000001", (), dry_run=False)


def test_lista_vale_tambem_em_producao():
    lista = ("5547990000001",)
    assert not numero_permitido("5547988887777", lista, dry_run=False)


def test_numero_vazio_nunca_passa():
    assert not numero_permitido("", (), dry_run=False)
    assert not numero_permitido("@s.whatsapp.net", ("5547990000001",), dry_run=True)


def test_extrai_remetente_da_evolution():
    payload = {
        "event": "messages.upsert",
        "data": {"key": {"remoteJid": "5547990000001@s.whatsapp.net", "fromMe": False}},
    }
    assert extrair_remetente(payload) == ("5547990000001@s.whatsapp.net", False)


def test_mensagem_enviada_pela_propria_empresa():
    payload = {"data": {"key": {"remoteJid": "5547990000001@s.whatsapp.net", "fromMe": True}}}
    assert extrair_remetente(payload)[1] is True


def test_payload_em_lista_e_payload_estranho():
    lista = {"data": [{"key": {"remoteJid": "5547990000001@s.whatsapp.net", "fromMe": False}}]}
    assert extrair_remetente(lista)[0] == "5547990000001@s.whatsapp.net"
    assert extrair_remetente({}) == ("", False)
    assert extrair_remetente({"data": "texto"}) == ("", False)


def test_lid_usa_remotejidalt():
    from app.agente.numeros import extrair_nome_perfil, extrair_texto

    payload = {
        "data": {
            "key": {"remoteJid": "123@lid", "remoteJidAlt": "5547990000001@s.whatsapp.net", "fromMe": False},
            "pushName": "Fulano",
            "message": {"conversation": " pastilha corsa 2008 "},
        }
    }
    assert extrair_remetente(payload)[0] == "5547990000001@s.whatsapp.net"
    assert extrair_texto(payload) == "pastilha corsa 2008"
    assert extrair_nome_perfil(payload) == "Fulano"
    assert extrair_texto({"data": {"message": {"extendedTextMessage": {"text": "oi"}}}}) == "oi"
    assert extrair_texto({"data": {"message": {"imageMessage": {}}}}) == ""
