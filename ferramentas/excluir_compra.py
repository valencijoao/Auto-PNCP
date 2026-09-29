from ferramentas.gerar_dataset import excluir_compra_dataset


if __name__ == "__main__":
    id_interno = input("ID_INTERNO da compra que deseja excluir: ").strip()

    if id_interno:
        excluir_compra_dataset(id_interno)
    else:
        print("Exclusão cancelada: nenhum ID informado.")
