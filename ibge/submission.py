import json

import requests

from ibge.config import API_TIMEOUT, SUBMISSION_URL
from ibge.models import Estatisticas


def _build_payload(stats: Estatisticas) -> dict:
    return {
        "stats": {
            "total_municipios": stats.total_municipios,
            "total_ok": stats.total_ok,
            "total_nao_encontrado": stats.total_nao_encontrado,
            "total_erro_api": stats.total_erro_api,
            "pop_total_ok": stats.pop_total_ok,
            "medias_por_regiao": stats.medias_por_regiao,
        }
    }


def _display_result(resultado: dict) -> None:
    print("\n" + "=" * 60)
    print("  RESULTADO DA CORRECAO")
    print("=" * 60)
    print(f"  Usuario  : {resultado.get('email', 'N/A')}")
    print(f"  Score    : {resultado.get('score', 'N/A')}")
    print(f"  Feedback : {resultado.get('feedback', 'N/A')}")
    if "components" in resultado:
        print("  Detalhes :")
        print(json.dumps(resultado["components"], indent=4, ensure_ascii=False))
    print("=" * 60)


def submeter_resultado(stats: Estatisticas, access_token: str) -> None:
    payload = _build_payload(stats)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    print("\n[SUBMIT] Enviando estatísticas para a API de correção...")
    print(f"[SUBMIT] Payload:\n{json.dumps(payload, indent=2, ensure_ascii=False)}")

    try:
        resp = requests.post(
            SUBMISSION_URL,
            headers=headers,
            json=payload,
            timeout=API_TIMEOUT,
        )
        resp.raise_for_status()
        resultado = resp.json()
    except requests.exceptions.Timeout:
        print("[ERRO] Timeout ao enviar para a API de correção.")
        return
    except requests.exceptions.HTTPError:
        print(f"[ERRO] HTTP {resp.status_code}: {resp.text}")
        return
    except requests.exceptions.RequestException as exc:
        print(f"[ERRO] Falha de rede: {exc}")
        return
    except json.JSONDecodeError:
        print(f"[ERRO] Resposta inválida da API de correção: {resp.text}")
        return

    _display_result(resultado)
