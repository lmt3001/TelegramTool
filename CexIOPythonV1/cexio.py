import requests
from colorama import init, Fore, Style
import time
import random
from datetime import datetime
init(autoreset=True)

start_text = """
█▀▀ █▀▀ ▀▄▀ █ █▀█
█▄▄ ██▄ █░█ █ █▄█
"""
# Reusable headers
HEADERS = {
    "origin": "https://cexp.cex.io",
    "referer": "https://cexp.cex.io"
}

BASE_URL = "https://cexp.cex.io/api/"
DEV_AUTH_DATA = 906306292

def make_post_request(endpoint, payload):
    url = BASE_URL + endpoint
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()  # Raise HTTPError for non-200 status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        #print(f"{Fore.RED + Style.BRIGHT}Error during {endpoint}: {e}")
        return None

def get_user_info(query_id):
    payload = {
        "devAuthData": DEV_AUTH_DATA,
        "authData": query_id,
        "data": {},
        "platform": "android"
    }
    return make_post_request("getUserInfo", payload)

def claim_farm(query_id):
    payload = {
        "devAuthData": DEV_AUTH_DATA,
        "authData": query_id,
        "data": {},
        "platform": "android"
    }
    return make_post_request("claimFarm", payload)

def start_farm(query_id):
    payload = {
        "devAuthData": DEV_AUTH_DATA,
        "authData": query_id,
        "data": {},
        "platform": "android"
    }
    return make_post_request("startFarm", payload)

def claim_taps(query_id, taps):
    payload = {
        "authData": query_id,
        'data': {'taps': taps},
    }
    return make_post_request("claimTaps", payload)

def countdown(secs):
    for i in range(secs, 0, -1):
        print(f"\r{Fore.MAGENTA+Style.BRIGHT}Sleeping for {i} seconds...", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 50, end="", flush=True)  # Clear the countdown message
    print("\n")  # Print a newline to ensure the prompt appears on a new line

def read_query_id(filename):
    with open(filename, "r") as file:
        return file.read().splitlines()

def main():
    filename = "query_id.txt"
    query_ids = read_query_id(filename)

    while True:
        #print(start_text)
        for query_id in query_ids:
            print(f"{Fore.YELLOW + Style.BRIGHT}[CEXP] [{datetime.now().strftime('%H:%M:%S')}] {query_id[:20] + '...' if len(query_id) > 20 else query_id}...")
            
            user_info = get_user_info(query_id)
            if user_info:
                balance = user_info['data'].get('balance', 'N/A')
                first_name = user_info['data'].get('first_name', 'N/A')
                last_name = user_info['data'].get('last_name', 'N/A')
                print(f"{Fore.GREEN + Style.BRIGHT}Name: {first_name} {last_name}  Balance: {balance} CEXP")
            else:
                print(f"{Fore.RED + Style.BRIGHT}User information is not available.")

            farm_info = claim_farm(query_id)
            if farm_info:
                print(f"{Fore.GREEN + Style.BRIGHT}Status: {farm_info['status']}")
                print(f"{Fore.GREEN + Style.BRIGHT}Balance: {farm_info['data'].get('balance', 'N/A')}")
                print(f"{Fore.GREEN + Style.BRIGHT}Claimed Balance: {farm_info['data'].get('claimedBalance', 'N/A')}")
            else:
                print(f"{Fore.BLUE + Style.BRIGHT}->Claim Farm: Not available.")
                
            start_info = start_farm(query_id)
            if start_info:
                print(f"{Fore.GREEN + Style.BRIGHT}->Start Farm: {start_info['status']}")
            else:
                print(f"{Fore.BLUE + Style.BRIGHT}->Start Farm: Not available.")
                
            claim_info = claim_taps(query_id, 5)
            if claim_info:
                print(f"{Fore.GREEN + Style.BRIGHT}->Claim Taps: {claim_info['status']}")
                available_taps = claim_info['data'].get('availableTaps', 0)
                print(f"{Fore.GREEN + Style.BRIGHT}->Remain Taps: {available_taps}")
            else:
                print(f"{Fore.BLUE + Style.BRIGHT}->Claim Taps: Not available.")
        
        random_delay = random.randint(300, 500)
        countdown(random_delay)

if __name__ == "__main__":
    main()
