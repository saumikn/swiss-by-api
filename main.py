import os
import sys
import requests
import sys
import json
from dotenv import load_dotenv
import csv
import logic
import sheets
import time

load_dotenv()   
token = os.getenv('LICHESS_TOKEN')
sheet_id = os.getenv('GOOGLE_SHEET_ID')
pairing_sheet = os.getenv('GOOGLE_PAIRING_SHEET')

## Use this at the beginning of the round
def start_round(pairing_files, output_file):
    game_stream = logic.start_stream()

    pairings = list()
    for section in pairing_files:
        cell = input(f'What cell should pairings for {section} start at? ')
        game_id_file = input(f'What game_id file should {section} use? ')
        pairings += logic.setup_pairings_lichess(cell=cell, pairing_file=section, game_id_file=game_id_file)
    logic.write_pairings(pairings, output_file)

    for line in game_stream.iter_lines():
        logic.parse_event(line, output_file)

## Use this if watching games broke in the middle of the round
def continue_round(pairing_objs):
    game_stream = logic.start_stream()
    for line in game_stream.iter_lines():
        logic.parse_event(line, pairing_objs)

def message(player_file, message_body):
    players = logic.read_player_key().values()
    headers = {'Authorization': f'Bearer {token}'}
    data = {'text':message_body}

    for p in players:
        response = requests.post(f'https://lichess.org/inbox/{p}', data=data, headers=headers)
        print(f'{p},{response.text}')

def create_game_id_file(game_id_file, time_control):
    time_control = time_control.split('+')
    with open(game_id_file, 'w+') as f:
        for i in range(30):
            data = {'clock.limit':time_control[0], 'clock.increment':time_control[1]}
            response0 = requests.post('https://lichess.org/api/challenge/open', data=data)
            print(response0.json()['challenge']['id'], file=f)
            print(response0)


def print_missing():
    pairings = []
    pairings += logic.convert_swiss_sys('open.csv')
    pairings += logic.convert_swiss_sys('u1600.csv')
    pairings += logic.convert_swiss_sys('u1000.csv')
    pairings = [i.lower() for sublist in pairings for i in sublist]
    # print(pairings)
    player_key = logic.read_player_key()
    # print(player_key)
    for p in pairings:
        if p in player_key:
            headers = {'Accept': 'application/json'}
            response = requests.get(f'https://lichess.org/api/user/{player_key[p]}', headers=headers)
            if 'id' not in response.json():
                print(player_key[p])
            pass
        else:
            print(p)
        
def test():
    pass

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print('Error: Not enough arguments')
    elif (sys.argv[1] in ['-start', '-S']):
        start_round(pairing_files=sys.argv[2:], output_file='pairing_objs.csv')
    elif (sys.argv[1] in ['-continue', '-C']):
        continue_round('pairing_objs.csv')
    elif (sys.argv[1] in ['-message', '-M']):
        welcome = "All games done in Round 5, and Round 6 will start shortly. Round 6 is the last round of the tournament today. You can see the tournament pairings and standings at https://tinyurl.com/y77t9kox."
        message('players.csv', welcome)
    elif (sys.argv[1] in ['-create']):
        create_game_id_file(sys.argv[2], '900+5')
    elif (sys.argv[1] in ['-print-missing']):
        print_missing()
    elif (sys.argv[1] in ['-test', '-T']):
        test()
    else:
        print('Wrong arguments passed. Try running again with -s or -c flags')

    # set_up_stream()
    # sheets.get_players()
    
    pass

