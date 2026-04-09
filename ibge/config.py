IBGE_API_URL: str = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
SUBMISSION_URL: str = "https://mynxlubykylncinttggu.functions.supabase.co/ibge-submit"

INPUT_FILE: str = "input.csv"
OUTPUT_FILE: str = "resultado.csv"

FUZZY_THRESHOLD: int = 88
API_TIMEOUT: int = 15

COLUNAS_SAIDA: list[str] = [
    "municipio_input",
    "populacao_input",
    "municipio_ibge",
    "uf",
    "regiao",
    "id_ibge",
    "status",
]
