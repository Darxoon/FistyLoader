import os
from hashlib import sha1
from pathlib import Path
from sys import exit
from main import add_section_header, patch_game, resource_path
from colorama import Fore, Style, just_fix_windows_console
from pefile import PE
from readchar import readkey
from io import BufferedRandom, BytesIO
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
import yaml

ORIGINAL_STANDALONE_HASH = "4636bee492816efb6cfcf4e283c431d37db03a2f"
ORIGINAL_STEAM_HASH = "b95168f43a7e8e8a6f621754fc84322b20d4db52"

def get_game_exe(f: BufferedRandom, game_path: Path) -> (str, bytes, Path):
    game_bytes = f.read()
    game_hash = sha1(game_bytes).hexdigest()
    
    if game_hash == ORIGINAL_STEAM_HASH:
        return "steam_win", game_bytes, game_path
    elif game_hash == ORIGINAL_STANDALONE_HASH:
        return "win", game_bytes, game_path
    
    # Try reading backup path
    for filename in (f"{game_path.stem}_backup.exe", "World of Goo 2_backup.exe", "WorldOfGoo2_backup.exe"):
        backup_path = game_path.parent / filename
        
        if backup_path.exists():
            with open(backup_path, 'rb') as f2:
                backup_bytes = f2.read()
            
            backup_hash = sha1(backup_bytes).hexdigest()
            if backup_hash == ORIGINAL_STEAM_HASH:
                return "steam_win", backup_bytes, backup_path
            elif backup_hash == ORIGINAL_STANDALONE_HASH:
                return "win", backup_bytes, backup_path
    
    # Couldn't find original game so exit
    print(f"\n{Fore.RED}Invalid game exe. Make sure you have are on the newest Windows Steam version of World of Goo 2.")
    print(f"If you have installed FistyLoader before, please restore it to the original version first.{Fore.RESET}")
    exit(1)

def install():
    # Enables color codes in Windows command prompt
    if os.name == 'nt':
        just_fix_windows_console()
    
    # Get user input
    try:
        print("Welcome to the FistyLoader installer! (version 1.1.1)")
        print("Make sure you are using the latest Windows release (Steam or DRM-free) of World of Goo 2.\n")
        
        print(f"If you are using the {Style.BRIGHT}Steam{Style.NORMAL} version: because Steam prevents copies of the game outside your Steam library from running")
        print("properly, you need to use the original WorldOfGoo2.exe in your Steam library for this.\n")
        
        print(f"If you are using the {Style.BRIGHT}DRM-free{Style.NORMAL} version: because its location (C:\\Program Files\\World of Goo 2) requires administrator")
        print("access, you need to copy the game to a new location first and use the new copy in the following step.\n")
        
        print("If that's done, drag and drop the original World of Goo 2.exe file to below.")
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
    game_path = Path(game_path)
    with open(game_path, 'rb+') as f:
        # Read exe
        try:
            ver, game_bytes, real_game_path = get_game_exe(f, game_path)
            
            # load static resources
            custom_code_path = resource_path(f'ver/{ver}/build/custom_code.bin')
            custom_code_symbols_path = resource_path(f'ver/{ver}/build/custom_code_symbols.o')
            hooks_path = resource_path(f'ver/{ver}/hooks.yaml')

            with open(custom_code_path, 'rb') as f2:
                section_content = f2.read()
            with open(custom_code_symbols_path, 'rb') as f2:
                symbols_bin = f2.read()
            with open(hooks_path, 'r') as f2:
                hooks_str = f2.read()

            symbols = ELFFile(BytesIO(symbols_bin))
            symtab = symbols.get_section_by_name(".symtab")
            assert isinstance(symtab, SymbolTableSection), ".symtab is not a Symbol Table"

            hooks = yaml.safe_load(hooks_str)['hooks']
            
            # load game binary
            with open(game_path.parent / f'{game_path.stem}_backup.exe', 'wb') as f2:
                f2.write(game_bytes)
            
            print(f'Reading {real_game_path.name}...')
            pe = PE(real_game_path)
            add_section_header(pe, len(section_content))
        except KeyboardInterrupt:
            print("\nExiting installer.")
            exit()
        
        # Write/modify exe
        try:
            modified = pe.write()
            f.seek(0)
            f.write(modified)
            
            patch_game(f, ver, bytes(modified), section_content, symtab, hooks)
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
