import requests
import json
import random
import string
from datetime import datetime
import time
from urllib.parse import unquote
from colorama import init, Fore, Style
from bots.query import QUERY_USER, QUERY_LOGIN, MUTATION_GAME_PROCESS_TAPS_BATCH, QUERY_GAME_CONFIG, QUERY_TAP_BOT_CLAIM, QUERY_TAP_BOT_START, QUERY_BOOSTER
import ssl
init(autoreset=True)

recharge_flag = 1

start_text = """
█▀▄▀█ █▀▀ █▀▄▀█ █▀▀ █▀▀ █
█░▀░█ ██▄ █░▀░█ ██▄ █▀░ █
"""
ssl_context = ssl._create_unverified_context()

HEADERS = {
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/json',
    'Origin': 'https://tg-app.memefi.club',
    'Referer': 'https://tg-app.memefi.club/',
    'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    'Sec-Ch-Ua-mobile': '?1',
    'Sec-Ch-Ua-platform': '"Android"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
}

url = "https://api-gw-tg.memefi.club/graphql"


def generate_random_nonce(length=52):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def format_balance(balance):
    return '{:,.0f}'.format(balance)


def login(query_id):
    raw_data = query_id
    tg_web_data = unquote(unquote(raw_data))
    query_id = tg_web_data.split('query_id=', maxsplit=1)[1].split('&user', maxsplit=1)[0]
    user_data = tg_web_data.split('user=', maxsplit=1)[1].split('&auth_date', maxsplit=1)[0]
    auth_date = tg_web_data.split('auth_date=', maxsplit=1)[1].split('&hash', maxsplit=1)[0]
    hash_ = tg_web_data.split('hash=', maxsplit=1)[1].split('&', maxsplit=1)[0]

    user_data_dict = json.loads(unquote(user_data))

    data = {
        "operationName": "MutationTelegramUserLogin",
        "variables": {
            "webAppData": {
                "auth_date": int(auth_date),
                "hash": hash_,
                "query_id": query_id,
                "checkDataString": f"auth_date={auth_date}\nquery_id={query_id}\nuser={unquote(user_data)}",
                "user": {
                    "id": user_data_dict["id"],
                    "allows_write_to_pm": user_data_dict["allows_write_to_pm"],
                    "first_name": user_data_dict["first_name"],
                    "last_name": user_data_dict["last_name"],
                    "username": user_data_dict.get("username", "Username N/A"),
                    "language_code": user_data_dict["language_code"],
                    "version": "7.2",
                    "platform": "ios"
                }
            }
        },
        "query": QUERY_LOGIN
    }

    response = requests.post(url, headers=HEADERS, json=data, verify=False)
    try:
        json_response = response.json()
        if 'errors' in json_response:
            return None
        else:
            access_token = json_response['data']['telegramUserLogin']['access_token']
            return access_token
    except requests.exceptions.JSONDecodeError:
        print("Không thể giải mã JSON")
        return None


def claim(session, query_id):
    headers = {**HEADERS, "Authorization": f'Bearer {query_id}'}
    tap_payload = {
        "operationName": "MutationGameProcessTapsBatch",
        "variables": {
            "payload": {
                "nonce": generate_random_nonce(),
                "tapsCount": random.randint(10, 35)
            }
        },
        "query": MUTATION_GAME_PROCESS_TAPS_BATCH
    }
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = session.post(url, headers=headers, json=tap_payload, verify=False)
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"{Fore.BLUE + Style.BRIGHT}Point Claim: Attempt {attempt + 1} failed... {e}")
            if attempt < 2:  # Don't delay on the last attempt
                time.sleep(2 ** attempt)  # Exponential backoff
    return None


def claim_tap_bot(session, query_id):
    headers = {**HEADERS, "Authorization": f'Bearer {query_id}'}
    tap_payload = {
        "operationName": "TapbotClaim",
        "variables": {},
        "query": QUERY_TAP_BOT_CLAIM
    }
    try:
        response = session.post(url, headers=headers, json=tap_payload, verify=False)
        response.raise_for_status()
        result = response.json()
        if 'errors' in result:
            print(f"{Fore.BLUE + Style.BRIGHT}Tap bot claim error: {result['errors'][0]['message']}")
            return None
        print(f"{Fore.BLUE + Style.BRIGHT}Tap bot claimed!")
        return result
    except requests.exceptions.RequestException as e:
        print(f"{Fore.BLUE + Style.BRIGHT}Claim Tap Bot: Not available... {e}")
        return None


def start_tap_bot(session, query_id):
    headers = {**HEADERS, "Authorization": f'Bearer {query_id}'}
    tap_payload = {
        "operationName": "TapbotStart",
        "variables": {},
        "query": QUERY_TAP_BOT_START
    }
    try:
        response = session.post(url, headers=headers, json=tap_payload, verify=False)
        response.raise_for_status()  # Raise HTTPError for non-200 status codes
        result = response.json()
        if 'errors' in result:
            print(f"{Fore.BLUE + Style.BRIGHT}Start Tap Bot error: {result['errors'][0]['message']}")
            return None
        print(f"{Fore.BLUE + Style.BRIGHT}Tap bot started!")
        return result
    except requests.exceptions.RequestException as e:
        print(f"{Fore.BLUE + Style.BRIGHT}Start Tap Bot: Not available... {e}")
        return None


def claim_booster(session, query_id, booster_type="Recharge"):
    headers = {**HEADERS, "Authorization": f'Bearer {query_id}'}
    payload = {
        "operationName": "telegramGameActivateBooster",
        "variables": {
            "boosterType": booster_type
        },
        "query": QUERY_BOOSTER
    }
    try:
        response = session.post(url, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        result = response.json()
        if 'errors' in result:
            print(f"{Fore.BLUE + Style.BRIGHT}Booster claim error: {result['errors'][0]['message']}")
            return None
        print(f"{Fore.BLUE + Style.BRIGHT}Booster claimed!")
        return result
    except requests.exceptions.RequestException as e:
        print(f"{Fore.BLUE + Style.BRIGHT}Claim Booster: Not available...{e}")
        return None


def countdown(secs):
    for i in range(secs, 0, -1):
        print(f"\r{Fore.MAGENTA + Style.BRIGHT}Sleeping for {i} seconds...", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 50, end="", flush=True)  # Clear the countdown message
    print("\n")  # Print a newline to ensure the prompt appears on a new line


def read_query_id(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        return [line.strip() for line in lines if line.strip() and not line.startswith('#')]


filename = "token.txt"
query_ids = read_query_id(filename)


def main():
    with requests.Session() as session:
        i = 1
        while True:
            for current_query_index, query_id in enumerate(query_ids):
                if current_query_index == 0 and i != 1:
                    i = 1
                print(f"{Fore.YELLOW + Style.BRIGHT}Token: {query_id[:30] + '...' if len(query_id) > 30 else query_id}...")

                account = login(query_id)
                claim_tap_bot(session, account)
                start_tap_bot(session, account)

                while True:
                    info = claim(session, account)
                    if not info or not info.get('data'):
                        print(f"{Fore.RED + Style.BRIGHT}Failed to get game info. Breaking the loop.")
                        break

                    try:
                        data = info['data']
                        batch = data.get('telegramGameProcessTapsBatch', {})
                        total = batch.get('coinsAmount', 'N/A')
                        current_health = batch.get('currentBoss', {}).get('currentHealth', 'N/A')
                        current_energy = batch.get('currentEnergy', 'N/A')

                        if any(val == 'N/A' for val in [total, current_health, current_energy]) or current_health == '0':
                            print(f"{Fore.RED + Style.BRIGHT}Invalid game info received. Breaking the loop.")
                            break

                        print(f"{Fore.GREEN + Style.BRIGHT}[MemeFi{i}] [{datetime.now().strftime('%H:%M:%S')}] Balance: {format_balance(total)}, Health: {format_balance(current_health)}, Energy: {current_energy}")

                        if current_energy < 100:
                            booster_claimed = claim_booster(session, account, booster_type="Recharge") if recharge_flag else None
                            if not booster_claimed:
                                break
                    except KeyError:
                        print(f"{Fore.RED + Style.BRIGHT}Game info not found in the game info response")

                    time.sleep(0.5)

                i += 1

            random_delay = random.randint(300, 600)
            countdown(random_delay)


if __name__ == "__main__":
    main()
