import pygetwindow as gw

def move_window_by_title(title, x, y, width, height):
    # Find the window
    windows = gw.getWindowsWithTitle(title)
    if windows:
        window = windows[0]
        window.moveTo(x, y)
        window.resizeTo(width, height)
    else:
        print(f"Window '{title}' not found.")

# List of window titles and their positions
windows_to_move = [
    ("Blum tool", 1306, 770, 620, 276),
    ("Yescoin tool", 537, 1, 939, 192),
    ("Memefi tool", 537, 770, 783, 276),
    ("Hamster tool", 537, 186, 802, 276),
    ("Gemz tool", 537, 455, 761, 322),
    ("CEXIO tool", 1462, 1, 480, 192),
    ("SEED tool", 1325, 186, 601, 276),
    ("TimeFarm tool", 1284, 455, 642, 322),
    ("PixelTap tool", 4, 3, 543, 255),
]

# Move each window if it exists
for title, x, y, width, height in windows_to_move:
    move_window_by_title(title, x, y, width, height)