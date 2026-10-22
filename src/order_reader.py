from .sap_interface import SystemFailure

def ler_ordem(interface, numero):
    if not interface.buscar_ordem(numero):
        return None
    dados = interface.ler_dados_ordem()
    if not isinstance(dados.numero, str) or "numero" not in dados.legiveis or not dados.numero.strip():
        raise SystemFailure("Impossível identificar a ordem atual")
    return dados
