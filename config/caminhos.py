from pathlib import Path
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

DADOS = BASE_DIR / "dados"
COMPRAS = DADOS / "compras"
BANCO = DADOS / "banco"
DATASETS = DADOS / "datasets"
CLIENTES = DADOS / "enviadas"
TRADUZIDOS = DADOS / "traduzidos"
PASTA_DE_REDE = Path(
    r"\\SERVIDOR\AutoPainel\datasets"
)
CAMINHO_DOMINIOS = DADOS / "dominios.json"
CAMINHO_ORGAOS = DADOS/ "orgaos.json"
CAMINHO_PORTAIS_TRATADOS = DADOS / "portais_tratados.json"
CAMINHO_BANCO = BANCO / "compras.db"

DADOS.mkdir(exist_ok=True)

COMPRAS.mkdir(exist_ok=True)
DATASETS.mkdir(exist_ok=True)
CLIENTES.mkdir(exist_ok=True)
TRADUZIDOS.mkdir(exist_ok=True)
