from ferramentas.gerar_orgaos import gerar_orgaos 
from ferramentas.gerar_dataset import gerar_dataset
from util.banco import inserir_orgaos, inserir_contratacoes, inserir_vinculos_clientes, inserir_clientes, consultar_contratacao
import sqlite3

df = gerar_dataset()

from util.banco import consultar_contratacao

from ferramentas.gerar_dataset import carregar_compra
from util.banco import inserir_compra, adicionar_cliente_contratacao, remover_cliente_contratacao
from config.caminhos import COMPRAS

import sqlite3

from util.banco import (
    inserir_orgaos,
    inserir_contratacoes,
    inserir_vinculos_clientes,
    inserir_clientes,
    consultar_contratacao
)


pasta = COMPRAS / "45787660000100-2026-268"

resultado = consultar_contratacao("18315218000109",2026,67)
print(resultado)