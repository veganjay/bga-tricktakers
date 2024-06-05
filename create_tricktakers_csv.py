#!/usr/bin/env python3

import json
import csv
from typing import List, Tuple, Dict


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


def read_data_json(filename: str) -> Dict:
    """
    Reads JSON data from a file and returns it as a dictionary.

    Args:
    filename: Path to the JSON file.

    Returns:
    Dictionary with the data from the JSON file.
    """
    with open(filename, 'r') as fp:
        return json.load(fp)


def format_range(player_range: Tuple[int, int]) -> str:
    """
    Formats a range tuple into a string.

    Args:
    player_range: Tuple containing the start and end of the range.

    Returns:
    Formatted string representation of the range.
    """
    min_players, max_players = player_range
    return (
        f'{min_players}-{max_players}'
        if min_players != max_players
        else str(min_players)
    )


def format_range_list(player_range_list: List[Tuple[int, int]]) -> str:
    """
    Formats a list of range tuples into a string.

    Args:
    player_range_list: List of tuples representing ranges.

    Returns:
    Formatted string representation of the list of ranges.
    """
    return ' or '.join(
        format_range(player_range) for player_range in player_range_list
    )


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
        player_numbers = format_range_list(
            list_to_ranges(item.get('player_numbers'))
        )
        tags = item.get('tags')
        status = (
            'alpha' if item.get('status') == 'private' else item.get('status')
        )
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
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Name', 'Status', 'Players'])
        csvwriter.writerows(sorted(data, key=lambda x: x[0]))


def main():
    data = read_data_json("data/bga-list.json")
    processed_data = process_data(data)
    write_to_csv(processed_data, 'bga-tricktakers.csv')


if __name__ == '__main__':
    main()
