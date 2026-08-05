from pathlib import Path
import json

PASTA = Path("dados/compras")
PASTA_COMPRAS = Path("dados/compras")

def salvar_json(caminho, dados):
    """
    Salva qualquer objeto Python em um arquivo JSON.
    """

    caminho = Path(caminho)

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            dados,
            f,
            indent=4,
            ensure_ascii=False
        )



def carregar_json(caminho):
    """
    Carrega um arquivo JSON
    """

    caminho = Path(caminho)

    if not caminho.exists():
        return None

    with open(
        caminho,
        encoding="utf-8"
    ) as f:

        return json.load()


def salvar_compra(cnpj, ano, sequencial, nome, dados):
    """
    Salva um recurso relacionado à uma compra.
    """

    pasta = (
        PASTA_COMPRAS /
        f"{cnpj}-{ano}-{sequencial}"
    )

    salvar_json(
        pasta / f"{nome}.json",
        dados
    )


def carregar_compra(cnpj, ano, sequencial, nome):
    """
    Carrega um recurso salvo de uma compra.
    """

    pasta = (
        PASTA_COMPRAS /
        f"{cnpj}-{ano}-{sequencial}"
    )

    return carregar_json(
        pasta / f"{nome}.json"
    )


 