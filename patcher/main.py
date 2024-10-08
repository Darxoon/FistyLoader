from io import BufferedRandom
from os import path
from posixpath import isfile
from sys import argv
import sys
from pefile import PE, SectionStructure

from hooks import inject_hooks

def add_section_header(pe: PE, section_size: int):
    print("Creating section .fisty...")
    section: SectionStructure = pe.sections[-1]
    section.Name = ".fisty".encode()
    section.Misc = section_size - 0x104
    section.Misc_PhysicalAddress = section_size - 0x104
    section.Misc_VirtualSize = section_size - 0x104
    # section.VirtualAddress = prev_section.VirtualAddress + prev_section.SizeOfRawData
    section.SizeOfRawData = section_size
    # section.PointerToRawData = prev_section.PointerToRawData + prev_section.SizeOfRawData
    section.PointerToRelocations = 0
    section.PointerToLinenumbers = 0
    section.NumberOfRelocations = 0
    section.NumberOfLinenumbers = 0
    section.Characteristics = 0xE0000000 # rwx permissions
    
    print(f"Virtual address of new section: 0x{section.VirtualAddress:x}")

def patch_game(file: BufferedRandom, game_bytes: bytes, section_content: bytes):
    fisty_section_offset = int.from_bytes(game_bytes[0x3dc:0x3e0], byteorder='little')
    file.seek(fisty_section_offset)
    file.write(section_content)
    inject_hooks(file)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
    return path.join(base_path, relative_path)

def dev_main():
    custom_code_path = resource_path('custom_code.bin')
    
    with open(custom_code_path, 'rb') as f:
        section_content = f.read()
    
    if not isfile('out.exe') or argv[1] in ['--clean', '-c']:
        print('Reading World of Goo 2.exe...')
        pe = PE("World of Goo 2.exe")
        
        add_section_header(pe, len(section_content))
        
        print("Writing out.exe...")
        pe.write("out.exe")
    else:
        print('out.exe exists already, only applying changes...')
    
    with open('out.exe', 'rb+') as f:
        patch_game(f, f.read(), section_content)

if __name__ == '__main__':
    dev_main()
