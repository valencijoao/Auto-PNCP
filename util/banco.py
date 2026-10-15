import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime
from config.caminhos import DADOS
import json
from config.caminhos import COMPRAS
from ferramentas.gerar_dataset import analisar_itens

PASTA_BANCO = DADOS / "banco"



ARQUIVO_BANCO = PASTA_BANCO / "compras.db"

def definir_banco(caminho):
    """Define o arquivo SQLite utilizado pelas conexões seguintes."""
    global ARQUIVO_BANCO, PASTA_BANCO
    ARQUIVO_BANCO = Path(caminho).expanduser().resolve()
    PASTA_BANCO = ARQUIVO_BANCO.parent
    return ARQUIVO_BANCO

def conectar():
    """
    Conectar ao banco de dados SQLite.
    """

    PASTA_BANCO.mkdir(
            exist_ok=True,
            parents=True
    )

    return sqlite3.connect(
        ARQUIVO_BANCO,
    ) 

def criar_banco():
    """
    Cria as tabelas do banco de dados.
    """

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orgaos (
        

            cnpj TEXT PRIMARY KEY,
            orgao TEXT,
            estado TEXT,
            unidade TEXT,
            esfera TEXT,
            municipio TEXT

        )
    
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contratacoes (

            id_interno TEXT PRIMARY KEY,
            id TEXT,
            numero_compra TEXT,
            ano_compra INTEGER,
            sequencial_compra INTEGER,
            cnpj TEXT,

            valor_estimado REAL,
            valor_homologado REAL,

            data_publicacao TEXT,
            data_envio TEXT,
            data_disputa TEXT,

            modalidade TEXT,
            modo_disputa TEXT,
            situacao TEXT,
            srp BOOLEAN,

            link_pncp TEXT,
            link_portal TEXT,

            FOREIGN KEY (cnpj)
                REFERENCES orgaos(cnpj)
        
        
        )

    """)


    colunas_contratacoes = {
        linha[1]
        for linha in cursor.execute("PRAGMA table_info(contratacoes)")
    }
    if "data_envio" not in colunas_contratacoes:
        cursor.execute("ALTER TABLE contratacoes ADD COLUMN data_envio TEXT")
    cursor.execute("""
        UPDATE contratacoes
        SET data_envio = data_publicacao
        WHERE data_envio IS NULL OR TRIM(data_envio) = ''
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes(
        
            cliente TEXT PRIMARY KEY
        
        )

    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contratacao_cliente (
            id_interno TEXT,
            cliente TEXT,

            PRIMARY KEY(
                id_interno,
                cliente
            ),

            FOREIGN KEY (id_interno)
                REFERENCES contratacoes(id_interno),

            FOREIGN KEY(cliente)
                REFERENCES clientes(cliente)
        
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_interno TEXT NOT NULL,
            material_ou_servico TEXT,
            tipo_beneficio_nome TEXT,

            FOREIGN KEY (id_interno)
                REFERENCES contratacoes(id_interno)
        
        )
    
    """)

    conn.commit()

    conn.close()

    print(
        f"Banco criado em: {ARQUIVO_BANCO}"
    )


def inserir_orgaos(orgaos):
    conn = conectar()
    cursor = conn.cursor()

    for cnpj, orgao in orgaos.items():
        cursor.execute("""
            INSERT OR IGNORE INTO orgaos (
                cnpj,
                orgao,
                estado,
                unidade,
                esfera,
                municipio
            )
            VALUES(?,?,?,?,?,?)
        """, (
            orgao.get('CNPJ'),
            orgao.get('RAZAO_SOCIAL'),
            orgao.get('UF'),
            orgao.get('UNIDADE'),
            orgao.get('ESFERA'),
            orgao.get('MUNICIPIO')
    ))

    conn.commit()
    conn.close()

    print(f"{len(orgaos)} órgãos processados.")


def inserir_contratacoes(df):
    conn = conectar()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO contratacoes (
                id_interno,
                id,
                numero_compra,
                ano_compra,
                sequencial_compra,
                cnpj,
                valor_estimado,
                valor_homologado,
                data_publicacao,
                data_envio,
                data_disputa,
                modalidade,
                modo_disputa,
                situacao,
                srp,
                link_pncp,
                link_portal
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            row["ID_INTERNO"],
            row["ID"],
            row["NUMERO_COMPRA"],
            row["ANO_COMPRA"],
            row["SEQUENCIAL_COMPRA"],
            row["CNPJ"],
            row["VALOR_ESTIMADO"],
            row["VALOR_HOMOLOGADO"],
            row["DATA_PUBLICACAO"],
            datetime.now().isoformat(sep=" ", timespec="seconds"),
            row["DATA_DISPUTA"],
            row["MODALIDADE"],
            row["MODO_DISPUTA"],
            row["SITUACAO"],
            row["SRP"],
            row["LINK_PNCP"],
            row["LINK_PORTAL"]
            
        ))

    conn.commit()
    conn.close()

    print(f"{len(df)} contratações processadas.")


def inserir_clientes(df):
    """
    Insere os cliente no banco de dados relacioando ao projeto.
    """

    conn = conectar()
    cursor = conn.cursor()

    clientes = df['CLIENTE'].dropna().unique()

    for cliente in clientes:
        cursor.execute("""
            INSERT OR IGNORE INTO clientes (
                cliente
            )
            VALUES (?)

    """,(cliente,))

    conn.commit()
    conn.close()

    print(f'{len(clientes)} clientes processados.')


def inserir_vinculos_clientes(df):
    """
    Cria os vínculos entre clientes e ID_INTERNO.
    """   

    conn = conectar()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO contratacao_cliente(  
                id_interno,
                cliente
            )
            VALUES (?, ?)
    """, (
        row['ID_INTERNO'],
        row['CLIENTE']
    )
    )

    conn.commit()
    conn.close()

    print(f"{len(df)} vínculos processados.")

def inserir_compra(compra):
    """
    Insere uma contratação desejada no banco de dados.
    """

    from ferramentas.gerar_dataset import extrair_dados_compra

    registro = extrair_dados_compra(compra)

    if registro is None:
        print("Compra sem dados suficientes. Não inserida.")
        return
    
    clientes = compra.get("clientes",{})
    itens = compra.get("itens",[])

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO orgaos (
        cnpj,
        orgao,
        estado,
        unidade,
        esfera,
        municipio
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,(
        registro["CNPJ"],
        registro["ORGAO"],
        registro["ESTADO"],
        registro["UNIDADE"],
        registro["ESFERA"],
        registro["MUNICIPIO"]
    ))

    cursor.execute("""
        INSERT OR IGNORE INTO contratacoes (
            id_interno,
            id,
            numero_compra,
            ano_compra,
            sequencial_compra,
            cnpj,
            valor_estimado,
            valor_homologado,
            data_publicacao,
            data_envio,
            data_disputa,
            modalidade,
            modo_disputa,
            situacao,
            srp,
            link_pncp,
            link_portal
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        registro["ID_INTERNO"],
        registro["ID"],
        registro["NUMERO_COMPRA"],
        registro["ANO_COMPRA"],
        registro["SEQUENCIAL_COMPRA"],
        registro["CNPJ"],
        registro["VALOR_ESTIMADO"],
        registro["VALOR_HOMOLOGADO"],
        registro["DATA_PUBLICACAO"],
        datetime.now().isoformat(sep=" ", timespec="seconds"),
        registro["DATA_DISPUTA"],
        registro["MODALIDADE"],
        registro["MODO_DISPUTA"],
        registro["SITUACAO"],
        registro["SRP"],
        registro["LINK_PNCP"],
        registro["LINK_PORTAL"]
    ))

    for cliente in clientes:
    
        cursor.execute("""
            INSERT OR IGNORE INTO clientes (
                cliente
            )
            VALUES(?)
        """, (cliente,))

        cursor.execute("""
            INSERT OR IGNORE INTO contratacao_cliente (
                id_interno,
                cliente
            )
            VALUES (?, ?)
    """, (
        registro['ID_INTERNO'],
        cliente
    ))

    id_interno = registro['ID_INTERNO']

    cursor.execute("""
        DELETE FROM itens
        WHERE id_interno = ?
    """, (id_interno,))

    for item in itens:
        cursor.execute("""
            INSERT INTO itens (
                id_interno,
                material_ou_servico,
                tipo_beneficio_nome
            )
            VALUES (?, ?, ?)
        """, (
            id_interno,
            item.get("materialOuServico"),
            item.get("tipoBeneficioNome")
        ))

    conn.commit()
    conn.close()

    print(f"Compra inserida: {id_interno}")


def obter_pasta_contratacao(id_interno):
    """
    Localiza a pasta de uma contratação a partir do ID_INTERNO.
    """

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            cnpj,
            ano_compra,
            sequencial_compra
        FROM contratacoes
        WHERE id_interno = ?
    """, (id_interno,))

    resultado = cursor.fetchone()

    conn.close()

    if resultado is None:
        return None

    cnpj, ano, sequencial = resultado

    return COMPRAS / f"{cnpj}-{ano}-{sequencial}"

def consultar_contratacao(cnpj,ano,sequencial):
    """
    Encontra um processo no banco de dados.
    """

    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.id_interno,
            c.id,
            c.numero_compra,
            c.sequencial_compra,
            c.ano_compra,
            c.cnpj,
            c.valor_estimado,
            c.valor_homologado,
            c.data_publicacao,
            c.data_envio,
            c.data_disputa,
            c.modalidade,
            c.modo_disputa,
            c.situacao,
            c.srp,
            c.link_pncp,
            c.link_portal,
            o.orgao,
            o.estado,
            o.unidade,
            o.esfera,
            o.municipio
        FROM contratacoes c
        LEFT JOIN orgaos o
            ON c.cnpj = o.cnpj
        WHERE c.cnpj = ?
            AND c.ano_compra = ?
            AND c.sequencial_compra = ?
    """, (
        cnpj,
        ano,
        sequencial
    ))

    resultado = cursor.fetchone()

    conn.close()

    return dict(resultado) if resultado is not None else None

def consultar_clientes_contratacao(id_interno):
    """Retorna os nomes dos clientes associados a uma contratação."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT cliente FROM contratacao_cliente WHERE id_interno = ? ORDER BY cliente", (id_interno,))
    clientes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return clientes

def consultar_contratacoes_filtro(filtro, valor):
    """Consulta contratações por estado, órgão, cliente ou situação."""
    campos = {
        "estado": "o.estado",
        "orgao": "o.orgao",
        "cliente": "cc.cliente",
        "situacao": "c.situacao",
    }
    if filtro not in campos:
        raise ValueError("Filtro não suportado.")
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT DISTINCT c.id_interno, c.id, c.numero_compra, c.ano_compra,
            c.sequencial_compra, c.cnpj, o.orgao, o.estado, c.situacao,
            c.valor_estimado, c.link_pncp
        FROM contratacoes c
        LEFT JOIN orgaos o ON c.cnpj = o.cnpj
        LEFT JOIN contratacao_cliente cc ON c.id_interno = cc.id_interno
        WHERE {campos[filtro]} LIKE ?
        ORDER BY c.ano_compra DESC, c.sequencial_compra
    """, (f"%{valor}%",))
    resultados = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return resultados

def mesclar_banco(caminho_backup):
    """Mescla registros ausentes do backup no banco atualmente selecionado.

    Em caso de conflito de chave primária, preserva o registro do banco de destino.
    Retorna a quantidade de registros adicionados por tabela.
    """
    backup = Path(caminho_backup).expanduser().resolve()
    destino = Path(ARQUIVO_BANCO).expanduser().resolve()
    if not backup.is_file() or backup.suffix.lower() != ".db":
        raise FileNotFoundError("O arquivo de backup .db não foi encontrado.")
    if backup == destino:
        raise ValueError("O backup selecionado é o próprio banco de destino.")

    colunas = {
        "orgaos": ("cnpj", "orgao", "estado", "unidade", "esfera", "municipio"),
        "contratacoes": (
            "id_interno", "id", "numero_compra", "ano_compra", "sequencial_compra",
            "cnpj", "valor_estimado", "valor_homologado", "data_publicacao",
            "data_envio", "data_disputa", "modalidade", "modo_disputa", "situacao", "srp",
            "link_pncp", "link_portal",
        ),
        "clientes": ("cliente",),
        "contratacao_cliente": ("id_interno", "cliente"),
    }

    conn = conectar()
    try:
        conn.execute("ATTACH DATABASE ? AS banco_backup", (str(backup),))
        colunas_backup = {}
        for tabela, esperadas in colunas.items():
            encontradas = {
                linha[1]
                for linha in conn.execute(f"PRAGMA banco_backup.table_info({tabela})")
            }
            requeridas = set(esperadas)
            if tabela == "contratacoes":
                requeridas.discard("data_envio")
            if not requeridas.issubset(encontradas):
                raise ValueError(f"O arquivo selecionado não possui uma tabela AutoPainel válida: {tabela}.")
            colunas_backup[tabela] = encontradas

        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("BEGIN IMMEDIATE")
        adicionados = {}
        for tabela, campos in colunas.items():
            lista = ", ".join(campos)
            fontes = []
            for campo in campos:
                if tabela == "contratacoes" and campo == "data_envio":
                    if "data_envio" in colunas_backup[tabela]:
                        fontes.append("COALESCE(NULLIF(data_envio, ''), data_publicacao)")
                    else:
                        fontes.append("data_publicacao")
                else:
                    fontes.append(campo)
            cursor = conn.execute(
                f"INSERT OR IGNORE INTO main.{tabela} ({lista}) "
                f"SELECT {', '.join(fontes)} FROM banco_backup.{tabela}"
            )
            adicionados[tabela] = cursor.rowcount
        conn.commit()
        return adicionados
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def adicionar_cliente_contratacao(id_interno, cliente):
    """
    Adiciona um cliente a uma contratação
    no banco de dados e no clientes.json.
    """

    pasta = obter_pasta_contratacao(id_interno)

    if pasta is None:
        print(
            f"Contratação '{id_interno}' não encontrada"
        )
        return

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO clientes (
            cliente
        )
        VALUES (?)
    """, (cliente,))

    cursor.execute("""
        INSERT OR IGNORE INTO contratacao_cliente (
            id_interno,
            cliente
        )
        VALUES (?, ?)
    """, (
        id_interno,
        cliente
    ))

    conn.commit()

    cursor.execute("""
        SELECT cliente
        FROM contratacao_cliente
        WHERE id_interno = ?
    """, (id_interno,))

    clientes = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    atualizar_clientes_json(
        pasta,
        clientes
    )

    print(
        f"Cliente '{cliente}' associado à contratação "
        f"{id_interno}."
    )


def remover_cliente_contratacao(id_interno, cliente):
    """
    Remove um cliente de uma contratação
    no banco de dados e no clientes.json.
    """

    pasta = obter_pasta_contratacao(id_interno)

    if pasta is None:
        print(
            f"Contratação: '{id_interno}' não encontrada."
        )
        return

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM contratacao_cliente
        WHERE id_interno = ?
          AND cliente = ?
    """, (
        id_interno,
        cliente
    ))

    removido = cursor.rowcount

    if removido:
        cursor.execute("""
            SELECT cliente
            FROM contratacao_cliente
            WHERE id_interno = ?
        """, (id_interno,))

        clientes = [
            row[0]
            for row in cursor.fetchall()
        ]

    conn.commit()
    conn.close()

    if removido:
        atualizar_clientes_json(
            pasta,
            clientes
        )

        print(
            f"Cliente '{cliente}' removido da contratação "
            f"{id_interno}."
        )

    else:
        print(
            f"Cliente '{cliente}' não está associado à contratação "
            f"{id_interno}."
        )




def atualizar_clientes_json(pasta, clientes):
    """
    Atualiza a lista de clientes no clientes.json
    de uma contratação.

    Mantém os demais dados do arquivo, como o campo 'item'.
    """

    arquivo = pasta / "clientes.json"

    if arquivo.exists():
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
    else:
        dados = {}

    if isinstance(dados, list):
        dados = {
            "clientes": dados
        }

    dados["clientes"] = clientes

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(
            dados,
            f,
            ensure_ascii=False,
            indent=4
        )

def consultar_dataset():
    """
    Lê o dataset diretamento no SQLite.
    """

    conn = conectar()

    consulta = """
        SELECT 
            c.id_interno AS ID_INTERNO,
            c.id AS ID,
            cc.cliente AS CLIENTE,

            c.numero_compra AS NUMERO_COMPRA,
            c.ano_compra AS ANO_COMPRA,
            c.sequencial_compra AS SEQUENCIAL_COMPRA,

            o.estado AS ESTADO,
            o.unidade AS UNIDADE,
            o.cnpj AS CNPJ,
            o.orgao AS ORGAO,
            o.esfera AS ESFERA,
            o.municipio AS MUNICIPIO,

            c.valor_estimado AS VALOR_ESTIMADO,
            c.valor_homologado AS VALOR_HOMOLOGADO,            
            
            c.data_publicacao AS DATA_PUBLICACAO,
            c.data_disputa AS DATA_DISPUTA,

            c.modalidade AS MODALIDADE,
            c.modo_disputa AS MODO_DISPUTA,
            c.situacao AS SITUACAO,
            c.srp AS SRP,
            
            c.link_pncp AS LINK_PNCP,
            c.link_portal AS LINK_PORTAL

        FROM contratacoes c

        LEFT JOIN orgaos o
            ON c.cnpj = o.cnpj
        
        LEFT JOIN contratacao_cliente cc
            ON c.id_interno = cc.id_interno

        ORDER BY 
            c.ano_compra DESC,
            c.sequencial_compra
    """

    consulta_itens = """
        SELECT
            id_interno,
            material_ou_servico,
            tipo_beneficio_nome
        FROM itens
        ORDER BY id_interno
    """

    try:
        df = pd.read_sql_query(consulta, conn)
        df_itens = pd.read_sql_query(consulta_itens, conn)
    finally:
        conn.close()

    itens_por_compra = {}

    for _, linha in df_itens.iterrows():
        id_interno = linha['id_interno']

        item = {
            "materialOuServico": linha["material_ou_servico"],
            "tipoBeneficioNome": linha["tipo_beneficio_nome"]
        }

        itens_por_compra.setdefault(id_interno, []).append(item)

    indicadores = df["ID_INTERNO"].map(
        lambda id_interno: analisar_itens(
            itens_por_compra.get(id_interno,[])
        )
    )

    df_indicadores = pd.DataFrame(
        indicadores.tolist(),
        index= df.index

    )

    df =  pd.concat(
        [df, df_indicadores],
        axis=1
    )

    return df


def validacao_compras_local():
    """
    Verifica as contratações armazenadas localmente
    e procura correspondência no banco de dados.
    Não altera dados.
    """

    from ferramentas.gerar_dataset import (
        carregar_compra,
        extrair_dados_compra)
    
    from config.caminhos import COMPRAS

    conn = conectar()
    cursor = conn.cursor()

    total_pastas = 0
    compras_com_dados = 0
    compras_com_itens = 0
    compras_encontradas = 0
    compras_nao_encontradas = 0
    total_itens = 0
    itens_de_compras_encontradas = 0
    compras_invalidas = 0

    try:        
        pastas = [
            pasta
            for pasta in COMPRAS.iterdir()
            if pasta.is_dir()
        ]

        total_pastas = len(pastas)



        for pasta in pastas:
            try:
                compra = carregar_compra(pasta)
                registro = extrair_dados_compra(compra)
            except (OSError, ValueError, TypeError) as erro:
                print(f"Falha ao processar {pasta.name}: {erro}")
                compras_invalidas += 1
                continue

            if not isinstance(compra, dict) or not compra.get("dados"):
                continue

            compras_com_dados += 1

            itens = compra.get("itens",[])

            if not isinstance(itens, list):
                compras_invalidas += 1
                continue

            quantidade_itens = len(itens)

            if quantidade_itens > 0:
                compras_com_itens +=1
                total_itens += quantidade_itens

            if not registro:
                compras_invalidas += 1
                continue

            id_interno = registro.get("ID_INTERNO")

            if not id_interno:
                compras_invalidas += 1
                continue
            
            cursor.execute("""
                SELECT 1
                FROM contratacoes
                WHERE id_interno = ?
                LIMIT 1
                """,
                (id_interno,),
            )

            resultado = cursor.fetchone()

            if resultado:
                compras_encontradas += 1
                itens_de_compras_encontradas += quantidade_itens
            else:
                compras_nao_encontradas += 1


    finally:
        conn.close()

    print("\n=== Validação das compras já baixadas ===")
    print(f"Pastas encontradas: {total_pastas}")
    print(f"Contratações com dados JSON: {compras_com_dados}")
    print(f"Contratações com itens nos JSONs: {compras_com_itens}")
    print(f"Total de itens nos JSONs: {total_itens}")
    print(f"Contratações encontradas no banco: {compras_encontradas}")
    print(f"Contratações não encontradas no banco: {compras_nao_encontradas}")
    print(f"Itens associados a contratações encontradas: {itens_de_compras_encontradas}")
    print(f"Pastas ou contratações inválidas: {compras_invalidas}")


        
if __name__ =="__main__":

    criar_banco()
 
 
