import sqlite3
from pathlib import Path
from config.caminhos import CAMINHO_BANCO

TABELAS_ESPERADAS = [
    "orgaos",
    "contratacoes",
    "clientes",
    "contratacao_cliente",
    "itens",
]

if not CAMINHO_BANCO.is_file():
    raise FileNotFoundError(
        f"Banco não encontrado: {CAMINHO_BANCO}\n"
        "Confira o caminho do arquivo SQLite utilizado pelo projeto."
    )

conn = sqlite3.connect(
    f"{CAMINHO_BANCO.as_uri()}?mode=ro",
    uri=True
)

conn.execute("PRAGMA foreign_keys = ON")

try:
    tabelas_existentes = {
        linha[0]
        for linha in conn.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
        """)
    }

    print(f"Banco auditado: {CAMINHO_BANCO}")

    print("\n=== 1. Tabelas e registros ===")

    for tabela in TABELAS_ESPERADAS:
        if tabela not in tabelas_existentes:
            print(f"\n{tabela}: TABELA AUSENTE")
            continue

        quantidade = conn.execute(
            f'SELECT COUNT(*) FROM "{tabela}"'
        ).fetchone()[0]

        print(f"\n{tabela}: {quantidade} registros")

        colunas = conn.execute(
            f'PRAGMA table_info("{tabela}")'
        ).fetchall()

        for coluna in colunas:
            nome = coluna[1]
            tipo = coluna[2]
            chave = " PK" if coluna[5] else ""
            print(f"  - {nome}: {tipo}{chave}")

    print("\n=== 2. Campos essenciais vazios ===")

    verificacoes = {
        "orgaos": ["cnpj"],
        "contratacoes": ["id_interno", "cnpj"],
        "clientes": ["cliente"],
        "contratacao_cliente": ["id_interno", "cliente"],
        "itens": ["id_interno"],
    }

    for tabela, campos in verificacoes.items():
        if tabela not in tabelas_existentes:
            continue

        colunas = {
            linha[1]
            for linha in conn.execute(
                f'PRAGMA table_info("{tabela}")'
            )
        }

        for campo in campos:
            if campo not in colunas:
                print(f"{tabela}.{campo}: COLUNA AUSENTE")
                continue

            sql = f"""
                SELECT COUNT(*)
                FROM "{tabela}"
                WHERE "{campo}" IS NULL
                   OR TRIM(CAST("{campo}" AS TEXT)) = ''
            """

            total = conn.execute(sql).fetchone()[0]
            print(f"{tabela}.{campo}: {total} valores vazios")

    print("\n=== 3. Integridade referencial ===")

    erros = conn.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    print(f"Violações de chaves estrangeiras: {len(erros)}")

    for erro in erros[:20]:
        print("  ", erro)

    consultas_orfaos = {
        "Contratações sem órgão correspondente": """
            SELECT COUNT(*)
            FROM contratacoes c
            LEFT JOIN orgaos o ON o.cnpj = c.cnpj
            WHERE o.cnpj IS NULL
        """,
        "Vínculos sem contratação": """
            SELECT COUNT(*)
            FROM contratacao_cliente cc
            LEFT JOIN contratacoes c
                ON c.id_interno = cc.id_interno
            WHERE c.id_interno IS NULL
        """,
        "Vínculos sem cliente": """
            SELECT COUNT(*)
            FROM contratacao_cliente cc
            LEFT JOIN clientes cl ON cl.cliente = cc.cliente
            WHERE cl.cliente IS NULL
        """,
        "Itens sem contratação": """
            SELECT COUNT(*)
            FROM itens i
            LEFT JOIN contratacoes c
                ON c.id_interno = i.id_interno
            WHERE c.id_interno IS NULL
        """,
    }

    print("\n=== 4. Registros sem correspondência ===")

    for descricao, sql in consultas_orfaos.items():
        tabelas_necessarias = {
            "Contratações sem órgão correspondente":
                {"contratacoes", "orgaos"},
            "Vínculos sem contratação":
                {"contratacao_cliente", "contratacoes"},
            "Vínculos sem cliente":
                {"contratacao_cliente", "clientes"},
            "Itens sem contratação":
                {"itens", "contratacoes"},
        }[descricao]

        if tabelas_necessarias.issubset(tabelas_existentes):
            total = conn.execute(sql).fetchone()[0]
            print(f"{descricao}: {total}")

    if {"contratacoes", "itens"}.issubset(tabelas_existentes):
        print("\n=== 5. Cobertura dos itens ===")

        resultado = conn.execute("""
            SELECT
                COUNT(*) AS total_contratacoes,
                COUNT(DISTINCT i.id_interno)
                    AS contratacoes_com_itens,
                SUM(CASE WHEN i.id_interno IS NULL
                    THEN 1 ELSE 0 END)
                    AS contratacoes_sem_itens
            FROM contratacoes c
            LEFT JOIN (
                SELECT DISTINCT id_interno
                FROM itens
            ) i ON i.id_interno = c.id_interno
        """).fetchone()

        print(f"Total de contratações: {resultado[0]}")
        print(f"Com itens: {resultado[1]}")
        print(f"Sem itens: {resultado[2]}")

finally:
    conn.close()

print("\nAuditoria concluída. Nenhum dado foi alterado.")
