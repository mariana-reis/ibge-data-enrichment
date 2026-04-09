from collections import defaultdict

from ibge.models import Estatisticas


def calcular_estatisticas(linhas: list[dict]) -> Estatisticas:
    total_municipios = len(linhas)
    total_ok = sum(1 for l in linhas if l["status"] == "OK")
    total_nao_encontrado = sum(1 for l in linhas if l["status"] == "NAO_ENCONTRADO")
    total_erro_api = sum(1 for l in linhas if l["status"] == "ERRO_API")

    ok_linhas = [l for l in linhas if l["status"] == "OK"]
    pop_total_ok = sum(l["populacao_input"] for l in ok_linhas)

    por_regiao: dict[str, list[int]] = defaultdict(list)
    for l in ok_linhas:
        por_regiao[l["regiao"]].append(l["populacao_input"])

    medias_por_regiao = {
        regiao: round(sum(pops) / len(pops), 2)
        for regiao, pops in por_regiao.items()
    }

    return Estatisticas(
        total_municipios=total_municipios,
        total_ok=total_ok,
        total_nao_encontrado=total_nao_encontrado,
        total_erro_api=total_erro_api,
        pop_total_ok=pop_total_ok,
        medias_por_regiao=medias_por_regiao,
    )
