from app.config import Settings


def limpo(monkeypatch):
    for nome in ("PEDIDO_DRY_RUN", "PEDIDO_FILIAIS_ORDEM", "PEDIDO_TRANSPORTADORA_RETIRA"):
        monkeypatch.delenv(nome, raising=False)


def test_modo_de_teste_vem_ligado_por_padrao(monkeypatch):
    limpo(monkeypatch)
    assert Settings(_env_file=None).pedido_dry_run is True


def test_modo_de_teste_so_desliga_de_proposito(monkeypatch):
    limpo(monkeypatch)
    monkeypatch.setenv("PEDIDO_DRY_RUN", "false")
    assert Settings(_env_file=None).pedido_dry_run is False


def test_joinville_e_a_primeira_filial(monkeypatch):
    limpo(monkeypatch)
    assert Settings(_env_file=None).filiais_ordem[0] == "JOI"


def test_ordem_das_filiais_aceita_espacos_e_minusculas(monkeypatch):
    limpo(monkeypatch)
    monkeypatch.setenv("PEDIDO_FILIAIS_ORDEM", " joi , itj ,, ch ")
    assert Settings(_env_file=None).filiais_ordem == ("JOI", "ITJ", "CH")


def test_sem_segredos_por_padrao(monkeypatch):
    # Nenhum valor secreto vem embutido no código.
    for nome in ("EVOLUTION_API_KEY", "NILO_SENHA", "ANTHROPIC_API_KEY", "WEBHOOK_SECRET"):
        monkeypatch.delenv(nome, raising=False)
    s = Settings(_env_file=None)
    assert s.evolution_api_key == "" and s.nilo_senha == ""
    assert s.anthropic_api_key == "" and s.webhook_secret == ""
