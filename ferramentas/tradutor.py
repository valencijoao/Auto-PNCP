import json
from pathlib import Path

from ferramentas.gerar_dominios import carregar_dominios

PASTA_TRADUZIDOS = Path("dados/traduzidos")

def traduzir(dominio, codigo):
    """
    Traduz um único código do domínio correspondente.
    """

    dominios = carregar_dominios()

    codigo = str(codigo)

    pares = dominios.get(dominio)

    if pares is None:
        return None

    
    return pares.get(codigo)


def traduzir_objeto(objeto):
    """
    Traduz todos os códigos encontrados em  um JSON.
    """

    if isinstance(objeto, dict):

        for chave in list(objeto):

            if chave.endswith("Id"):

                nome = chave[:-2]

                descricao = traduzir(
                    nome,
                    objeto[chave]
                )
            
                if descricao is not None:

                    objeto[nome + "Nome"] = descricao

            valor = objeto[chave]

            traduzir_objeto(valor)

    elif isinstance(objeto, list):

        for item in objeto:

            traduzir_objeto(item)

    else:

        return


def traduzir_arquivo(caminho):
    """
    Definimos o JSON específico para ser traduzido.
    """

    caminho = Path(caminho)

    with open(caminho, encoding="utf-8") as f:
        objeto = json.load(f)

    traduzir_objeto(objeto)

    nome_pasta = caminho.parent.name

    pasta_destino = PASTA_TRADUZIDOS / nome_pasta

    pasta_destino.mkdir(
        parents=True,
        exist_ok=True
    )

    arquivo_destino = pasta_destino / caminho.name

    with open(
        arquivo_destino,
        "w",
        encoding="utf-8"
        ) as f:

            json.dump(
                objeto,
                f,
                ensure_ascii=False,
                indent=4
            )

def traduzir_pasta(pasta):
    """
    Percorre todos os JSON de uma pasta e os traduz. 
    """

    pasta = Path(pasta)

    for arquivo in pasta.glob("*.json"):

        print(f"Traduzindo {arquivo.name}...")

        traduzir_arquivo(arquivo)



if __name__== "__main__":

    traduzir_pasta(r"dados\compras\39215827000158-2026-8")




