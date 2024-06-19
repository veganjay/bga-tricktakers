#!/usr/bin/env python3

import json
import csv
import re
import os
import requests
from typing import List, Tuple, Dict

from bs4 import BeautifulSoup
from dotenv import load_dotenv


def list_to_ranges(numbers: List[int]) -> List[Tuple[int, int]]:
    """
    Converts a list of integers into a list of consecutive ranges.

    Example:
    list_to_ranges([1, 2, 3, 4, 5]))  # Output: [(1, 5)]
    list_to_ranges([1, 2, 3, 5, 6, 7))  # Output: [(1, 3), (5, 7)]

    Args:
    numbers: List of integers.

    Returns:
    List of tuples where each tuple represents a range (start, end).
    """
    if not numbers:
        return []
    numbers.sort()
    ranges = []
    start = numbers[0]
    end = numbers[0]
    for number in numbers[1:]:
        if number == end + 1:
            end = number
        else:
            ranges.append((start, end))
            start = number
            end = number
    ranges.append((start, end))
    return ranges


def format_range(player_range: Tuple[int, int]) -> str:
    """
    Formats a range tuple into a string.

    Args:
    player_range: Tuple containing the start and end of the range.

    Returns:
    Formatted string representation of the range.
    """
    min_players, max_players = player_range
    return f'{min_players}-{max_players}' if min_players != max_players else str(min_players)


def format_range_list(player_range_list: List[Tuple[int, int]]) -> str:
    """
    Formats a list of range tuples into a string.

    Args:
    player_range_list: List of tuples representing ranges.

    Returns:
    Formatted string representation of the list of ranges.
    """
    return ' or '.join(format_range(player_range) for player_range in player_range_list)


def is_tricktaker(tag_tuple_list: List[Tuple[int, int]]) -> bool:
    """
    Checks if a game is a trick-taking game based on its tags.

    Args:
    tag_tuple_list: List of tuples representing tags.

    Returns:
    Boolean indicating whether the game is a trick-taking game.
    """
    return any(tag == 220 for tag, _ in tag_tuple_list)


def process_data(data: List[Dict]) -> List[Tuple[str, str, str]]:
    """
    Processes the JSON data to extract relevant information and format it.

    Args:
    data: List of dictionaries containing the game data.

    Returns:
    List of tuples containing the name, status, and player numbers.
    """
    processed_data = []
    for item in data:
        name = item.get('display_name_en')
        player_numbers = format_range_list(list_to_ranges(item.get('player_numbers')))
        tags = item.get('tags')
        status = 'alpha' if item.get('status') == 'private' else item.get('status')
        if is_tricktaker(tags):
            processed_data.append((name, status, player_numbers))
    return processed_data


def write_to_csv(data: List[Tuple[str, str, str]], filename: str) -> None:
    """
    Writes processed data to a CSV file.

    Args:
    data: List of tuples containing the name, status, and player numbers.
    filename: Path to the CSV file.

    Returns:
    None
    """
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, lineterminator="\n")
        csvwriter.writerow(['Name', 'Status', 'Players'])
        csvwriter.writerows(sorted(data, key=lambda x: x[0]))


def main():
    # Load env variables
    load_dotenv()

    # Step 1: Retrieve HTML file by URL
    url = 'https://boardgamearena.com'
    
    # Load cookies from .env file
    cookies = {
        'PHPSESSID': os.getenv('PHPSESSID'),
        'TournoiEnLigne_sso_id': os.getenv('TournoiEnLigne_sso_id'),
        'TournoiEnLigne_sso_user': os.getenv('TournoiEnLigne_sso_user'),
        'TournoiEnLigneid': os.getenv('TournoiEnLigneid'),
        'TournoiEnLigneidt': os.getenv('TournoiEnLigneidt'),
        'TournoiEnLignetk': os.getenv('TournoiEnLignetk'),
        'TournoiEnLignetkt': os.getenv('TournoiEnLignetkt'),
        '__stripe_mid': os.getenv('__stripe_mid'),
    }
    
    response = requests.get(url, cookies=cookies)
    html_content = response.text
    
    # Step 2: Find the JavaScript <script> section
    soup = BeautifulSoup(html_content, 'html.parser')
    scripts = soup.find_all('script')
    
    # Step 3: Obtain the value for the variable globalUsersInfo
    global_users_info = None
    for script in scripts:
        if 'globalUserInfos' in script.text:
            # Use regular expression to extract the value of globalUsersInfo
            match = re.search(r'globalUserInfos\s*=\s*({.*?});', script.text, re.DOTALL)
            if match:
                global_users_info = match.group(1)
                break
    
    global_users_info_dict = json.loads(global_users_info)
    
    # Process and write data to CSV
    game_list = global_users_info_dict.get('game_list')
    processed_data = process_data(game_list)

    # Create a filename
    filename = 'bga-tricktakers.csv'

    print(f'Writing to {filename}')
    write_to_csv(processed_data, filename)


if __name__ == '__main__':
    main()
