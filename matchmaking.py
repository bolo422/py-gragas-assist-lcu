import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from enum import Enum
from logger import log, LogLevel

class GameflowPhase(Enum):
    LOBBY = "Lobby"
    MATCHMAKING = "Matchmaking"
    READY_CHECK = "ReadyCheck"
    CHAMP_SELECT = "ChampSelect"
    IN_PROGRESS = "InProgress"

def to_gameflow_phase(phase_str):
    try:
        return GameflowPhase(phase_str)
    except ValueError:
        return None


def accept_ready_check(url, basic_token):
    """
    Aceita o ready check do matchmaking.

    Args:
        url (str): A URL base do LCU.
        basic_token (str): O token básico de autenticação.

    Returns:
        bool: True se a requisição for bem-sucedida, False caso contrário.
    """
    log(LogLevel.INFO, "Aceitando ready check do matchmaking...")
    try:
        response = requests.post(
            f"{url}/lol-matchmaking/v1/ready-check/accept",
            headers={"Authorization": f"Basic {basic_token}"},
            verify=False
        )
        return response.status_code == 204  # Sucesso
    except Exception as e:
        log(LogLevel.ERROR, f"Error accepting ready check: {e}")
        return False

def get_gameflow_phase(url, basic_token):
    """
    Obtém a fase atual do gameflow.

    Args:
        url (str): A URL base do LCU.
        basic_token (str): O token básico de autenticação.

    Returns:
        str: A fase atual do gameflow ou None se houver um erro.
    """
    try:
        response = requests.get(
            f"{url}/lol-gameflow/v1/gameflow-phase",
            headers={"Authorization": f"Basic {basic_token}"},
            verify=False
        )
        if response.status_code == 200:
            state = response.text.strip('"')  # Retorna a string sem aspas
            log(LogLevel.INFO, f"Fase atual do gameflow: {state}")
            return to_gameflow_phase(state)
        else:
            log(LogLevel.ERROR, f"Error fetching gameflow phase: {response.status_code}")
            return None
    except Exception as e:
        log(LogLevel.ERROR, f"Error fetching gameflow phase: {e}")
        return None