import aiohttp
import asyncio
import time
from datetime import datetime
from colorama import init, Fore, Style
import random
init(autoreset=True)

start_text = """
▀█▀ █ █▀▄▀█ █▀▀   █▀▀ ▄▀█ █▀█ █▀▄▀█
░█░ █ █░▀░█ ██▄   █▀░ █▀█ █▀▄ █░▀░█
"""

# Reusable headers
HEADERS = {
    "accept": "*/*",
    "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "content-type": "application/json",
    "priority": "u=1, i",
    "referer": "https://tg-tap-miniapp.laborx.io/"
}


import aiohttp

async def get_user(session, query_id):
    url = "https://tg-bot-tap.laborx.io/api/v1/auth/validate-init"
    payload = {
        "auth_date": 1718166034,
        "user": {},
        "query_id": "AAH0IgU2AAAAAPQiBTbsx9CW&user=%7B%22id%22%3A906306292%2C%22first_name%22%3A%22Khanh%22%2C%22last_name%22%3A%22Ngoc%22%2C%22username%22%3A%22thoel30%22%2C%22language_code%22%3A%22vi%22%2C%22allows_write_to_pm%22%3Atrue%7D&auth_date=1718166034&hash=35da4708fd894ac5c599b890e26db8845a7dbdd3f3986499ccf313e0063a6626"
    }
    try:
        async with session.post(url, headers=HEADERS, json=payload) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.RED+Style.BRIGHT}Error fetching profile: {e}")
        return None
    


async def claim(session, query_id):
    headers = {**HEADERS, "Authorization": f'Bearer {query_id}'}
    url = "https://tg-bot-tap.laborx.io/api/v1/farming/finish"
    try:
        async with session.post(url, headers=headers) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT}Point Claim: Not available...")
async def start(session, query_id):
    headers = {**HEADERS, "Authorization": f'Bearer {query_id}'}
    url = "https://tg-bot-tap.laborx.io/api/v1/farming/start"
    try:
        async with session.post(url, headers=headers) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT}Start Claim: Not available...") 
        
        
async def acc_info(session, query_id):
    headers = {**HEADERS, "Authorization": f'Bearer {query_id}'}
    url = "https://tg-bot-tap.laborx.io/api/v1/farming/info"
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT}Acc info not available...")               

def countdown(secs):
    for i in range(secs, 0, -1):
        print(f"\r{Fore.MAGENTA+Style.BRIGHT}Sleeping for {i} seconds...", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 50, end="", flush=True)  # Clear the countdown message

def format_balance(balance):
    return '{:,.0f}'.format(balance)
# Read query_id from file
def read_query_id(filename):
    with open(filename, "r") as file:
        return file.read().splitlines()

# Example usage
filename = "authorization.csv"
query_ids = read_query_id(filename)

async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            #print(start_text)
            for query_id in query_ids:
                print(f"{Fore.YELLOW+Style.BRIGHT}[TIME FARM] [{datetime.now().strftime('%H:%M:%S')}] Token: {query_id[:30] + '...' if len(query_id) > 30 else query_id}...")
                # user = await get_user(session, query_id)
                # if user:
                #     try:
                #         user_name = user['balanceInfo']['user']
                #         print(f"{Fore.GREEN+Style.BRIGHT} user: {user_name}")
                #     except KeyError:
                #         print(f"{Fore.RED+Style.BRIGHT}Cant get account info")
                info = await acc_info(session, query_id)
                if info:
                    try:
                        total_balance = info['balance']
                        total_balance = float(total_balance)
                        formatted_number = "{:,.3f}".format(total_balance)
                        print(f"{Fore.GREEN+Style.BRIGHT} Balance: {formatted_number}")
                    except KeyError:
                        print(f"{Fore.RED+Style.BRIGHT}Cant get account info") 
                finish = await claim(session, query_id)
                if finish:
                    try:
                        balance = finish['balance']
                        print(f"{Fore.GREEN+Style.BRIGHT}Claimed: {balance}")
                    except KeyError:
                        print(f"{Fore.RED+Style.BRIGHT}Claimed Not available") 
                go = await start(session, query_id)
                if go:
                    try:
                        #balance = info['balance']
                        print(f"{Fore.GREEN+Style.BRIGHT}Started...")
                    except KeyError:
                        print(f"{Fore.RED+Style.BRIGHT}Start not available")
                
            random_delay = random.randint(500, 800)
            countdown(random_delay)
asyncio.run(main())