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

        arquivos_dados = next(
            pasta.glob("dados*.json"),
            None
        )

        if arquivos_dados is None:
            continue
  

        try:

            with open(
                arquivos_dados,
                encoding="utf-8",
                ) as arquivo:

                dados = json.load(arquivo)

        except Exception as e:

            print(
                f"Erro ao carregar {arquivos_dados}: {e}"
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


def salvar_orgao(orgaos):
    """
    Salva a documentação dos órgãos em JSON e CSV.
    """

    PASTA_COMPRAS.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        ARQUIVO_JSON,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            orgaos,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


    df = pd.DataFrame(
        orgaos.values()
    )

    df.to_csv(
        ARQUIVO_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"\nÓrgãos documentados: {len(orgaos)}"
    )

    print(
        f"JSON salvo em: {ARQUIVO_JSON}"
    )

    print(
        f"CSV salvo em: {ARQUIVO_CSV}"
    )



if __name__ == "__main__":

    orgaos = gerar_orgaos()

    salvar_orgao(
        orgaos
    )
