# RoboAP — Vendedor IA de Peças

Agente que atende clientes pelo WhatsApp, consulta peças no sistema da empresa e fecha o pedido.

## Fluxo

1. Cliente pede uma peça no WhatsApp (Evolution API).
2. O backend interpreta o pedido e consulta o site, com até 5 sessões simultâneas.
3. A IA envia preço, disponibilidade e foto da peça.
4. O cliente confirma e a IA fecha o pedido no site.
5. Casos que a IA não resolve são escalados para um humano no Chatwoot.

## Escopo

- Dentro: cotação, consulta, envio de imagem e fechamento do pedido.
- Fora: pagamento, envio físico e faturamento.

## Segurança

Nenhuma credencial fica neste repositório. Chaves, senhas e tokens são configurados
como variáveis de ambiente no servidor (veja `.env.example`, quando existir).

## Estado

Em construção. Já existem e estão testados: regras de pedido (peça, carro e ano), fluxo da
conversa, escolha de filial, pagamento e transportadora, e a trava de números de teste.
Ainda falta o módulo que opera o site Nilo e a ligação com o modelo de IA e com o Chatwoot.

O robô nasce em **modo de teste**: não envia pedido e só responde a números autorizados.
Veja `docs/nilo-fluxo.md`.

## Testes

```
pip install -r requirements.txt
python -m pytest -q
```
