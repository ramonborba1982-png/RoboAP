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

## Pontos ainda em aberto

- Qual filial usar quando mais de uma tem estoque.
- Qual condição de pagamento usar (o campo é obrigatório e a lista tem opções como PIX, 7, 10, 28, 38, 42 e 49 dias).
- Qual transportadora usar (aparece uma pré-selecionada).
- Se o botão **+** da lista de clientes registra check-in.
- Origem da imagem (endereço direto ou apenas exibida na tela).

## Estratégia para a foto

A imagem aparece no painel **Detalhes do Produto**. A captura deve ser feita só do elemento da
imagem (recorte do elemento no Playwright), não da tela inteira. Assim o recorte não depende da
posição na tela.
