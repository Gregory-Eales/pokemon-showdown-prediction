import pandas as pd
import json 
import os
from tqdm import tqdm




"""
what features do we want on the first pass in our dataset
- player 1 / 2 names
- player 1 / 2 elo scores
- player 1 / 2 pokemon names, 1 - 6 each (order won't matter on first pass)
- the winner name, and the winner player number 1 / 2
"""



def parse_game_file(file_name):

    file = open("data/raw-html-games/"+file_name).read()
    # open 
    
    #file_json = json.loads(open("data/raw-json-games/" + file_name.strip("html") + "json").read())

    data = {
        "game_id" : None,
        "file_name": file_name,
        "game_format": None,
        "tier": None,
        "p1_name": None,
        "p2_name": None,
        "p1_elo": None,
        "p2_elo": None,
        "p1_p1": None,
        "p1_p2": None,
        "p1_p3": None,
        "p1_p4": None,
        "p1_p5": None,
        "p1_p6": None,
        "p2_p1": None,
        "p2_p2": None,
        "p2_p3": None,
        "p2_p4": None,
        "p2_p5": None,
        "p2_p6": None,
        "winner_name": None,
        "winner_player_number": None
    }

    lines = file.split('\n')
    for line in lines:

        """
            |tier|
        """

        if '|tier|' in line:
            data['tier'] = line.split('|tier|')[1].split('|')[0]

        if '|gametype|' in line:
            data['game_format'] = line.split('|gametype|')[1]

        """
            player 1 name - |player|p1|pollinosis|candice|
            player 2 name - |player|p2|WeaselmanWasTaken|parasollady|
        """

        if '|player|p1|' in line:
            data['p1_name'] = line.split('|player|p1|')[1].split('|')[0]
        elif '|player|p2|' in line:
            data['p2_name'] = line.split('|player|p2|')[1].split('|')[0]

        if '|poke|p1|' in line:
            for i in range(1, 7):
                if data[f"p1_p{i}"] is None:
                    # plit after the next special character
                    data[f"p1_p{i}"] = line.split('|poke|p1|')[1].split('|')[0].split(',')[0]
                    break
                else:
                    continue
                
        elif '|poke|p2|' in line:
            for i in range(1, 7):
                if data[f"p2_p{i}"] is None:
                    data[f"p2_p{i}"] = line.split('|poke|p2|')[1].split('|')[0].split(',')[0]
                    break
                else:
                    continue

        # |win|{player name}
        if '|win|' in line:
            data['winner_name'] = line.split('|win|')[1]
            if data['winner_name'] == data['p1_name']:
                data['winner_player_number'] = 1
            else:
                data['winner_player_number'] = 2

        

    # pretty print with json
    #print(json.dumps(data, indent=4))

    return data


def main():
    game_df = pd.DataFrame()
    file_names = os.listdir("data/raw-html-games/")
    for file_name in tqdm(file_names):
        data = parse_game_file(file_name)
        game_df = pd.concat([game_df, pd.DataFrame(data, index=[0])])

    game_df.to_csv("data/parsed-games.csv", index=False)
    

if __name__ == "__main__":
    main()