import json
from pathlib import Path
import pandas as pd

from config.caminhos import COMPRAS, DADOS

PASTA_COMPRAS = COMPRAS
PASTA_DADOS = DADOS

ARQUIVO_JSON = DADOS / "orgaos.json"
ARQUIVO_CSV = DADOS / "orgaos.csv"

def gerar_orgaos():
    """
    Percorre todas as compras baixadas e documenta os órgãos encontrados por CNJP.
    """

    orgaos = {}

    for pasta in PASTA_COMPRAS.iterdir():

        if not pasta.is_dir():
            continue

        arquivo_dados = pasta / next (
            (
                arquivo.name
                for arquivo in pasta.glob("*.json")
            ),
            ""
        )

        if not arquivo_dados:
            continue

        try:

            with open(
                arquivo_dados,
                encoding="utf-8",
                ) as arquivo:

                dados = json.load(arquivo)

        except Exception as e:

            print(
                f"Erro ao carregar {arquivo_dados}: {e}"
            )

            continue

        orgao = dados.get(
            "orgaoEntidade",
            {}
        )

        unidade = dados.get(
            "unidadeOrgao",
            {}
        )

        cnpj = orgao.get(
            "cnpj"
        )

        if not cnpj:
            continue

        if cnpj not in orgaos:

            orgaos[cnpj] = {
                "CNPJ": cnpj,
                "RAZAO_SOCIAL": orgao.get(
                    "razaoSocial"
                ),
                "ESFERA": orgao.get(
                    "esferaId"
                ),
                "UF": unidade.get(
                    "ufNome"
                ),
                "MUNICIPIO": unidade.get(
                    "municipioNome"
                ),
                "UNIDADE": unidade.get(
                    "nomeUnidade"
                ),
                "QTD_CONTRATACOES": 0
            }

        orgaos[cnpj]["QTD_CONTRATACOES"] += 1

    return orgaos