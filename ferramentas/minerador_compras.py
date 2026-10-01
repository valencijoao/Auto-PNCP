from ferramentas.cliente_api import executar_endpoint
from util.cache import salvar_compra
from ferramentas.gerar_dataset import gerar_dataset, gerar_dataset_cliente, salvar_dataset_cliente, gerar_id_interno, carregar_compra, filtrar_novas_contratacoes
import json
from pathlib import Path
from util.portais import identificar_portal
from config.caminhos import COMPRAS
from util.portais import obter_origem
from util.banco import inserir_compra


PASTA_COMPRAS = COMPRAS



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
            "Informe os clientes: "
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


def obter_dados_contratacao(pasta):
    """
    Retorna os clientes associados à contratação.
    """

    caminho = pasta / "clientes.json"

    if not caminho.exists():
        return None

    with open(
        caminho,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)

    


def salvar_dados_contratacao(pasta, clientes, item):
    """
    Salva os clientes e o item associados à contratação.
    """

    caminho = pasta / "clientes.json"

    dados = {
        "clientes": clientes,
        "item": item
    }

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            dados,
            f,
            ensure_ascii=False,
            indent=4
        )

    print("\nDados salvos:")
    print("Clientes:", clientes)
    print("Item:", item)

def solicitar_dados_contratacao():
    """
    Solicita os clientes e o item da contratação que será baixada.
    """

    entrada_clientes = input(
        "Informe os clientes: "
    )

    clientes = [
        cliente.strip()
        for cliente in entrada_clientes.split(",")
        if cliente.strip()
    ]

    item = input(
        "Informe o item: "
    ).strip()

    return clientes, item



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

    pasta = (
        PASTA_COMPRAS
        / f"{cnpj}-{ano}-{sequencial}"
    )

    pasta.mkdir(
        parents=True,
        exist_ok=True
    )

    dados_contratacao = obter_dados_contratacao(
        pasta
    )

    if dados_contratacao is None:

        clientes, item = solicitar_dados_contratacao()

        salvar_dados_contratacao(
            pasta,
            clientes,
            item
        )

    else:

        if isinstance(
            dados_contratacao,
            list
        ):

            clientes = dados_contratacao
            item = ""

        else:

            clientes = dados_contratacao.get(
                "clientes",
                []
            )

            item = dados_contratacao.get(
                "item",
                ""
            )

        print(
            f"Clientes já associados: "
            f"{', '.join(clientes)}"
        )

        print(
            f"Item já associado: {item}"
        )

        resposta = input(
            "Esta contratação já foi baixada. Deseja baixá-la novamente? (s/n): "
        ).strip().lower()
        if resposta not in {"s", "sim"}:
            print("Download cancelado para esta contratação.")
            return

    print(
        "\n=== Baixando contratação ==="
    )

    #
    # ENDPOINTS OBRIGATÓRIOS
    #

    dados = executar_endpoint(
        "consulta/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}",
        path=path
    )

    if not dados:

        print(
            "Não foi possível obter os dados "
            "principais da contratação."
        )

        return

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

    #
    # ID INTERNO
    #

    origem = obter_origem(
        dados
    )

    id_interno = gerar_id_interno(
        cnpj,
        ano,
        sequencial,
        origem
    )

    compra = carregar_compra(
        pasta
    )
    
    inserir_compra(compra)

    novas_contratacoes.append(
        id_interno
    )
    print(f"ID interno da nova contratação: {id_interno}")

def baixar_compras(contratacoes, novas_contratacoes):
    """
    Baixa uma lista de contratações, ou uma contratação individual.

    O parâmetro exigido é:

    'CNPJ/ANO/SEQUENCIAL'
    
    """

    for contratacao in contratacoes:

        contratacao = contratacao.strip()

        partes = contratacao.split("/")

        if len(partes) != 3:

            print(
                f"Contratação inválida: {contratacao}"
            )

            continue

        cnpj = partes[0].strip()
        ano = partes[1].strip()
        sequencial = partes[2].strip()

        try:

            ano = int(ano)
            sequencial = int(sequencial)

        except ValueError:

            print(
                f"Contratação inválida: {contratacao}"
            )

            continue

        print(f"\n==== Processando contratação: {contratacao} ====")

        baixar_compra_completa(
            cnpj,
            ano,
            sequencial,
            novas_contratacoes
        )

def atualizar_datasets_mineracao(novas_contratacoes):
    """Atualiza os datasets somente para contratações baixadas nesta execução."""
    if not novas_contratacoes:
        print("Nenhuma contratação foi baixada; os datasets não foram alterados.")
        return

    print("\n=== Preparando dados das novas contratações ===")
    print(f"Contratações baixadas nesta execução: {len(novas_contratacoes)}")
    df = gerar_dataset()

    df_novas = filtrar_novas_contratacoes(df, novas_contratacoes)
    if df_novas.empty or "CLIENTE" not in df_novas.columns:
        print("Não foram encontrados registros para as novas contratações no dataset.")
        return

    print("\n=== Gerando planilhas dos clientes das novas contratações ===")
    df_clientes = df_novas.loc[df_novas["CLIENTE"].notna()].copy()
    df_clientes["CLIENTE"] = df_clientes["CLIENTE"].astype(str).str.strip()
    df_clientes = df_clientes[df_clientes["CLIENTE"] != ""]
    clientes = df_clientes["CLIENTE"].unique()
    if not len(clientes):
        print("As novas contratações não possuem cliente associado.")
        return

    print(f"Clientes encontrados: {', '.join(clientes)}")
    gerados = 0
    falhas = []
    for cliente in clientes:
        try:
            df_cliente = gerar_dataset_cliente(df_clientes, cliente)
            salvar_dataset_cliente(df_cliente, cliente)
            gerados += 1
        except Exception as erro:
            falhas.append(cliente)
            print(f"Não foi possível gerar a planilha de '{cliente}': {erro}")

    print(f"Planilhas geradas/atualizadas: {gerados} de {len(clientes)}.")
    if falhas:
        print(f"Clientes com falha: {', '.join(falhas)}")

if __name__ == "__main__":

    novas_contratacoes = []

    contratacoes = [

        '89848949000150/2026/1174', '18338855000192/2026/37', '85361863000147/2026/143', '17161837000115/2026/9', '75442756000190/2026/113', '76285345000109/2026/255', '29138294000102/2026/811', '07693989000105/2026/62', '18244087000108/2026/15', '18025981000197/2026/102', '95640520000175/2026/47', '87849923000109/2026/336', 

    ]

    baixar_compras(
        contratacoes,
        novas_contratacoes
    )

    # python -m ferramentas.minerador_compras
    atualizar_datasets_mineracao(novas_contratacoes)
