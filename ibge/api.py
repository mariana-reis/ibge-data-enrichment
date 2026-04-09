import json

import requests

from ibge.config import API_TIMEOUT, IBGE_API_URL
from ibge.models import MunicipioIBGE
from ibge.text import normalize

_cache: list[MunicipioIBGE] | None = None


def _request_ibge_data() -> list[dict]:
    try:
        response = requests.get(IBGE_API_URL, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise RuntimeError("Timeout ao acessar a API do IBGE.")
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(f"Erro HTTP na API do IBGE: {exc}")
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Erro de rede: {exc}")
    except json.JSONDecodeError:
        raise RuntimeError("Resposta inválida (não JSON) da API do IBGE.")


def _parse_municipio(raw: dict) -> MunicipioIBGE | None:
    try:
        microrregiao = raw.get("microrregiao") or {}
        mesorregiao = microrregiao.get("mesorregiao") or {}
        uf = mesorregiao.get("UF") or {}
        regiao = uf.get("regiao") or {}

        return MunicipioIBGE(
            id_ibge=raw["id"],
            nome=raw["nome"],
            uf=uf.get("sigla", ""),
            regiao=regiao.get("nome", ""),
        )
    except (KeyError, AttributeError):
        return None


def fetch_ibge_municipios() -> list[MunicipioIBGE]:
    global _cache
    
    if _cache is not None:
        return _cache
    
    print("[IBGE] Buscando lista de municípios...")
    raw_data = _request_ibge_data()
    
    municipios: list[MunicipioIBGE] = []
    for item in raw_data:
        parsed = _parse_municipio(item)
        if parsed is not None:
            municipios.append(parsed)
    
    print(f"[IBGE] {len(municipios)} municípios carregados.")
    _cache = municipios
    return municipios


def build_lookup(municipios: list[MunicipioIBGE]) -> dict[str, MunicipioIBGE]:
    return {normalize(m.nome): m for m in municipios}
