import re
from .models import FIELDS

def validar_ordem(numero, dados, operadores, tipo="Manutenção"):
    if not operadores:
        raise ValueError("Lista de operadores vazia")
    if dados is None:
        return {"ORDEM_NAO_ENCONTRADA": False}
    readable = all(f in dados.legiveis and isinstance(getattr(dados, f), str) for f in FIELDS)
    def text(name):
        value = getattr(dados, name)
        return value.strip() if isinstance(value, str) else ""
    h, m = text("horas"), text("minutos")
    time_ok = bool(re.fullmatch(r"[0-9]{1,9}", h) and re.fullmatch(r"[0-9]{1,2}", m))
    time_ok = time_ok and 0 <= int(m) < 60 and int(h) * 60 + int(m) > 0
    return {
        "CAMPO_ILEGIVEL": readable,
        "NUMERO_DIVERGENTE": text("numero") == numero,
        "STATUS_INVALIDO": text("status") == "Fechado",
        "SEM_HORAS_CONSUMIDAS": bool(time_ok),
        "TIPO_ORDEM_INVALIDO": text("tipo") == tipo,
        "SOLICITANTE_VAZIO": bool(text("solicitante")),
        "OPERADOR_VAZIO": bool(text("operador_id") and text("operador_nome")),
        "OPERADOR_NAO_AUTORIZADO": text("operador_id") in operadores,
        "TECNICO_PREENCHIDO": not (text("tecnico_id") or text("tecnico_nome")),
    }
