import aiohttp
import asyncio
import random
import base64
import os
import datetime
import re
import urllib.parse
import time
from colorama import init, Fore, Style
import random
init(autoreset=True)

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
    'Content-Type': 'application/json',
    'Origin': 'https://ff.notgemz.gemz.fun',
    'Referer': 'https://ff.notgemz.gemz.fun/',
    'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'Sec-Ch-Ua-Mobile': '?1',
    'Sec-Ch-Ua-Platform': '"Android"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
}

def taoSid():
    return base64.b64encode(os.urandom(6)).decode('utf-8')[:9]

def read_query_id(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        return [line.strip() for line in lines if line.strip() and not line.startswith('#')]
def convert_timestamp(timestamp_ms):
    timestamp_sec = timestamp_ms / 1000
    dt_obj = datetime.datetime.fromtimestamp(timestamp_sec)
    formatted_time = dt_obj.strftime('%H:%M:%S')
    return formatted_time
def check_energy(energy):
    if energy > 30:
        return energy 
    else: 
        return None
def format_balance(balance):
    return '{:,.0f}'.format(balance)
def convert_query_id(query_id):
    query_params = urllib.parse.parse_qs(query_id)
    user_info = query_params.get('user', [None])[0]
    if user_info:
        user_data = urllib.parse.unquote(user_info)
        user_id_match = re.search(r'"id":(\d+)', user_data)
        user_id = user_id_match.group(1) if user_id_match else None
        return user_id
    else:
        print ('Cant convert query_id')

def countdown(secs):
    for i in range(secs, 0, -1):
        print(f"\r{Fore.MAGENTA+Style.BRIGHT}Sleeping for {i} seconds...", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 50, end="", flush=True)  # Clear the countdown message
    print("\n")  # Print a newline to ensure the prompt appears on a new line

async def get_user_info(session,query_id,user_id):
    url = "https://gemzcoin.us-east-1.replicant.gc-internal.net/gemzcoin/v2.18.0/loginOrCreate"
    payload1 = {
        'sid': taoSid(),
        'id': user_id,
        'auth': query_id.replace('&', '\n')
    }
    try:      
        async with session.post(url=url, json=payload1, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            if data['data'] is not None:
                username = data['data']['state'].get('username', 'N/A')
                balance = data['data']['state'].get('balance', 'N/A')
                energy = data['data']['state'].get('energy', 'N/A')
                rev = data['data'].get('rev', 'N/A')
                token = data['data'].get('token', 'N/A')
                return username, balance, energy, rev, token
            else:
                print('Data is None')
                return None, None, None, None, None
    except Exception as e:
        print(f"{Fore.RED+Style.BRIGHT}Error fetching profile: {e}")
        return None, None, None    

async def claim(session,user_id,rev,token):
    url = "https://gemzcoin.us-east-1.replicant.gc-internal.net/gemzcoin/v2.18.0/replicate"
    queue_length = random.randint(20,80)
    queue = [{"fn": "tap", "async": False, "meta": {"now": int(time.time() * 1000)}} for _ in range(queue_length)]
    payload2 = {
        "abTestsDynamicConfig": {
            "0002_invite_drawer": {"active": True, "rollOut": 1},
            "0003_invite_url": {"active": True, "rollOut": 1},
            "0004_invite_copy": {"active": True, "rollOut": 1},
            "0010_localization": {"active": True, "rollOut": 1},
            "0006_daily_reward": {"active": False, "rollOut": 0},
            "0011_earn_page_buttons": {"active": True, "rollOut": 1},
            "0005_invite_message": {"active": True, "rollOut": 1},
            "0008_retention_with_points": {"active": True, "rollOut": 1},
            "0018_earn_page_button_2_friends": {"active": True, "rollOut": 1},
            "0012_rewards_summary": {"active": True, "rollOut": 1},
            "0022_localization": {"active": True, "rollOut": 1},
            "0023_earn_page_button_connect_wallet": {"active": True, "rollOut": 1},
            "0016_throttling": {"active": True, "rollOut": 1},
            "0024_rewards_summary2": {"active": True, "rollOut": 1},
            "0016_throttling_v2": {"active": True, "rollOut": 1},
            "0014_gift_airdrop": {"active": True, "rollOut": 1}
        },
        "queue": queue,
        "rev": rev,
        "requestedProfileIds": [],
        "consistentFetchIds": [],
        "sid": taoSid(),
        "clientRandomSeed": 0,
        "crqid": taoSid(),
        "id": user_id,
        "auth": token
    }
    try:      
        async with session.post(url=url, json=payload2, headers=headers) as response:
            response.raise_for_status() 
            data = await response.json()
            if data['data'] is not None:
                timeUpdate = data.get('t','N/A')
                return timeUpdate
            else:
                print('Claim response data is None')
                return None
    except aiohttp.ClientError as e:
        print(f"{Fore.RED+Style.BRIGHT}Error claiming: {e}")
    


filename = "query.txt"
query_ids = read_query_id(filename)
async def main():
    async with aiohttp.ClientSession() as session:
        i = 1
        while True:
            for current_query_index, query_id in enumerate(query_ids):
                if current_query_index == 0 and i != 1:
                    i = 1
                print(f"{Fore.YELLOW + Style.BRIGHT}Token: {query_id[:30] + '...' if len(query_id) > 30 else query_id}...")
                user_id = convert_query_id(query_id)
                while True:
                    try:
                        userName, Balance, Energy, rev, token = await get_user_info(session, query_id, user_id)
                        if userName is not None:
                            timeUpdate = await claim(session, user_id, rev, token)
                            if timeUpdate is not None:
                                print(f"{Fore.GREEN + Style.BRIGHT}[GEMZ{i}] [{convert_timestamp(timeUpdate)}] Username: {userName} Balance: {format_balance(Balance)} Energy: {format_balance(Energy)}")
                            if Energy < 50:
                                break
                        else:
                            print(f"{Fore.RED+Style.BRIGHT}Username or Balance or Energy is None")
                        #await asyncio.sleep(0.5)
                    except KeyError:
                        print(f"{Fore.RED+Style.BRIGHT}Game info not found in the game info response")
                        break
                i += 1
            random_delay = random.randint(50, 120)
            countdown(random_delay)
    
asyncio.run(main())