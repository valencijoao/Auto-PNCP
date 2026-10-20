from util.banco import conectar

conn = conectar()

itens = conn.execute("""
SELECT COUNT(*) AS itens_sem_contratacao
FROM itens i
LEFT JOIN contratacoes c
    ON c.id_interno = i.id_interno
WHERE c.id_interno IS NULL;
    """).fetchone()


print(itens)

conn.close()



