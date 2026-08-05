import requests
import json
from pathlib import Path

BASE_URL = "https://pncp.gov.br/api/"



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


if __name__ == "__main__":

    




    dados = executar_endpoint("/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens/{numeroItem}/resultados", path={
        "cnpj":"92457217000143",
        "ano":"2026",
        "sequencial":25,
        "numeroItem":1
    })




