import aiohttp
import asyncio
import time,random
from colorama import init, Fore, Style
from datetime import datetime

init(autoreset=True)

start_text = """
█▀ █▀▀ █▀▀ █▀▄
▄█ ██▄ ██▄ █▄▀
"""
# Reusable headers
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "content-type": "application/json",
    "origin": "https://cf.seeddao.org",
    "priority": "u=1, i",
    "referer": "https://cf.seeddao.org/"
}

async def get_profile(session, query_id):
    headers = {**HEADERS, "Telegram-Data": query_id}
    url = "https://elb.seeddao.org/api/v1/profile"
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.RED+Style.BRIGHT}Error fetching profile: {e}")
        return None

async def get_balance(session, query_id):
    headers = {**HEADERS, "Telegram-Data": query_id}
    url = "https://elb.seeddao.org/api/v1/profile/balance"
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"{Fore.RED+Style.BRIGHT}Error fetching balance: {e}")
        return None

def format_balance(balance_value):
    balance_str = str(balance_value)
    if len(balance_str) > 9:
        integer_part = balance_str[:-9]
        decimal_part = balance_str[-9:]
        formatted_balance = f"{integer_part}.{decimal_part}"
    else:
        formatted_balance = f"0.{balance_str.zfill(9)}"
    return "{:.6f}".format(float(formatted_balance))

async def claim(session, query_id):
    headers = {**HEADERS, "Telegram-Data": query_id}
    url = "https://elb.seeddao.org/api/v1/seed/claim"
    try:
        async with session.post(url, headers=headers, json={}) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            print(f"{Fore.GREEN+Style.BRIGHT}->Point Claim: Successful!")
    except aiohttp.ClientError as e:
        #print(f"{Fore.RED+Style.BRIGHT}Claim failed: {e}")
        print(f"{Fore.BLUE+Style.BRIGHT}->Point Claim: Not available...")

async def login_bonus(session, query_id):
    headers = {**HEADERS, "Telegram-Data": query_id}
    url = "https://elb.seeddao.org/api/v1/login-bonuses"
    try:
        async with session.post(url, headers=headers, json={}) as response:
            response.raise_for_status()  # Raise HTTPError for non-200 status codes
            print(f"{Fore.GREEN+Style.BRIGHT}->Login Bonus: Claim successful!")
    except aiohttp.ClientError as e:
        #print(f"{Fore.RED+Style.BRIGHT}Claim login bonus failed: {e}")
        print(f"{Fore.BLUE+Style.BRIGHT}->Login Bonus: Not available...")

# Countdown function
def countdown(secs):
    for i in range(secs, 0, -1):
        print(f"\r{Fore.MAGENTA+Style.BRIGHT}Sleeping for {i} seconds...", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 50, end="", flush=True)  # Clear the countdown message
    print("\n")  # Print a newline to ensure the prompt appears on a new line

# Read query_id from file
def read_query_ids(filename):
    try:
        with open(filename, "r") as file:
            return [line.strip() for line in file.readlines() if line.strip() and not line.startswith('#')]
    except IOError:
        print(f"{Fore.RED+Style.BRIGHT}Error reading file {filename}")
        return []

# Example usage
filename = "query_id.txt"
query_ids = read_query_ids(filename)

async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            #print(f"{Fore.MAGENTA+Style.BRIGHT} {start_text}")
            for query_id in query_ids:
                print(f"{Fore.YELLOW+Style.BRIGHT}[SEED] [{datetime.now().strftime('%H:%M:%S')}] {query_id[:20] + '...' if len(query_id) > 20 else query_id}")
                profile = await get_profile(session, query_id)
                balance = await get_balance(session, query_id)
                if profile and balance:
                    try:
                        print(f"{Fore.GREEN+Style.BRIGHT}User: {profile['data']['name']}  Balance: {format_balance(balance['data'])}")
                    except KeyError:
                        print(f"{Fore.RED+Style.BRIGHT}User name and balance not found in the profile response")
                else:
                    print(f"{Fore.RED+Style.BRIGHT}Failed to retrieve profile")
                await login_bonus(session, query_id)
                await claim(session, query_id)
            random_delay = random.randint(100, 900)
            countdown(random_delay)

asyncio.run(main())
