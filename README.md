# Automação de ordens de manutenção — PCM / SAP Business One

Núcleo Python para validar ordens BR One e produzir rastreabilidade individual. O modo padrão **DRY_RUN** usa exclusivamente dados fictícios; não abre o SAP e não imprime.

## Instalação e execução no desenvolvimento

Requer Python 3.11 ou superior. Não há dependências externas, serviços, credenciais ou privilégios administrativos necessários para simulação.

```bash
python --version
python -m unittest discover -s tests -v
python -m src.main --config config.example.json
```

Execute na raiz do repositório. Os caminhos do JSON são relativos ao próprio arquivo de configuração. Opcionalmente crie um ambiente com `python -m venv .venv`; não é necessário instalar pacotes. Em Windows use `py -3` no lugar de `python`, somente onde a execução for autorizada pela TI.

## Utilização

1. Copie `config.example.json` para `config.local.json`.
2. Prepare um TXT UTF-8 com um número por linha e outro com `matricula;nome`. Linhas vazias são ignoradas. Listas vazias, identificadores inválidos e duplicidades bloqueiam todo o lote antes de consultar qualquer ordem.
3. Ajuste os caminhos e, para simulação, os registros em `data/simulacao.json`. O simulador nunca presume que uma ordem ausente está válida.
4. Execute `python -m src.main --config config.local.json`.
5. Consulte a pasta exclusiva da execução em `reports/runs/<id>/`. Ela contém `resumo.json`, `relatorio.csv`, `relatorio.txt` e `tecnico.jsonl`.

Matrículas são strings: `00247` difere de `247`. Horas são inteiras não negativas e minutos entre 0 e 59; o total deve ser positivo. Os dez campos devem estar explicitamente marcados como legíveis, inclusive campos de técnico vazios. Regras de texto usam comparação exata após remoção de espaços nas extremidades. `order_type` configura o tipo permitido; o padrão é `Manutenção`.

Os relatórios diferenciam aprovação, solicitação, envio e confirmação física. `SIMULADA_SEM_ENVIO` nunca conta como impressão enviada. Quantidades não processadas e falhas técnicas aparecem separadamente. O CSV protege valores que iniciem fórmulas. Nomes de solicitantes, operadores e técnicos não são copiados aos relatórios; a matrícula é mantida para rastreabilidade. A TI deve definir acesso, retenção e descarte desses dados.

## Implementado, simulado e pendente

- **Implementado:** modelos, leitores, validações, bloqueio de duplicidades, processamento sequencial, interrupção entre etapas, relatórios, protocolo de integração e máquina de estados de impressão testada com adaptadores falsos.
- **Simulado:** leitura de ordens por JSON; cenários de impressão dos testes nunca acessam impressoras.
- **Pendente de ambiente corporativo:** captura de controles reais, adaptador Windows/PAD, consulta real autorizada, tempos de espera, confirmação de spool e homologação da impressão. `RealSap` e configurações reais permanecem bloqueados intencionalmente. Não existe integração SAP pronta nesta entrega.

O núcleo tem modo `CONSULTA` para uso por um futuro adaptador e testes; a CLI bloqueia qualquer modo real até a integração. Não basta mudar uma opção do JSON para habilitar impressão. O protocolo é contrato de código, não uma autorização de TI nem uma conexão pronta com PAD.

## Segurança e falhas

Nenhuma ação de criação, atualização ou fechamento de ordens é exposta. Não há armazenamento de senha, automação de login, elevação de privilégios, impressão silenciosa ou coordenadas fixas. Falhas comuns de validação permitem continuar; exceções técnicas e perda de contexto interrompem o lote. Impressão incerta exige reconciliação humana e nunca é repetida automaticamente. A política conservadora também interrompe quando só o envio, sem comprovação física, foi confirmado.

Ctrl+C cancela o fluxo e registra o que foi possível observar. Adaptadores reais deverão oferecer cancelamento durante esperas. A interrupção forçada do processo ou falha de disco pode impedir o relatório final: o adaptador de produção deverá persistir um diário durável antes de cada envio e reconciliá-lo antes de qualquer retomada. Não reinicie um lote de impressão após falha sem avaliação individual.

Consulte [Power Automate Desktop](docs/POWER_AUTOMATE.md), [homologação](docs/HOMOLOGACAO.md) e [arquitetura](docs/ARQUITETURA.md). Os exemplos são fictícios e não constituem evidência de funcionamento no SAP.
