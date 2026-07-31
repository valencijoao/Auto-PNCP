import json
from pathlib import Path

from api.session import criar_sessao


URL_SWAGGER = "https://pncp.gov.br/pncp-api/v3/api-docs"

PASTA_DADOS = Path('dados')
PASTA_DADOS.mkdir(exist_ok=True)

ARQUIVO_SAIDA = PASTA_DADOS / 'swagger.json'

session = criar_sessao()

def baixar_swagger():
    """
    Baixa a documentação do PNCP e retorna um arquivo JSON para consulta.
    """

    resposta = session.get(
        URL_SWAGGER,
        timeout=60
    )

    resposta.raise_for_status()

    swagger = resposta.json()

    with open(
        ARQUIVO_SAIDA,
        "w",
        encoding="utf-8"
    ) as arquivo:
        
        json.dump(
            swagger,
            arquivo,
            indent=4,
            ensure_ascii=False
        )

    print('Arquivo salvo!')


if __name__== "__main__":
    baixar_swagger()