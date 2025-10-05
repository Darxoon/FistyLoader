import os
from hashlib import sha1
from pathlib import Path
from sys import exit
from main import add_section_header, patch_game, resource_path
from colorama import Fore, just_fix_windows_console
from pefile import PE
from readchar import readkey
from io import BufferedRandom, BytesIO
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
import yaml

def install():
    # Enables color codes in Windows command prompt
    if os.name == 'nt':
        just_fix_windows_console()
    
    custom_code_path = resource_path('custom_code.bin')
    custom_code_symbols_path = resource_path('custom_code_symbols.o')
    hooks_path = resource_path('data/hooks.yaml')
    
    with open(custom_code_path, 'rb') as f:
        section_content = f.read()
    with open(custom_code_symbols_path, 'rb') as f:
        symbols_bin = f.read()
    with open(hooks_path, 'r') as f:
        hooks_str = f.read()
    
    symbols = ELFFile(BytesIO(symbols_bin))
    symtab = symbols.get_section_by_name(".symtab")
    assert isinstance(symtab, SymbolTableSection)
    
    hooks = yaml.safe_load(hooks_str)['hooks']
    
    # Get user input
    try:
        print("Welcome to the FistyLoader installer! (version 1.1)\n")
        print("Make sure you are using the latest Windows Steam release of World of Goo 2.")
        print("If you have installed FistyLoader in the past, please restore the WorldOfGoo2.exe")
        print("back to how it was originally.\n")
        
        print("Because Steam forces all copies of the game to run the .exe in your Steam library,")
        print("you need to use the original WorldOfGoo2.exe for this.\n")
        
        print("If that's done, drag and drop the original WorldOfGoo2.exe to below.")
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
            game_bytes, game_path = get_game_exe(f, game_path)
            
            with open(game_path.parent / 'WorldOfGoo2_backup.exe', 'wb') as f2:
                f2.write(game_bytes)
            
            print('Reading WorldOfGoo2.exe...')
            pe = PE(game_path)
            add_section_header(pe, len(section_content))
        except KeyboardInterrupt:
            print("\nExiting installer.")
            exit()
        
        # Write/modify exe
        try:
            modified = pe.write()
            f.seek(0)
            f.write(modified)
            
            patch_game(f, bytes(modified), section_content, symtab, hooks)
        except KeyboardInterrupt:
            print("Restoring original...")
            
            f.seek(0)
            f.write(game_bytes)
            
            print("Exiting installer.")
            exit()
        
        print("Done. Press any key to exit...")
        readkey()

ORIGINAL_GAME_HASH = "b95168f43a7e8e8a6f621754fc84322b20d4db52"

def get_game_exe(f: BufferedRandom, game_path: Path) -> (bytes, Path):
    game_bytes = f.read()
    game_hash = sha1(game_bytes).hexdigest()
    
    if game_hash == ORIGINAL_GAME_HASH:
        return game_bytes, game_path
    
    # Try reading backup path
    backup_path = game_path.parent / "WorldOfGoo2_backup.exe"
    if backup_path.exists():
        with open(backup_path, 'rb') as f2:
            backup_bytes = f2.read()
        
        backup_hash = sha1(backup_bytes).hexdigest()
        if backup_hash == ORIGINAL_GAME_HASH:
            return backup_bytes, backup_path
    
    # Couldn't find original game so exit
    print(f"\n{Fore.RED}Invalid game exe. Make sure you have are on the newest Windows Steam version of World of Goo 2.")
    print(f"If you have installed FistyLoader before, please restore it to the original version first.{Fore.RESET}")
    exit(1)

if __name__ == '__main__':
    install()
