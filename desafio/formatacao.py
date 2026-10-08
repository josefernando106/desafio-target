from decimal import Decimal, InvalidOperation


def formatar_moeda(valor: Decimal) -> str:
    """Formata no padrão brasileiro: R$ 1.234,56"""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def ler_valor(texto: str) -> Decimal:
    """Aceita '1234.56', '1234,56' ou '1.234,56'."""
    texto = texto.strip().replace("R$", "").strip()
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return Decimal(texto)
    except InvalidOperation:
        raise ValueError(f"Valor inválido: '{texto}'.")
