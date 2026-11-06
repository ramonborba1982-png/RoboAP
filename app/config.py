"""Configuração lida só de variáveis de ambiente. Nenhum segredo fica no código."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    evolution_api_url: str = ""
    evolution_instance: str = "ap"
    evolution_api_key: str = ""

    chatwoot_url: str = ""
    chatwoot_account_id: int = 1
    chatwoot_api_token: str = ""

    nilo_url: str = "https://nilo.autopratense.com.br"
    nilo_cnpj: str = ""
    nilo_login: str = ""
    nilo_senha: str = ""
    nilo_max_sessoes: int = Field(default=5, ge=1, le=10)

    anthropic_api_key: str = ""
    anthropic_model: str = ""

    database_url: str = ""

    gestor_whatsapp: str = ""
    webhook_secret: str = ""

    # Modo de teste: vai até a janela "Enviar Pedido" e PARA antes de clicar em enviar.
    # Só desligue (false) quando a empresa autorizar o envio real.
    pedido_dry_run: bool = True
    # Ordem de preferência das filiais. Joinville primeiro.
    pedido_filiais_ordem: str = "JOI,ITJ,CH,SJ,CRI"
    # Nome da opção de retirada na lista de transportadoras.
    pedido_transportadora_retira: str = "RETIRA-JOI"

    # Números autorizados a falar com o robô durante os testes (só dígitos, com DDI, separados
    # por vírgula). Em modo de teste, sem lista, o robô não responde a ninguém.
    teste_numeros_permitidos: str = ""

    @property
    def numeros_permitidos(self) -> tuple[str, ...]:
        return tuple(n.strip() for n in self.teste_numeros_permitidos.split(",") if n.strip())

    @property
    def filiais_ordem(self) -> tuple[str, ...]:
        return tuple(f.strip().upper() for f in self.pedido_filiais_ordem.split(",") if f.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()
