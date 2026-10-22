# Arquitetura

`main` → `config` / `txt_reader` → `workflow` → `order_reader` / `order_validator` → `print_manager` → `report_generator` / `logger`.

`SapInterface` separa a interface gráfica das regras de negócio; `Simulator` implementa somente a consulta fictícia. `RealSap` falha de forma explícita até existir um adaptador homologado.

## Contrato do adaptador futuro

- `buscar_ordem(numero)`: colocar a sessão autorizada em primeiro plano, verificar janela e modo, Ctrl+F, selecionar explicitamente o campo Nº do documento, substituir seu texto, Enter e aguardar carregamento. Retornar falso somente para uma resposta inequívoca de ordem inexistente. Timeouts, sessão expirada e janelas inesperadas são `SystemFailure`.
- `ler_dados_ordem()`: ler os dez valores separadamente e preencher `legiveis` somente com leituras confiáveis. Identificador e descrição de operador/técnico são controles distintos. Vazio confirmado é diferente de falha de leitura. Imagem isolada não autoriza impressão.
- `confirmar_contexto(numero)`: verificar sessão, janela, documento atual e ausência de alterações/interferência. Revalidar os dados imediatamente antes da impressão; se mudaram, interromper. O método deve ser válido também com o diálogo de impressão aberto.
- `abrir_impressao(numero)`: Ctrl+P, aguardar e verificar diálogo, destino e identidade do documento quando disponível; nunca clicar por posição fixa. A falta de correlação exige uma prova alternativa homologada ou bloqueio.
- `enviar_impressao()`: exatamente um acionamento visível de Imprimir, sem retentativa; não retornar até poder consultar o resultado.
- `confirmar_envio()`: evidência correlacionada do envio ao spool, sem confundir fechamento da janela com sucesso.
- `confirmar_impressao_fisica()`: somente evidência independente homologada ou confirmação humana explícita. Um trabalho no spool não comprova saída física.

O adaptador deverá receber limites configuráveis: `search_timeout_seconds`, `dialog_timeout_seconds`, `send_timeout_seconds` e `navigation_attempts` (valores iniciais sugeridos: 30, 15, 30 e 1). Validar valores positivos e impor limite em cada espera, consultando cancelamento. Esses parâmetros são requisitos do adaptador pendente, não opções atualmente implementadas na CLI. Retentativa limitada só é permitida antes de iniciar a impressão, após provar o contexto seguro. Nunca repetir o clique de impressão.

A implementação de produção precisará de diário transacional persistido antes da impressão, exclusão de concorrência por sessão e bloqueio de retomada de trabalhos incertos. Os relatórios atuais são escritos ao final do lote; não substituem esse diário. Não utilizar o núcleo com impressão real antes de implementar e homologar essas proteções.
