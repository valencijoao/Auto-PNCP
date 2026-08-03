import requests

BASE_URL = "https://pncp.gov.br/api/pncp"

from explorar_swagger import carregar_swagger


def gerar_modelo_requisicao(swagger, endpoint):
    """
    Gera um modelo de requisição para um endpoint.
    """

    paths = swagger.get("paths",{})

    if endpoint not in paths:
        print(f"Endpoint '{endpoint}' não encontrado. ")
        return

    print(f"\n===== {endpoint} =====\n")

    for metodo, info in paths[endpoint].items():

        print(f"{metodo.upper()}")

        parametros = info.get("parameters",[])

        path = []
        query = []

        for parametro in parametros:

            nome = parametro.get("name")
            local = parametro.get("in")

            if local == "path":
                path.append(nome)

            elif local == "query":
                query.append(nome)

        print("\nPATH")

        for p in path:
            print("-", p)

        print("\nQUERY")

        if query:
            for q in query:
                print("-", q)

        else:
            print("Nenhum")

        url = endpoint

        if query:

            url += "?"

            url += "&".join( 
                f"{q}={{{q}}}"
                for q in query
                )

        print("\nModelo da URL")

        print(url)

        print()


def executar_endpoint(endpoint, parametros=None):
    """
    Executa um endpoint GET da API do PNCP.
    """

    url = BASE_URL + endpoint

    print(url)

    resposta = requests.get(
        url,
        params=parametros,
        timeout=60
    )

    print(f"URL: {resposta.url}")
    print(f"Status: {resposta.status_code}")

    resposta.raise_for_status()

    return resposta.json()



if __name__ == "__main__":

    swagger = carregar_swagger("consulta")

    # gerar_modelo_requisicao(swagger, "endpoint")

#     executar_endpoint(
#      "/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens",
#     path={
#         "cnpj": "...",
#         "ano": 2025,
#         "sequencial": 15
#     },
#     query={
#         "pagina": 1,
#         "tamanhoPagina": 50
#     }
# )

executar_endpoint("/v1/modalidades")


