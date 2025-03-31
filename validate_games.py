import json
import argparse
import re
from datetime import datetime, timedelta


def is_valid_lingo_solution(solution, all_solutions):
    """Validate a lingo solution."""
    # Check if solution is exactly 5 characters
    if len(solution) != 5:
        return False, f"Lingo solution '{solution}' is not exactly 5 characters."

    # Check if solution has only letters (no spaces, numbers, or special characters)
    if not re.match(r'^[a-zA-Z]+$', solution):
        return False, f"Lingo solution '{solution}' contains invalid characters (only letters allowed)."

    # Check for uniqueness
    if solution in all_solutions:
        return False, f"Lingo solution '{solution}' is not unique."

    return True, None


def is_valid_scryptogram_target(target, all_targets):
    """Validate a scryptogram target."""
    # Check if target is longer than 25 characters
    if len(target) <= 25:
        return False, f"Scryptogram target is too short: {len(target)} characters (must be > 25)."

    # Check if target contains any words longer than 12 characters
    words = re.findall(r'\w+', target)
    for word in words:
        if len(word) > 12:
            return False, f"Scryptogram target contains a word longer than 12 characters: '{word}'."

    # Check for uniqueness
    if target in all_targets:
        return False, f"Scryptogram target is not unique."

    # Check for consecutive escaped quotes
    if '\\"\\"' in target:
        return False, f"Scryptogram target contains consecutive escaped quotes."

    return True, None


def is_valid_scryptogram_hint(hint):
    """Validate a scryptogram hint."""
    # Check if hint is longer than 6 characters
    if len(hint) <= 6:
        return False, f"Scryptogram hint is too short: {len(hint)} characters (must be > 6)."

    # Check if hint contains a colon
    if ':' not in hint:
        return False, f"Scryptogram hint does not contain a ':' character."

    return True, None


def is_valid_scryptogram_cipher(cipher):
    """Validate a scryptogram cipher."""
    # Check if cipher is exactly 26 characters
    if len(cipher) != 26:
        return False, f"Scryptogram cipher is not exactly 26 characters: {len(cipher)}."

    # Check if all characters are uppercase
    if not cipher.isupper():
        return False, f"Scryptogram cipher is not all uppercase: '{cipher}'."

    # Check that no character is in its original position in the alphabet
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i in range(26):
        if cipher[i] == alphabet[i]:
            return False, f"Scryptogram cipher has '{cipher[i]}' in its original position {i+1}."

    return True, None


def validate_json(end_date_str):
    # Parse the end date
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # Set start date to Mar 3, 2025
    start_date = datetime.strptime("2025-03-05", "%Y-%m-%d")

    # Read the JSON file
    try:
        with open("prompts.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File prompts.json not found.")
        return False
    except json.JSONDecodeError:
        print(f"Error: prompts.json is not a valid JSON file.")
        return False

    # Check if 'games' object exists
    if 'games' not in data:
        print("Error: JSON file does not contain a 'games' object.")
        return False

    # Track all solutions and targets for uniqueness checks
    all_lingo_solutions = set()
    all_scryptogram_targets = set()
    valid = True

    # Validate games for each date
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")

        # Check if there's an entry for this date
        if date_str not in data['games']:
            print(f"Error: Missing game for date {date_str}")
            valid = False
            current_date += timedelta(days=1)
            continue

        game = data['games'][date_str]

        # Check if game has at least 2 elements
        if len(game) < 2:
            print(f"Error: Game for {date_str} doesn't have at least 2 elements")
            valid = False
            current_date += timedelta(days=1)
            continue

        # Validate lingo game (first element)
        if game[0]['type'] != 'lingo':
            print(f"Error: First game for {date_str} is not of type 'lingo'")
            valid = False
        elif 'config' not in game[0] or 'solution' not in game[0]['config']:
            print(f"Error: Lingo game for {date_str} is missing config or solution")
            valid = False
        else:
            solution = game[0]['config']['solution']
            solution_valid, error_msg = is_valid_lingo_solution(solution, all_lingo_solutions)
            if not solution_valid:
                print(f"Error on {date_str}: {error_msg}")
                valid = False
            else:
                all_lingo_solutions.add(solution)

        # Validate scryptogram game (second element)
        if game[1]['type'] != 'scryptogram':
            print(f"Error: Second game for {date_str} is not of type 'scryptogram'")
            valid = False
        elif 'config' not in game[1] or any(key not in game[1]['config'] for key in ['target', 'hint', 'cipher']):
            print(f"Error: Scryptogram game for {date_str} is missing config, target, hint, or cipher")
            valid = False
        else:
            config = game[1]['config']

            # Validate target
            target_valid, target_error = is_valid_scryptogram_target(config['target'], all_scryptogram_targets)
            if not target_valid:
                print(f"Error on {date_str}: {target_error}")
                valid = False
            else:
                all_scryptogram_targets.add(config['target'])

            # Validate hint
            hint_valid, hint_error = is_valid_scryptogram_hint(config['hint'])
            if not hint_valid:
                print(f"Error on {date_str}: {hint_error}")
                valid = False

            # Validate cipher
            cipher_valid, cipher_error = is_valid_scryptogram_cipher(config['cipher'])
            if not cipher_valid:
                print(f"Error on {date_str}: {cipher_error}")
                valid = False

        current_date += timedelta(days=1)

    if valid:
        print(f"Validation successful for all games from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.")
    else:
        print("Validation failed. Please fix the issues above.")

    return valid


def main():
    parser = argparse.ArgumentParser(description='Validate JSON file for daily games.')
    parser.add_argument('file', help='Path to the JSON file')
    parser.add_argument('endDate', help='End date in YYYY-MM-DD format')

    args = parser.parse_args()

    validate_json(args.endDate)

if __name__ == "__main__":
    main()
# import json
# import argparse
# import re
# from datetime import datetime, timedelta
#
#
# def validate_json(end_date_str):
#     # Parse the end date
#     end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
#
#     # Set start date to Mar 3, 2025
#     start_date = datetime.strptime("2025-03-03", "%Y-%m-%d")
#
#     # Read the JSON file
#     try:
#         with open("prompts.json", 'r', encoding='utf-8') as f:
#             data = json.load(f)
#     except FileNotFoundError:
#         print(f"Error: File prompts.json not found.")
#         return False
#     except json.JSONDecodeError:
#         print(f"Error: prompts.json is not a valid JSON file.")
#         return False
#
#     # Check if 'prompts' array exists
#     if 'games' not in data:
#         print("Error: JSON file does not contain a 'games' object.")
#         return False
#
#     # for each date between start_date and end_date:
#     # make sure there's a data['games'][date string] object
#     # check the object (let's call it 'game') for the following (create separate functions if it makes sense)
#     # game[0]['type'] = 'lingo'
#     # game[0]['config']['solution'] is exactly 5 chars with no spaces, numbers or special characters
#     # game[0]['config']['solution'] unique among all of the game objects
#     # game[1]['type'] = 'scryptogram'
#     # game[1]['config']['target'] is longer than 25 chars
#     # game[1]['config']['target'] does not contain any words longer than 12 chars, including punctuation
#     # game[1]['config']['target'] is unique among all of the game objects.
#     # game[1]['config']['target'] does not contain 2 escaped double quotes in a row. (ie, /" is ok, but /"/" is bad.)
#     # game[1]['config']['hint'] is a string longer than 6 chars, and contains a ":" character
#     # game[1]['config']['cipher'] 26 chars, all upper case
#     # game[1]['config']['cipher'] has no characters in their "right place" in the alphabet. (ie, A is never in pos 1, B is never in pos 2, etc)
#     # print out any violations of these rules.
#
# def main():
#     parser = argparse.ArgumentParser(description='Validate JSON file for daily games.')
#     parser.add_argument('file', help='Path to the JSON file')
#     parser.add_argument('endDate', help='End date in YYYY-MM-DD format')
#
#     args = parser.parse_args()
#
#     validate_json(args.endDate)
#
# if __name__ == "__main__":
#     main()