from pathlib import Path

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DADOS = BASE_DIR / "dados"

COMPRAS = DADOS / "compras"
DATASETS = DADOS / "datasets"
CLIENTES = DADOS / "enviadas"
TRADUZIDOS = DADOS / "traduzidos"

DADOS.mkdir(exist_ok=True)

COMPRAS.mkdir(exist_ok=True)
DATASETS.mkdir(exist_ok=True)
CLIENTES.mkdir(exist_ok=True)
TRADUZIDOS.mkdir(exist_ok=True)