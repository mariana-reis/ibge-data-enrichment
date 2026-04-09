from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MunicipioIBGE:
    id_ibge: int
    nome: str
    uf: str
    regiao: str


@dataclass(frozen=True, slots=True)
class RegistroInput:
    municipio: str
    populacao: int


@dataclass(frozen=True, slots=True)
class LinhaResultado:
    municipio_input: str
    populacao_input: int
    municipio_ibge: str
    uf: str
    regiao: str
    id_ibge: int | str
    status: str


@dataclass(frozen=True, slots=True)
class Estatisticas:
    total_municipios: int
    total_ok: int
    total_nao_encontrado: int
    total_erro_api: int
    pop_total_ok: int
    medias_por_regiao: dict[str, float]
