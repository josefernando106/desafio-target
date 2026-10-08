"""
Executar com:  python app.py
"""
import tkinter as tk
from datetime import date
from decimal import Decimal
from pathlib import Path
from tkinter import messagebox, ttk

from desafio.comissao import adicionar_venda, carregar_vendas, resumir_por_vendedor, salvar_vendas
from desafio.estoque import ENTRADA, SAIDA, Estoque
from desafio.formatacao import formatar_moeda, ler_valor
from desafio.juros import calcular_juros, ler_data

PASTA = Path(__file__).parent
ARQ_VENDAS = PASTA / "vendas.json"
ARQ_ESTOQUE = PASTA / "estoque.json"
ARQ_MOVIMENTACOES = PASTA / "movimentacoes.json"


def criar_tabela(pai, colunas, altura=8):
    """Cria um Treeview com barra de rolagem. colunas = [(titulo, largura, alinhamento)]."""
    moldura = ttk.Frame(pai)
    tabela = ttk.Treeview(moldura, columns=[c[0] for c in colunas], show="headings", height=altura)
    for titulo, largura, alinhamento in colunas:
        tabela.heading(titulo, text=titulo)
        tabela.column(titulo, width=largura, anchor=alinhamento)
    rolagem = ttk.Scrollbar(moldura, orient="vertical", command=tabela.yview)
    tabela.configure(yscrollcommand=rolagem.set)
    tabela.pack(side="left", fill="both", expand=True)
    rolagem.pack(side="right", fill="y")
    return moldura, tabela


def limpar_tabela(tabela):
    tabela.delete(*tabela.get_children())


# --------------------------------------------------------------------------- #
# Aba 1 - Comissões (Passo 5.3)
# --------------------------------------------------------------------------- #
class AbaComissoes(ttk.Frame):
    def __init__(self, pai):
        super().__init__(pai, padding=10)
        self.vendas = []  # lista completa, na mesma ordem do vendas.json

        ttk.Label(self, text="Comissão por vendedor", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            self, text="Regra por venda: < R$ 100 → 0%  |  < R$ 500 → 1%  |  ≥ R$ 500 → 5%"
        ).pack(anchor="w", pady=(0, 8))

        # A linha de cada vendedor usa o próprio nome como iid (identificador da linha)
        moldura, self.tabela = criar_tabela(
            self,
            [("Vendedor", 200, "w"), ("Qtd. vendas", 100, "center"),
             ("Total vendido", 150, "e"), ("Comissão", 150, "e")],
            altura=5,
        )
        moldura.pack(fill="x")
        self.tabela.bind("<<TreeviewSelect>>", self.mostrar_detalhes)

        self.total = tk.StringVar()
        ttk.Label(self, textvariable=self.total, style="Destaque.TLabel").pack(anchor="e", pady=4)

        # Formulário para incluir venda
        form = ttk.LabelFrame(self, text="Incluir venda", padding=8)
        form.pack(fill="x")

        ttk.Label(form, text="Vendedor:").grid(row=0, column=0, sticky="w")
        self.vendedor = ttk.Combobox(form, width=30)  # editável: aceita um nome novo
        self.vendedor.grid(row=0, column=1, sticky="w", padx=(4, 12))

        ttk.Label(form, text="Valor (R$):").grid(row=0, column=2, sticky="w")
        self.valor = tk.StringVar()
        campo_valor = ttk.Entry(form, textvariable=self.valor, width=15)
        campo_valor.grid(row=0, column=3, sticky="w", padx=(4, 12))
        campo_valor.bind("<Return>", lambda _evento: self.incluir())

        ttk.Button(form, text="Incluir venda", command=self.incluir).grid(row=0, column=4)
        ttk.Label(form, text="Escolha um vendedor da lista ou digite um nome novo.", foreground="gray").grid(
            row=1, column=0, columnspan=5, sticky="w", pady=(4, 0))

        self.mensagem = tk.StringVar()
        ttk.Label(self, textvariable=self.mensagem, style="Destaque.TLabel").pack(anchor="w", pady=4)

        # Vendas do vendedor selecionado: o iid de cada linha é a posição da venda em self.vendas
        ttk.Label(self, text="Vendas do vendedor selecionado:").pack(anchor="w", pady=(4, 2))
        moldura, self.detalhes = criar_tabela(
            self,
            [("Valor da venda", 150, "e"), ("Percentual", 100, "center"), ("Comissão", 150, "e")],
            altura=6,
        )
        moldura.pack(fill="both", expand=True)

        botoes = ttk.Frame(self)
        botoes.pack(fill="x", pady=(8, 0))
        ttk.Button(botoes, text="Remover venda selecionada", command=self.remover).pack(side="left")
        ttk.Button(botoes, text="Recarregar vendas.json", command=self.carregar).pack(side="right")

        self.carregar()

    def carregar(self):
        try:
            self.vendas = carregar_vendas(ARQ_VENDAS)
        except (OSError, ValueError, KeyError) as erro:
            messagebox.showerror("Erro ao ler vendas", str(erro))
            return
        self.mensagem.set("")
        self.atualizar()

    def atualizar(self, vendedor=None):
        """Recalcula as comissões e redesenha as tabelas, selecionando o vendedor informado."""
        resumos = resumir_por_vendedor(self.vendas)
        self.vendedor["values"] = [r.vendedor for r in resumos]

        limpar_tabela(self.tabela)
        limpar_tabela(self.detalhes)
        for r in resumos:
            self.tabela.insert("", "end", iid=r.vendedor, values=(
                r.vendedor, len(r.vendas), formatar_moeda(r.total_vendido), formatar_moeda(r.comissao)
            ))
        total = sum((r.comissao for r in resumos), Decimal("0"))
        self.total.set(f"Total de comissões: {formatar_moeda(total)}")

        if vendedor and self.tabela.exists(vendedor):
            self.tabela.selection_set(vendedor)  # dispara mostrar_detalhes
            self.tabela.see(vendedor)

    def mostrar_detalhes(self, _evento=None):
        limpar_tabela(self.detalhes)
        selecao = self.tabela.selection()
        if not selecao:
            return
        nome = selecao[0]
        self.vendedor.set(nome)  # facilita incluir outra venda para o mesmo vendedor
        for indice, venda in enumerate(self.vendas):
            if venda.vendedor == nome:
                self.detalhes.insert("", "end", iid=str(indice), values=(
                    formatar_moeda(venda.valor), f"{venda.percentual * 100:.0f}%", formatar_moeda(venda.comissao)
                ))

    def incluir(self):
        try:
            venda = adicionar_venda(self.vendas, self.vendedor.get(), ler_valor(self.valor.get()))
        except ValueError as erro:
            messagebox.showerror("Venda não incluída", str(erro))
            return
        if not self.salvar():
            return
        self.valor.set("")
        self.atualizar(venda.vendedor)
        self.mensagem.set(
            f"Venda de {formatar_moeda(venda.valor)} incluída para {venda.vendedor} "
            f"(comissão {formatar_moeda(venda.comissao)})."
        )

    def remover(self):
        selecao = self.detalhes.selection()
        if not selecao:
            messagebox.showwarning("Remover venda", "Selecione uma venda na tabela \"Vendas do vendedor selecionado\".")
            return
        indice = int(selecao[0])
        venda = self.vendas[indice]
        if not messagebox.askyesno(
            "Remover venda", f"Remover a venda de {formatar_moeda(venda.valor)} de {venda.vendedor}?"
        ):
            return
        del self.vendas[indice]
        if not self.salvar():
            return
        self.atualizar(venda.vendedor)
        self.mensagem.set(f"Venda de {formatar_moeda(venda.valor)} removida de {venda.vendedor}.")

    def salvar(self):
        """Grava no vendas.json. Se falhar, recarrega o arquivo para desfazer a alteração na tela."""
        try:
            salvar_vendas(ARQ_VENDAS, self.vendas)
            return True
        except OSError as erro:
            messagebox.showerror("Erro ao salvar vendas.json", str(erro))
            self.carregar()
            return False


# --------------------------------------------------------------------------- #
# Aba 2 - Estoque (Passo 5.4)
# --------------------------------------------------------------------------- #
class AbaEstoque(ttk.Frame):
    def __init__(self, pai):
        super().__init__(pai, padding=10)
        self.estoque = Estoque(ARQ_ESTOQUE, ARQ_MOVIMENTACOES)

        ttk.Label(self, text="Movimentação de estoque", style="Titulo.TLabel").pack(anchor="w", pady=(0, 8))

        # Formulário
        form = ttk.Frame(self)
        form.pack(fill="x")

        ttk.Label(form, text="Produto:").grid(row=0, column=0, sticky="w", pady=3)
        self.produto = ttk.Combobox(form, state="readonly", width=40)
        self.produto.grid(row=0, column=1, columnspan=2, sticky="w")

        ttk.Label(form, text="Tipo:").grid(row=1, column=0, sticky="w", pady=3)
        self.tipo = tk.StringVar(value=ENTRADA)
        ttk.Radiobutton(form, text="Entrada", value=ENTRADA, variable=self.tipo).grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(form, text="Saída", value=SAIDA, variable=self.tipo).grid(row=1, column=2, sticky="w")

        ttk.Label(form, text="Quantidade:").grid(row=2, column=0, sticky="w", pady=3)
        self.quantidade = tk.StringVar(value="1")
        ttk.Spinbox(form, from_=1, to=100000, textvariable=self.quantidade, width=10).grid(
            row=2, column=1, sticky="w")

        ttk.Label(form, text="Descrição:").grid(row=3, column=0, sticky="w", pady=3)
        self.descricao = tk.StringVar()
        ttk.Entry(form, textvariable=self.descricao, width=43).grid(row=3, column=1, columnspan=2, sticky="w")

        ttk.Button(form, text="Lançar movimentação", command=self.lancar).grid(
            row=4, column=1, sticky="w", pady=6)

        self.resultado = tk.StringVar()
        ttk.Label(self, textvariable=self.resultado, style="Destaque.TLabel").pack(anchor="w", pady=4)

        # Tabelas
        ttk.Label(self, text="Saldo atual:").pack(anchor="w")
        moldura, self.tabela_produtos = criar_tabela(
            self, [("Código", 80, "center"), ("Produto", 260, "w"), ("Estoque", 100, "e")], altura=5)
        moldura.pack(fill="x")

        ttk.Label(self, text="Histórico de movimentações:").pack(anchor="w", pady=(8, 0))
        moldura, self.tabela_movs = criar_tabela(
            self,
            [("ID", 50, "center"), ("Data/hora", 140, "center"), ("Produto", 180, "w"),
             ("Tipo", 80, "center"), ("Qtd.", 60, "e"), ("Descrição", 180, "w"), ("Estoque final", 100, "e")],
        )
        moldura.pack(fill="both", expand=True)

        self.atualizar()

    def lancar(self):
        try:
            if not self.produto.get():
                raise ValueError("Selecione um produto.")
            codigo = int(self.produto.get().split(" - ")[0])
            try:
                quantidade = int(self.quantidade.get())
            except ValueError:
                raise ValueError("A quantidade deve ser um número inteiro.")
            mov = self.estoque.movimentar(codigo, self.tipo.get(), quantidade, self.descricao.get())
        except ValueError as erro:
            messagebox.showerror("Movimentação não realizada", str(erro))
            return

        produto = self.estoque.produtos[codigo]
        self.resultado.set(
            f"Movimentação #{mov.id} registrada. Estoque final de '{produto.descricao}': {mov.estoque_final}"
        )
        self.descricao.set("")
        self.quantidade.set("1")
        self.atualizar()

    def atualizar(self):
        selecionado = self.produto.get()
        self.produto["values"] = [f"{p.codigo} - {p.descricao}" for p in self.estoque.produtos.values()]
        self.produto.set(selecionado)

        limpar_tabela(self.tabela_produtos)
        for p in self.estoque.produtos.values():
            self.tabela_produtos.insert("", "end", values=(p.codigo, p.descricao, p.estoque))

        limpar_tabela(self.tabela_movs)
        for m in reversed(self.estoque.movimentacoes):  # mais recente primeiro
            nome = self.estoque.produtos[m.codigo_produto].descricao
            self.tabela_movs.insert("", "end", values=(
                m.id, m.data_hora, nome, m.tipo.capitalize(), m.quantidade, m.descricao, m.estoque_final
            ))


# --------------------------------------------------------------------------- #
# Aba 3 - Juros (Passo 5.5)
# --------------------------------------------------------------------------- #
class AbaJuros(ttk.Frame):
    def __init__(self, pai):
        super().__init__(pai, padding=10)

        ttk.Label(self, text="Juros por atraso", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(self, text="2,5% ao dia sobre o valor (juros simples).").pack(anchor="w", pady=(0, 8))

        form = ttk.Frame(self)
        form.pack(anchor="w")

        ttk.Label(form, text="Valor (R$):").grid(row=0, column=0, sticky="w", pady=3)
        self.valor = tk.StringVar()
        ttk.Entry(form, textvariable=self.valor, width=20).grid(row=0, column=1, sticky="w")

        ttk.Label(form, text="Vencimento (dd/mm/aaaa):").grid(row=1, column=0, sticky="w", pady=3, padx=(0, 8))
        self.vencimento = tk.StringVar()
        ttk.Entry(form, textvariable=self.vencimento, width=20).grid(row=1, column=1, sticky="w")

        ttk.Label(form, text="Data de hoje:").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Label(form, text=date.today().strftime("%d/%m/%Y")).grid(row=2, column=1, sticky="w")

        ttk.Button(form, text="Calcular", command=self.calcular).grid(row=3, column=1, sticky="w", pady=6)

        self.resultado = tk.StringVar()
        ttk.Label(self, textvariable=self.resultado, style="Destaque.TLabel", justify="left").pack(
            anchor="w", pady=8)

    def calcular(self):
        try:
            r = calcular_juros(ler_valor(self.valor.get()), ler_data(self.vencimento.get()))
        except ValueError as erro:
            messagebox.showerror("Dados inválidos", str(erro))
            return

        situacao = f"{r.dias_atraso} dia(s) de atraso" if r.dias_atraso else "Em dia (sem atraso)"
        self.resultado.set(
            f"{situacao}\n"
            f"Valor original: {formatar_moeda(r.valor)}\n"
            f"Juros:          {formatar_moeda(r.juros)}\n"
            f"Total a pagar:  {formatar_moeda(r.total)}"
        )


# --------------------------------------------------------------------------- #
# Janela principal (Passo 5.2)
# --------------------------------------------------------------------------- #
def main():
    root = tk.Tk()
    root.title("Desafio Target")
    root.geometry("900x700")
    root.minsize(760, 600)

    estilo = ttk.Style()
    estilo.configure("Titulo.TLabel", font=("Segoe UI", 13, "bold"))
    estilo.configure("Destaque.TLabel", font=("Consolas", 10, "bold"))

    abas = ttk.Notebook(root)
    abas.pack(fill="both", expand=True)
    abas.add(AbaComissoes(abas), text="  Comissões  ")
    abas.add(AbaEstoque(abas), text="  Estoque  ")
    abas.add(AbaJuros(abas), text="  Juros  ")

    root.mainloop()


if __name__ == "__main__":
    main()
