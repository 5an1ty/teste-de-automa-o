# Homologação antes de impressão real

Responsáveis: TI aprova ambiente e mecanismos; PCM verifica regras e documentos; operador acompanha a sessão. Registrar versão do código/fluxo, versão SAP/BR One/PAD, seletores, destino e evidências sem dados pessoais desnecessários.

1. Executar a suíte Python e a simulação. Esperado para o exemplo: 4 ordens, 1 aprovada, 3 reprovadas, nenhuma impressão enviada. Revisar os quatro artefatos de relatório.
2. Capturar seletores no SAP de teste conforme POWER_AUTOMATE.md. Verificar leitura individual de todos os campos, diferenças de escala/resolução, foco, modais e campos vazios. Não usar produção para descobrir controles.
3. Implementar adaptador autorizado ou fluxo nativo PAD; incluir tempos máximos, cancelamento, exclusão de concorrência e diário durável antes do envio. Revisar que somente busca, leitura e impressão são acionadas.
4. Homologar consulta sem impressão com ordens conhecidas: válida; status incorreto; tempo zero; minutos positivos; tempo ilegível/negativo/inconsistente; tipo diferente; solicitante vazio; matrícula não cadastrada/parcial/com zeros; técnico por código ou nome; documento divergente/inexistente; falha de leitura. Comparar manualmente todos os dados e motivos.
5. Ensaiar sessão expirada, janela inesperada, troca de foco, intervenção humana, Ctrl+C/parada PAD e falha de navegação. Confirmar parada segura e preservação do relatório/diário. Nenhum próximo documento deve ser impresso após perda de controle.
6. Com autorização específica, usar uma ordem fictícia no destino de teste. Conferir documento no diálogo e papel emitido; registrar solicitação, envio e confirmação separadamente. Simular falha antes e após clique, spool indisponível, confirmação ausente, encerramento forçado e reinício. Provar que não há duplicação ou reenvio automático.
7. Somente liberar após todas as evidências aceitas por TI e PCM. Modificar o bloqueio do adaptador/CLI em tarefa de integração revisada; não liberar apenas alterando JSON. Definir retenção dos logs, permissão de acesso e procedimento humano de reconciliação.

Critério de aceite: nenhuma impressão para qualquer reprovação; documentos corretos e individuais para aprovadas; rastreabilidade correlacionada; nenhuma repetição em resultado incerto; cancelamento e perda de contexto seguros. Não alegar confirmação física com base apenas no clique ou no spool.
