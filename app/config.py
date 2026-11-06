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

    pedido_filial_padrao: str = ""
    pedido_condicao_pagamento_padrao: str = ""
    pedido_transportadora_padrao: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
