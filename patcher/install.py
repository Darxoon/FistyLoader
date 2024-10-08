import os
from hashlib import sha1
from pathlib import Path
from sys import exit
from main import add_section_header, patch_game, resource_path
from colorama import Fore, just_fix_windows_console
from pefile import PE
from readchar import readkey

def install():
    # Enables color codes in Windows command prompt
    if os.name == 'nt':
        just_fix_windows_console()
    
    custom_code_path = resource_path('custom_code.bin')
    
    with open(custom_code_path, 'rb') as f:
        section_content = f.read()
    
    # Get user input
    try:
        print("Welcome to the FistyLoader installer!\n")
        print("Make sure you are not modifying your original World of Goo 2 installation.")
        print("Copy the game to a new location if you haven't already.\n")
        
        print("If that's done, drag and drop the new World of Goo 2.exe to below.")
        game_path = input("World of Goo 2 exe path: ")
        
        if game_path.startswith('"') and game_path.endswith('"'):
            game_path = game_path[1:-1]
        elif game_path.startswith("'") and game_path.endswith("'"):
            game_path = game_path[1:-1]
        elif game_path.startswith("& '") and game_path.endswith("'"):
            game_path = game_path[3:-1]
        elif game_path.startswith('& "') and game_path.endswith('& "'):
            game_path = game_path[3:-1]
        
        if not Path(game_path).is_file():
            print(f"\nCould not find file '{game_path}'.")
            exit(1)
    except KeyboardInterrupt:
        print("\nExiting installer.")
        exit()
    
    # Handle exe file
    with open(game_path, 'rb+') as f:
        # Read exe
        try:
            game_bytes = f.read()
            game_hash = sha1(game_bytes).hexdigest()
            
            if game_hash != "715253535eaa08d7b1e643c7dfaabf1a478a6cc4":
                print(f"\n{Fore.RED}Invalid game exe. Make sure you have updated World of Goo 2 to the newest version.{Fore.RESET}")
                exit(1)
            
            print('Reading World of Goo 2.exe...')
            pe = PE(game_path)
        except KeyboardInterrupt:
            print("\nExiting installer.")
            exit()
        
        # Write/modify exe
        try:
            add_section_header(pe, len(section_content))
            modified = pe.write()
            f.seek(0)
            f.write(modified)
            
            patch_game(f, bytes(modified), section_content)
        except KeyboardInterrupt:
            print("Restoring original...")
            
            f.seek(0)
            f.write(game_bytes)
            
            print("Exiting installer.")
            exit()
        
        print("Done. Press any key to exit...")
        readkey()
        

if __name__ == '__main__':
    install()
