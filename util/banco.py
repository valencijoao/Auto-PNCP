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
            numero_compras TEXT,
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


if __name__ =="__main__":

    criar_banco()
