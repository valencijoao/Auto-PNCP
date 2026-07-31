import json
from pathlib import Path

PASTA =Path('dados')

def carregar_swagger(tipo='consulta'):
    """
    Carrega um arquivo swagger do PNCP.
    """

    arquivos = {
        "consulta": "swagger_consulta.json",
        "manutencao": "swagger_manutencao.json"

    }


    caminho = PASTA / arquivos[tipo]

    with open(caminho, encoding='utf-8') as f:
        return json.load(f)
    
def resumo_api(swagger):
    """
    Resume as informações contidas no swagger.json.
    """

    print("\n===== RESUMO =====\n")

    print("OpenAPI:", swagger.get('openapi'))

    info = swagger.get("info", {})

    print("Título :", info.get("title"))
    print("Versão :", info.get("version"))
    print("Descrição: ", info.get("description"))

    print("\nQuantidade de endpoints:",
        len(swagger.get('components', {}))
          )

    print("\nQuantidade de schemas:",
        len(swagger.get('components',{}).get('schemas',{}))
          )


def pesquisar_endpoints(swagger,palavra):
    """
    Procura uma palavra nos endpoints da API.
    """

    print(f"\n====='{palavra}'=====\n")

    encontrou = False

    paths = swagger.get("paths",{})

    for endpoint, metodos in sorted(paths.items()):

        if palavra.lower() not in endpoint.lower():
            continue

        encontrou = True

        for metodo, info in metodos.items():

            summary = info.get("summary","Sem resumo")

            print(f"{metodo.upper():6} {endpoint}")
            print(f"        {summary}")

        print()

    if not encontrou:
        print("Nenhum endpoint encontrado.")


def listar_schemas(swagger):
    """
    Lista todos os schemas do Swagger.
    """

    print("\n===== SCHEMAS =====\n")

    schemas = swagger.get("components", {}).get("schemas", {})

    for schema in schemas:
        print(schema)


def inspecionar_schema(swagger, nome_schema):
    """
    Exibe todas as informações de um schema específico.
    """

    schemas = swagger.get("components", {}).get("schemas", {})

    if nome_schema not in schemas:
        print(f"\nSchema '{nome_schema}' não encontrado.")
        return

    schema = schemas[nome_schema]

    print(f"====='{nome_schema}'=====\n")

    print(json.dumps(
        schema,
        indent=4,
        ensure_ascii=False
    ))


def listar_campos_schemas(swagger, nome_schema):
    """
    Lista os campos de um schema.
    """

    schemas = swagger.get("components", {}).get("schemas", {})

    if nome_schema not in schemas:
        print(f"\nSchema '{nome_schema}' não encontrado.")
        return

    schema = schemas[nome_schema]

    propriedades = schema.get("properties", {})

    print(f"\n===== CAMPOS DE {nome_schema} =====\n")

    if not propriedades:
        print("Este schema não possui propriedades.")
        return

    for campo, info in propriedades.items():

        tipo = info.get("type","$ref")

        descricao = info.get("description", "")

        print(f"{campo}")
        print(f"   tipo: {tipo}")

        if descricao:
            print(f"   descrição: {descricao}")

        if "$ref" in info:
            print(f"   referência: {info['$ref']}")

        print()


def listar_endpoints(swagger):
    """
    Lista todos os endpoints disponíveis.
    """

    print("\n===== ENDPOINTS =====\n")

    paths = swagger.get("paths", {})

    for endpoint in sorted(paths):

        metodos = ", ".join(paths[endpoint].keys())

        print(f"{metodos.upper():8} {endpoint}")

    print()


def inspecionar_endpoint(swagger, endpoint):
    """
    Exibe todas as informações de um endpoint.
    """

    paths = swagger.get("paths", {})

    if endpoint not in paths:
        print("Endpoint '{endpoint}' não encontrado")

    print(f"\n====='{endpoint}'=====\n")

    for metodo, info in paths[endpoint].items():

        print(f"MÉTODO: {metodo.upper()}")

        resumo = info.get("summary")

        if resumo:
            print("\nResumo:")
            print(resumo)

        descricao = info.get("description")

        if descricao:
            print("\nDescrição:")
            print(descricao)

        parametros = info.get("parameters",[])
        

        if parametros:
            print("\nParâmetros")

            for parametro in parametros:

                print(

                    f"- {parametro.get('name')}"
                    f"({parametro.get('in')})"

                    )

        request_body = info.get("requestBody")

        if request_body:
            print(f"\nBody da requisição")

            conteudos = request_body.get("content",{})

            for tipo, dados in conteudos.items():

                schema = (
                    dados
                    .get("schema",{})
                    .get("$ref")
                )

            print(f"- {tipo}")

            if schema:
                print(f"   {schema.split('/')[-1]}")

        

        respostas = info.get("responses",{})

        if respostas:
            print("\nRespostas:")

            for codigo, resposta in respostas.items():
                print(f"- {codigo}")

                descricao = resposta.get("description")

                if descricao:
                    print(descricao)

                conteudos = resposta.get("content",{})

                for tipo, dados in conteudos.items():

                    schema = (
                        dados
                        .get("schema",{})
                        .get("$ref")
                    )

                if schema:

                    print(
                        f"Schema: {schema.split('/')[-1]}"
                    )

        content = resposta.get("content", {})
            
        for tipo, dados in content.items():
            
            print(f"  Tipo: {tipo}")
            
            schema = dados.get("schema", {})
            
            if "$ref" in schema:
                print(
                "  Schema:",
                schema["$ref"].split("/")[-1]
                )
            
            elif "items" in schema:
            
                items = schema["items"]
            
                if "$ref" in items:
                    print(
                    "  Lista de:",
                    items["$ref"].split("/")[-1]
                    )

                if "$ref" in items:

                    schema = items["$ref"].split("/")[-1]

                    print(f"  Lista de: {schema}")

                    listar_campos_schemas(swagger, schema)
                

        print()

                

def procurar_endpoint(swagger, palavra):
    """
    Procura endpoints contendo determinada palavra.
    """

    print(f"\n===== BUSCANDO '{palavra}' =====\n")

    paths = swagger.get("paths", {})

    for endpoint in paths:

        if palavra.lower() in endpoint.lower():
            print(endpoint)


def procurar_codigo_descricao(swagger):
    """
    Procura schemas que possuem campos de código e descrição.
    """

    schemas = (
        swagger
        .get("components", {})
        .get("schemas", {})
    )

    print("\n===== POSSÍVEIS DOMÍNIOS =====\n")

    for nome, schema in schemas.items():

        propriedades = schema.get("properties", {})

        nomes = {
            chave.lower()
            for chave in propriedades.keys()
        }

        possui_codigo = any(
            x in nomes
            for x in (
                "codigo",
                "id",
                "valor"
            )
        )

        possui_descricao = any(
            x in nomes
            for x in (
                "descricao",
                "nome",
                "titulo"
            )
        )

        if possui_codigo and possui_descricao:
            print(nome)




if __name__ == "__main__":

    swagger = carregar_swagger("consulta")

    # resumo_api(swagger)

    # listar_endpoints(swagger)

    pesquisar_endpoints(swagger, "compra")

    # listar_schemas(swagger)

    # pesquisar_schemas(swagger, "modal")

    # procurar_codigo_descricao(swagger)

    # procurar_endpoint(swagger, "unidade")

    inspecionar_endpoint(swagger, "/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens")

    #listar_campos_schemas(swagger, "Compra")
