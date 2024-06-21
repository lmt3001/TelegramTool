import pygetwindow as gw

def print_windows_info():
    windows = gw.getAllTitles()
    for title in windows:
        if title:
            window = gw.getWindowsWithTitle(title)[0]
            print(f"Title: {title}")
            #print(f"Position: {window.left}, {window.top}")
            #print(f"Size: {window.width} x {window.height}")
            print(f"{window.left}, {window.top}, {window.width}, {window.height}")
            
            print()

if __name__ == "__main__":
    print_windows_info()
