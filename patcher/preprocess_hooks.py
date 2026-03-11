from os import path
from sys import argv
from pathlib import Path

import yaml

from hooks import Hook

def generate_asm_definitions(ver_path: Path, hooks: list[Hook]):
    result = ""
    
    for hook in hooks:
        result += f"extern {hook.symbol_name}_return\n"
    
    with open(ver_path / 'build/hook_returns.inc.s', 'w') as f:
        f.write(result)

def generate_linker_script(ver: str, ver_path: Path, hooks: list[Hook]):
    with open(ver_path / 'game_symbols.ld', 'r') as f:
        game_symbols = f.read()
    with open("template.ld", 'r') as f:
        ld_template = f.read()
    
    match ver:
        case "steam_win":
            ld_template = ld_template.replace("FISTY_BASE_OFFSET", "0x24FC000")
        case "win":
            ld_template = ld_template.replace("FISTY_BASE_OFFSET", "0x24F3000")
    
    result = "/* game symbols */\n" + game_symbols + "\n/* hook returns */\n"
    
    for hook in hooks:
        result += f"{hook.symbol_name}_return = {hex(hook.target_addr + hook.byte_length)};\n"
    
    result += "\n/* template.ld */\n" + ld_template
    
    with open(ver_path / 'build/main.ld', 'w') as f:
        f.write(result)

def preprocess_hooks():
    if len(argv) != 2 or argv[1] in ('-h', '--help'):
        print('Usage: python preprocess_hooks.py <type of game>')
        return
    
    ver = argv[1]
    ver_path = Path('ver', ver)
    (ver_path / 'build').mkdir(exist_ok=True)
    
    with open(ver_path / 'hooks.yaml', 'r') as f:
        input_file = f.read()
    
    hooks_dict: dict[str, dict] = yaml.safe_load(input_file)['hooks']
    hooks = [Hook.from_dict(symbol_name, args) for symbol_name, args in hooks_dict.items()]
    
    generate_asm_definitions(ver_path, hooks)
    generate_linker_script(ver, ver_path, hooks)

if __name__ == '__main__':
    preprocess_hooks()
