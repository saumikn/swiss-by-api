import requests
import csv
import sheets
import json
import main
import time

class Pairing:
    def __init__(self, cell, white, black, gameId, status='created',result='',link=''):
        self.cell = cell
        self.white = white
        self.black = black
        # self.white = f'=hyperlink("https://lichess.org/{gameId}?color=white", "{white}")'
        # self.black = f'=hyperlink("https://lichess.org/{gameId}?color=black", "{black}")'
        self.gameId = gameId
        self.status = status
        self.result = result
        self.link = link

    def __str__(self):
        return ','.join([self.cell, self.white, self.black, self.gameId, self.status, self.result, self.link])

def setup_match_sheets(cell, white, black, gameId):
    token = main.token
    players = read_player_key()

    headers = {'Authorization': f'Bearer {token}'}
    if white not in players or black not in players:
        print(f'Error with {white} - {black}')

    return Pairing(cell, white, black, gameId)

def setup_pairings_sheets(cell, pairing_file, game_id_file):
    pairing_names = convert_swiss_sys(pairing_file)
    game_ids = read_game_ids(game_id_file)
    confirmation = input(f'Are you sure you want to start {len(pairing_names)} matches? Enter "y" to continue: ')
    if confirmation != 'y':
        return
    pairings = []

    for i in range(len(pairing_names)):
        white = pairing_names[i][0]
        black = pairing_names[i][1]
        gameid = game_ids[i].strip()
        cell = cell[0] + str(int(cell[1:])+1)
        if black == '1 ' or black == '½ ':
            pairings.append(Pairing(cell=cell, gameId='', white=white, result=black, black='BYE'))
            continue
        pairings.append(setup_match_sheets(cell, white, black, gameid))

    for p in pairings:
        if p:
            print(p.white)
            sheets.update_pairing(p)
    return pairings

def setup_match_lichess(cell, white, black, gameid):
    token = main.token
    players = read_player_key()
    headers = {'Authorization': f'Bearer {token}'}
    white = white.lower()
    black = black.lower()
    if white not in players or black not in players:
        print(f'Error with {white} - {black}')
        return Pairing(cell,white,black,'ERROR', status='ERROR',result='ERROR')
    whiteId = players[white]
    blackId = players[black]

    urlWhite = f'https://lichess.org/{gameid}?color=white'
    urlBlack = f'https://lichess.org/{gameid}?color=black'

    dataW = {'text':f'Please click on the link to start your game: {urlWhite}'}
    response = requests.post(f'https://lichess.org/inbox/{whiteId}', data=dataW, headers=headers)

    dataB = {'text':f'Please click on the link to start your game: {urlBlack}'}
    response = requests.post(f'https://lichess.org/inbox/{blackId}', data=dataB, headers=headers)
    return Pairing(cell, white, black, gameid) 

def setup_pairings_lichess(cell, pairing_file, game_id_file):
    pairing_names = convert_swiss_sys(pairing_file)
    game_ids = read_game_ids(game_id_file)
    confirmation = input(f'Are you sure you want to start {len(pairing_names)} matches? Enter "y" to continue: ')
    if confirmation != 'y':
        return
    pairings = []

    for i in range(len(pairing_names)):
        white = pairing_names[i][0]
        black = pairing_names[i][1]
        gameid = game_ids[i].strip()
        cell = cell[0] + str(int(cell[1:])+1)
        if black == '1 ' or black == '½ ':
            pairings.append(Pairing(cell=cell, gameId='', white=white, result=black, black='BYE'))
            continue
        pairings.append(setup_match_lichess(cell, white, black, gameid))

    for p in pairings:
        if p:
            print(p.white)
            sheets.update_pairing(p)
    return pairings


def parse_event(event, pairing_objs='pairing_objs.csv'):
    players = read_player_key()

    event = event.decode('utf-8')
    if (event == ''):
        print('Empty Event')
        return
    event = json.loads(event)

    pairings = read_pairings(pairing_objs)
    gameId = event['id']
    status = event['status']
    white = event['players']['white']['userId']
    black = event['players']['black']['userId']
    for p in pairings:
        if p.white not in players or p.black not in players:
            # print(f'{p.white} vs {p.black} had an error')
            continue
        pWhite = players[p.white].lower()
        pBlack = players[p.black].lower()
        if gameId == p.gameId:
            p.result = get_result(gameId, status)
            p.link = get_link(gameId, status)
            sheets.update_pairing(p)
        if pWhite == white and pBlack == black and p.result in ['','0F-0F']:
            p.result = get_result(gameId, status)
            p.link = get_link(gameId, status)
            sheets.update_pairing(p)
    write_pairings(pairings, pairing_objs)

def get_result(gameId, status):
    if status in [10,20,60]:
        return ''
    if status in [25,37]:
        return '0F-0F'
    if status in [32,34]:
        return '0.5-0.5'
    if status in [30,31,33,35]:
        headers = {'Accept': 'application/json'}
        response = requests.get(f'https://lichess.org/game/export/{gameId}', headers=headers)
        if 'winner' not in response.json():
            return '0.5-0.5'
        return '1-0' if response.json()['winner'] == 'white' else '0-1'
    if status in [36]:
        headers = {'Accept': 'application/json'}
        response = requests.get(f'https://lichess.org/game/export/{gameId}', headers=headers)
        if 'winner' not in response.json():
            print("shouldn't get here...")
            return '0.5-0.5'
        return '1F-0F' if response.json()['winner'] == 'white' else '0F-1F'

def get_link(gameId, status):
    if status == 10:
        return ''
    return f'https://lichess.org/{gameId}'

def convert_swiss_sys(pairing_file):
    pairings = []
    with open(pairing_file, encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)
        next(reader)
        for bd,res1,white,res2,black in reader:
            if black.strip() == 'BYE':
                pairings.append([white,res1])
            else:
                pairings.append([white,black])
    return pairings


def read_game_ids(game_id_file):
    with open(game_id_file) as f:
        return f.readlines()

def start_stream():
    players = read_player_key()
    data = ','.join(set(players.values()))
    game_stream = requests.post("https://lichess.org/api/stream/games-by-users", data=data, stream=True)
    return game_stream



## Generic IO Funtions

def read_pairings(pairing_file):
    pairings = []
    with open(pairing_file, 'r') as f:
        reader = csv.reader(f)
        for (cell,white,black,gameId,status,result,link) in reader:
            pairings.append(Pairing(cell,white,black,gameId,status,result,link))
    return pairings

def write_pairings(pairings, file):
    ## Change this to 'a+' in order to append instead of overwrite!
    with open(file, 'w+') as f:
        for p in pairings:
            print(p, file=f)

def read_player_key(player_file='data.csv', k=0, v=3, output=False):
    players = dict()
    with open(player_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[k] == '' or row[v] == '' or len(row) <= max(k,v):
                if output:
                    print(f'Missing {row[0]}')
                continue
            players[row[k].lower()] = row[v]
    return players

def get_paired_players(pairings):
    player_key = read_player_key()
    paired_players = []
    for p in pairings:
        if p.white in player_key:
            paired_players.append(player_key[p.white])
        else:
            print(f'No username for {p.white}')
        if p.black in player_key:
            paired_players.append(player_key[p.black])
        else:
            print(f'No username for {p.black}')
    return paired_players