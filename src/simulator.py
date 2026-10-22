import json
from pathlib import Path
from .models import Order, FIELDS

class Simulator:
    def __init__(self, path):
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        self.orders = {key: Order(**{**value, "legiveis": frozenset(value.get("legiveis", FIELDS))}) for key, value in raw.items()}
        self.current = None

    def buscar_ordem(self, numero):
        self.current = self.orders.get(numero)
        return self.current is not None

    def ler_dados_ordem(self):
        return self.current

    def confirmar_contexto(self, numero):
        return self.current is not None and self.current.numero == numero

    def abrir_impressao(self, numero):
        raise AssertionError("Simulador não imprime")
