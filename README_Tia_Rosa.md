# Sistema de Gerenciamento para Coffee Shops Tia Rosa

Este repositório contém um sistema completo de gerenciamento de pedidos, cardápio e fidelização de clientes, desenvolvido inteiramente em Python, com base nas necessidades operacionais da cafeteria fictícia *Coffee Shops Tia Rosa*. O sistema foi pensado para ser simples, funcional, claro e acessível a colaboradores com pouca familiaridade com tecnologia.

## Objetivo

Desenvolver um sistema autoral, funcional e didático, que permita a simulação do atendimento e da gestão diária da cafeteria, utilizando exclusivamente recursos da linguagem Python padrão.

## Funcionalidades Implementadas

- Cadastro de produtos no cardápio, com categorias, preços, ingredientes e promoções
- Cadastro de clientes com controle de pontos de fidelidade e histórico de pedidos
- Registro de comandas com data, hora e valor total
- Sugestão personalizada de itens com base no histórico do cliente
- Combos prontos com nomes temáticos inspirados no Rio de Janeiro
- Relatório de vendas do dia, com resumo e ranking dos itens mais vendidos
- Salvamento e carregamento automático dos dados em arquivos JSON

## Tecnologias Utilizadas

- Python 3 (sem bibliotecas externas)
- Bibliotecas padrão: `json`, `datetime`, `os`, `random`, `collections`

Obs: o uso da biblioteca `colorama` é opcional, apenas para exibição colorida no terminal. O sistema também funciona normalmente sem ela. 

## Estrutura

O sistema foi organizado em funções e classes para manter clareza e escalabilidade. As principais estruturas utilizadas incluem:

- `ItemCardapio`: representa um item individual do cardápio
- `Cliente`: representa um cliente com seus dados e pontos acumulados
- `Comanda`: representa um pedido fechado com data, itens e valor
- Arquivos `.json` para persistência local dos dados
- Lógica personalizada para sugestões, fidelização e promoções

## Instruções de Execução

1. Certifique-se de ter o Python 3 instalado em seu computador.
2. Baixe o arquivo do sistema.
3. Execute o script pelo terminal com o comando:

```bash
python nome_do_arquivo.py
