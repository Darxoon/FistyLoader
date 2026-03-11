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
    section.Name = ".fisty".encode()
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
    
    print(f"Virtual address of new section: 0x{section.VirtualAddress:x}")

def patch_game(file: BufferedRandom, game_bytes: bytes, section_content: bytes, symtab: SymbolTableSection, hooks: dict):
    fisty_section_size = int.from_bytes(game_bytes[0x3d8:0x3dc], byteorder='little')
    fisty_section_offset = int.from_bytes(game_bytes[0x3dc:0x3e0], byteorder='little')
    
    if len(section_content) > fisty_section_size:
        raise ValueError("Content of .fisty section is too large!")
    
    section_content = section_content.ljust(fisty_section_size, b"\0")
    
    file.seek(fisty_section_offset)
    file.write(section_content)
    inject_hooks(file, symtab, hooks)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
    return path.join(base_path, relative_path)

def dev_main():
    custom_code_path = resource_path('bin/custom_code.bin')
    custom_code_symbols_path = resource_path('bin/custom_code_symbols.o')
    hooks_path = resource_path('data/hooks.yaml')
    
    with open(custom_code_path, 'rb') as f:
        section_content = f.read()
    with open(custom_code_symbols_path, 'rb') as f:
        symbols_bin = f.read()
    with open(hooks_path, 'r') as f:
        hooks_str = f.read()
    
    if not isfile('out.exe') or (len(argv) >= 2 and argv[1] in ['--clean', '-c']):
        print('Reading WorldOfGoo2.exe...')
        pe = PE("WorldOfGoo2.exe")
        
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
        patch_game(f, f.read(), section_content, symtab, hooks)

if __name__ == '__main__':
    dev_main()
