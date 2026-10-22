import argparse
from .config import load
from .txt_reader import read_orders, read_operators
from .simulator import Simulator
from .workflow import run

def main():
    parser = argparse.ArgumentParser(description="PCM SAP — simulador seguro")
    parser.add_argument("--config", default="config.example.json")
    args = parser.parse_args()
    try:
        config = load(args.config)
        results, directory, stopped = run(read_orders(config["orders"]), read_operators(config["operators"]), Simulator(config["fixtures"]), config["reports"], tipo=config.get("order_type", "Manutenção"))
        print(f"Relatórios: {directory}; ordens: {len(results)}; interrompido: {stopped}")
        return 2 if stopped else 0
    except (ValueError, OSError, TypeError) as exc:
        print(f"Execução bloqueada: {exc}")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
