# Fluxo do sistema Nilo (observado)

Registro do que foi visto nos prints e na navegação de leitura. **Os seletores ainda não foram
validados no site real**; tudo aqui descreve o comportamento, não o HTML.

## Login

- Tela `/#/login` com três campos: CNPJ, login (formato `NNN-nome`) e senha.
- Os valores vêm de variáveis de ambiente (`NILO_CNPJ`, `NILO_LOGIN`, `NILO_SENHA`). Nunca no código.
- Depois do login o usuário aparece no topo (vendedor logado).

## Telas e etapas

| # | Tela | Endereço | O que a IA faz |
|---|---|---|---|
| 1 | Clientes cadastrados | `/#/vendedorFiles/listCli` | Não é necessária. A coluna **Checkin** sugere que o botão **+** pode registrar visita; evitar até confirmar. |
| 2 | Catálogo | `/#/catalogo/listCatCompleto` | Escolhe o cliente no seletor (itens no formato `código - nome`), digita no campo **Pesquisar** e aperta Enter. |
| 3 | Resultado da busca | mesma tela | Lê os cards: marca, código, descrição, valor unitário, quantidade múltipla, unidade e etiqueta (Disponível, Indisponível, Outra Unidade). 20 por página. |
| 4 | Detalhes do Produto | painel lateral ao clicar no card | Mostra a imagem (muitas vezes um desenho técnico), marca e código, descrição e os botões **Ficha Técnica**, **Aplicação**, **Conversão** e **Erro de Cadastro**. A aba **Aplicação** serve para conferir a compatibilidade. |
| 5 | Adicionar ao Carrinho | janela ao clicar em **Adicionar** | Mostra valor, disponibilidade e quantidade (setas). Botões **Continuar Comprando** e **Ir para o Carrinho**. |
| 6 | Pedidos em Aberto | `/#/pedidos/pedidosAbertos` | Lista o pedido aberto do cliente, com itens, quantidade, total e estoque por filial (JOI, ITJ, CH, SJ, CRI). Botões **Adicionar Item** e **Excluir Pedido**. |
| 7 | Enviar Pedido (Por filial) | janela ao clicar no botão da filial | Campos obrigatórios: **Cliente**, **Transportadora** e **Condição de Pagamento**. Há **Observações** (200 caracteres) e o botão **Enviar Pedido**. |

## Ações com efeito real (exigem confirmação do cliente e cuidado nos testes)

1. **Adicionar** ao carrinho: cria ou altera um pedido aberto no cliente.
2. **Excluir Pedido** e o ícone de lixeira do item: apagam dados. A IA não usa.
3. **Enviar Pedido**: envia o pedido ao sistema. É o ponto sem volta do projeto.

## Regras definidas pela empresa

| Tema | Regra | Código |
|---|---|---|
| Informações do pedido | Só busca com **peça, carro e ano**. Se faltar algo, pergunta só o que falta. | `app/agente/regras.py` |
| Compatibilidade | Confere o ano do carro com os anos abreviados da descrição. Se a descrição não basta, confere na aba **Aplicação**. | `app/agente/regras.py` |
| Filial | **Joinville primeiro.** Sem estoque, a próxima da ordem (JOI, ITJ, CH, SJ, CRI). Sem estoque em nenhuma, escala para humano. | `app/agente/pedido.py` |
| Pagamento | **28 dias** em 1 parcela. Se não existir, **à vista**. Se nenhuma, escala. | `app/agente/pedido.py` |
| Transportadora | Sempre pergunta ao cliente: **entrega** (MotoX Joinville) ou **retirada**. Retirada usa a opção da filial que despacha (Joinville: `RETIRA-JOI`). | `app/agente/pedido.py` |
| Cliente | O código vem do nome do contato salvo no WhatsApp (`012478-Nome`). Sem código, não adivinha: pergunta ou escala. | `app/agente/clientes.py` |
| Confirmação | Pede confirmação da peça. Só adiciona ao carrinho depois do "sim". | `app/agente/fluxo.py` |
| Mais peças | Depois de adicionar, pergunta se precisa de mais alguma peça. | `app/agente/fluxo.py` |

Sequência: pedido completo, busca, confirmação, adicionar, "precisa de mais alguma peça?",
"entrega ou retirada?", enviar.

## Modo de teste

`PEDIDO_DRY_RUN=true` (padrão) faz o robô ir até a janela **Enviar Pedido** e **parar antes de
clicar em enviar**. Só mude para `false` com autorização da empresa.

Durante os testes o robô só responde aos números de `TESTE_NUMEROS_PERMITIDOS`. Sem a lista, em
modo de teste, ele não responde a ninguém. Mensagens enviadas pela própria empresa nunca
disparam resposta.

## Pontos ainda em aberto

- Nome das opções de retirada das outras filiais (só `RETIRA-JOI` foi confirmada). Se a opção
  não existir, escala para humano em vez de escolher outra.
- Ordem das filiais depois de Joinville (hoje: ITJ, CH, SJ, CRI).
- Se o botão **+** da lista de clientes registra check-in (por isso não é usado).
- Origem da imagem (endereço direto ou apenas exibida na tela).
- Formato real do evento da Evolution (o código espera `data.key.remoteJid` e `data.key.fromMe`).

## Estratégia para a foto

A imagem aparece no painel **Detalhes do Produto**. A captura deve ser feita só do elemento da
imagem (recorte do elemento no Playwright), não da tela inteira. Assim o recorte não depende da
posição na tela.
