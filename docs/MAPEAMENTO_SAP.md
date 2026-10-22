# Mapeamento visual dos prints fornecidos

As imagens foram analisadas visualmente. Não foram incorporadas ao repositório porque contêm informações corporativas e pessoais sem necessidade para executar o simulador. Este mapeamento não contém seletores técnicos, coordenadas nem leituras homologadas.

## Elementos observados

| Elemento | Observação e implicação para a captura PAD |
| --- | --- |
| Janela | Título visível `BR One :: Ordem de manutenção/metrologia`. Capturar a janela filha dentro da sessão SAP autorizada. |
| Nº do documento | Parte superior direita da janela. O print completo mostra `446`; o recorte separado mostra `1894`. São referências diferentes, que não devem ser combinadas como se fossem uma única leitura. |
| Status | Abaixo do número; `Fechado` aparece no print completo. No recorte do documento 1894, o campo não apresenta valor legível. Não transferir o status de 446 para 1894. |
| Horas consumidas | Parte superior esquerda. A linha aparenta possuir áreas separadas, mas as imagens não permitem confirmar valores de horas/minutos nem as propriedades dos controles. Capturar cada valor individualmente no PAD. Ausência de texto na imagem não equivale a zero. |
| Tipo da ordem | Abaixo de Horas consumidas, com valor visível `Manutenção`; o recorte mostra um controle de seleção. Ler valor selecionado, sem alterar seleção. |
| Solicitante | Campos de identificação e descrição na parte superior esquerda. Não copiar nomes aos logs. A captura real deve comprovar preenchimento do campo definido pelo PCM. |
| Operador | Matrícula e descrição separadas. No print completo aparece matrícula `427`, presente na lista autorizada. O texto do nome está truncado; a autorização não depende de comparação aproximada desse nome. |
| Técnico | Identificação e descrição aparentam estar vazias. Somente leitura bem sucedida de ambos os controles comprova vazio; imagem sem texto não basta. |
| Diálogo de impressão | Não fornecido. Permanecem pendentes captura do diálogo, botão, destino, correlação com documento e evidência de envio. |

## Consequências para a validação

A ordem 446 não está aprovada apenas por esse print: mesmo com status e tipo compatíveis e operador 427 cadastrado, o tempo consumido não foi confirmado. A ordem 1894 do recorte também não está aprovada, pois faltam os demais dados. Os exemplos de simulação são independentes dessas imagens e não representam extração real.

Não implementar cliques nos botões OK/Cancelar para consultar ordens: podem ter efeitos dependentes do modo da janela. Validar busca com Ctrl+F e foco explícito no campo Nº do documento no ambiente de teste. Não inferir seletores a partir da posição visual.

## Pendências objetivas no Windows

1. Capturar elementos reais e verificar propriedades textuais/valor selecionado, mantendo identificadores de matrícula como strings.
2. Confirmar os dois controles de tempo e a distinção entre valor vazio, zero e falha de leitura.
3. Testar pesquisa de documento inexistente, carregamento, troca de foco e modais inesperados.
4. Capturar diálogo de impressão e evidências de envio, sem acionar impressão de produção durante a configuração.
5. Executar o procedimento de homologação antes de substituir o adaptador real bloqueado.
