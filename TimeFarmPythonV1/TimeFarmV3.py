import asyncio
import json
import random
import time
from datetime import datetime
import aiohttp
import urllib.parse
from colorama import init, Fore, Style
from datetime import datetime, timedelta, timezone
import ssl
# Initialize colorama for colored output
init(autoreset=True)
start_text = """
▀█▀ █ █▀▄▀█ █▀▀   █▀▀ ▄▀█ █▀█ █▀▄▀█
░█░ █ █░▀░█ ██▄   █▀░ █▀█ █▀▄ █░▀░█
"""
# Constants
URL_VALIDATE_INIT = "https://tg-bot-tap.laborx.io/api/v1/auth/validate-init"
URL_FINISH_FARMING = "https://tg-bot-tap.laborx.io/api/v1/farming/finish"
URL_START_FARMING = "https://tg-bot-tap.laborx.io/api/v1/farming/start"
URL_ACCOUNT_INFO = "https://tg-bot-tap.laborx.io/api/v1/farming/info"

HEADERS = {
    "accept": "*/*",
    "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "cache-control": "no-cache",
    "content-type": "text/plain;charset=UTF-8",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "Referer": "https://tg-tap-miniapp.laborx.io/",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}
ssl_context = ssl._create_unverified_context()
# Function to read query_ids from file
def read_query_ids(filename):
    try:
        with open(filename, "r") as file:
            return [line.strip() for line in file.readlines() if line.strip() and not line.startswith('#')]
    except IOError:
        print(f"{Fore.RED+Style.BRIGHT}Error reading file {filename}")
        return []

# Function to decode query_id and extract user data
def decode_query_id(query_id):
    try:
        decoded_query = urllib.parse.parse_qs(query_id)
        user_data = json.loads(decoded_query.get('user', [''])[0])
        return user_data
    except Exception as e:
        print(f"{Fore.RED+Style.BRIGHT}Error decoding query_id: {e}")
        return {}

# Function to login and retrieve access token
async def login(session, query_id):
    try:
        async with session.post(URL_VALIDATE_INIT, headers=HEADERS, data=query_id, ssl=ssl_context) as response:
            response.raise_for_status()
            json_response = await response.json()
            if 'errors' in json_response:
                return None
            else:
                return json_response.get('token')
    except aiohttp.ClientError as e:
        print(f"{Fore.RED+Style.BRIGHT}Error logging in: {e}")
        return None

# Function to claim points
async def claim_points(session, token):
    try:
        headers = {**HEADERS, "Authorization": f'Bearer {token}'}
        async with session.post(URL_FINISH_FARMING, headers=headers, ssl=ssl_context) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT} ->Point Claim: Not available")
        return None

# Function to start farming
async def start_farming(session, token):
    try:
        headers = {**HEADERS, "Authorization": f'Bearer {token}'}
        async with session.post(URL_START_FARMING, headers=headers, ssl=ssl_context) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT} ->Start Claim: Not available")
        return None

# Function to fetch account information
async def fetch_account_info(session, token):
    try:
        headers = {**HEADERS, "Authorization": f'Bearer {token}'}
        async with session.get(URL_ACCOUNT_INFO, headers=headers, ssl=ssl_context) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.RED+Style.BRIGHT}Error fetching account info: {e}")
        return None

# Function to format balance
def format_balance(balance):
    try:
        return '{:,.3f}'.format(float(balance))
    except ValueError:
        return "Invalid"

def calculate_remaining_time(start_time_str, farming_duration_sec):
    start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    end_time = start_time + timedelta(seconds=farming_duration_sec)
    current_time = datetime.now(timezone.utc)
    remaining_time = end_time - current_time
    is_ended = remaining_time.total_seconds() <= 0
    if is_ended:
        return "0", is_ended
    else:
        return str(remaining_time).split('.')[0], is_ended

# Function to perform countdown
def countdown(secs):
    for i in range(secs, 0, -1):
        print(f"\r{Fore.MAGENTA+Style.BRIGHT}Sleeping for {i} seconds...", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 50, end="", flush=True)  # Clear the countdown message
    print("\n")  # Print a newline to ensure the prompt appears on a new line

# Main asynchronous function
async def main():
    filename = "query_id.txt"
    query_ids = read_query_ids(filename)
    
    async with aiohttp.ClientSession() as session:
        while True:
            for query_id in query_ids:
                print(f"{Fore.YELLOW+Style.BRIGHT}[TIME FARM] [{datetime.now().strftime('%H:%M:%S')}] {query_id[:30] + '...' if len(query_id) > 30 else query_id}")
                user_data = decode_query_id(query_id)
                last_name = user_data.get('last_name')
                first_name = user_data.get('first_name')
                token = await login(session, query_id)
                if not token:
                    continue
                # Fetch account info
                account_info = await fetch_account_info(session, token)
                if account_info:
                    try:
                        total_balance = account_info.get('balance')
                        remain_time,is_ended = calculate_remaining_time(account_info.get('activeFarmingStartedAt'), account_info.get('farmingDurationInSec'))
                        formatted_balance = format_balance(total_balance)
                        print(f"{Fore.GREEN+Style.BRIGHT}User: {first_name} {last_name}  Balance: {formatted_balance} Remaining time: {remain_time}")
                        if is_ended:
                            print(f"{Fore.GREEN+Style.BRIGHT} ->Farming ended, Start Claiming...")
                            claim_result = await claim_points(session, token)
                            if claim_result:
                                try:
                                    claimed_balance = claim_result.get('balance')
                                    print(f"{Fore.GREEN+Style.BRIGHT}  ->Claimed: {format_balance(claimed_balance)}")
                                    start_result = await start_farming(session, token)
                                    if start_result:
                                        try:
                                            print(f"{Fore.GREEN+Style.BRIGHT}  ->Started farming")
                                        except KeyError:
                                            print(f"{Fore.RED+Style.BRIGHT}Unable to start farming")   
                                except KeyError:
                                    print(f"{Fore.RED+Style.BRIGHT}Claim result not available")                       
                        else:
                            print(f"{Fore.BLUE+Style.BRIGHT} ->Farming on-going")
                    except KeyError:
                        print(f"{Fore.RED+Style.BRIGHT}Unable to retrieve account info")
            random_delay = random.randint(500, 800)
            countdown(random_delay)

# Run the main asyncio loop
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW+Style.BRIGHT}Program terminated by user")
