import json
import pandas as pd


from config.caminhos import CAMINHO_ORGAOS, CAMINHO_PORTAIS_TRATADOS
from ferramentas.gerar_dominios import carregar_dominios
from util.portais import traduzir_portal


UF_VALIDAS = {
    "AC", "AL", "AP", "AM",
    "BA", "CE", "DF", "ES",
    "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR",
    "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC",
    "SP", "SE", "TO"
}
COLUNAS_DATASET_INTERNO = [
    "ID_INTERNO",
    "CLIENTE",
    "ID",
    "NUMERO_COMPRA",
    "ANO_COMPRA",
    "SEQUENCIAL_COMPRA",
    "ESTADO",
    "UNIDADE",
    "CNPJ",
    "ORGAO",
    "ESFERA",
    "MUNICIPIO",
    "VALOR_ESTIMADO",
    "VALOR_HOMOLOGADO",
    "DATA_PUBLICACAO",
    "DATA_DISPUTA",
    "MODALIDADE",
    "MODO_DISPUTA",
    "SITUACAO",
    "SRP",
    "LINK_PNCP",
    "LINK_PORTAL",
    "PORTAL"
]
PORTAIS_TRATADOS = CAMINHO_PORTAIS_TRATADOS
with open(
    PORTAIS_TRATADOS,
    encoding="utf-8"
) as arquivo:
    PORTAIS_TRATADOS = json.load(
        arquivo
    )

DOMINIOS = carregar_dominios()
ORGAOS = CAMINHO_ORGAOS
with open(
    ORGAOS,
    encoding="utf-8"
) as arquivo:
    ORGAO = json.load(
        arquivo
    )


def normalizar_texto(valor):
    """
    Normaliza espaços e caracteres invisíveis de um texto.
    """

    if pd.isna(valor):
        return valor

    valor = str(valor)

    valor = valor.replace( 
        "\xa0",
        " "
    )

    valor = " ".join(
        valor.split()
    )

    return valor.strip()

def normalizar_data(valor):
    """
    Converte as datas para o tipo datetime.
    """

    if pd.isna(valor):
        return pd.NaT

    return pd.to_datetime(
        valor,
        errors="coerce"
    )

def normalizar_valores(valor):
    """
    Converte monetário para numérico.
    """

    if pd.isna(valor):
        return pd.NA

    if isinstance(valor, str):

        valor = valor.strip()

        if valor.lower() == "sigiloso":
            return pd.NA

        valor = valor.replace(
            ".",
            ""
        )

        valor = valor.replace(
            ",",
            "."
        )

    try:
        return float(valor)

    except (ValueError, TypeError):
        return pd.NA

def normalizar_cnpj(valor):
    """
    Normaliza o CNPJ mantendo somente os dígitos.
    Não tenta reconstruir CNPJs incompletos.
    """

    if pd.isna(valor):
        return pd.NA

    valor = str(valor).strip()

    if valor.endswith(".0"):
        valor = valor[:-2]

    valor = "".join(
        caractere
        for caractere in valor
        if caractere.isdigit()
    )

    return valor

def normalizar_dominio(valor, dominio):
    """
    Traduz um código utilizando um termo cadastrado como domínio.
    """

    if pd.isna(valor):
        return valor

    dominio = DOMINIOS.get(
        dominio,
        {}
    )

    chave = str(valor)

    return dominio.get(
        chave,
        valor
    )

def normalizar_orgao(df):
    """
    Padroniza os dados do órgão utilizando o CNPJ
    como chave de relacionamento.
    """

    if "CNPJ" not in df.columns:
        return df

    for indice, linha in df.iterrows():

        cnpj = linha["CNPJ"]

        if pd.isna(cnpj):
            continue

        cnpj = str(cnpj).strip()

        if len(cnpj) != 14:
            continue

        dados_orgao = ORGAO.get(cnpj)

        if not dados_orgao:
            continue

        if dados_orgao.get("RAZAO_SOCIAL"):

            df.at[
                indice,
                "ORGAO"
            ] = dados_orgao[
                "RAZAO_SOCIAL"
            ]

        if dados_orgao.get("UF"):

            df.at[
                indice,
                "ESTADO"
            ] = dados_orgao[
                "UF"
            ]

        if dados_orgao.get("MUNICIPIO"):

            df.at[
                indice,
                "MUNICIPIO"
            ] = dados_orgao[
                "MUNICIPIO"
            ]

        if dados_orgao.get("UNIDADE"):

            df.at[
                indice,
                "UNIDADE"
            ] = dados_orgao[
                "UNIDADE"
            ]

    return df

def validar_orgaos(df):
    """
    Valida a correspondência dos órgãos do dataset
    com o cadastro de orgaos.json.
    """

    relatorio = {}

    if "CNPJ" not in df.columns:

        relatorio["CNPJ"] = "Coluna não encontrada"

        return relatorio

    cnpjs = df["CNPJ"]

    cnpjs_normalizados = cnpjs.apply(
        normalizar_cnpj
    )

    cnpjs_vazios = (
        cnpjs_normalizados.isna()
    ).sum()

    cnpjs_validos = cnpjs_normalizados[
        cnpjs_normalizados.notna()
    ]

    cnpjs_validos = cnpjs_validos[
        cnpjs_validos.apply(
            lambda x:
                str(x).isdigit()
                and len(str(x)) == 14
        )
    ]

    encontrados = cnpjs_validos[
        cnpjs_validos.isin(
            ORGAO.keys()
        )
    ]

    nao_encontrados = cnpjs_validos[
        ~cnpjs_validos.isin(
            ORGAO.keys()
        )
    ]

    relatorio[
        "TOTAL_REGISTROS"
    ] = len(df)

    relatorio[
        "CNPJ_VAZIO"
    ] = cnpjs_vazios

    relatorio[
        "CNPJ_VALIDO"
    ] = len(cnpjs_validos)

    relatorio[
        "ORGAOS_ENCONTRADOS"
    ] = len(encontrados)

    relatorio[
        "ORGAOS_NAO_ENCONTRADOS"
    ] = len(nao_encontrados)

    relatorio[
        "TAXA_CORRESPONDENCIA"
    ] = (
        len(encontrados)
        / len(cnpjs_validos)
        * 100
        if len(cnpjs_validos) > 0
        else 0
    )

    relatorio[
        "CNPJS_NAO_ENCONTRADOS"
    ] = sorted(
        nao_encontrados.unique()
    )

    return relatorio

def exibir_validacao_orgaos(relatorio):
    """
    Exibe o resultado da validação dos órgãos.
    """

    print(
        "\n=== VALIDAÇÃO DOS ÓRGÃOS ==="
    )

    print(
        f"Total de registros: "
        f"{relatorio['TOTAL_REGISTROS']}"
    )

    print(
        f"CNPJ vazio: "
        f"{relatorio['CNPJ_VAZIO']}"
    )

    print(
        f"CNPJ válido: "
        f"{relatorio['CNPJ_VALIDO']}"
    )

    print(
        f"Órgãos encontrados: "
        f"{relatorio['ORGAOS_ENCONTRADOS']}"
    )

    print(
        f"Órgãos não encontrados: "
        f"{relatorio['ORGAOS_NAO_ENCONTRADOS']}"
    )

    print(
        f"Taxa de correspondência: "
        f"{relatorio['TAXA_CORRESPONDENCIA']:.2f}%"
    )

    if relatorio[
        "CNPJS_NAO_ENCONTRADOS"
    ]:

        print(
            "\nCNPJs não encontrados:"
        )

        for cnpj in relatorio[
            "CNPJS_NAO_ENCONTRADOS"
        ]:

            print(
                cnpj
            )

def normalizar_portal(valor):
    """
    Normaliza o portal utilizando as regras
    existentes em util.portais.
    """

    if pd.isna(valor):
        return valor

    valor = str(valor).strip()

    if not valor:
        return valor

    return traduzir_portal(
        valor
    )

def validar_portais(df):
    """
    Valida os portais presentes no dataset.

    UFs são consideradas origens válidas quando a contratação
    não possui link do sistema de origem.
    """

    relatorio = {}

    if "PORTAL" not in df.columns:

        relatorio["PORTAL"] = "Coluna não encontrada"

        return relatorio

    portais = df["PORTAL"]

    portais_validos = portais[
        portais.notna()
    ].astype(str).str.strip()

    portais_validos = portais_validos[
        portais_validos != ""
    ]

    cadastrados = set(
        PORTAIS_TRATADOS.values()
    )

    encontrados = portais_validos[
        portais_validos.isin(
            cadastrados
        )
    ]

    origens_uf = portais_validos[
        portais_validos.isin(
            UF_VALIDAS
        )
    ]

    desconhecidos = portais_validos[
        ~portais_validos.isin(cadastrados)
        & ~portais_validos.isin(UF_VALIDAS)
    ]

    relatorio["TOTAL_REGISTROS"] = len(df)

    relatorio["PORTAL_VAZIO"] = (
        portais.isna()
        | portais.astype(str).str.strip().eq("")
    ).sum()

    relatorio["PORTAIS_ENCONTRADOS"] = len(
        encontrados
    )

    relatorio["ORIGENS_UF"] = len(
        origens_uf
    )

    relatorio["PORTAIS_DESCONHECIDOS"] = len(
        desconhecidos
    )

    relatorio["TIPOS_DE_PORTAIS"] = (
        portais_validos.nunique()
    )

    relatorio["ORIGENS_UF_ENCONTRADAS"] = sorted(
        origens_uf.unique()
    )

    relatorio["PORTAIS_NAO_CADASTRADOS"] = sorted(
        desconhecidos.unique()
    )

    return relatorio

def exibir_validacao_portais(relatorio):
    """
    Exibe o resultado da validação dos portais.
    """

    print(
        "\n=== VALIDAÇÃO DOS PORTAIS ==="
    )

    print(
        f"Total de registros: "
        f"{relatorio['TOTAL_REGISTROS']}"
    )

    print(
        f"Portal vazio: "
        f"{relatorio['PORTAL_VAZIO']}"
    )

    print(
        f"Tipos de origens: "
        f"{relatorio['TIPOS_DE_PORTAIS']}"
    )

    print(
        f"Portais cadastrados: "
        f"{relatorio['PORTAIS_ENCONTRADOS']}"
    )

    print(
        f"Origens por UF: "
        f"{relatorio['ORIGENS_UF']}"
    )

    print(
        f"Portais desconhecidos: "
        f"{relatorio['PORTAIS_DESCONHECIDOS']}"
    )

    if relatorio[
        "ORIGENS_UF_ENCONTRADAS"
    ]:

        print(
            "\nOrigens por UF:"
        )

        for uf in relatorio[
            "ORIGENS_UF_ENCONTRADAS"
        ]:

            print(
                f"- {uf}"
            )

    if relatorio[
        "PORTAIS_NAO_CADASTRADOS"
    ]:

        print(
            "\nPortais não cadastrados:"
        )

        for portal in relatorio[
            "PORTAIS_NAO_CADASTRADOS"
        ]:

            print(
                f"- {portal}"
            )

def normalizar_dataset(df):
    """
    Aplica formatações no DataFrame bruto.
    """

    colunas_texto =  [
        "CLIENTE",
        "ORGAO",
        "ESTADO",
        "UNIDADE",
        "MUNICIPIO",
        "MODALIDADE",
        "MODO_DISPUTA",
        "SITUACAO"
    ]

    for coluna in colunas_texto:

        if coluna in df.columns:

            df[coluna] = df[coluna].apply(
                normalizar_texto,
            )

    if "CNPJ" in df.columns:

        df["CNPJ"] = df["CNPJ"].apply(
            normalizar_cnpj
        )


    colunas_data = [
        "DATA_DISPUTA",
        "DATA_PUBLICACAO"
    ]

    for coluna in colunas_data:

        if coluna in df.columns:

            df[coluna] = df[coluna].apply(
                normalizar_data
            )


    colunas_valor = [
        "VALOR_ESTIMADO",
        "VALOR HOMOLOGADO"
    ]

    for coluna in colunas_valor:

        if coluna in df.columns:

            df[coluna] = df[coluna].apply(
                normalizar_valores
            )

    if "MODALIDADE" in df.columns:

        df["MODALIDADE"] = df[
            "MODALIDADE"
        ].apply(
            lambda x: normalizar_dominio(
                x,
                "modalidade"
            )
        )

    if "MODO_DISPUTA" in df.columns:

        df["MODO_DISPUTA"] = df[
            "MODO_DISPUTA"
        ].apply(
            lambda x: normalizar_dominio(
                x,
                "modoDisputa"
            )
        )

    if "SITUACAO" in df.columns:

        df["SITUACAO"] = df[
            "SITUACAO"
        ].apply(
            lambda x: normalizar_dominio(
                x,
                "situacaoCompra"
            )
        )

    if "PORTAL" in df.columns:

        df["PORTAL"] = df[
            "PORTAL"
        ].apply(
            normalizar_portal
        )

    df = normalizar_orgao(df)

    return df

def validar_dataset(df):
    """
    Valida a qualidade do dataset após a normalização.
    Retorna um relatório com possíveis inconsistências.
    """

    relatorio = {}

    relatorio["TOTAL_REGISTROS"] = len(df)

    # ==========================================
    # CNPJ
    # ==========================================

    if "CNPJ" in df.columns:

        cnpj_vazio = df["CNPJ"].isna().sum()

    def cnpj_valido(valor):

        if pd.isna(valor):
            return True

        valor = str(valor).strip()

        if valor.endswith(".0"):
            valor = valor[:-2]

        return (
        valor.isdigit()
        and len(valor) == 14
    )   

    cnpj_invalidos = df[
        "CNPJ"
        ].apply(
    lambda x: not cnpj_valido(x)
        ).sum()

    print("\n=== CNPJs considerados inválidos ===")

    for valor in df["CNPJ"]:

        if pd.isna(valor):
            continue

        if not cnpj_valido(valor):

            print(
                repr(valor)
            )

    relatorio["CNPJ_VAZIO"] = cnpj_vazio
    relatorio["CNPJ_INVALIDO"] = cnpj_invalidos

    # ==========================================
    # DATAS
    # ==========================================

    for coluna in [
        "DATA_PUBLICACAO",
        "DATA_DISPUTA"
    ]:

        if coluna in df.columns:

            relatorio[
                f"{coluna}_INVALIDA"
            ] = df[coluna].isna().sum()

    # ==========================================
    # VALORES
    # ==========================================

    for coluna in [
    "VALOR_ESTIMADO",
    "VALOR_HOMOLOGADO"
    ]:

        if coluna in df.columns:

            preenchidos = df[
                coluna
            ].dropna()

            valores_invalidos = pd.to_numeric(
                preenchidos,
                errors="coerce"
            ).isna().sum()

            relatorio[
                f"{coluna}_VAZIO"
            ] = df[coluna].isna().sum()

            relatorio[
                f"{coluna}_INVALIDO"
            ] = valores_invalidos

    # ==========================================
    # ESTADO
    # ==========================================

    ufs_validas = {
        "AC", "AL", "AP", "AM",
        "BA", "CE", "DF", "ES",
        "GO", "MA", "MT", "MS",
        "MG", "PA", "PB", "PR",
        "PE", "PI", "RJ", "RN",
        "RS", "RO", "RR", "SC",
        "SP", "SE", "TO"
    }

    if "ESTADO" in df.columns:

        estados_invalidos = df[
            "ESTADO"
        ].dropna().apply(
            lambda x: x not in ufs_validas
        ).sum()

        relatorio[
            "ESTADO_INVALIDO"
        ] = estados_invalidos

    # ==========================================
    # PORTAL
    # ==========================================

    if "PORTAL" in df.columns:

        portais_vazios = df[
            "PORTAL"
        ].isna().sum()

        relatorio[
            "PORTAL_VAZIO"
        ] = portais_vazios

    # ==========================================
    # ÓRGÃO
    # ==========================================

    if "ORGAO" in df.columns:

        orgaos_vazios = df[
            "ORGAO"
        ].isna().sum()

        relatorio[
            "ORGAO_VAZIO"
        ] = orgaos_vazios

    return relatorio

def exibir_validacao(relatorio):
    """
    Exibe o resultado da validação.
    """

    print(
        "\n=== VALIDAÇÃO DO DATASET ==="
    )

    for campo, valor in relatorio.items():

        print(
            f"{campo}: {valor}"
        )

def validar_estrutura_dataset(df):
    """
    Valida a estrutura do dataset interno.
    """

    relatorio = {}

    colunas_atuais = list(df.columns)

    colunas_faltantes = [
        coluna
        for coluna in COLUNAS_DATASET_INTERNO
        if coluna not in colunas_atuais
    ]

    colunas_extras = [
        coluna
        for coluna in colunas_atuais
        if coluna not in COLUNAS_DATASET_INTERNO
    ]

    relatorio["COLUNAS_FALTANTES"] = colunas_faltantes
    relatorio["COLUNAS_EXTRAS"] = colunas_extras

    relatorio["ORDEM_CORRETA"] = (
        colunas_atuais == COLUNAS_DATASET_INTERNO
    )

    relatorio["TOTAL_COLUNAS"] = len(
        colunas_atuais
    )

    relatorio["TOTAL_REGISTROS"] = len(
        df
    )

    return relatorio

def validar_ids_dataset(df):
    """
    Valida a unicidade da combinação ID_INTERNO + CLIENTE.
    """

    relatorio = {}

    colunas = [
        "ID_INTERNO",
        "CLIENTE"
    ]

    if not all(
        coluna in df.columns
        for coluna in colunas
    ):

        relatorio["ERRO"] = (
            "ID_INTERNO ou CLIENTE ausente"
        )

        return relatorio

    relatorio["ID_INTERNO_VAZIO"] = (
        df["ID_INTERNO"].isna().sum()
    )

    relatorio["CLIENTE_VAZIO"] = (
        df["CLIENTE"].isna().sum()
    )

    duplicados = df.duplicated(
        subset=colunas,
        keep=False
    )

    relatorio["REGISTROS_DUPLICADOS"] = (
        duplicados.sum()
    )

    relatorio["COMBINACOES_UNICAS"] = (
        df[
            colunas
        ].drop_duplicates().shape[0]
    )

    return relatorio

def validar_estrutura_completa(df):
    """
    Executa todas as validações estruturais do dataset.
    """

    return {
        "ESTRUTURA": validar_estrutura_dataset(df),
        "IDS": validar_ids_dataset(df)
    }

def exibir_validacao_estrutura(relatorio):
    """
    Exibe a validação estrutural do dataset.
    """

    estrutura = relatorio[
        "ESTRUTURA"
    ]

    ids = relatorio[
        "IDS"
    ]

    print(
        "\n=== VALIDAÇÃO DA ESTRUTURA ==="
    )

    print(
        f"Total de registros: "
        f"{estrutura['TOTAL_REGISTROS']}"
    )

    print(
        f"Total de colunas: "
        f"{estrutura['TOTAL_COLUNAS']}"
    )

    print(
        f"Ordem correta: "
        f"{estrutura['ORDEM_CORRETA']}"
    )

    print(
        f"ID_INTERNO vazio: "
        f"{ids['ID_INTERNO_VAZIO']}"
    )

    print(
        f"CLIENTE vazio: "
        f"{ids['CLIENTE_VAZIO']}"
    )

    print(
        f"Registros duplicados: "
        f"{ids['REGISTROS_DUPLICADOS']}"
    )

    if estrutura["COLUNAS_FALTANTES"]:

        print(
            "\nColunas faltantes:"
        )

        for coluna in estrutura[
            "COLUNAS_FALTANTES"
        ]:

            print(
                f"- {coluna}"
            )

    if estrutura["COLUNAS_EXTRAS"]:

        print(
            "\nColunas extras:"
        )

        for coluna in estrutura[
            "COLUNAS_EXTRAS"
        ]:

            print(
                f"- {coluna}"
            )

if __name__ == "__main__":


    

    df = pd.read_csv(
        "dados/datasets/dataset_interno.csv"
    )

    relatorio = validar_estrutura_completa(
        df
    )

    exibir_validacao_estrutura(
        relatorio
    )

