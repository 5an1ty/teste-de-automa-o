from pathlib import Path
import re

def _lines(path):
    return [(i, s.strip()) for i, s in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1) if s.strip()]

def read_orders(path):
    orders = []
    for i, value in _lines(path):
        if not re.fullmatch(r"[0-9]+", value):
            raise ValueError(f"Ordem inválida na linha {i}")
        if value in orders:
            raise ValueError(f"Ordem duplicada na linha {i}")
        orders.append(value)
    if not orders:
        raise ValueError("Lista de ordens vazia")
    return orders

def read_operators(path):
    operators = {}
    for i, line in _lines(path):
        parts = [p.strip() for p in line.split(";")]
        if len(parts) != 2 or not re.fullmatch(r"[0-9]+", parts[0]) or not parts[1]:
            raise ValueError(f"Operador inválido na linha {i}")
        if parts[0] in operators:
            raise ValueError(f"Matrícula duplicada na linha {i}")
        operators[parts[0]] = parts[1]
    if not operators:
        raise ValueError("Lista de operadores vazia")
    return operators
