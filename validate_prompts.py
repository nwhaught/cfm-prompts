import json
import argparse
import re
from datetime import datetime, timedelta

def check_prompt_format(prompt_obj):
    """
    Checks if the prompt follows the forbidden pattern "Prompt for YYYY-MM-DD"
    Returns True if the prompt is valid (doesn't match the pattern)
    Returns False if the prompt matches the forbidden pattern
    """
    if 'Prompt' not in prompt_obj:
        return True  # No Prompt property to check

    prompt_text = prompt_obj['Prompt']
    prompt_date = prompt_obj['Date']
    # Pattern to match "Prompt for YYYY-MM-DD"
    pattern = r"^Prompt for \d{4}-\d{2}-\d{2}$"
    if re.match(pattern, prompt_text):
        print(f"Error: Invalid prompt format: '{prompt_text}'")
        return False

    if 'Lesson' not in prompt_obj:
        print(f"[{prompt_date}] is missing a Lesson title")
        return False

    if 'WeekDay' not in prompt_obj:
        print(f"[{prompt_date}] is missing a WeekDay")
        return False

    if 'WeekNum' not in prompt_obj:
        print(f"[{prompt_date}] is missing a WeekNum")
        return False

    if 'WeekLabel' not in prompt_obj:
        print(f"[{prompt_date}] is missing a WeekLabel")
        return False

    if 'Month' not in prompt_obj:
        print(f"[{prompt_date}] is missing a Month")
        return False

    if 'Link' not in prompt_obj:
        print(f"[{prompt_date}] is missing a Link")
        return False

    if 'Lesson' not in prompt_obj:
        print(f"[{prompt_date}] is missing a Lesson")
        return False

    if 'Prompt' not in prompt_obj:
        print(f"[{prompt_date}] is missing a Prompt")
        return False

    if 'PromptLink' not in prompt_obj:
        print(f"[{prompt_date}] is missing a PromptLink")
        return False

    return True

def check_youtube_link(prompt_obj):
    """
    Checks if the prompt has a PromptLink property with a YouTube link
    Returns True if the YouTube link is present
    Returns False if PromptLink is missing or doesn't contain a YouTube link
    """
    if 'Date' not in prompt_obj:
        return True  # No date to reference in error message

    prompt_date = prompt_obj['Date']

    if 'PromptLink' not in prompt_obj:
        print(f"[{prompt_date}] is missing YouTube link")
        return False

    prompt_link = prompt_obj['PromptLink']

    # Pattern to match YouTube links
    youtube_patterns = [
        r"https?://(?:www\.)?youtube\.com/",
        r"https?://(?:www\.)?youtu\.be/"
    ]

    for pattern in youtube_patterns:
        if re.search(pattern, prompt_link):
            return True

    print(f"[{prompt_date}] has PromptLink but it's not a YouTube link: '{prompt_link}'")
    return False

def check_escaped_quotes(prompt_obj):
    """
    Checks if the Prompt property contains consecutive escaped double quotes
    Returns True if no consecutive escaped double quotes are found
    Returns False if consecutive escaped double quotes are found
    """
    if 'Prompt' not in prompt_obj or 'Date' not in prompt_obj:
        return True  # No Prompt property to check or no date for the error message

    prompt_text = prompt_obj['Prompt']
    prompt_date = prompt_obj['Date']

    # Pattern to match consecutive escaped double quotes (\"\" or \"\")
    # The regex looks for backslash followed by double quote, repeated
    pattern = r'\"+\"+'

    if re.search(pattern, prompt_text):
        print(f"[{prompt_date}] Prompt contains consecutive escaped double quotes")
        return False

    return True

def validate_json(end_date_str):
    # Parse the end date
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # Set start date to Feb 15, 2025
    start_date = datetime.strptime("2025-03-03", "%Y-%m-%d")

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

    # Check if 'prompts' array exists
    if 'prompts' not in data or not isinstance(data['prompts'], list):
        print("Error: JSON file does not contain a 'prompts' array.")
        return False

    # Create a set of dates from the JSON
    json_dates = set()
    for prompt in data['prompts']:
        if 'Date' in prompt:
            try:
                prompt_date = datetime.strptime(prompt['Date'], "%Y-%m-%d")
                json_dates.add(prompt_date.strftime("%Y-%m-%d"))
                if prompt_date <= end_date and prompt_date >= start_date:
                    check_prompt_format(prompt)
                    check_youtube_link(prompt)
                    check_escaped_quotes(prompt)
            except ValueError:
                # Skip invalid date formats
                continue
    # Check if all required dates exist
    missing_dates = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        if date_str not in json_dates:
            missing_dates.append(date_str)
        current_date += timedelta(days=1)

    if missing_dates:
        print(f"Error: Missing prompts for the following dates:")
        for date in missing_dates:
            print(f"  - {date}")
        return False
    else:
        print("Success: All required dates are present in the prompts array.")
        return True



def main():
    parser = argparse.ArgumentParser(description='Validate JSON file for daily prompts.')
    parser.add_argument('file', help='Path to the JSON file')
    parser.add_argument('endDate', help='End date in YYYY-MM-DD format')

    args = parser.parse_args()

    validate_json(args.endDate)

if __name__ == "__main__":
    main()