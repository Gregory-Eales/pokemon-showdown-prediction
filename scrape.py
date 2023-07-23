from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import requests as r
import json
import time
import glob


def get_ladder_links(ladder_url):
    """
    pull and parse the link to all different ladder from ladder url
    """

    response = r.get(ladder_url)

    content = response.content

    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text()

    # extract the ladders
    hrefs = [a.get("href") for a in soup.find_all("a") if a.get("href")]
    hrefs = [href for href in hrefs if '/ladder/' in href and href != '/ladder/']

    # convert to links
    links = ["https://pokemonshowdown.com{}".format(href) for href in hrefs] 

    return links


def get_ladder_users(ladder_link):
    response = r.get(ladder_link)

    content = response.content

    soup = BeautifulSoup(content, "html.parser")

    text = soup.get_text()

    if text.lower() == "denied":
        print('denied access using link: {}'.format(ladder_link))
        return None

    # load tht table into a dataframe
    tbody_element = soup.find("table")
    df = pd.read_html(str(tbody_element))[0]

    # drop unmamed Unnamed: 0
    df = df.drop("Unnamed: 0", axis=1)

    # extract the usersnames
    hrefs = [a.get("href") for a in soup.find_all("a") if a.get("href")]
    hrefs = [href for href in hrefs if '/users/' in href and href != '/users/']

    usernames = [username.replace('/users/', '') for username in hrefs]

    df["usernames"] = usernames

    df['ladder_url'] = ladder_link

    return df


def scrape_ladders():
    
    # url for the different ladders
    ladder_url = 'https://pokemonshowdown.com/ladder/'

    ladder_links = get_ladder_links(ladder_url)

    print("found {} ladder links".format(len(ladder_links)))

    ladder_users = pd.DataFrame()

    print("getting usernames from each ladder link...")
    for ladder_link in tqdm(ladder_links):
        time.sleep(0.5)
        try:
            print('running for {}'.format(ladder_link))
            temp_df = get_ladder_users(ladder_link)
            if temp_df is not None:
                ladder_users = pd.concat([ladder_users, temp_df], ignore_index=True)
        except:
            pass
            

    ladder_users.to_csv('data/ladder_users.csv')


def scrape_ladder_player_games(ladder_users_path):

    df = pd.read_csv(ladder_users_path)

    usernames = df['usernames'].unique().tolist()

    game_links = []

    progress = tqdm(total=len(usernames), desc="game links: 0")
    for username in usernames:
        
        try:
            # scrape all game_links
            game_links += get_user_game_links(username)
        
        except:
            pass
        
        progress.set_description(f"game links: {len(game_links)}")
        progress.update(1)

        # only pull 500 for now
        if len(game_links) > 50000:
            break

    progress.close()

    return game_links


def get_user_game_links(username):

    

    links = []
    # exit text 

    page = 1
    while True:

        games_link = "https://replay.pokemonshowdown.com/search?user={username}&format=&page={page}&output=html"
        
        response = r.get(games_link.format(username=username, page=page))

        content = response.content

        soup = BeautifulSoup(content, "html.parser")

        text = soup.get_text()

        if text == "Can't search any further back":
            break

        # https://replay.pokemonshowdown.com/

        hrefs = [a.get("href") for a in soup.find_all("a") if a.get("href")]
        hrefs = ['https://replay.pokemonshowdown.com{}.json'.format(href) for href in hrefs]

        if len(hrefs) == 0:
            break

        links += hrefs

        # increment page
        page += 1

    return links


def download_game(game_url):

    # make a request to the URL and get the response
    response = r.get(game_url)
    data = response.json()


    start = game_url.find('https://replay.pokemonshowdown.com/') + len('https://replay.pokemonshowdown.com/')
    end = game_url.find('.json')
    filename = game_url[start:end]
    filename = "data/raw-games/{}.json".format(filename)

    with open(filename, "w") as outfile:
        json.dump(data, outfile, indent=4)


def download_games(game_links):

    download_game(game_links[0])

    for game_link in tqdm(game_links):
        try:
            download_game(game_link)
        except:
            pass



def get_game_files(path):
    json_files = glob.glob(path + "*.json")
    return json_files


def parse_game(raw_game):
    """
    loop through each game and extract metadata:
        - winners
        - pokemon teams
    """
    
    keys = list(raw_game.keys())

    print(raw_game['log'])

    for key in keys:

        if key == 'log':
            continue

        print(f"{key} : {raw_game[key]}")
    
    # p1_name = raw_game['p1']
    # p2_name = raw_game['p2']
    # p1_id = raw_game['p1id']
    # p2_id = raw_game['p2id']
    # game_format = raw_game['format']

    # lines = raw_game['log'].split('\n')

    # for line in lines:
    #     print(line)


def load_game(path):
    with open(path) as f:
        game = json.load(f)
    return game


def main():

    # # #scrape_ladders()
    # game_links = scrape_ladder_player_games('data/ladder_users.csv')
    # # save as json file
    # with open("data/game_links.json", "w") as f:
    #     json.dump(game_links , f, indent=4)

    # with open('data/game_links.json') as f:
    #     game_links = json.load(f)

    
    # download_games(game_links)

    game_files = get_game_files('data/raw-games/')
    for game_file in game_files:
        game = load_game(game_file)
        parse_game(game)
        break

    
if __name__ == "__main__":
    main()

