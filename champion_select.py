import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
from logger import log, LogLevel

# Variáveis globais
player_cell_id = None
player_session = None
forbidden_champions_list = []

def get_session_data(url, basic_token, summoner_id):
    """
    Faz uma chamada para o endpoint de sessão e busca o cellId do jogador baseado no summonerId,
    salvando também os dados da sessão inteira.

    Args:
        url (str): A URL base do LCU.
        basic_token (str): O token básico de autenticação.
        summoner_id (int): O summonerId do jogador que queremos encontrar.

    Returns:
        tuple: (bool, dict) Retorna um booleano indicando se o cellId foi encontrado e a sessão completa.
    """
    global player_cell_id, player_session
    
    try:
        response = requests.get(
            f"{url}/lol-champ-select/v1/session",
            headers={"Authorization": f"Basic {basic_token}"},
            verify=False
        )
        
        if response.status_code == 200:
            session_data = response.json()
            player_session = session_data  # Salva a sessão completa
            player_cell_id = session_data.get('localPlayerCellId')
            
            # Procura o summonerId no myTeam
            #for player in session_data.get('myTeam', []):
            #    if player.get('summonerId') == summoner_id:
            #        player_cell_id = player.get('cellId')
            #        log(LogLevel.ERROR, f"cellId encontrado: {player_cell_id}")
            if player_cell_id is not None:
                return True, session_data

            log(LogLevel.ERROR, f"summonerId {summoner_id} não encontrado em myTeam.")
            return False, session_data
        else:
            log(LogLevel.ERROR, f"Erro ao buscar a sessão: {response.status_code}")
            return False, None

    except Exception as e:
        log(LogLevel.ERROR, f"Erro ao buscar a sessão de jogo: {e}")
        return False, None

def declare_pick_intent(url, basic_token, summoner_id, pick_champion_list):
    """
    Declara a intenção do jogador de escolher um campeão se ele não possui nenhum.

    Args:
        url (str): A URL base do LCU.
        basic_token (str): O token básico de autenticação.
        summoner_id (int): O summonerId do jogador.
        pick_champion_list (list): Lista de campeões disponíveis para pick.

    Returns:
        bool: True se a intenção de pick foi declarada com sucesso, False caso contrário.
    """
    global player_session

    if player_session is None:
        log(LogLevel.ERROR, "Dados da sessão não disponíveis.")
        return
    
    # Verifica se o jogador já possui um campeão
    player_has_pick = False
    player_has_pick_intent = False
    for player in player_session.get('myTeam', []):
        if player.get('summonerId') == summoner_id:
            champion_id = player.get('championId')
            champion_pick_intent = player.get('championPickIntent')
            player_has_pick = champion_id != 0
            player_has_pick_intent = champion_pick_intent != 0
            break

    # jogador já possui um campeão ou intenção de pick
    if player_has_pick == True or player_has_pick_intent == True:
        return False

    # Se o jogador não possui campeões, seleciona o primeiro da lista de picks
    if pick_champion_list:
        first_champion_id = pick_champion_list[0]
        # Aqui você pode querer buscar o action_id novamente para a nova intenção de pick
        if complete_action(url, basic_token, None, first_champion_id):
            log(LogLevel.INFO, f"Intenção de pick declarada com o campeão {first_champion_id} (completado como False).")
            # Aqui você pode definir completed como False
            return True
        else:
            log(LogLevel.ERROR, f"Erro ao declarar a intenção de pick com o campeão {first_champion_id}.")
            return False

def get_forbidden_champions(summoner_id):
    """
    Identifica os campeões que os aliados estão usando ou pretendem usar,
    salvando os IDs em uma lista de campeões proibidos, ignorando o summoner em questão.

    Args:
        summoner_id (int): O summonerId do jogador que queremos ignorar.
    """
    global forbidden_champions_list, player_session

    if player_session is None:
        log(LogLevel.ERROR, "Dados da sessão não disponíveis.")
        return None
    
    forbidden_champions_list.clear()  # Limpa a lista antes de preenchê-la

    for player in player_session.get('myTeam', []):
        if player.get('summonerId') != summoner_id:  # Ignora o summoner em questão
            champion_id = player.get('championId')
            champion_pick_intent = player.get('championPickIntent')

            if champion_id and champion_id != 0:
                forbidden_champions_list.append(champion_id)
            if champion_pick_intent and champion_pick_intent != 0:
                forbidden_champions_list.append(champion_pick_intent)

    # Remove duplicatas, se houver
    forbidden_champions_list = list(set(forbidden_champions_list))
    #log(LogLevel.ERROR, "Lista de campeões proibidos:", forbidden_champions_list)
    return forbidden_champions_list


def check_current_actions():
    """
    Verifica se alguma ação em progresso pertence ao meu summoner.

    Returns:
        tuple: (bool, int, str) 
                - bool: Indica se a ação do summoner está em progresso.
                - int: ID da ação em progresso.
                - str: Tipo da ação.
    """
    global player_session

    if player_session is None or 'actions' not in player_session:
        log(LogLevel.ERROR, "Dados da sessão ou ações não disponíveis.")
        return False, None, None
    
    for action_list in player_session['actions']:  # Percorre cada lista de ações
        for action in action_list:  # Percorre cada ação na lista
            actor_cell_id = action.get('actorCellId')
            is_in_progress = action.get('isInProgress')
            action_id = action.get('id')
            action_type = action.get('type')

            if actor_cell_id == player_cell_id and is_in_progress:
                #log(LogLevel.ERROR, f"Ação em progresso encontrada: ID={action_id}, Tipo={action_type}")
                return True, action_id, action_type

    #log(LogLevel.ERROR, "Nenhuma ação em progresso encontrada para o summoner.")
    return False, None, None

def complete_action(url, basic_token, action_id, champion_id):
    """
    Completa uma ação de seleção de campeão.

    Args:
        url (str): A URL base do LCU.
        basic_token (str): O token básico de autenticação.
        action_id (int): O ID da ação a ser completada.
        champion_id (int): O ID do campeão a ser atribuído à ação.

    Returns:
        bool: True se a ação foi completada com sucesso, False caso contrário.
    """
    try:
        response = requests.patch(
            f"{url}/lol-champ-select/v1/session/actions/{action_id}",
            headers={"Authorization": f"Basic {basic_token}"},
            json={"championId": champion_id, "completed": True},
            verify=False
        )
        
        if response.status_code == 204:
            log(LogLevel.INFO, f"Ação {action_id} completada com sucesso com o campeão {champion_id}.")
            return True
        else:
            log(LogLevel.ERROR, f"Erro ao completar a ação: {response.status_code}, Mensagem: {response.text}")
            return False

    except Exception as e:
        log(LogLevel.ERROR, f"Erro ao completar a ação: {e}")
        return False

def manage_champion_selection(url, basic_token, summoner_id, pick_champion_list, ban_champion_list):
    """
    Gerencia a seleção e banimento de campeões com base na sessão atual e na lista de campeões proibidos.

    Args:
        url (str): A URL base do LCU.
        basic_token (str): O token básico de autenticação.
        summoner_id (int): O ID do summoner.
        pick_champion_list (list): Lista de campeões disponíveis para pick.
        ban_champion_list (list): Lista de campeões disponíveis para ban.

    Returns:
        None
    """
    # Obtém os dados da sessão
    session_data = get_session_data(url, basic_token, summoner_id)  # Supondo que você tenha esse método implementado

    if session_data is None:
        log(LogLevel.ERROR, "Não foi possível obter os dados da sessão.")
        return
    
    # Declara a intenção de pick se o jogador não possui campeões
    #if(declare_pick_intent(url, basic_token, summoner_id, pick_champion_list)):
    #    return

    # Verifica se a ação é do summoner
    is_in_progress, action_id, action_type = check_current_actions()  # Método anteriormente definido

    if not is_in_progress:
        #log(LogLevel.ERROR, "Nenhuma ação em progresso encontrada para o summoner.")
        return

    # Obtém a lista de campeões proibidos
    forbidden_champions_list = get_forbidden_champions(session_data)  # Método que você implementou anteriormente
    # Verifica se a ação é um "pick" ou "ban"
    if action_type == "pick":
        for champion_id in pick_champion_list:
            if champion_id not in forbidden_champions_list:
                # Completa a ação de pick
                if complete_action(url, basic_token, action_id, champion_id):
                    log(LogLevel.INFO, f"Campeão {champion_id} selecionado com sucesso.")
                    return
                else:
                    log(LogLevel.ERROR, f"Erro ao tentar selecionar o campeão {champion_id}.")
        log(LogLevel.WARNING, "Todos os campeões na lista de pick estão proibidos.")
    
    elif action_type == "ban":
        for champion_id in ban_champion_list:
            if champion_id not in forbidden_champions_list:
                # Completa a ação de ban
                if complete_action(url, basic_token, action_id, champion_id):
                    log(LogLevel.INFO, f"Campeão {champion_id} banido com sucesso.")
                    return
                else:
                    log(LogLevel.ERROR, f"Erro ao tentar banir o campeão {champion_id}.")
        log(LogLevel.WARNING, "Todos os campeões na lista de ban estão proibidos.")
    
    else:
        log(LogLevel.ERROR, "Ação não reconhecida. Apenas 'pick' ou 'ban' são permitidos.")

from login import generate_auth
from summoner import Summoner
import time

if __name__ == "__main__":
    # login then call session every 0.5s, printing the value of "counter"
    login_data = generate_auth()
    summoner = Summoner.get_current_summoner(login_data)
    while True:
        session = get_session_data(login_data['url'], login_data['basic_token'], summoner.summoner_id)
        if session:
            now = time.time()
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now))
            try:
                log(LogLevel.INFO, time_str, ': ', session.get('counter'))
            except:
                log(LogLevel.ERROR, time_str, ': ', 'no counter')
        time.sleep(0.5)