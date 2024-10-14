import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
import base64
import json
from dotenv import load_dotenv
from logger import log, LogLevel

# Carregar o caminho da pasta Riot Games do arquivo .env
load_dotenv()
riot_games_folder = os.getenv("RIOT_GAMES_FOLDER")

if riot_games_folder is None:
    raise Exception("Caminho para a pasta Riot Games não foi definido no arquivo .env")

lockfile_path = os.path.join(riot_games_folder, 'League of Legends', 'lockfile')
output_file = 'login_data.json'  # Arquivo JSON para salvar os dados de login

def read_lockfile():
    try:
        with open(lockfile_path, 'r') as f:
            data = f.read()
        return data
    except FileNotFoundError:
        raise Exception(f"Arquivo lockfile não encontrado no caminho: {lockfile_path}")

def generate_auth(should_mock_lcu=False):
    if should_mock_lcu:
        return {
            "password": "senha",
            "port": "5353",
            "protocol": "http",
            "url": "http://riot:senha@127.0.0.1:5353",
            "basic_token": "cmlvdDpzZW5oYQ=="
        }
    
    lockfile_content = read_lockfile()
    
    # O lockfile tem os seguintes campos separados por ":":
    # nome_do_process, PID, porta, senha, protocolo
    data = lockfile_content.split(':')
    
    if len(data) < 5:
        raise Exception("O lockfile não contém os dados necessários.")
    
    password = data[3]
    port = data[2]
    protocol = data[4]
    
    # Gerar a URL de conexão local
    url = f"https://riot:{password}@127.0.0.1:{port}"
    
    # Gerar o Basic Token (password codificado em Base64)
    token_string = f"riot:{password}"
    basic_token = base64.b64encode(token_string.encode()).decode()

    auth_data = {
        "password": password,
        "port": port,
        "protocol": protocol,
        "url": url,
        "basic_token": basic_token
    }
    save_auth_data(auth_data, 'login_data.json')
    return auth_data

def save_auth_data(auth_data, file_path):
    try:
        with open(file_path, 'w') as f:
            json.dump(auth_data, f, indent=4)
        log(LogLevel.INFO, f"Dados de login salvos em: {file_path}")
    except Exception as e:
        log(LogLevel.ERROR, f"Erro ao salvar os dados de login: {e}")

if __name__ == "__main__":
    auth_info = generate_auth()
    
    # Exibir os dados no terminal
    log(LogLevel.WARNING, f"Password: {auth_info['password']}")
    log(LogLevel.WARNING, f"URL: {auth_info['url']}")
    log(LogLevel.WARNING, f"Basic Token: {auth_info['basic_token']}")
