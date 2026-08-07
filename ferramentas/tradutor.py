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

if __name__ == "__main__":
    print(traduzir('modalidade', 6))
    



