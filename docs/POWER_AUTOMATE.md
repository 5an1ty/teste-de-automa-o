# Integração e alternativa nativa — Power Automate Desktop

O PAD está disponível segundo o requisito do projeto. A disponibilidade não concede autorização para novos fluxos: a TI deverá aprovar captura, execução, armazenamento e impressão na sessão de teste. Não instalar Python ou executáveis no computador corporativo sem autorização. Este documento é uma especificação implementável de fluxo; não é um pacote PAD exportado nem foi executado no SAP.

## Captura necessária no ambiente de teste

No gravador/coleção de elementos de interface do PAD, capture e nomeie localmente:

| Elemento | Evidência necessária |
| --- | --- |
| Sessão SAP / janela BR One :: Ordem de manutenção/metrologia | Sessão e título corretos, primeiro plano e ausência de modal inesperado |
| Nº do documento | Campo específico editável em busca e legível após carregamento |
| Status, Tipo da ordem, Solicitante | Valor selecionado/texto acessível, com distinção entre vazio e erro |
| Horas e Minutos | Dois controles distintos, valores inteiros |
| Operador: matrícula e descrição | Dois controles, leitura textual preservando zeros |
| Técnico: identificador e descrição | Dois controles, inclusive comprovação de vazio |
| Resultado inexistente / carregamento | Sinais inequívocos de término e inexistência |
| Diálogo, documento e botão Imprimir | Correlação com ordem e destino autorizado |
| Envio/spool e confirmação | Identificação individual do trabalho e resultado observável |

Use seletores capturados, inspecionados e testados com mais de uma ordem. Não invente automation IDs. Evite seletores dependentes do número atual. Se os elementos não forem acessíveis, investigar acessibilidade Windows ou UI API autorizada; manter o campo ilegível e bloquear impressão até existir leitura confiável. OCR/imagem pode auxiliar localização, nunca ser a única prova de aprovação.

## Alternativa com ações nativas (sem Python)

Implemente os subfluxos abaixo no editor PAD com ações de arquivos, texto, listas, tabelas, condições, automação de UI e tratamento de erro. Os nomes das ações podem variar por versão/localização.

1. **Inicializar:** definir `DryRun=True`, `PrintEnabled=False`, tipo permitido, timeouts e identificador de execução; criar pasta de relatórios; mostrar botão/diálogo de cancelamento. Autenticação SAP é manual.
2. **Ler entradas:** ler TXT UTF-8, dividir por linhas, aparar espaços; validar cada ordem com expressão `^[0-9]+$`. Manter todos os números como texto, sem conversão numérica. Construir lista de vistos e rejeitar duplicatas antes de abrir o SAP. Para operadores, dividir cada linha por `;`, exigir exatamente dois campos, matrícula numérica e nome não vazio. Rejeitar duplicidade ou lista vazia.
3. **Simular primeiro:** criar tabela local de dados fictícios com as colunas do modelo; para cada ordem localizar a linha; ausência é ORDEM_NAO_ENCONTRADA. DryRun não deve executar nenhuma ação SAP ou impressora. Gerar os mesmos resultados esperados do exemplo.
4. **Buscar (somente após autorização de consulta):** ativar sessão/janela capturada; verificar ausência de modal; Ctrl+F; focar explicitamente Nº do documento por elemento; selecionar conteúdo e preencher a ordem; Enter; aguardar sinal de carregamento com limite. Não enviar Enter se o foco não for comprovado.
5. **Ler:** obter propriedade textual dos dez controles, guardando indicador de sucesso para cada um. Campo vazio só é aceito quando a leitura foi bem sucedida. Número ilegível ou perda de contexto interrompe lote; inexistência inequívoca reprova apenas a ordem.
6. **Validar:** acumular todos os motivos. Exigir número exato, status Fechado, tipo permitido, solicitante preenchido, matrícula e descrição de operador preenchidas, matrícula contida exatamente na lista autorizada e ambos os campos de técnico vazios. Validar horas/minutos como inteiros não negativos, minutos <60 e total >0. Converter apenas tempo, nunca matrículas. Exigir sucesso de todas as leituras.
7. **Imprimir (somente após homologação):** revalidar contexto e dados; persistir linha de diário como SOLICITADA antes do envio; Ctrl+P; aguardar diálogo; verificar identidade/destino; clicar Imprimir uma única vez; persistir imediatamente resultado. Esperar envio correlacionado; confirmação física exige prova separada. Na incerteza registrar NAO_CONFIRMADA, interromper e encaminhar reconciliação humana, sem repetir.
8. **Registrar:** adicionar linha individual com execução, horário, número, matrícula, status, tempo, verificações, motivos e estados de impressão. Evitar nomes pessoais e capturas de tela desnecessárias. Escrever tabela CSV e resumo TXT com totais distintos; manter também diário incremental. Proteger campos de fórmula ao exportar CSV. Ordens remanescentes após interrupção são NAO_PROCESSADA.
9. **Tratar falhas:** erro de validação continua; sessão expirada, janela inesperada, timeout, troca de foco ou falha técnica interrompem. Não inserir ações Atualizar, Adicionar ou Fechar ordem. Não fechar modais desconhecidos automaticamente.
10. **Cancelar:** usar mecanismo de parada autorizado do PAD; checar cancelamento antes de cada etapa e durante esperas limitadas. Nunca assumir que cancelamento desfaz um envio já efetuado.

Não executar dois lotes na mesma sessão. Uma intervenção humana invalida o contexto e exige parada/revalidação. Ao reiniciar, reconciliar o diário e a fila; trabalhos enviados/incertos não podem ser automaticamente reenfileirados. Testar o fluxo com TI e PCM antes de habilitar impressão. A versão PAD e seus seletores deverão ser exportados e versionados após captura real, sem credenciais.
