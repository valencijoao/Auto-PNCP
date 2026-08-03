import json
from pathlib import Path

from api.session import criar_sessao


URL_SWAGGER = "https://pncp.gov.br/pncp-api/v3/api-docs"

PASTA_DADOS = Path('dados')
PASTA_DADOS.mkdir(exist_ok=True)

ARQUIVO_SAIDA = PASTA_DADOS / 'swagger.json'

session = criar_sessao()

SWAGGERS = {
    "consulta": {
        "url": "https://pncp.gov.br/api/pncp/swagger-ui/index.html",
        "arquivo": "swagger_consulta.json"

    },

    "manutencao": {
        "url": "https://pncp.gov.br/api/pncp/v3/api-docs",
        "arquivo": "swagger_manutencao.json"

    }
    }


def baixar_swagger(nome, url, arquivo):
    """
    Baixa a documentação do PNCP e retorna um arquivo JSON para consulta.
    """

    print(f"\nBaixando Swagger '{nome}'...")

    resposta = session.get(
        URL_SWAGGER,
        timeout=60
    )

    resposta.raise_for_status()

    dados = resposta.json()

    swagger = resposta.json()

    caminho = PASTA_DADOS / arquivo

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(
            dados,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"{arquivo} salvo!")


def atualizar_swaggers():
    """
    Baixa todos os swaggers do PNCP
    """

    for nome, info in SWAGGERS.items():

        try:

            baixar_swagger(
                nome,
                info['url'],
                info['arquivo']

            )


        except Exception as e:

            print(f"Erro ao baixar '{nome}': {e}")


if __name__== "__main__":

    atualizar_swaggers()