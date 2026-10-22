from .sap_interface import SystemFailure

def imprimir_ordem(interface, result, *, enabled=False):
    if result.resultado != "APROVADA" or not result.verificacoes or not all(result.verificacoes.values()):
        raise SystemFailure("Impressão sem validação completa bloqueada")
    if not enabled:
        result.impressao = "SIMULADA_SEM_ENVIO"
        return
    if result.solicitada:
        raise SystemFailure("Repetição de impressão bloqueada")
    if not interface.confirmar_contexto(result.numero):
        raise SystemFailure("Contexto da ordem alterado antes da impressão")
    result.solicitada = True
    result.impressao = "SOLICITADA"
    try:
        if not interface.abrir_impressao(result.numero):
            raise SystemFailure("Diálogo de impressão não identificado")
        if not interface.confirmar_contexto(result.numero):
            raise SystemFailure("Contexto da ordem alterado no diálogo")
        # O adaptador deve aguardar envio; nunca repetir após este ponto.
        result.impressao = "NAO_CONFIRMADA"
        interface.enviar_impressao()
        result.enviada = bool(interface.confirmar_envio())
        if not result.enviada:
            raise SystemFailure("Envio não confirmado")
        result.impressao = "ENVIADA"
        result.confirmada = bool(interface.confirmar_impressao_fisica())
        result.impressao = "CONFIRMADA" if result.confirmada else "NAO_CONFIRMADA"
        if not result.confirmada:
            raise SystemFailure("Impressão física não confirmada; reconciliação manual necessária")
    except Exception as exc:
        result.falha_tecnica = True
        result.motivos.append("IMPRESSAO_NAO_CONFIRMADA" if result.impressao == "NAO_CONFIRMADA" else "FALHA_IMPRESSAO")
        raise SystemFailure("Impressão interrompida; não repetir automaticamente") from exc
