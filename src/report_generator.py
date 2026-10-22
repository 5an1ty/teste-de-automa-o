import csv
import json
from pathlib import Path
from datetime import datetime, timezone

def generate(root, run_id, results, mode):
    directory = Path(root) / run_id
    directory.mkdir(parents=True, exist_ok=False)
    summary = {
        "execucao": run_id, "data": datetime.now(timezone.utc).isoformat(), "modo": mode,
        "total": len(results),
        "aprovadas": sum(r.resultado == "APROVADA" for r in results),
        "reprovadas": sum(r.resultado == "REPROVADA" for r in results),
        "nao_processadas": sum(r.resultado == "NAO_PROCESSADA" for r in results),
        "solicitadas": sum(r.solicitada for r in results),
        "enviadas": sum(r.enviada for r in results),
        "confirmadas": sum(r.confirmada for r in results),
        "nao_confirmadas": sum(r.impressao == "NAO_CONFIRMADA" for r in results),
        "falhas_tecnicas": sum(r.falha_tecnica for r in results),
    }
    (directory / "resumo.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    with (directory / "relatorio.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["execucao", "data", *results[0].to_dict()])
        writer.writeheader()
        for result in results:
            row = result.to_dict()
            for key in ("motivos", "verificacoes"):
                row[key] = json.dumps(row[key], ensure_ascii=False)
            # Mitigar fórmulas ao abrir CSV em planilhas.
            row = {k: ("'" + v if isinstance(v, str) and v.startswith(("=", "+", "-", "@")) else v) for k, v in row.items()}
            writer.writerow({"execucao": run_id, "data": summary["data"], **row})
    lines = ["RELATÓRIO DE ORDENS — PCM", json.dumps(summary, ensure_ascii=False)]
    lines += [f"Ordem: {r.numero} | {r.resultado} | Impressão: {r.impressao} | Motivos: {', '.join(r.motivos)}" for r in results]
    (directory / "relatorio.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    from .logger import registrar_resultado
    for result in results:
        registrar_resultado(directory / "tecnico.jsonl", run_id, result)
    return directory
