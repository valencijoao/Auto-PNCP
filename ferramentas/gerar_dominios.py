import json
from pathlib import Path
from collections import defaultdict

from ferramentas.cliente_api import executar_endpoint

ARQUIVO = Path("dados/dominios.json")

def carregar_dominios():
    """
    Carrega os domínios retornados pela API.
    """

    if ARQUIVO.exists():

        with open(ARQUIVO, encoding="utf=8") as f:
            return json.load()

    return{}

def salvar_dominios(dominios):
    """
    Salva novos domínios encontrados na consulta à API.
    """

    with open(
        ARQUIVO,
        "w", 
        encoding="utf=8"

    ) as f:

        json.dump(
            dominios,
            f,
            ensure_ascii=False,
            indent=4
        )

def atualizar_dominios(nome, endpoint):
    """
    Atualiza os dados de um domínio específico.
    """

    print(f"Minerando {nome}...")

    dados = executar_endpoint(endpoint)

    dominios = carregar_dominios()

    dominios[nome] = dados

    salvar_dominios(dominios)

    print("OK")


if __name__ == "__main__":

    carregar_dominios()
    salvar_dominios()
    atualizar_dominios()