import json
from pathlib import Path

def load(path):
    path = Path(path).resolve()
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("mode", "DRY_RUN") != "DRY_RUN":
        raise ValueError("Modo real indisponível até integração e homologação documentadas")
    if config.get("printing_enabled", False):
        raise ValueError("Impressão real bloqueada")
    for key in ("orders", "operators", "fixtures", "reports"):
        if not isinstance(config.get(key), str) or not config[key]:
            raise ValueError(f"Configuração ausente: {key}")
        config[key] = path.parent / config[key]
    return config
