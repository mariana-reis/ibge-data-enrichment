import json
import os
import sys
from dataclasses import asdict

from dotenv import load_dotenv

from ibge.api import build_lookup, fetch_ibge_municipios
from ibge.config import INPUT_FILE, OUTPUT_FILE
from ibge.csv_io import read_input, write_output
from ibge.processing import processar
from ibge.statistics import calcular_estatisticas
from ibge.submission import submeter_resultado

load_dotenv()


def _resolve_access_token() -> str | None:
    return os.environ.get("ACCESS_TOKEN") or (
        sys.argv[1] if len(sys.argv) > 1 else None
    )


def main() -> None:
    access_token = _resolve_access_token()
    if not access_token:
        print(
            "[AVISO] ACCESS_TOKEN não fornecido. O envio para a API de correção será pulado.\n"
            "        Forneça via: ACCESS_TOKEN=seu_token uv run main.py\n"
            "        Ou como argumento: uv run main.py SEU_TOKEN\n"
        )

    try:
        municipios_ibge = fetch_ibge_municipios()
    except RuntimeError as e:
        print(f"[ERRO FATAL] {e}")
        sys.exit(1)

    lookup = build_lookup(municipios_ibge)
    nomes_normalizados = list(lookup.keys())

    print(f"\n[INPUT] Lendo '{INPUT_FILE}'...")
    try:
        registros = read_input(INPUT_FILE)
    except FileNotFoundError:
        print(f"[ERRO FATAL] Arquivo '{INPUT_FILE}' não encontrado.")
        sys.exit(1)
    except (ValueError, KeyError) as e:
        print(f"[ERRO FATAL] Formato inválido no input: {e}")
        sys.exit(1)

    print(f"[INPUT] {len(registros)} municípios lidos.\n")

    print("[PROCESS] Fazendo matching com dados do IBGE...")
    linhas = processar(registros, lookup, nomes_normalizados)

    write_output(OUTPUT_FILE, linhas)

    stats = calcular_estatisticas(linhas)
    stats_dict = asdict(stats)
    print("\n[STATS] Estatísticas calculadas:")
    print(json.dumps(stats_dict, indent=2, ensure_ascii=False))

    if access_token:
        submeter_resultado(stats, access_token)
    else:
        print("\n[SUBMIT] Pulado (sem ACCESS_TOKEN).")


if __name__ == "__main__":
    main()