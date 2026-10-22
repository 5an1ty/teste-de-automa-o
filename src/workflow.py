from uuid import uuid4
from .models import Result
from .order_reader import ler_ordem
from .order_validator import validar_ordem
from .print_manager import imprimir_ordem
from .sap_interface import SystemFailure
from .report_generator import generate

def run(orders, operators, interface, output, *, tipo="Manutenção", mode="DRY_RUN", printing=False, cancelled=lambda: False):
    if not orders or len(set(orders)) != len(orders) or not operators:
        raise ValueError("Lote vazio, duplicado ou sem operadores")
    if mode not in ("DRY_RUN", "CONSULTA", "IMPRESSAO") or printing != (mode == "IMPRESSAO"):
        raise ValueError("Modo de execução inconsistente")
    results = [Result(n) for n in orders]
    stopped = False
    for result in results:
        if stopped:
            result.motivos.append("LOTE_INTERROMPIDO")
            continue
        try:
            if cancelled():
                raise KeyboardInterrupt
            dados = ler_ordem(interface, result.numero)
            result.verificacoes = validar_ordem(result.numero, dados, operators, tipo)
            result.motivos = [key for key, ok in result.verificacoes.items() if not ok]
            result.resultado = "REPROVADA" if result.motivos else "APROVADA"
            if dados:
                for target, source in (("operador", "operador_id"), ("status", "status"), ("horas", "horas"), ("minutos", "minutos")):
                    setattr(result, target, getattr(dados, source))
            if cancelled():
                raise KeyboardInterrupt
            if result.resultado == "APROVADA" and mode != "CONSULTA":
                imprimir_ordem(interface, result, enabled=printing)
        except KeyboardInterrupt:
            result.motivos.append("INTERRUPCAO_MANUAL")
            stopped = True
        except Exception:
            result.falha_tecnica = True
            if not result.motivos or "FALHA_IMPRESSAO" not in result.motivos and "IMPRESSAO_NAO_CONFIRMADA" not in result.motivos:
                result.motivos.append("ERRO_NAVEGACAO")
            stopped = True
    path = generate(output, uuid4().hex, results, mode)
    return results, path, stopped
