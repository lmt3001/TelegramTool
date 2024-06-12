import requests
from colorama import init, Fore, Style
import time

init(autoreset=True)

# Reusable headers
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "content-type": "application/json",
    "origin": "https://cf.seeddao.org",
    "priority": "u=1, i",
    "referer": "https://cf.seeddao.org/"
}

def get_profile(query_id):
    headers = {**HEADERS, "Telegram-Data": query_id}
    url = "https://elb.seeddao.org/api/v1/profile"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for non-200 status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED+Style.BRIGHT}Error fetching profile: {e}")
        return None

def get_balance(query_id):
    headers = {**HEADERS, "Telegram-Data": query_id}
    url = "https://elb.seeddao.org/api/v1/profile/balance"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for non-200 status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED+Style.BRIGHT}Error fetching balance: {e}")
        return None

def format_balance(balance_value):
    balance_str = str(balance_value)
    if len(balance_str) > 9:
        integer_part = balance_str[:-9]
        decimal_part = balance_str[-9:]
        formatted_balance = f"{integer_part}.{decimal_part}"
    else:
        formatted_balance = f"0.{balance_str.zfill(9)}"
    return "{:.6f}".format(float(formatted_balance))




def claim(query_id):
    headers = {**HEADERS, "Telegram-Data": query_id}
    url = "https://elb.seeddao.org/api/v1/seed/claim"
    try:
        response = requests.post(url, headers=headers, json={})
        response.raise_for_status()  # Raise HTTPError for non-200 status codes
        print(f"{Fore.GREEN+Style.BRIGHT}Point Claim: Successful!")
    except requests.exceptions.RequestException as e:
        #print(f"{Fore.RED+Style.BRIGHT}Claim failed: {e}")
        print(f"{Fore.BLUE+Style.BRIGHT}Point Claim: Not available...")
        
def login_bonus(query_id):
    headers = {**HEADERS, "Telegram-Data": query_id}
    url = "https://elb.seeddao.org/api/v1/login-bonuses"
    try:
        response = requests.post(url, headers=headers, json={})
        response.raise_for_status()  # Raise HTTPError for non-200 status codes
        print(f"{Fore.GREEN+Style.BRIGHT}Login Bonus: Claim successful!")
    except requests.exceptions.RequestException as e:
        #print(f"{Fore.RED+Style.BRIGHT}Claim login bonus failed: {e}")
        print(f"{Fore.BLUE+Style.BRIGHT}Login Bonus: Not available...")
        
# Countdown function
def countdown(secs):
    for i in range(secs, 0, -1):
        print(f"\r{Fore.MAGENTA+Style.BRIGHT}Sleeping for {i} seconds...", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 50, end="", flush=True)  # Clear the countdown message

# Read query_id from file
def read_query_id(filename):
    with open(filename, "r") as file:
        return file.read().splitlines()

# Example usage
filename = "query_id.txt"
query_ids = read_query_id(filename)

while True:
    for query_id in query_ids:
        print(f"{Fore.YELLOW+Style.BRIGHT}Claiming for query_id: {query_id[:20] + '...' if len(query_id) > 20 else query_id}...")
        profile = get_profile(query_id)
        if profile:
            try:
                print(f"{Fore.BLUE+Style.BRIGHT}User Name: {profile['data']['name']}")
            except KeyError:
                print(f"{Fore.RED+Style.BRIGHT}Key 'data' or 'name' not found in the profile response")
        else:
            print(f"{Fore.RED+Style.BRIGHT}Failed to retrieve profile")

        balance = get_balance(query_id)
        if balance:
            try:
                total_coin = format_balance(balance['data'])
                print(f"{Fore.BLUE+Style.BRIGHT}Balance: {total_coin}")
            except KeyError:
                print(f"{Fore.RED+Style.BRIGHT}Key 'data' not found in the balance response")
        else:
            print(f"{Fore.RED+Style.BRIGHT}Failed to retrieve balance")
        login_bonus(query_id)
        claim(query_id)
    countdown(600)
