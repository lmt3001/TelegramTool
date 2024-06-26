import subprocess
import time
import pygetwindow as gw

def run_command_and_move_window(title, command, x, y, width, height):
    # Run the command in a new cmd window
    subprocess.Popen(f'start "{title}" cmd /k "{command}"', shell=True)
    time.sleep(2)  # Wait a bit for the window to open
    
    # Find the window and move it
    windows = gw.getWindowsWithTitle(title)
    if windows:
        window = windows[0]
        window.moveTo(x, y)
        window.resizeTo(width, height)

def main():
    tools = [
        ("Blum tool", "cd /d BlumPython && python blumpyV2.py", 1306, 770, 620, 276),
        ("Yescoin tool", "cd /d YescoinPythonV2 && python yesV2.py", 537, 1, 939, 192),
        ("Memefi tool", "cd /d MemeFiPython && python MemeFiV4.py", 537, 770, 783, 276),
        ("Hamster tool", "cd /d HamsterPythonV2 && python hamsterKombatV3.py", 537, 186, 802, 276),
        ("Gemz tool", "cd /d GemzPython && python GemzV2.py", 537, 455, 761, 322),
        ("CEXIO tool", "cd /d CexIOPythonV1 && python cexio.py", 1462, 1, 480, 192),
        ("SEED tool", "cd /d SeedPython && python seedV2.py", 1325, 186, 601, 276),
        ("TimeFarm tool", "cd /d TimeFarmPythonV1 && python TimeFarmV3.py", 1284, 455, 642, 322),
        ("PixelTap tool", "cd /d PicxelTap && python PixelTap.py", 4, 3, 543, 255),
    ]

    while True:
        print("===============================")
        print("             MENU")
        print("===============================")
        print("1 : Run Blum tool")
        print("2 : Run Yescoin tool")
        print("3 : Run Memefi tool")
        print("4 : Run Hamster tool")
        print("5 : Run Gemz tool")
        print("6 : Run CexIO tool")
        print("7 : Run Seed tools")
        print("8 : Run TimeFarm tool")
        print("9 : Run PixelTap tool")
        print("a : Run All")
        print("0 : Exit")
        choice = input("Please choose an option (0-9 or a): ").strip()

        if choice == "0":
            break
        elif choice == "a":
            for tool in tools:
                run_command_and_move_window(*tool)
        elif choice in "123456789":
            index = int(choice) - 1
            run_command_and_move_window(*tools[index])
        else:
            print("Invalid choice. Please choose again.")
        input("Press Enter to continue...")

if __name__ == "__main__":
    main()
