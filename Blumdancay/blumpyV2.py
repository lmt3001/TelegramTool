import aiohttp
import asyncio
import json,random
import time
from colorama import init, Fore, Style
from datetime import datetime, timezone
init(autoreset=True)

BASE_URL = "https://telegram.blum.codes"
API_URL = "https://gateway.blum.codes"
GAME_URL = "https://game-domain.blum.codes"

COMMON_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "origin": BASE_URL,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
}

async def get_new_token(query_id):
    headers = COMMON_HEADERS.copy()
    headers["content-type"] = "application/json"
    data = json.dumps({"query": query_id})
    url = f"{API_URL}/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP"
    async with aiohttp.ClientSession() as session:
        for attempt in range(3):
            print(f"\r{Fore.YELLOW+Style.BRIGHT}Get token....",end="", flush=True)
            try:
                async with session.post(url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    if 'errors' in result:
                        print(f"\r{Fore.RED + Style.BRIGHT}Get token error: {result['errors'][0]['message']}")
                        return None
                    print(f"\r{Fore.GREEN+Style.BRIGHT}Get token Success")
                    return result['token']['refresh']
            except aiohttp.ClientError as e:
                print(f"\r{Fore.RED+Style.BRIGHT}Get token Fail retry {attempt + 1}: {e}")
        print(f"\r{Fore.RED+Style.BRIGHT}Get token fail after 3 times")
        return None

async def getUserInfo(session, token):
    headers = COMMON_HEADERS.copy()
    headers['Authorization'] = f'Bearer {token}'
    url = f'{API_URL}/v1/user/me'
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT} ->Progress error: {e}")
        return None
    
        
async def getBalance(session, token):
    headers = COMMON_HEADERS.copy()
    headers['Authorization'] = f'Bearer {token}'
    url = f'{GAME_URL}/api/v1/user/balance'
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT} ->Progress error: {e}")
        return None
        
async def claimBalance(session, token):
    headers = COMMON_HEADERS.copy()
    headers['Authorization'] = f'Bearer {token}'
    url = f'{GAME_URL}/api/v1/farming/claim'
    try:
        async with session.post(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT}->Claim farm: Not available")
        return None
async def startFarming(session, token):
    headers = COMMON_HEADERS.copy()
    headers['Authorization'] = f'Bearer {token}'
    url = f'{GAME_URL}/api/v1/farming/start'
    try:
        async with session.post(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT}->Start Farm: Not available")
        return None
        
async def getBalanceFriend(session, token):
    headers = COMMON_HEADERS.copy()
    headers['Authorization'] = f'Bearer {token}'
    url = f'{API_URL}/v1/friends/balance'
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT} ->Progress error: {e}")
        return None
    
async def claimBalanceFriend(session, token):
    headers = COMMON_HEADERS.copy()
    headers['Authorization'] = f'Bearer {token}'
    url = f'{GAME_URL}/api/v1/farming/claim-friends'
    try:
        async with session.post(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT}->Claim Friend: Not available")
        return None



def convert_time(end_time_ms):
    end_time = datetime.fromtimestamp(end_time_ms / 1000, tz=timezone.utc)
    current_time = datetime.now(timezone.utc)
    remaining_time = end_time - current_time
    # If remaining time is negative, set it to zero
    if remaining_time.total_seconds() < 0:
        remaining_time = datetime.utcfromtimestamp(0) - datetime.utcfromtimestamp(0)
    total_seconds = max(remaining_time.total_seconds(), 0)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    remaining_time_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    return remaining_time_str

def format_balance(balance):
    try:
        integer_balance = int(float(balance))
        formatted_balance = '{:,}'.format(integer_balance)
        return formatted_balance
    except ValueError:
        return "Invalid"
    
def countdown(secs):
    for i in range(secs, 0, -1):
        print(f"\r{Fore.MAGENTA+Style.BRIGHT}Sleeping for {i} seconds...", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 50, end="", flush=True)  # Clear the countdown message
    print("\n")  # Print a newline to ensure the prompt appears on a new line
    
def read_query_ids(filename):
    try:
        with open(filename, "r") as file:
            return [line.strip() for line in file.readlines() if line.strip() and not line.startswith('#')]
    except IOError:
        print(f"{Fore.RED+Style.BRIGHT}Error reading file {filename}")
        return []
    
    
async def main():
    filename = "query.txt"
    query_ids = read_query_ids(filename)
    
    async with aiohttp.ClientSession() as session:
        while True:
            for query_id in query_ids:
                print(f"{Fore.YELLOW+Style.BRIGHT}Token: {query_id[:30] + '...' if len(query_id) > 30 else query_id}...")
                token = await get_new_token(query_id)
                if token:
                    user_info = await getUserInfo(session,token)
                    balance = await getBalance(session,token)
                    if user_info and balance:
                        user_name = user_info.get('username','N/A')
                        balance_info = balance.get('availableBalance','N/A')
                        playPass = balance.get('playPasses','N/A')
                        endFarmTime = balance['farming']['endTime']
                        startFarmingTime = balance['farming']['startTime']
                        currentFarmBalance = balance['farming']['balance']
                        remain_time_str = convert_time(endFarmTime)
                        print(f"{Fore.GREEN+Style.BRIGHT}User: {user_name}  Balance: {format_balance(balance_info)}  Game ticket: {playPass} ")
                        print(f"{Fore.GREEN+Style.BRIGHT}->Farm Balance: {format_balance(currentFarmBalance)} Remain: {remain_time_str}")
                        if remain_time_str == '00:00:00':
                            claimInfo = await claimBalance(session,token)
                            if claimInfo:
                                print(f"{Fore.GREEN+Style.BRIGHT}->Claim Success")
                                startFarmInfo = await startFarming(session,token)
                                if startFarmInfo:
                                    print(f"{Fore.GREEN+Style.BRIGHT}->Start Farm Success")
                    balance_friend = await getBalanceFriend(session,token)
                    if balance_friend:
                        balance_friend_info = balance_friend['canClaim']
                        print(f"{Fore.BLUE+Style.BRIGHT}->Claim Friend: {balance_friend_info}")
                        if balance_friend_info:
                            claimFriendInfo = await claimBalanceFriend(session,token)
                            if claimFriendInfo:
                                print(f"{Fore.BLUE+Style.BRIGHT}->Claim Friend Success")                 
                    else:
                        print(f"{Fore.RED+Style.BRIGHT}User info or balance not found")
            random_delay = random.randint(500, 1000)
            countdown(random_delay)


asyncio.run(main())

