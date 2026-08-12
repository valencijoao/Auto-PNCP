from ferramentas.cliente_api import executar_endpoint
from util.cache import salvar_compra
from ferramentas.gerar_dataset import gerar_dataset, salvar_dataset, gerar_dataset_cliente, salvar_dataset_cliente, filtrar_novas_contratacoes, gerar_id_interno
import json
from pathlib import Path
from util.portais import identificar_portal

PASTA_COMPRAS = Path("dados/compras")



def tentar_endpoint(endpoint, path=None, query=None):
    """
    Executa um endpoint opcional.
    Se falhar, retorna None e continua a coleta.
    """

    try:
        return executar_endpoint(
            endpoint,
            path=path,
            query=query
        )

    except Exception as e:
        print(f"Falha em {endpoint}")
        print(e)
        return None


def solicitar_clientes():
    """
    Solicita a inclusão dos clientes que receberão a compra.
    """

    while True:

        entrada = input(
            "Clientes à enviar: "
        )

        clientes = [
            cliente.strip()
            for cliente in entrada.split(',')
            if cliente.strip()
        ]

        if clientes:
            return clientes

        print(
            "Informe pelo menos um cliente."
        )


def obter_clientes(pasta):
    """
    Retorna os clientes associados à contratação.
    """

    caminho = pasta / "clientes.json"

    if caminho.exists():

        with open(
            caminho,
            encoding="utf-8"
        ) as f:

            return json.load(f)

    return None


def salvar_clientes(pasta, clientes):

    caminho = pasta / "clientes.json"

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            clientes,
            f,
            ensure_ascii=False,
            indent=4
        )


def baixar_compra_completa(
    cnpj,
    ano,
    sequencial,
    novas_contratacoes
):
    """
    Baixa todas as informações disponíveis de uma contratação.
    """

    path = {
        "cnpj": cnpj,
        "ano": ano,
        "sequencial": sequencial
    }

    pasta = PASTA_COMPRAS / f"{cnpj}-{ano}-{sequencial}"

    pasta_nova = not pasta.exists()

    pasta.mkdir(
        parents=True,
        exist_ok=True
    )

    clientes = obter_clientes(pasta)

    if clientes is None:

        clientes = solicitar_clientes()

        salvar_clientes(
            pasta,
            clientes
        )

    else:

        print(
            f"Clientes já associados: {', '.join(clientes)}"
        )

    print("\n=== Baixando contratação ===")

    #
    # ENDPOINTS OBRIGATÓRIOS
    #

    dados = executar_endpoint(
        "consulta/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}",
        path=path
    )


    link_portal = dados.get(
    "linkSistemaOrigem"
    )

    origem = identificar_portal(link_portal)

    id_interno = gerar_id_interno(cnpj,
    ano,
    sequencial,
    origem
    )

    salvar_compra(
        cnpj,
        ano,
        sequencial,
        "dados",
        dados
    )

    itens = executar_endpoint(
        "pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens",
        path=path
    )

    salvar_compra(
        cnpj,
        ano,
        sequencial,
        "itens",
        itens
    )

    #
    # ENDPOINTS OPCIONAIS
    #

    arquivos = tentar_endpoint(
        "pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/arquivos",
        path=path
    )

    salvar_compra(
        cnpj,
        ano,
        sequencial,
        "arquivos",
        arquivos
    )

    historico = tentar_endpoint(
        "pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/historico",
        path=path
    )

    salvar_compra(
        cnpj,
        ano,
        sequencial,
        "historico",
        historico
    )

    fontes_orcamentarias = tentar_endpoint(
        "pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/fonte-orcamentaria",
        path=path
    )

    salvar_compra(
        cnpj,
        ano,
        sequencial,
        "fontes_orcamentarias",
        fontes_orcamentarias
    )

    if pasta_nova:

        novas_contratacoes.append(
            id_interno
        )



if __name__ == "__main__":

    novas_contratacoes = []

    baixar_compra_completa(
"18296699000144",2026,278,
        novas_contratacoes
    )



    print("\n=== Atualizando dataset interno ===")

    df = gerar_dataset()

    salvar_dataset(df)

    print("\n=== Filtrando novas contratações ===")

    df_novas = filtrar_novas_contratacoes(
        df,
        novas_contratacoes
    )

    print(
        f"Novas contratações: {len(novas_contratacoes)}"
    )

    if not df_novas.empty:

        clientes = df_novas[
            "CLIENTE"
        ].dropna().unique()

        print(
            f"Clientes encontrados: {', '.join(clientes)}"
        )

        for cliente in clientes:

            df_cliente = gerar_dataset_cliente(
                df_novas,
                cliente
            )

            salvar_dataset_cliente(
                df_cliente,
                cliente
            )

    else:

        print(
            "Nenhuma nova contratação para gerar arquivos de clientes."
        )