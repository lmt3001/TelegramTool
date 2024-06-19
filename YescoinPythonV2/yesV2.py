import aiohttp
import asyncio
import time,json
from datetime import datetime
from datetime import timedelta
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
    collectAmount = random.randint(5,20)
    try:
        async with session.post(url, headers=headers, json=collectAmount) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            return await response.json()

    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT}Point Claim: Not available...")

async def claim_special_box(session, query_id):
    headers = {**HEADERS, "Token": query_id}
    url = "https://api.yescoin.gold/game/collectSpecialBoxCoin"
    collectAmount = 200
    payload = {
        "boxType": 2,
        "coinCount": collectAmount
    }
    try:
        async with session.post(url, headers=headers, json=payload) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            response_text = await response.text()
            data = json.loads(response_text)
            message = data.get('message', [])
            collect_amount = data.get('data', {}).get('collectAmount', [])
            return message, collect_amount
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE + Style.BRIGHT}Point Claim: Not available... Error: {e}")
        return None, None

async def recover_special_box(session, query_id):
    headers = {**HEADERS, "Token": query_id}
    url = "https://api.yescoin.gold/game/recoverSpecialBox"
    try:
        async with session.post(url, headers=headers) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            response_text = await response.text()
            data = json.loads(response_text)
            message = data.get('message', [])
            return message
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE + Style.BRIGHT}Recover Special Box: Not available... Error: {e}")
        return None
    
async def claim_offline(session, query_id):
    headers = {**HEADERS, "Token": query_id}
    url = "https://api.yescoin.gold/game/claimOfflineYesPacBonus"
    try:
        async with session.post(url, headers=headers) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            response_text = await response.text()
            data = json.loads(response_text)
            message = data.get('message', [])
            collect_amount = None
            if 'data' in data and data['data'] is not None:
                collect_amount = data['data'].get('collectAmount', [])
            return message, collect_amount
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE + Style.BRIGHT}Claim offline Error: {e}")
        return None
    
async def get_daily(session, query_id):
    headers = {**HEADERS, "Token": query_id}
    url = "https://api.yescoin.gold/signIn/list"
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            response_text = await response.text()
            data = json.loads(response_text)
            message = data.get('message', "")
            expired_info = [
                {"id": item['id'], "expired": str(timedelta(seconds=item['expired']))}
                for item in data['data'] if item.get('expired') not in (0, None)
            ]
            expired_ids = [info['id'] for info in expired_info]
            expired_times = [info['expired'] for info in expired_info]
            return message, expired_ids, expired_times
    except aiohttp.ClientError as e:
        print(f"Claim offline Error: {e}")
        return None
# async def claim_daily(session, query_id, daily_id):
#     headers = {**HEADERS, "Token": query_id}
#     url = "https://api.yescoin.gold/signIn/claim"
#     payload = {
#         "id": str(daily_id),
#         "signInType": 1,
#         "destination": "",
#         "createAt": "1718785952"
#     }
#     try:
#         async with session.post(url, headers=headers, json=payload) as response:
#             response.raise_for_status()  # Raise HTTPError for non-200 status codes
#             response_text = await response.text()
#             data = json.loads(response_text)
#             message = data.get('message', "")
#             collect_amount = None
#             if 'data' in data and data['data'] is not None:
#                 collect_amount = data['data'].get('reward', 0)
#             return message, collect_amount
#     except aiohttp.ClientError as e:
#         print(f"Client error: {e}")
#     except Exception as e:
#         print(f"Unexpected error: {e}")
        
async def full_recovery(session, query_id):
    headers = {**HEADERS, "Token": query_id}
    url = "https://api.yescoin.gold/game/recoverCoinPool"
    try:
        async with session.post(url, headers=headers, json=10) as response:
            response.raise_for_status() 
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT}Full Recovery: Not available...{e.message}")       

def countdown(secs):
    for i in range(secs, 0, -1):
        print(f"\r{Fore.MAGENTA+Style.BRIGHT}Sleeping for {i} seconds...", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 50, end="", flush=True)  # Clear the countdown message
    print("\n")  # Print a newline to ensure the prompt appears on a new line

def format_balance(balance):
    return '{:,.0f}'.format(balance)
# Read query_id from file
def read_query_id(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        return [line.strip() for line in lines if line.strip() and not line.startswith('#')]

# Example usage
filename = "token.txt"
query_ids = read_query_id(filename)

async def main():
    async with aiohttp.ClientSession() as session:
        i = 1
        while True:
            print(start_text)
            for current_query_index, query_id in enumerate(query_ids):
                if current_query_index == 0 and i != 1:
                    i = 1
                print(f"{Fore.YELLOW+Style.BRIGHT}Token: {query_id[:30] + '...' if len(query_id) > 30 else query_id}...")
                
                profile = await get_account_info(session, query_id)
                if profile:
                    balance=profile['data']['currentAmount']
                    print(f"{Fore.YELLOW+Style.BRIGHT} [Yes{i}] [{datetime.now().strftime('%H:%M:%S')}] Balance: {format_balance(balance)}")
                
                offline_mess, offline_amount = await claim_offline(session, query_id)
                if offline_mess == "Success":
                    print(f"{Fore.GREEN+Style.BRIGHT}->Claim offline status: {offline_mess} Claimed: {offline_amount}")
                else:
                    print(f"{Fore.BLUE+Style.BRIGHT}->Claim offline status: {offline_mess}")
                
                openSpecialBox = await recover_special_box(session, query_id)
                print(f"{Fore.BLUE+Style.BRIGHT}->Open box status: {openSpecialBox}")
                if openSpecialBox == "Success":
                    collectBoxes, collectAmount = await claim_special_box(session, query_id)
                    print(f"{Fore.GREEN+Style.BRIGHT}->Collect point: {collectBoxes} Claimed: {collectAmount}")
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
                                            info = claim_response['data']
                                            print(f"{Fore.GREEN+Style.BRIGHT}[Yes{i}] [{datetime.now().strftime('%H:%M:%S')}] Balance: {formatted_balance}  Remaining: {left_coins} Info: {info}")
                                        except KeyError:
                                            print(f"{Fore.RED+Style.BRIGHT}Get account info not found in the profile response")
                                    else:
                                        print(f"{Fore.RED+Style.BRIGHT}Failed to retrieve profile")
                                else:
                                    print(f"{Fore.RED+Style.BRIGHT}Claim failed")
                            else:
                                charge = await full_recovery(session, query_id)
                                print(f"{Fore.BLUE+Style.BRIGHT}Full recovery: {charge['data']}")
                                if charge['data'] == None:
                                    break 
                        except KeyError:
                            print(f"{Fore.RED+Style.BRIGHT}Game info not found in the game info response")
                    await asyncio.sleep(0.5)
                i += 1
            random_delay = random.randint(200, 300)
            countdown(random_delay)
asyncio.run(main())