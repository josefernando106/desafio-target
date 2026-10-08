"""Desafio 2 - movimentação de estoque.

O arquivo estoque.json guarda o saldo inicial e não é alterado. Cada lançamento
fica em movimentacoes.json; ao abrir o sistema, o saldo atual é recalculado a
partir do inicial + histórico, o que garante IDs únicos entre execuções.
"""
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

ENTRADA = "ENTRADA"
SAIDA = "SAIDA"


@dataclass
class Produto:
    codigo: int
    descricao: str
    estoque: int


@dataclass
class Movimentacao:
    id: int
    codigo_produto: int
    tipo: str
    quantidade: int
    descricao: str
    data_hora: str
    estoque_final: int


class Estoque:
    def __init__(self, caminho_estoque: Path, caminho_movimentacoes: Path | None = None):
        self.caminho_movimentacoes = caminho_movimentacoes
        self.produtos: dict[int, Produto] = {}
        self.movimentacoes: list[Movimentacao] = []

        with open(caminho_estoque, encoding="utf-8") as arquivo:
            for p in json.load(arquivo)["estoque"]:
                self.produtos[p["codigoProduto"]] = Produto(
                    p["codigoProduto"], p["descricaoProduto"], p["estoque"]
                )

        if caminho_movimentacoes and caminho_movimentacoes.exists():
            with open(caminho_movimentacoes, encoding="utf-8") as arquivo:
                for m in json.load(arquivo):
                    mov = Movimentacao(**m)
                    self._aplicar(mov.codigo_produto, mov.tipo, mov.quantidade)
                    self.movimentacoes.append(mov)

    def proximo_id(self) -> int:
        return max((m.id for m in self.movimentacoes), default=0) + 1

    def movimentar(self, codigo: int, tipo: str, quantidade: int, descricao: str) -> Movimentacao:
        if codigo not in self.produtos:
            raise ValueError(f"Produto {codigo} não encontrado.")
        if tipo not in (ENTRADA, SAIDA):
            raise ValueError("Tipo deve ser ENTRADA ou SAIDA.")
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        if not descricao.strip():
            raise ValueError("Informe uma descrição para a movimentação.")

        produto = self.produtos[codigo]
        if tipo == SAIDA and quantidade > produto.estoque:
            raise ValueError(
                f"Estoque insuficiente: '{produto.descricao}' tem {produto.estoque} unidade(s)."
            )

        self._aplicar(codigo, tipo, quantidade)
        mov = Movimentacao(
            id=self.proximo_id(),
            codigo_produto=codigo,
            tipo=tipo,
            quantidade=quantidade,
            descricao=descricao.strip(),
            data_hora=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            estoque_final=produto.estoque,
        )
        self.movimentacoes.append(mov)
        self._salvar()
        return mov

    def _aplicar(self, codigo: int, tipo: str, quantidade: int) -> None:
        sinal = 1 if tipo == ENTRADA else -1
        self.produtos[codigo].estoque += sinal * quantidade

    def _salvar(self) -> None:
        if not self.caminho_movimentacoes:
            return
        with open(self.caminho_movimentacoes, "w", encoding="utf-8") as arquivo:
            json.dump([asdict(m) for m in self.movimentacoes], arquivo, ensure_ascii=False, indent=2)
