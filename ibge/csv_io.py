import csv

from ibge.config import COLUNAS_SAIDA


def read_input(filepath: str) -> list[dict]:
    registros: list[dict] = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            registros.append({
                "municipio": row["municipio"].strip(),
                "populacao": int(row["populacao"].strip()),
            })
    return registros


def write_output(filepath: str, linhas: list[dict]) -> None:
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUNAS_SAIDA)
        writer.writeheader()
        writer.writerows(linhas)
    print(f"\n[OUTPUT] '{filepath}' gerado com {len(linhas)} linhas.")
