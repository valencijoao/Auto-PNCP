import json
from pathlib import Path

from ferramentas.cliente_api import executar_endpoint

ARQUIVO = Path("dados/dominios.json")
PASTA_COMPRAS = Path("dados/compras")

def carregar_dominios():
    """
    Carrega os domínios retornados pela API.
    """

    if ARQUIVO.exists():

        with open(ARQUIVO, encoding="utf=8") as f:
            return json.load(f)


def ordenar_dominios(dominios):
    """
    Ordena os domínios e seus respectivos códigos.
    """

    dominios_ordenados = {}

    for dominio in sorted(dominios):

        pares = dominios[dominio]

        dominios_ordenados[dominio] = dict(
            sorted(
                pares.items(),
                key=lambda item: int(item[0])
            )
        )

    return dominios_ordenados


def salvar_dominios(dominios):
    """
    Salva novos domínios encontrados na consulta à API.
    """

    dominios = ordenar_dominios(dominios)

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


def normalizar_nomes(nome):
    """
    Remove os sufixos presentes nos domínios encontrados.
    """

    for sufixo in (
        "id",
        "Nome"
    ):
        if nome.endswith(sufixo):
            return nome[:-len(sufixo)]

    return nome


def registrar_par(dominios, dominio, codigo, descricao):
    """
    Registra um par código -> descrição dentro de um domínio.
    """

    dominio = normalizar_nomes(dominio)

    if dominio not in dominios:
        dominios[dominio] = {}

    dominios[dominio][str(codigo)] = descricao


def extrair_pares(objeto, dominios, pai=None):
    """
    Percorre o JSON e mapeia pares de nomes e códigos.
    """

    if isinstance(objeto, dict):


        if(
            pai is not None
            and "codigo" in objeto
            and "nome" in objeto
        ):
            registrar_par(
                dominios,
                pai,
                objeto["codigo"],
                objeto["nome"]
            )

    
        for chave in objeto:

            if chave.endswith("Id"):
                            

                nome = chave[:-2]
                chave_nome = nome + "Nome"

                if chave_nome in objeto:

                    registrar_par(
                        dominios,
                        nome,
                        objeto[chave],
                        objeto[chave_nome]
                        )

            valor = objeto[chave]

            extrair_pares(
                valor,
                dominios,
                pai=chave
            )

            
    elif isinstance(objeto, list):
            
        for item in objeto:

            extrair_pares(
                item,
                dominios,
                pai=pai
            )
           
    else:

        return


def minerar_arquivo(caminho, dominios):
    """
    Extrai todos os domínios de um JSON.
    """

    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)

    
    extrair_pares(
        dados,
        dominios
    )


def minerar_pasta():
    """
    Extrai os domínios de todos o JSON de um pasta.
    """

    dominios = carregar_dominios()

    for pasta in PASTA_COMPRAS.iterdir():

        if not pasta.is_dir():
            continue

        print(f"\nCompras:{pasta.name}")

        for arquivo in pasta.glob("*.json"):

            print(f" Minerando {arquivo.name}")

            minerar_arquivo(arquivo, dominios)

        salvar_dominios(dominios)

        print("\nDominios atualizados.")


if __name__ == "__main__":

    minerar_pasta()