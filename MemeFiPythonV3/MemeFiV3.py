import aiohttp
import asyncio
import json
import random
import string
import time
from urllib.parse import unquote
from colorama import init, Fore, Style
from bots.headers import headers_set
from bots.query import QUERY_USER, QUERY_LOGIN, MUTATION_GAME_PROCESS_TAPS_BATCH, QUERY_GAME_CONFIG
import os
init(autoreset=True)


start_text = """
█▀▄▀█ █▀▀ █▀▄▀█ █▀▀ █▀▀ █
█░▀░█ ██▄ █░▀░█ ██▄ █▀░ █
"""

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
def format_balance(balance):
    return '{:,.0f}'.format(balance)
async def login(query_id):
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
                    "username": user_data_dict.get("username", "Username không được đặt"),
                    "language_code": user_data_dict["language_code"],
                    "version": "7.2",
                    "platform": "ios"
                }
            }
        },
        "query": QUERY_LOGIN
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=HEADERS, json=data) as response:
            try:
                json_response = await response.json()
                if 'errors' in json_response:
                    return None
                else:
                    access_token = json_response['data']['telegramUserLogin']['access_token']
                    return access_token
            except aiohttp.ContentTypeError:
                print("Không thể giải mã JSON")
                return None
            
async def claim(session, query_id):
    headers = {**HEADERS, "Authorization": f'Bearer {query_id}'}

    tap_payload = {
    "operationName": "MutationGameProcessTapsBatch",
    "variables": {
        "payload": {
            "nonce": generate_random_nonce(),
            "tapsCount": random.randint(5,10)
        }
    },
    "query": MUTATION_GAME_PROCESS_TAPS_BATCH
    }
    try:
        async with session.post(url, headers=headers, json=tap_payload) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT}Point Claim: Not available... {e}")
        
        
        
        
def countdown(secs):
    for i in range(secs, 0, -1):
        print(f"\r{Fore.MAGENTA+Style.BRIGHT}Sleeping for {i} seconds...", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 50, end="", flush=True)  # Clear the countdown message
def read_query_id(filename):
    with open(filename, "r") as file:
        return file.read().splitlines()
filename = "query_id.txt"
query_ids = read_query_id(filename)
async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            print(start_text)
            for query_id in query_ids:
                print(f"{Fore.YELLOW+Style.BRIGHT}Claiming for query_id: {query_id[:30] + '...' if len(query_id) > 30 else query_id}...")
                while True:
                    account = await login(query_id)
                    info = await claim(session, account)
                    if info:
                        try:
                            total = info['data']['telegramGameProcessTapsBatch']['coinsAmount']
                            currentHealth = info['data']['telegramGameProcessTapsBatch']['currentBoss']['currentHealth']
                            currentEnergy = info['data']['telegramGameProcessTapsBatch']['currentEnergy']
                            print(f"{Fore.GREEN+Style.BRIGHT}Balance: {format_balance(total)}, Health: {format_balance(currentHealth)}, Energy: {currentEnergy}")
                            if currentEnergy < 100:
                                break
                        except KeyError:
                            print(f"{Fore.RED+Style.BRIGHT}Game info not found in the game info response")
                    await asyncio.sleep(0.5)  # Wait for  0.5 seconds before the next check
                    
                    
            random_delay = random.randint(100, 200)
            countdown(random_delay)
        
asyncio.run(main())
