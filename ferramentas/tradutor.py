from ferramentas.gerar_dominios import carregar_dominios

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

        for chave in objeto:

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


if __name__ == "__main__":

    objeto = {
        "modalidadeId": 6,
        "modoDisputaId": 1,
        "criterioJulgamentoId": 1
}

traduzir_objeto(objeto)

print(objeto)
    



