import requests


BASE_URL = "https://pncp.gov.br/api/"



def executar_endpoint(endpoint, path=None, query=None, metodo="GET"):
    """
    Executa um endpoint GET da API do PNCP.
    """

    path = path or {}
    query = query or {}

    url = BASE_URL + endpoint.format(**path)

    print(f"\n{metodo} {url}")

    try:
        resposta = requests.request(
            metodo,
            url,
            params=query,
            timeout=60
        )

    except requests.exceptions.Timeout:
        print(f"Timeout ao acessar: {url}")

        return None

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




