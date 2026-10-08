"""Desafio 3 - juros por atraso (2,5% ao dia, juros simples)."""
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

TAXA_DIARIA = Decimal("0.025")
CENTAVOS = Decimal("0.01")


@dataclass
class ResultadoJuros:
    valor: Decimal
    vencimento: date
    hoje: date
    dias_atraso: int
    juros: Decimal

    @property
    def total(self) -> Decimal:
        return self.valor + self.juros


def ler_data(texto: str) -> date:
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
    except ValueError:
        raise ValueError(f"Data inválida: '{texto}'. Use o formato dd/mm/aaaa.")


def calcular_juros(valor: Decimal, vencimento: date, hoje: date | None = None) -> ResultadoJuros:
    if valor <= 0:
        raise ValueError("O valor deve ser maior que zero.")
    hoje = hoje or date.today()
    dias_atraso = max(0, (hoje - vencimento).days)
    juros = (valor * TAXA_DIARIA * dias_atraso).quantize(CENTAVOS, ROUND_HALF_UP)
    return ResultadoJuros(valor, vencimento, hoje, dias_atraso, juros)
