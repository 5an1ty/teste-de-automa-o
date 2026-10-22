import json
from datetime import datetime, timezone

def registrar_resultado(path, run_id, result):
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"execucao": run_id, "data": datetime.now(timezone.utc).isoformat(), **result.to_dict()}, ensure_ascii=False) + "\n")
