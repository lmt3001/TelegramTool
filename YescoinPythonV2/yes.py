import aiohttp
import asyncio
import time
from colorama import init, Fore, Style
import random
init(autoreset=True)

start_text = """
█▄█ █▀▀ █▀
░█░ ██▄ ▄█
"""
# Reusable headers
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "content-type": "application/json",
    "origin": "https://www.yescoin.gold",
    "priority": "u=1, i",
    "referer": "https://www.yescoin.gold/"
}

async def get_account_info(session, query_id):
    headers = {**HEADERS, "Token": query_id}
    url = "https://api.yescoin.gold/account/getAccountInfo"
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.RED+Style.BRIGHT}Error fetching profile: {e}")
        return None
    
async def get_game_info(session, query_id):
    headers = {**HEADERS, "Token": query_id}
    url = "https://api.yescoin.gold/game/getGameInfo"
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.RED+Style.BRIGHT}Error fetching profile: {e}")
        return None

async def claim(session, query_id):
    headers = {**HEADERS, "Token": query_id}
    url = "https://api.yescoin.gold/game/collectCoin"
    try:
        async with session.post(url, headers=headers, json=10) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            return await response.json()

    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT}Point Claim: Not available...")
        
# Countdown function
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
            print(start_text)
            for query_id in query_ids:
                print(f"{Fore.YELLOW+Style.BRIGHT}Claiming for query_id: {query_id[:30] + '...' if len(query_id) > 30 else query_id}...")
                while True:
                    info = await get_game_info(session, query_id)
                    if info:
                        try:
                            left_coins = info['data']['coinPoolLeftCount']
                            if left_coins > 100:
                                claim_response = await claim(session, query_id)
                                if claim_response:
                                    profile = await get_account_info(session, query_id)
                                    if profile:
                                        try:
                                            balance=profile['data']['currentAmount']
                                            formatted_balance = format_balance(balance)
                                            print(f"{Fore.GREEN+Style.BRIGHT}Info: {claim_response['data']} --------- Remaining: {left_coins} --------Balance: {formatted_balance}")
                                        except KeyError:
                                            print(f"{Fore.RED+Style.BRIGHT}Get account info not found in the profile response")
                                    else:
                                        print(f"{Fore.RED+Style.BRIGHT}Failed to retrieve profile")
                                else:
                                    print(f"{Fore.RED+Style.BRIGHT}Claim failed")
                            else:
                                print(f"{Fore.CYAN+Style.BRIGHT}Coin pool is not available, Sleep...")
                                break  # Exit the loop if left_coins <= 10
                        except KeyError:
                            print(f"{Fore.RED+Style.BRIGHT}Game info not found in the game info response")
                    await asyncio.sleep(0.5)  # Wait for 0.5 seconds before the next check
            random_delay = random.randint(200, 300)
            countdown(random_delay)
asyncio.run(main())