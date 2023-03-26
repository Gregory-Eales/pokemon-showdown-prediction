from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import requests as r
import json
import time


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
        if len(game_links) > 500:
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

    


def main():

    #scrape_ladders()
    game_links = scrape_ladder_player_games('data/ladder_users.csv')
    # save as json file
    with open("data/game_links.json", "w") as f:
        json.dump(game_links , f, indent=4)

    
if __name__ == "__main__":
    main()

