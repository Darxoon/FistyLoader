from argparse import ArgumentParser
from array import array
from io import BufferedRandom, BytesIO
from os import path
from posixpath import isfile
from sys import argv
import sys
from pefile import PE, SectionStructure
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
import yaml

from hooks import inject_hooks

def add_section_header(pe: PE, section_size: int):
    print("Creating section .fisty...")
    section: SectionStructure = pe.sections[-1]
    section.Name = b".fisty"
    # section.Misc = section_size - 0x104
    # section.Misc_PhysicalAddress = section_size - 0x104
    # section.Misc_VirtualSize = section_size - 0x104
    # section.VirtualAddress = prev_section.VirtualAddress + prev_section.SizeOfRawData
    # section.SizeOfRawData = section_size
    # section.PointerToRawData = prev_section.PointerToRawData + prev_section.SizeOfRawData
    section.PointerToRelocations = 0
    section.PointerToLinenumbers = 0
    section.NumberOfRelocations = 0
    section.NumberOfLinenumbers = 0
    section.Characteristics = 0xE0000000 # rwx permissions
    
    print(f"Virtual address of new section: {section.VirtualAddress:#x}")

def patch_game(file: BufferedRandom, ver: str, game_bytes: bytes, section_content: bytes, symtab: SymbolTableSection, hooks: dict):
    game_bytes_arr: array[int] = array('I', game_bytes)
    pe_header_start = game_bytes_arr.index(int.from_bytes(b'PE\0\0', byteorder='little'))
    
    assert game_bytes[pe_header_start * 4 + 0x270:pe_header_start * 4 + 0x278].strip(b'\0') == b'.fisty'
    fisty_section_size = game_bytes_arr[pe_header_start + 0xa0]
    fisty_section_offset = game_bytes_arr[pe_header_start + 0xa1]
    
    if len(section_content) > fisty_section_size:
        raise ValueError("Content of .fisty section is too large!")
    
    section_content = section_content.ljust(fisty_section_size, b"\0")
    
    file.seek(fisty_section_offset)
    file.write(section_content)
    inject_hooks(file, ver, symtab, hooks)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', "")
    return path.join(base_path, relative_path)

def dev_main():
    parser = ArgumentParser(
        prog="main.py",
        description="Outputs patched executable into out.exe. Use build_installer.sh to create an installer.",
    )
    
    parser.add_argument('-t', '--type', choices=['steam_win', 'win'], default='steam_win', help="the version of the game")
    parser.add_argument('-c', '--clean', action='store_true')
    args = parser.parse_args()
    
    custom_code_path = resource_path(f'ver/{args.type}/build/custom_code.bin')
    custom_code_symbols_path = resource_path(f'ver/{args.type}/build/custom_code_symbols.o')
    hooks_path = resource_path(f'ver/{args.type}/hooks.yaml')
    
    executable_name = "WorldOfGoo2.exe" if args.type == "steam_win" else "World of Goo 2.exe"
    
    with open(custom_code_path, 'rb') as f:
        section_content = f.read()
    with open(custom_code_symbols_path, 'rb') as f:
        symbols_bin = f.read()
    with open(hooks_path, 'r') as f:
        hooks_str = f.read()
    
    if not isfile('out.exe') or args.clean:
        print(f'Reading {executable_name}...')
        pe = PE(executable_name)
        
        add_section_header(pe, len(section_content))
        
        print("Writing out.exe...")
        pe.write("out.exe")
    else:
        print('out.exe exists already, only applying changes...')
    
    symbols = ELFFile(BytesIO(symbols_bin))
    symtab = symbols.get_section_by_name(".symtab")
    assert isinstance(symtab, SymbolTableSection)
    
    hooks = yaml.safe_load(hooks_str)['hooks']
    
    with open('out.exe', 'rb+') as f:
        patch_game(f, args.type, f.read(), section_content, symtab, hooks)

if __name__ == '__main__':
    dev_main()
