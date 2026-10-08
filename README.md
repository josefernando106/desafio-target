## DESAFIO

1. Considerando que o json de vendas tem registros de vendas de um time comercial, faça um programa que leia os dados e calcule a comissão de cada vendedor, seguindo a seguinte regra para cada venda:
    - Vendas abaixo de R$100,00 não gera comissão
    - Vendas abaixo de R$500,00 gera 1% de comissão
    - A partir de R$500,00 gera 5% de comissão

{
  "vendas": [
    { "vendedor": "João Silva", "valor": 1200.50 },
    { "vendedor": "João Silva", "valor": 950.75 },
    { "vendedor": "João Silva", "valor": 1800.00 },
    { "vendedor": "João Silva", "valor": 1400.30 },
    { "vendedor": "João Silva", "valor": 1100.90 },
    { "vendedor": "João Silva", "valor": 1550.00 },
    { "vendedor": "João Silva", "valor": 1700.80 },
    { "vendedor": "João Silva", "valor": 250.30 },
    { "vendedor": "João Silva", "valor": 480.75 },
    { "vendedor": "João Silva", "valor": 320.40 },
    
    { "vendedor": "Maria Souza", "valor": 2100.40 },
    { "vendedor": "Maria Souza", "valor": 1350.60 },
    { "vendedor": "Maria Souza", "valor": 950.20 },
    { "vendedor": "Maria Souza", "valor": 1600.75 },
    { "vendedor": "Maria Souza", "valor": 1750.00 },
    { "vendedor": "Maria Souza", "valor": 1450.90 },
    { "vendedor": "Maria Souza", "valor": 400.50 },
    { "vendedor": "Maria Souza", "valor": 180.20 },
    { "vendedor": "Maria Souza", "valor": 90.75 },
    
    { "vendedor": "Carlos Oliveira", "valor": 800.50 },
    { "vendedor": "Carlos Oliveira", "valor": 1200.00 },
    { "vendedor": "Carlos Oliveira", "valor": 1950.30 },
    { "vendedor": "Carlos Oliveira", "valor": 1750.80 },
    { "vendedor": "Carlos Oliveira", "valor": 1300.60 },
    { "vendedor": "Carlos Oliveira", "valor": 300.40 },
    { "vendedor": "Carlos Oliveira", "valor": 500.00 },
    { "vendedor": "Carlos Oliveira", "valor": 125.75 },
    
    { "vendedor": "Ana Lima", "valor": 1000.00 },
    { "vendedor": "Ana Lima", "valor": 1100.50 },
    { "vendedor": "Ana Lima", "valor": 1250.75 },
    { "vendedor": "Ana Lima", "valor": 1400.20 },
    { "vendedor": "Ana Lima", "valor": 1550.90 },
    { "vendedor": "Ana Lima", "valor": 1650.00 },
    { "vendedor": "Ana Lima", "valor": 75.30 },
    { "vendedor": "Ana Lima", "valor": 420.90 },
    { "vendedor": "Ana Lima", "valor": 315.40 }
  ]
}

2. Faça um programa onde eu possa lançar movimentações de estoque dos produtos que estão no json abaixo, dando entrada ou saída da mercadoria no meu depósito, onde cada movimentação deve ter:
    - Um número identificador único.
    - Uma descrição para identificar o tipo da movimentação realizada
E que ao final da movimentação me retorne a qtde final do estoque do produto movimentado.

{
	"estoque":
	[
	  {
		"codigoProduto": 101,
		"descricaoProduto": "Caneta Azul",
		"estoque": 150
	  },
	  {
		"codigoProduto": 102,
		"descricaoProduto": "Caderno Universitário",
		"estoque": 75
	  },
	  {
		"codigoProduto": 103,
		"descricaoProduto": "Borracha Branca",
		"estoque": 200
	  },
	  {
		"codigoProduto": 104,
		"descricaoProduto": "Lápis Preto HB",
		"estoque": 320
	  },
	  {
		"codigoProduto": 105,
		"descricaoProduto": "Marcador de Texto Amarelo",
		"estoque": 90
	  }
	]
}


3. Faça um programa que a partir de um valor e de uma data de vencimento, calcule o valor dos juros na data de hoje considerando que a multa seja de 2,5% ao dia.


## Resolução

Guia passo a passo para construir a solução. A ideia é entender **o que** cada parte faz e **por quê**, antes de escrever o código.

### Visão geral

- **Linguagem:** Python 3.10 ou superior.
- **Interface:** Tkinter, que já vem instalado com o Python. Não é preciso instalar nenhuma biblioteca.
- **Organização:** a regra de negócio fica separada da interface. Cada desafio tem um arquivo só com a lógica (funções simples, fáceis de testar). A interface apenas lê o que o usuário digita, chama essas funções e mostra o resultado.

```
desafio-target/
├── vendas.json            # dados do desafio 1 (alterado ao incluir/remover vendas)
├── estoque.json           # saldo inicial do desafio 2 (não alterar)
├── movimentacoes.json     # criado automaticamente pelo sistema (histórico)
├── app.py                 # interface gráfica (janela com 3 abas)
├── desafio/
│   ├── __init__.py        # marca a pasta como pacote Python
│   ├── formatacao.py      # funções auxiliares (R$ e leitura de valores)
│   ├── comissao.py        # desafio 1
│   ├── estoque.py         # desafio 2
│   └── juros.py           # desafio 3
└── tests/
    └── test_desafio.py    # testes automáticos das regras
```

```
 Usuário ──► app.py (Tkinter) ──► desafio/*.py (regras) ──► arquivos .json
            mostra o resultado ◄──────── retorna os valores calculados
```

### Testes automáticos (`tests/test_desafio.py`)

Use o `unittest`, que já vem com o Python. Teste principalmente os **casos de fronteira**:

| Teste                                | Esperado              |
|--------------------------------------|-----------------------|
| comissão de 99,99                    | 0,00                  |
| comissão de 100,00                   | 1,00                  |
| comissão de 499,99                   | 5,00                  |
| comissão de 500,00                   | 25,00                 |
| saída maior que o estoque            | gera `ValueError`     |
| entrada de 10 na Caneta Azul (150)   | estoque final 160     |
| dois lançamentos seguidos            | IDs 1 e 2             |
| juros com vencimento no futuro       | 0 dias, juros 0,00    |
| 1000,00 vencido há 10 dias           | juros 250,00          |

Nos testes de estoque, crie o `Estoque` **sem** o caminho do `movimentacoes.json`. Assim, os testes não sujam o histórico real.

Para rodar:

```bash
python -m unittest discover tests
```

---

### Executar o sistema

Rode o comando abaixo **na pasta do projeto**. É dessa pasta que o Python encontra o pacote `desafio/` e os arquivos `.json`.

```bash
python app.py
```

**Roteiro para conferir cada aba:**

1. **Comissões:** a tabela já abre preenchida com os 4 vendedores. Clique em um vendedor e confira, na tabela de baixo, o percentual aplicado em cada venda. Por exemplo, a venda de R$ 90,75 da Maria tem 0% de comissão, e a de R$ 500,00 do Carlos tem 5%.
   - **Incluir:** selecione a Ana Lima, digite `600` no valor e clique em **Incluir venda**. A quantidade de vendas dela sobe de 9 para 10, e a comissão aumenta R$ 30,00 (5% de 600).
   - **Remover:** na tabela de baixo, selecione a venda de R$ 600,00, clique em **Remover venda selecionada** e confirme. Os valores voltam ao que eram antes.
   - **Vendedor novo:** digite um nome que não existe (ex.: "Pedro Costa"), um valor qualquer, e ele aparece como uma nova linha no resumo.
   - **Erros:** tente incluir sem nome ou com valor `0`. Deve aparecer uma janela de erro.
2. **Estoque:**
   1. Escolha "101 - Caneta Azul", marque *Saída*, quantidade 30, descrição "Venda balcão" e clique em **Lançar**. A mensagem deve ser *"Movimentação #1 registrada. Estoque final de 'Caneta Azul': 120"*.
   2. Tente uma saída de 500 do mesmo produto. Deve aparecer a janela de erro *"Estoque insuficiente"*.
   3. Feche e abra o programa de novo. O saldo (120) e o histórico continuam lá, e o próximo ID será 2.
   4. Para voltar ao estoque original, apague o arquivo `movimentacoes.json`.
3. **Juros:** digite o valor `1000` e uma data de vencimento 10 dias antes de hoje. O resultado deve ser *10 dia(s) de atraso, juros R$ 250,00 e total R$ 1.250,00*. Depois teste uma data futura (juros zero) e uma data inválida, como `31/02/2026` (deve aparecer uma janela de erro).

**Como o código está organizado (`app.py`):**

| Trecho                       | Passo do README | O que faz                                                        |
|------------------------------|-----------------|------------------------------------------------------------------|
| `criar_tabela()`             | 5.1             | função auxiliar que cria um `Treeview` com barra de rolagem      |
| `class AbaComissoes`         | 5.3             | carrega as vendas, mostra o resumo e o detalhe; `incluir()`, `remover()` e `salvar()` |
| `class AbaEstoque`           | 5.4             | formulário, `lancar()` com `try/except` e `atualizar()` das tabelas |
| `class AbaJuros`             | 5.5             | lê os campos, chama `calcular_juros()` e mostra o resultado      |
| `main()`                     | 5.2             | cria a janela, os estilos e as 3 abas, e chama `mainloop()`      |

Cada aba é uma **classe** que herda de `ttk.Frame`. Assim, os campos (`self.valor`, `self.tabela`...) ficam guardados dentro do objeto, e os métodos dos botões conseguem acessá-los.

O `if __name__ == "__main__":` no final faz a janela abrir apenas quando o arquivo é executado diretamente, e não quando ele é importado por outro arquivo.

O `.gitignore` deixa `movimentacoes.json` e `__pycache__/` fora do Git. Esses arquivos são gerados enquanto o programa roda e não fazem parte do código.

