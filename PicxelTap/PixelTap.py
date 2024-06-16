import asyncio
import json
import random
import time
from datetime import datetime
import aiohttp
import urllib.parse
from datetime import datetime, timezone
from colorama import init, Fore, Style
init(autoreset=True)

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "Referer": "https://sexyzbot.pxlvrs.io/",
    "Secret": "717c5a4e9bcbb84de6804c6f768b8a7ee79a90441bb7d620e6b32e3a5c4e914f"
    }

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
async def getUsers(session, query_id):
    url = "https://api-clicker.pixelverse.xyz/api/users"
    headers = {**HEADERS, "Initdata": query_id}
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT} ->User error: {e}")
        return None
    
async def getProgress(session, query_id):
    url = "https://api-clicker.pixelverse.xyz/api/mining/progress"
    headers = {**HEADERS, "Initdata": query_id}
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT} ->Progress error: {e}")
        return None

async def claim(session, query_id):
    url = "https://api-clicker.pixelverse.xyz/api/mining/claim"
    headers = {**HEADERS, "Initdata": query_id}
    try:
        async with session.post(url, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.BLUE+Style.BRIGHT} ->Progress error: {e}")
        return None
def format_balance(balance):
    try:
        integer_balance = int(float(balance))
        formatted_balance = '{:,}'.format(integer_balance)
        return formatted_balance
    except ValueError:
        return "Invalid"

# Function to perform countdown
def countdown(secs):
    for i in range(secs, 0, -1):
        print(f"\r{Fore.MAGENTA+Style.BRIGHT}Sleeping for {i} seconds...", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 50, end="", flush=True)  # Clear the countdown message
    print("\n")  # Print a newline to ensure the prompt appears on a new line
def get_remaining_time(future_time_str):
    future_time = datetime.fromisoformat(future_time_str.rstrip('Z')).replace(tzinfo=timezone.utc)
    current_time = datetime.now(timezone.utc)
    remaining_time = future_time - current_time
    total_seconds = remaining_time.total_seconds()
    if total_seconds < 0:
        total_seconds = 0
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    remaining_time_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    return remaining_time_str
async def main():
    filename = "query_id.txt"
    query_ids = read_query_ids(filename)
    
    async with aiohttp.ClientSession() as session:
        while True:
            for query_id in query_ids:
                print(f"{Fore.YELLOW+Style.BRIGHT}[PixelTap] [{datetime.now().strftime('%H:%M:%S')}] {query_id[:30] + '...' if len(query_id) > 30 else query_id}")
                user_data = await getUsers(session,query_id)
                username = user_data.get('username','N/A')
                balance = user_data.get('clicksCount','N/A')
                print(f"{Fore.GREEN+Style.BRIGHT}User: {username} Balance: {format_balance(balance)}")
                
                progress = await getProgress(session,query_id)
                if progress:
                    try:
                        maxAvailable = progress.get('maxAvailable','N/A')
                        currentlyAvailable = progress.get('currentlyAvailable','N/A')
                        nextFullRestorationDate = progress.get('nextFullRestorationDate','N/A')
                        remaining_time = get_remaining_time(nextFullRestorationDate)
                        print(f"{Fore.BLUE+Style.BRIGHT}->Earn Progress: {format_balance(currentlyAvailable)}/{format_balance(maxAvailable)} Remaining time: {remaining_time}")
                        #if currentlyAvailable > maxAvailable/2:
                        if currentlyAvailable > 10000:
                            claim_info = await claim(session,query_id)
                            if claim_info:
                                claimedAmount=claim_info.get('claimedAmount','N/A')
                                print(f"{Fore.GREEN+Style.BRIGHT}->Claim success: {format_balance(claimedAmount)}")
                            else:
                                print(f"{Fore.RED+Style.BRIGHT}->Claim failed")
                        else:
                            print(f"{Fore.BLUE+Style.BRIGHT}->Not enough point to claim")    
                    except KeyError:
                        print(f"{Fore.RED+Style.BRIGHT}Unable to get progress")
            random_delay = random.randint(500, 1000)
            countdown(random_delay)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW+Style.BRIGHT}Program terminated by user")
