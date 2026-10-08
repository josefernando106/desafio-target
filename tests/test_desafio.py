"""Testes das regras (Passo 6 do README).

Executar com:  python -m unittest discover tests
"""
import tempfile
import unittest
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from desafio.comissao import (
    Venda, adicionar_venda, calcular_comissao, carregar_vendas, resumir_por_vendedor, salvar_vendas,
)
from desafio.estoque import ENTRADA, SAIDA, Estoque
from desafio.formatacao import formatar_moeda, ler_valor
from desafio.juros import calcular_juros, ler_data

ARQ_ESTOQUE = Path(__file__).parent.parent / "estoque.json"


class TestComissao(unittest.TestCase):
    def test_fronteiras(self):
        casos = {
            "99.99": "0.00",
            "100.00": "1.00",
            "499.99": "5.00",
            "500.00": "25.00",
            "1200.50": "60.03",
        }
        for valor, esperado in casos.items():
            with self.subTest(valor=valor):
                self.assertEqual(calcular_comissao(Decimal(valor)), Decimal(esperado))

    def test_agrupa_por_vendedor(self):
        vendas = [
            Venda("Ana", Decimal("500")),
            Venda("Ana", Decimal("200")),
            Venda("Bruno", Decimal("50")),
        ]
        resumos = {r.vendedor: r for r in resumir_por_vendedor(vendas)}
        self.assertEqual(resumos["Ana"].total_vendido, Decimal("700"))
        self.assertEqual(resumos["Ana"].comissao, Decimal("27.00"))
        self.assertEqual(resumos["Bruno"].comissao, Decimal("0.00"))

    def test_adicionar_venda_fica_junto_do_vendedor(self):
        vendas = [Venda("Ana", Decimal("100")), Venda("Bruno", Decimal("200"))]
        nova = adicionar_venda(vendas, "  ana  ", Decimal("300"))  # mesmo vendedor, outra grafia
        self.assertEqual(nova.vendedor, "Ana")
        self.assertEqual([v.vendedor for v in vendas], ["Ana", "Ana", "Bruno"])

    def test_adicionar_vendedor_novo(self):
        vendas = [Venda("Ana", Decimal("100"))]
        adicionar_venda(vendas, "Carla", Decimal("50"))
        self.assertEqual(vendas[-1], Venda("Carla", Decimal("50.00")))

    def test_adicionar_venda_invalida(self):
        for vendedor, valor in [("", Decimal("10")), ("Ana", Decimal("0")), ("Ana", Decimal("-5"))]:
            with self.subTest(vendedor=vendedor, valor=valor), self.assertRaises(ValueError):
                adicionar_venda([], vendedor, valor)

    def test_salvar_e_carregar(self):
        vendas = [Venda("João Silva", Decimal("1200.50")), Venda("Ana", Decimal("75.30"))]
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "vendas.json"
            salvar_vendas(caminho, vendas)
            self.assertEqual(carregar_vendas(caminho), vendas)


class TestEstoque(unittest.TestCase):
    def setUp(self):
        # Sem caminho de movimentações: não grava nada em disco
        self.estoque = Estoque(ARQ_ESTOQUE)

    def test_entrada(self):
        mov = self.estoque.movimentar(101, ENTRADA, 10, "Compra fornecedor")
        self.assertEqual(mov.estoque_final, 160)

    def test_saida(self):
        mov = self.estoque.movimentar(101, SAIDA, 30, "Venda balcão")
        self.assertEqual(mov.estoque_final, 120)

    def test_ids_unicos_e_sequenciais(self):
        m1 = self.estoque.movimentar(101, ENTRADA, 1, "A")
        m2 = self.estoque.movimentar(102, SAIDA, 1, "B")
        self.assertEqual((m1.id, m2.id), (1, 2))

    def test_saida_maior_que_estoque(self):
        with self.assertRaises(ValueError):
            self.estoque.movimentar(101, SAIDA, 500, "Venda")
        self.assertEqual(self.estoque.produtos[101].estoque, 150)  # nada mudou

    def test_validacoes(self):
        for args in [(999, ENTRADA, 1, "x"), (101, ENTRADA, 0, "x"), (101, ENTRADA, 1, "  ")]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                self.estoque.movimentar(*args)


class TestJuros(unittest.TestCase):
    HOJE = date(2026, 10, 8)

    def test_dez_dias_de_atraso(self):
        r = calcular_juros(Decimal("1000"), self.HOJE - timedelta(days=10), self.HOJE)
        self.assertEqual(r.dias_atraso, 10)
        self.assertEqual(r.juros, Decimal("250.00"))
        self.assertEqual(r.total, Decimal("1250.00"))

    def test_vencimento_futuro(self):
        r = calcular_juros(Decimal("1000"), self.HOJE + timedelta(days=5), self.HOJE)
        self.assertEqual(r.dias_atraso, 0)
        self.assertEqual(r.juros, Decimal("0.00"))

    def test_data_invalida(self):
        with self.assertRaises(ValueError):
            ler_data("31/02/2026")


class TestFormatacao(unittest.TestCase):
    def test_ler_valor(self):
        for texto in ["1234.56", "1234,56", "1.234,56", "R$ 1.234,56"]:
            with self.subTest(texto=texto):
                self.assertEqual(ler_valor(texto), Decimal("1234.56"))

    def test_formatar_moeda(self):
        self.assertEqual(formatar_moeda(Decimal("1234.5")), "R$ 1.234,50")


if __name__ == "__main__":
    unittest.main()
