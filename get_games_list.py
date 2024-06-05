#!/usr/bin/env python3

from datetime import datetime
import argparse
import json
import os
import requests
import re

from bs4 import BeautifulSoup
from dotenv import load_dotenv


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timestamp", action="store_true", default=False)
    return parser.parse_args()


def main():
    args = parse_args()

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
    
    out = json.dumps(global_users_info_dict.get('game_list'), indent=2)
    
    # Get the current date
    current_date = datetime.now()
    
    # Format the date as YYYYMMDD
    timestamp = current_date.strftime('%Y%m%d')
    
    # Create a filename
    if args.timestamp:
        filename = f'data/bga-list-{timestamp}.json'
    else:
        filename = 'data/bga-list.json'

    print(f'Writing to {filename}')
    
    with open(filename, 'w') as fp:
        json.dump(global_users_info_dict.get('game_list'), fp, indent=2)


if __name__ == '__main__':
    main()
