from datetime import datetime

def formatar_data(data):
    """
    Padroniza todas as datas para o modelo correto
    """

    if not data:
        return None
    
    try:
        return datetime.fromisoformat(
            data.replace("Z","")
        ).strftime("%d/%m/%Y")
    
    except Exception:
        return data