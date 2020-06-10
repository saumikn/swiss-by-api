import requests
import logic
import json
import sys

players = logic.read_player_key()
uscf_key = logic.read_player_key(k=1,v=2)
name_key = logic.read_player_key(k=1, v=3)

def get_game_winner(game_response):
    if 'winner' not in game_response:
        return '0.5-0.5'
    return '1-0' if game_response['winner'] == 'white' else '0-1'

def get_results(tournament_id):
    headers = {'Accept': 'application/x-ndjson'}
    response = requests.get(f'https://lichess.org/api/{tournament_id}/games', headers=headers)

    results = []
    for line in response.iter_lines():
        line = line.decode('utf-8')
        line = json.loads(line)

        white = line['players']['white']['user']['id']
        black = line['players']['black']['user']['id']

        if white in uscf_key and uscf_key[white].isnumeric() and black in uscf_key and uscf_key[black].isnumeric():
            result = get_game_winner(line)
            length = len(line['moves'].split())
            date = line['createdAt']
            if length > 1:
                results.append([white,black,result,date])
        if white not in uscf_key:
            print(white)
        if black not in uscf_key:
            print(black)
        
    results.sort(key=lambda x:x[3])
    results = [r[0:3] for r in results]
    return results

def get_players(results):
    players = set()
    for result in results:
        players.add(result[0])
        players.add(result[1])
    
    pruned_players = []
    for p in players:
        if p not in uscf_key:
            print(f'{p} is missing')
            continue
        if uscf_key[p].isnumeric():
            pruned_players.append(p)
        else:
            print(f'{p} is nonnumeric')
    return pruned_players

def get_xtable(players):
    xtable = []
    for p in players:
        xtable.append([p, [''] * 100])
    return xtable

def get_indexes(players, xtable):
    indexes = dict()
    for p in players:
        for i,x in enumerate(xtable):
            if p == x[0]:
                indexes[p]=i
                break
    return indexes

def add_result(xtable, result, indexes):
    w_i = indexes[result[0]]
    b_i = indexes[result[1]]
    if result[2] == '0.5-0.5':
        w_r = f'D{b_i+1}W'
        b_r = f'D{w_i+1}B'
    elif result[2] == '1-0':
        w_r = f'W{b_i+1}W'
        b_r = f'L{w_i+1}B'
    elif result[2] == '0-1':
        w_r = f'L{b_i+1}W'
        b_r = f'W{w_i+1}B'
    else:
        w_r = f'ERROR'
        b_r = f'ERROR'

    w = xtable[w_i][1]
    b = xtable[b_i][1]

    for i in range(len(xtable)):            
        if w[i] == '' and b[i] == '':
            xtable[w_i][1][i] = w_r
            xtable[b_i][1][i] = b_r
            return xtable
    
    print("shouldn't get here")
    return xtable

def add_results(xtable, results, indexes):
    for result in results:
        xtable = add_result(xtable, result, indexes)

    last = 0
    for _, games in xtable:
        for i,g in enumerate(games):
            if g != '':
                last = max(last,i)
    
    for i,(players, games) in enumerate(xtable):
        games = games[:last+1]
        for j,g in enumerate(games):
            if g == '':
                games[j] = 'U--'
        xtable[i] = [players,games]
    return xtable

def write_xtable(xtable, output_file='xtable.csv'):
    with open(output_file, 'w+') as f:
        header = 'Number,Rk,Fed,Title,Username,Name'
        for i in range(len(xtable[0][1])):
            header += f',RND{i+1}'
        header += ',Score,SB'
        print(header, file=f)
        for i,row in enumerate(xtable):
            # row = f'{row[0]},{name_key[row[0]]},{uscf_key[row[0]]},' + ','.join(row[1])
            row = f'{i+1},{i+1},,,{row[0]},{name_key[row[0]]},' + ','.join(row[1])
            print(row, file=f)


if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print('Missing URL')
    else:
        tournament_url = sys.argv[1].split('lichess.org/')[1]
        results = get_results(tournament_url)
        # results = get_results('swiss/wPodHVni')
        players = get_players(results)
        xtable = get_xtable(players)
        indexes = get_indexes(players, xtable)
        xtable = add_results(xtable, results, indexes)
        write_xtable(xtable)


# player_key = logic.read_player_key()
# print(player_key)
