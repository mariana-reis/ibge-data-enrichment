from collections import defaultdict
from dataclasses import asdict

from ibge.matching import match_municipio
from ibge.models import LinhaResultado, MunicipioIBGE
from ibge.text import normalize


def _build_empty_result(nome: str, populacao: int, status: str) -> LinhaResultado:
    return LinhaResultado(
        municipio_input=nome,
        populacao_input=populacao,
        municipio_ibge="",
        uf="",
        regiao="",
        id_ibge="",
        status=status,
    )


def _build_matched_result(
    nome: str, populacao: int, dados: MunicipioIBGE, status: str
) -> LinhaResultado:
    return LinhaResultado(
        municipio_input=nome,
        populacao_input=populacao,
        municipio_ibge=dados.nome,
        uf=dados.uf,
        regiao=dados.regiao,
        id_ibge=dados.id_ibge,
        status=status,
    )


def processar(
    registros: list[dict],
    lookup: dict[str, MunicipioIBGE],
    nomes_normalizados: list[str],
) -> list[dict]:
    contagem_input: dict[str, int] = defaultdict(int)
    for r in registros:
        contagem_input[normalize(r["municipio"])] += 1

    cache_match: dict[str, tuple[MunicipioIBGE | None, str]] = {}
    linhas: list[dict] = []

    for r in registros:
        nome = r["municipio"]
        pop = r["populacao"]
        norm = normalize(nome)

        if contagem_input[norm] > 1:
            resultado = _build_empty_result(nome, pop, "AMBIGUO")
            print(f"  [AMBIGUO] '{nome}' aparece múltiplas vezes no input.")
            linhas.append(asdict(resultado))
            continue

        if norm not in cache_match:
            cache_match[norm] = match_municipio(nome, lookup, nomes_normalizados)

        dados, status = cache_match[norm]

        if dados:
            resultado = _build_matched_result(nome, pop, dados, status)
            print(f"  [OK]      '{nome}' -> '{dados.nome}' ({dados.uf})")
        else:
            resultado = _build_empty_result(nome, pop, status)
            print(f"  [{status}] '{nome}'")

        linhas.append(asdict(resultado))

    return linhas
