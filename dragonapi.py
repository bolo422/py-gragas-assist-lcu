import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import json
import requests
from logger import log, LogLevel

def fetch_latest_version():
    """
    Obtém a versão mais recente da API do Dragon.
    
    Returns:
        str: A versão mais recente.
    """
    try:
        response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
        if response.status_code == 200:
            # this response is a list of versions in json format like this: {["1.1", "1.2", "1.3"]}
            # should get the first one and set it as the latest version
            versions = response.json()
            log(LogLevel.INFO, versions[0])
            return versions[0]  # Retorna a primeira versão
        else:
            log(LogLevel.ERROR, f"Error fetching versions: {response.status_code}")
            return None
    except Exception as e:
        log(LogLevel.ERROR, f"Error fetching versions: {e}")
        return None

def fetch_all_champions(version=None):
    """
    Obtém todos os campeões da API do Dragon.
    
    Args:
        latest_version (str): A versão mais recente da API.

    Returns:
        dict: Um dicionário com os campeões.
    """
    if(version == '' or version == None):
        version = fetch_latest_version()
    try:
        response = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/pt_BR/champion.json")
        if response.status_code == 200:
            champions_data = response.json()
            # Salva os dados dos campeões em um arquivo JSON
            with open('all_champions.json', 'w', encoding='utf-8') as f:
                json.dump(champions_data, f, ensure_ascii=False, indent=4)
            return champions_data
        else:
            log(LogLevel.ERROR, f"Error fetching champions: {response.status_code}")
            return None
    except Exception as e:
        log(LogLevel.ERROR, f"Error fetching champions: {e}")
        return None
    
def parse_champions(input_file='all_champions.json', output_file='parsed_champions.json'):
    """
    Lê o arquivo all_champions.json e cria um novo JSON com chave como nome do campeão e valor como ID.
    
    Args:
        input_file (str): O caminho para o arquivo JSON de entrada.
        output_file (str): O caminho para o arquivo JSON de saída.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            champions_data = json.load(f)

        # Extrai os campeões em um dicionário simples
        champions_dict = {champion_data['id']: champion_data['key'] for champion_data in champions_data['data'].values()}

        # Salva o novo dicionário em um arquivo JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(champions_dict, f, ensure_ascii=False, indent=4)

        # return a dict of parsed champions
        log(LogLevel.INFO, f"Parsed champions saved to {output_file}")
        return champions_dict

    except Exception as e:
        log(LogLevel.ERROR, f"Error parsing champions: {e}")
        return None
    
if __name__ == "__main__":
    fetch_all_champions()
    parse_champions()