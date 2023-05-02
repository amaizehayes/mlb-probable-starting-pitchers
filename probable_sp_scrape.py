
import bs4
import requests
import pandas as pd
from datetime import date, datetime
import time


def roto_sps():
    '''
    function that scrapes roto grinders for probable starters, their handedness, and their opponent.
    Outputs two CSVs, one to be added to history, and the other a standalone for the current day.
    If a SP is missing, it might throw an error, I'll be updating and fixing.
    '''
    # URL to scrape
    url = 'https://rotogrinders.com/lineups/mlb?site=draftkings'
    # Send a GET request to the URL and store the response
    response = requests.get(url)
    # Get the content of the response
    html = response.content
    # Create a BeautifulSoup object to parse the HTML
    soup = bs4.BeautifulSoup(html, 'html.parser')

    # Find all divs with class 'pitcher players'
    lineup_header_divs = soup.find_all(class_='pitcher players')

    # Extract all 'player-popup' classes within each 'pitcher players' div
    player_names = []
    for lineup_header_div in lineup_header_divs:
        player_links = lineup_header_div.find_all(class_='player-popup')
        for link in player_links:
            player_names.append(link.get_text())

    # Find all divs with class 'meta stats'
    lineup_hand_divs = soup.find_all(class_='meta stats')

    # Extract all 'stats' classes within each 'meta stats' div
    player_hands = []
    for lineup_header_div in lineup_hand_divs:
        player_links = lineup_header_div.find_all(class_='stats')
        for link in player_links:
            player_hands.append(link.get_text().strip())

    # Find all divs with class 'teams'
    lineup_team_divs = soup.find_all(class_='teams')

    # Extract all 'shrt' classes within each 'teams' div
    team_names = []
    for lineup_header_div in lineup_team_divs:
        player_links = lineup_header_div.find_all(class_='shrt')
        for link in player_links:
            team_names.append(link.get_text().strip())

    # Define a function to flip every pair of elements in a list
    def flip_every_pair(my_list):
        # Initialize an empty list to store flipped elements
        flipped_list = []
        # Iterate through pairs of elements in the list
        for i in range(0, len(my_list), 2):
            # Add the second element followed by the first element to the flipped list
            flipped_list.append(my_list[i+1])
            flipped_list.append(my_list[i])
        return flipped_list

    # Extract the date from the page header
    span_element = soup.select_one('#top > div > section > div > header > h1 > span')
    span_text = span_element.text.strip()
    date_str = span_text.split(' (')[0]
    date_obj = datetime.strptime(date_str, '%B %d, %Y')
    date_string = date_obj.date().strftime('%Y-%m-%d')

    # Create a list of tuples containing player names, handedness, and team names (with flipped opponents)
    data = list(zip(player_names, player_hands, team_names, flip_every_pair(team_names)))

    # Create a DataFrame from the list of tuples, with columns for Name, Handedness, Team, Opponent, and Date
    df = pd.DataFrame(data, columns=['Name', 'Handedness', 'Team', 'Opponent'])
    df['Date'] = date_string

    df.to_csv('probable_starter_history.csv', index=False, header=False, mode='a')
    df.to_csv('probable_starter_today.csv', index=False, header=True)

    # Return the DataFrame
    return print(str(len(df)) + ' probable starters scraped successfully.')


roto_sps()
