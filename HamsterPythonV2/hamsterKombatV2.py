import aiohttp
import asyncio
import time 
from colorama import init, Fore, Style
import random
init(autoreset=True)

start_text = """
█░█ ▄▀█ █▀▄▀█ █▀ ▀█▀ █▀▀ █▀█
█▀█ █▀█ █░▀░█ ▄█ ░█░ ██▄ █▀▄
"""
today_code = "HAMSTER"


HEADERS = {
    'Content-Type': 'application/json'
}

BASE_URL = 'https://api.hamsterkombat.io'
async def Claim_point(session, authorization):
    headers = {**HEADERS, 'Authorization': f'Bearer {authorization}'}
    payload = {
        'count': random.randint(1,3),
        'availableTaps': 1500,
        'timestamp': int(time.time() * 1000)
    }
    url = 'https://api.hamsterkombat.io/clicker/tap'
    try:
        async with session.post(url, json=payload, headers=headers) as response:
            response.raise_for_status() 
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT}Claim point ERR: {e}...")
    return None

# async def getBalance(session, authorization):
#     headers = {**HEADERS, 'Authorization': f'Bearer {authorization}'}
#     url = 'https://api.hamsterkombat.io/clicker/sync'
#     try:
#         async with session.post(url, headers=headers) as response:
#             return await response.json()
#     except aiohttp.ClientError as e:
#         print(f"{Fore.BLUE+Style.BRIGHT}Claim point ERR: {e}...")
#     return None
#s
async def claimDailyCipher(session, authorization):
    try:
        payload = {
            'cipher' : f'{today_code}'
        }
        headers = {**HEADERS, 'Authorization': f'Bearer {authorization}'}
        async with session.post(f'{BASE_URL}/clicker/claim-daily-cipher', json=payload, headers=headers) as response:
            if response.status == 200:
                print('Finished claim cipher')
            if response.status == 400:
                print(f"{Fore.GREEN+Style.BRIGHT} Today already claim cipher {today_code}")
            else:
                print(f'Cant claim cipher. Status code: {response.status}')
    except Exception as e:
        print('Error:', e)
    return None

async def check_tasks(session, authorization):
    try:
        headers = {**HEADERS, 'Authorization': f'Bearer {authorization}'}
        async with session.post(f'{BASE_URL}/clicker/list-tasks', headers=headers) as response:
            if response.status == 200:
                tasks = (await response.json())['tasks']
                for task in tasks:
                    if task['id'] == 'streak_days' and not task['isCompleted']:
                        await session.post(f'{BASE_URL}/clicker/check-task', json={'taskId': 'streak_days'}, headers=headers)
                        print(f'Checked daily task for token {authorization}')
                async with session.post(f'{BASE_URL}/clicker/boosts-for-buy', headers=headers) as boosts_response:
                    if boosts_response.status == 200:
                        boosts = (await boosts_response.json())['boostsForBuy']
                        boost_full_available_taps = next((boost for boost in boosts if boost['id'] == 'BoostFullAvailableTaps'), None)
                        if boost_full_available_taps and boost_full_available_taps['cooldownSeconds'] == 0:
                            buy_boost_payload = {
                                'boostId': 'BoostFullAvailableTaps',
                                'timestamp': int(time.time())
                            }
                            await session.post(f'{BASE_URL}/clicker/buy-boost', json=buy_boost_payload, headers=headers)
                            print(f'Claim Boost Full Energy for token {authorization}')
                    else:
                        print(f'Cant boosts. Status code: {boosts_response.status}')
            else:
                print(f'Cant get task. Status code: {response.status}')
    except Exception as e:
        print('Error:', e)

import time
async def buy_upgrades(session, token, money):
    headers = {**HEADERS, 'Authorization': f'Bearer {token}'}
    try:
        async with session.post(f'{BASE_URL}/clicker/upgrades-for-buy', headers=headers) as response:
            upgrades = (await response.json())['upgradesForBuy']
            for upgrade in upgrades:
                cooldown_seconds = upgrade.get('cooldownSeconds')
                if cooldown_seconds is not None and cooldown_seconds > 0:
                    print(f"{Fore.MAGENTA+Style.BRIGHT} Skipping upgrade {upgrade['id']:>30} || Cooldown {cooldown_seconds} seconds")
                    continue
                if upgrade['isAvailable'] and not upgrade['isExpired'] and upgrade['price'] < money and not upgrade['profitPerHour'] == 0:
                    try:
                        buy_upgrade_payload = {
                            'upgradeId': upgrade['id'],
                            'timestamp': int(time.time())
                        }
                        async with session.post(f'{BASE_URL}/clicker/buy-upgrade', json=buy_upgrade_payload, headers=headers) as purchase_response:
                            if purchase_response.status == 200:
                                print(f"{Fore.GREEN+Style.BRIGHT} Upgraded {upgrade['id']:>30} || Price: {format_balance(upgrade['price'])}")
                            # if purchase_response.status == 400:
                            #     print(f"{Fore.MAGENTA+Style.BRIGHT} Skipping upgrade {upgrade['id']:>30} || Price: {format_balance(upgrade['price'])} || Not enough balance: {format_balance(current_balance)}")
                            else:
                                print(f"{Fore.RED+Style.BRIGHT} Failed to upgrade {upgrade['id']} - Status code: {purchase_response.status}")
                    except Exception as error:
                        print(f"Failed to buy upgrade {upgrade['id']}. Error: {error}")
    except Exception as error:
        print(f"{Fore.RED+Style.BRIGHT} Fail upgrade, go next token...")
        return False


def countdown(secs):
    for i in range(secs, 0, -1):
        print(f"\r{Fore.MAGENTA+Style.BRIGHT}Sleeping for {i} seconds...", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 50, end="", flush=True)  # Clear the countdown message

def format_balance(balance):
    return '{:,.0f}'.format(balance)
def read_query_id(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        return [line.strip() for line in lines if line.strip() and not line.startswith('#')]

def split_query_id(string):
    return string.split('|')
    

filename = "token.txt"
tokens = read_query_id(filename)

async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            print(start_text)
            for token in tokens:
                money = int(split_query_id(token)[0])
                query_id= split_query_id(token)[1]
                print(f"{Fore.YELLOW+Style.BRIGHT}Claiming for token: {query_id[:30] + '...' if len(query_id) > 30 else query_id}...")
                print(f"{Fore.YELLOW+Style.BRIGHT}Upgarde money: {format_balance(money)}...")
                print(f"{Fore.YELLOW+Style.BRIGHT}Morse Code Today: {today_code}...")
                await buy_upgrades(session, query_id, money)
                await check_tasks(session, query_id)
                await claimDailyCipher(session, query_id)
                while True:
                    claim_point = await Claim_point(session, query_id)
                    if claim_point:
                        try:
                            id = claim_point['clickerUser']['id']
                            total_balance = claim_point['clickerUser']['balanceCoins']
                            availableTaps = claim_point['clickerUser']['availableTaps']
                            level = claim_point['clickerUser']['level']
                            print(f"{Fore.GREEN+Style.BRIGHT} ID: {id}  Balance: {format_balance(total_balance)}  Available tap: {format_balance(availableTaps)} Level {level}")
                            if availableTaps < 10:
                                break
                        except KeyError:
                            print(f"{Fore.RED+Style.BRIGHT}Cant get account info") 
            random_delay = random.randint(100, 200)
            countdown(random_delay)
asyncio.run(main())