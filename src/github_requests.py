import requests
import json


# Classe criada para comunicação com a API do Github
class GitApiRequests:

    def __init__(self, usuario):
        self._usuario = usuario

    # Função que retorna um arquivo JSON com as informações dos repositórios do usuário ou um INT quando
    # isso não é possível como, por exemplo, quando o usuário não existir.
    def github_request_repos(self):
        answer = requests.get(
            f'https://api.github.com/users/{self._usuario}/repos')
        if answer.status_code == 200:
            return answer.json()
        else:
            return answer.status_code

    # Função que retorna um arquivo JSON com as informações do repositório específico do usuário ou um INT quando
    # isso não é possível como, por exemplo, quando o usuário ou repositório não existirem
    def github_request_repo_details(self, repo):
        answer = requests.get(
            f'https://api.github.com/repos/{self._usuario}/{repo}')
        if answer.status_code == 200:
            return answer.json()
        else:
            return answer.status_code

    # Função que cria um oauth token com permissão para criar um repo público via método post. Além da autenticação, a
    # descrição do token (token_note) é um parâmetro obrigatório.
    def github_request_create_token(self, password, token_note):
        payload = {
            "scopes": [
                "public_repo"
            ],
            "note": token_note
        }

        answer = requests.post('https://api.github.com/authorizations', auth=(self._usuario, password),
                               data=json.dumps(payload))
        return answer

    # Função que cria um repositório via método post. Além da autenticação, o nome do repositório (repo_name)
    # e a descrição (description) são obrigatórios.
    def github_request_create_repo(self, username, token, repo_name, description):

        payload = {'name': repo_name, 'description': description, 'auto_init': 'true'}

        answer = requests.post('https://api.github.com/' + 'user/repos', auth=(username, token),
                               data=json.dumps(payload))
        return answer
