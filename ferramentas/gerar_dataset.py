import json
from pathlib import Path
import pandas as pd
import hashlib

PASTA_COMPRAS = Path("dados/compras")

def gerar_id_interno(cnpj, ano, sequencial, portal):
    """
    Gera um identificador interno determinístico para uma contratação.
    """

    base = f"{cnpj}-{ano}-{sequencial}"

    hash_id = hashlib.sha256(
        base.encode("utf-8")
    ).hexdigest()[:12]

    return f"{portal}-{hash_id.upper()}"



def carregar_compra(pasta):
    """
    Carrega os arquivos JSON de uma compras.
    """

    dados = {}

    for arquivo in pasta.glob("*.json"):

        with open(
            arquivo,
            encoding="utf-8"
        ) as f:

            dados[arquivo.stem] = json.load(f)

    return dados


def extrair_dados_compra(compra):
    """
    Extrai os dados necessários de uma contratação.
    """

    dados = compra.get("dados",{})

    return{

    }

if __name__ =="__main__":

    pasta = Path(
        "dados/compras/39215827000158-2026-8"
    )

    compra = carregar_compra(pasta)

    print(compra.keys())

