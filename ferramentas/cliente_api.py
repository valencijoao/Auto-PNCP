import requests
import json
from pathlib import Path

BASE_URL = "https://pncp.gov.br/api/pncp"
PASTA_DADOS = Path("dados")
PASTA_DADOS.mkdir(exist_ok=True)

from explorar_swagger import carregar_swagger



def executar_endpoint(endpoint, path=None, query=None, metodo="GET"):
    """
    Executa um endpoint GET da API do PNCP.
    """

    path = path or {}
    query = query or {}

    url = BASE_URL + endpoint.format(**path)

    print(f"\n{metodo}{url}")

    resposta = requests.request(
        metodo,
        url,
        params=query,
        timeout=60
    )

    print(f"Status:",resposta.status_code)

    resposta.raise_for_status()

    if resposta.content:
        return resposta.json()

    return None


def salvar_json(nome, dados):
    """
    Salva os dados recuperados dos endpoints em um arquivo JSON.
    """

    caminho = PASTA_DADOS / nome

    with open(caminho,"w",encoding="utf-8") as f:
        json.dump(
            dados,
            f,
            indent=4,
            ensure_ascii=False
        )



if __name__ == "__main__":

    swagger = carregar_swagger("consulta")




    dados = executar_endpoint("/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens", path={
        "cnpj":"06553937000170",
        "ano":"2026",
        "sequencial":64
    })

    salvar_json("itens_compra.json",dados)


