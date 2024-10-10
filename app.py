import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from flask import Flask, render_template, jsonify, request, redirect, url_for
import json
import os
import requests
import threading
import time
import random
import argparse
from login import generate_auth
from summoner import Summoner
from matchmaking import accept_ready_check, get_gameflow_phase, GameflowPhase
from dragonapi import fetch_all_champions
from champion_select import manage_champion_selection

app = Flask(__name__)

auth_info = {}
summoner = None
should_mock_lcu = False
have_gameflow_check_started = False

def load_persistent_data():
    file_path = 'persistent_data.json'
    default_data = {
        'accept_matches': False,
        'selected_ban_champions': [],
        'selected_pick_champions': []
    }

    if not os.path.exists(file_path):
        # File doesn't exist, create it with default data
        with open(file_path, 'w') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Validate the loaded data
        if not all(key in data for key in default_data.keys()):
            raise ValueError("Invalid data structure in persistent_data.json")
        
        return data
    except (json.JSONDecodeError, ValueError):
        # File exists but is not valid JSON or has invalid structure
        # Overwrite with default data
        with open(file_path, 'w') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data

# Add this function to save persistent data
def save_persistent_data():
    data = {
        'accept_matches': accept_matches,
        'selected_ban_champions': selected_ban_champions,
        'selected_pick_champions': selected_pick_champions
    }
    with open('persistent_data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

persistent_data = load_persistent_data()
accept_matches = persistent_data['accept_matches']
selected_ban_champions = persistent_data['selected_ban_champions']
selected_pick_champions = persistent_data['selected_pick_champions']

def get_summoner_data():
    global auth_info, summoner
    auth_info = generate_auth(should_mock_lcu)
    summoner = Summoner.get_current_summoner(auth_info)
    return summoner

@app.route('/')
def index():
    if summoner:
        start_gameflow_check()
        return redirect(url_for('actions'))
    return render_template('index.html', summoner=summoner)

@app.route('/champions')
def get_champions():
    try:
        with open('parsed_champions.json', 'r') as f:
            champions = json.load(f)
        return jsonify(champions), 200
    except Exception as e:
        print(f"Error loading champions: {e}")
        return jsonify({"error": "Unable to load champions"}), 500

@app.route('/actions', methods=['GET', 'POST'])
def actions():
    global accept_matches, summoner, selected_ban_champions, selected_pick_champions
    if request.method == 'POST':
        accept_matches = request.form.get('accept_matches') == 'true'
        save_persistent_data()
        return '', 204
    
    # Aqui, você pode carregar os campeões e passá-los para o template
    with open('parsed_champions.json', 'r') as f:
        champions = json.load(f)
    
    return render_template('actions.html', 
                           accept_matches=accept_matches, 
                           summoner=summoner, 
                           champions=champions,
                           selected_ban_champions=selected_ban_champions,
                           selected_pick_champions=selected_pick_champions)

@app.route('/actions/select_champion', methods=['POST'])
def select_champion():
    global selected_ban_champions, selected_pick_champions
    data = request.get_json()
    champion_key = data['champion']
    champion_type = data['type']  # 'ban' ou 'pick'
    is_selecting = data['selecting']  # True se está selecionando, False se desmarcando

    if champion_type == 'ban':
        if is_selecting:
            if len(selected_ban_champions) < 3:
                selected_ban_champions.append(champion_key)
        else:
            if champion_key in selected_ban_champions:
                selected_ban_champions.remove(champion_key)

    elif champion_type == 'pick':
        if is_selecting:
            if len(selected_pick_champions) < 3:
                selected_pick_champions.append(champion_key)
        else:
            if champion_key in selected_pick_champions:
                selected_pick_champions.remove(champion_key)


    #with open('selected_champions_dump.json', 'w') as dump_file:
    #    json.dump(selected_ban_champions, dump_file)
    #print(selected_ban_champions)

    save_persistent_data()
    return jsonify({
        'selectedChampions': {
            'bans': selected_ban_champions,
            'picks': selected_pick_champions
        }
    })

def job_check_gameflow():
    """
    Verifica o estado do game flow e aceita a partida se necessário.
    Executa em um intervalo aleatório entre 1 e 3 segundos.
    """
    global accept_matches, auth_info
    while True:
        phase = get_gameflow_phase(auth_info['url'], auth_info['basic_token'])
        #print(f"Current gameflow phase: {phase}")

        if phase == GameflowPhase.READY_CHECK and accept_matches:
            success = accept_ready_check(auth_info['url'], auth_info['basic_token'])
            print(f"Accepted ready check: {success}")
        
        if phase == GameflowPhase.CHAMP_SELECT and (selected_ban_champions or selected_pick_champions):
            manage_champion_selection(auth_info['url'], auth_info['basic_token'], selected_ban_champions, selected_pick_champions)

        # Aguarda um intervalo aleatório entre 1 e 3 segundos
        time.sleep(random.uniform(1, 3))

# Inicie o job em um thread separado
def start_gameflow_check():
    if(have_gameflow_check_started):
        return
    threading.Thread(target=job_check_gameflow, daemon=True).start()

@app.route('/start', methods=['POST'])
def start():
    global summoner
    summoner = get_summoner_data()
    if summoner:
        start_gameflow_check()  # Iniciar a verificação do game flow
        return redirect(url_for('actions'))
    return '', 204

@app.route('/accept_match', methods=['POST'])
def accept_match():
    global auth_info
    if not auth_info:
        return jsonify({"error": "Authentication information is missing."}), 400

    success = accept_ready_check(auth_info['url'], auth_info['basic_token'])
    return jsonify({"success": success}), 200

@app.route('/login_data', methods=['GET'])
def login_data():
    print("fetching login data")
    with open('login_data.json', 'r') as f:
        return f.read()

def parse_arguments():
    """
    Analisa os argumentos de linha de comando.
    """
    parser = argparse.ArgumentParser(description='League of Legends Client Mock')
    parser.add_argument('-mock', action='store_true', help='Ativar modo de mock da LCU')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    should_mock_lcu = args.mock 
    fetch_all_champions()
    try:
        summoner = get_summoner_data()
        start_gameflow_check()
    except Exception as e:
        print(f"Error fetching summoner data: {e}")

    app.run(debug=True)
