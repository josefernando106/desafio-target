"""Desafio 1 - comissão por vendedor."""
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

CENTAVOS = Decimal("0.01")


@dataclass
class Venda:
    vendedor: str
    valor: Decimal

    @property
    def percentual(self) -> Decimal:
        return percentual_comissao(self.valor)

    @property
    def comissao(self) -> Decimal:
        return calcular_comissao(self.valor)


@dataclass
class ResumoVendedor:
    vendedor: str
    vendas: list
    total_vendido: Decimal
    comissao: Decimal


def percentual_comissao(valor: Decimal) -> Decimal:
    if valor < 100:
        return Decimal("0")
    if valor < 500:
        return Decimal("0.01")
    return Decimal("0.05")


def calcular_comissao(valor: Decimal) -> Decimal:
    return (valor * percentual_comissao(valor)).quantize(CENTAVOS, ROUND_HALF_UP)


def carregar_vendas(caminho: Path) -> list[Venda]:
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo, parse_float=Decimal)
    return [Venda(v["vendedor"], Decimal(v["valor"])) for v in dados["vendas"]]


def salvar_vendas(caminho: Path, vendas: list[Venda]) -> None:
    """Grava no mesmo formato do arquivo original: uma venda por linha, valor com 2 casas."""
    linhas = [
        f'    {{ "vendedor": {json.dumps(v.vendedor, ensure_ascii=False)}, "valor": {v.valor:.2f} }}'
        for v in vendas
    ]
    conteudo = '{\n  "vendas": [\n' + ",\n".join(linhas) + "\n  ]\n}\n"
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)


def adicionar_venda(vendas: list[Venda], vendedor: str, valor: Decimal) -> Venda:
    """Valida e inclui a venda logo após a última venda do mesmo vendedor."""
    vendedor = " ".join(vendedor.split())  # remove espaços extras
    if not vendedor:
        raise ValueError("Informe o nome do vendedor.")
    if valor <= 0:
        raise ValueError("O valor da venda deve ser maior que zero.")

    # "joão silva" e "João Silva" são o mesmo vendedor: reaproveita o nome já cadastrado
    for v in vendas:
        if v.vendedor.casefold() == vendedor.casefold():
            vendedor = v.vendedor
            break

    venda = Venda(vendedor, valor.quantize(CENTAVOS, ROUND_HALF_UP))
    posicoes = [i for i, v in enumerate(vendas) if v.vendedor == vendedor]
    vendas.insert(posicoes[-1] + 1 if posicoes else len(vendas), venda)
    return venda


def resumir_por_vendedor(vendas: list[Venda]) -> list[ResumoVendedor]:
    agrupado: dict[str, list[Venda]] = {}
    for venda in vendas:
        agrupado.setdefault(venda.vendedor, []).append(venda)

    return [
        ResumoVendedor(
            vendedor=nome,
            vendas=lista,
            total_vendido=sum((v.valor for v in lista), Decimal("0")),
            comissao=sum((v.comissao for v in lista), Decimal("0")),
        )
        for nome, lista in agrupado.items()
    ]
