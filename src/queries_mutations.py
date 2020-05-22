from github_requests import GitApiRequests
from ariadne import ObjectType, QueryType, gql, make_executable_schema, MutationType
from ariadne.asgi import GraphQL

# Definição do esquema.
type_defs = gql("""

    type Query {
        return_repositories_names(username: String!): [Repository!]!
        return_repository_details(username: String!, name: String!): [Repository!]!
    }

    type Repository {
        id: String,
        node_id: String,
        name: String
        full_name: String,
        html_url: String,
        description: String,
        git_url: String,
        clone_url: String
    }
    
    type Mutation {
        create_token(username: String!, password: String!, token_note: String!): String!
        create_public_repo(username: String!, token: String!,
            repo_name: String!, description: String!): String!
    }

""")

# Binding resolvers com o schema.
query = QueryType()
mutation = MutationType()

# Mapeando a função resolver para o tipo Repository criado
repository = ObjectType("Repository")


# Query que exige o username e retorna os repos desse user através da classe GitApiRequests.
@query.field("return_repositories_names")
def resolve_return_repositories_names(*_, username):
    repo_request = GitApiRequests(username)
    return repo_request.github_request_repos()


# Query que exige o username e o nome do repo e retorna alguns campos desse repo através da classe GitApiRequests.
@query.field("return_repository_details")
def resolve_return_repository_details(*_, username, name):
    repo_request = GitApiRequests(username)
    git_hub_api_response_json = repo_request.github_request_repo_details(name)
    return [{
        "id": git_hub_api_response_json["id"],
        "node_id": git_hub_api_response_json["node_id"],
        "full_name": git_hub_api_response_json["full_name"],
        "html_url": git_hub_api_response_json["html_url"],
        "description": git_hub_api_response_json["description"],
        "git_url": git_hub_api_response_json["git_url"],
        "clone_url": git_hub_api_response_json["clone_url"]
    }]


# Mutation que cria um novo oath token para um determinado usuário solicitando os campos obrigatórios.
# Em caso de sucesso o token será exibido.
@mutation.field("create_token")
def resolve_create_token(*_, username, password, token_note):
    token_requested = GitApiRequests(username).github_request_create_token(password, token_note)
    if token_requested.status_code == 201:
        return "Oauth Token criado com sucesso. Token: " + token_requested.json()["token"]
    else:
        return "Não foi possível criar a chave. Código do erro: "+str(token_requested.status_code) + \
            ". Para mais informações sobre esse erro consulte a API do Github: https://developer.github.com/v3/"


# Mutation que cria um novo repositório para um determinado usuário solicitando os campos obrigatórios.
# Em caso de sucesso a URL será exibida.
@mutation.field("create_public_repo")
def resolve_create_public_repo(*_, username, token, repo_name, description):
    repo_requested = GitApiRequests(username).github_request_create_repo(username, token, repo_name, description)
    if repo_requested.status_code == 201:
        new_repo_url = ("https://github.com/"+username+"/"+repo_name).replace(" ", "-")
        return "Repositório criado com sucesso. Repo API URL: "+new_repo_url
    else:
        return "Não foi possível criar a chave. Código do erro: " + str(repo_requested.status_code) + \
               ". Para mais informações sobre esse erro consulte a API do Github: https://developer.github.com/v3/"


# Cria o schema executável.
schema = make_executable_schema(type_defs, [query, mutation], repository)

# Cria uma aplicação ASGI usando o schema definido anteriormente.
app = GraphQL(schema, debug=True)
