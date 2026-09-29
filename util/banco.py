import sqlite3
from pathlib import Path
from config.caminhos import DADOS

PASTA_BANCO = DADOS / "banco"

ARQUIVO_BANCO = PASTA_BANCO / "compras.db"

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
    Cria o banco de dados.
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
                data_disputa,
                modalidade,
                modo_disputa,
                situacao,
                srp,
                link_pncp,
                link_portal
            )
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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




if __name__ =="__main__":

    criar_banco()
