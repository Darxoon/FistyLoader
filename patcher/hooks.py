from dataclasses import dataclass
from io import BufferedRandom
from elftools.elf.sections import SymbolTableSection

@dataclass
class Hook:
    symbol_name: str
    target_addr: int
    byte_length: int
    
    @staticmethod
    def from_dict(symbol_name: str, hook_dict: dict) -> 'Hook':
        target_addr = hook_dict['target_addr']
        assert isinstance(target_addr, int), f"'target_addr' field has to be an int ({symbol_name!r})"
        
        byte_length = hook_dict['byte_length']
        assert isinstance(byte_length, int), f"'byte_length' field has to be an int ({symbol_name!r})"
        assert byte_length >= 5, f"byte_length has to be at least 5 ({symbol_name!r})"
        
        return Hook(symbol_name, target_addr, byte_length)

# from https://stackoverflow.com/a/36361832/10079808
NOP_SEQUENCES = [
    None, # 0-byte nop doesn't exist
	bytes([0x90]), # 1-byte nop
	bytes([0x66, 0x90]), # 2-byte nop
	bytes([0x0F, 0x1F, 0x00]), # 3-byte nop
	bytes([0x0F, 0x1F, 0x40, 0x00]), # 4-byte nop
	bytes([0x0F, 0x1F, 0x44, 0x00, 0x00]), # 5-byte nop
	bytes([0x66, 0x0F, 0x1F, 0x44, 0x00, 0x00]), # 6-byte nop
	bytes([0x0F, 0x1F, 0x80, 0x00, 0x00, 0x00, 0x00]), # 7-byte nop
	bytes([0x0F, 0x1F, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00]), # 8-byte nop
	bytes([0x66, 0x0F, 0x1F, 0x84, 0x00, 0x00, 0x00, 0x00, 0x00]), # 9-byte nop
]

def overwrite_bytes(file: BufferedRandom, virtual_address: int, replacement: bytes):
    # calculate physical address
    if virtual_address < 0x140001000 or virtual_address >= 0x140001000 + 0x85AE00:
        raise Exception(f"Hook to addr {virtual_address:x} is outside of .text section")
    
    physical_address = virtual_address - 0x140001000 + 0x400
    file.seek(physical_address)
    file.write(replacement)

def hook_addr(file: BufferedRandom, virtual_address: int, target_address: int, *, padding: int = 0):
    relative_target_addr = target_address - (virtual_address + 5)
    buf = bytes([0xe9, *relative_target_addr.to_bytes(4, 'little')])
    
    if padding > 0:
        buf += bytes([0]) * padding
    
    overwrite_bytes(file, virtual_address, buf)

def hook_symbol(file: BufferedRandom, symtab: SymbolTableSection, virtual_address: int, target_symbol: str, *, padding: int = 0):
    symbols = symtab.get_symbol_by_name(target_symbol)
    if symbols is None or len(symbols) == 0:
        raise Exception(f"Could not find symbol called {target_symbol}")
    
    [symbol] = symbols
    hook_addr(file, virtual_address, 0x140000000 | symbol.entry.st_value, padding=padding)

def inject_hooks(file: BufferedRandom, symtab: SymbolTableSection, hooks: dict):
    print("Injecting hooks...")
    
    # Hooks
    for symbol_name, args in hooks.items():
        hook = Hook.from_dict(symbol_name, args)
        hook_symbol(file, symtab, 0x140000000 | hook.target_addr, symbol_name, padding=hook.byte_length - 5)
    
    # Direct asm patches
    # Skip SteamAPI (crashes)
    # overwrite_bytes(file, 0x14041a75f, NOP_SEQUENCES[5])
    
    # BallFactory::load: add r14, 0x4cb48 + cmp edi, 0x27 -> 7-byte nop + cmp edi, r14d (unhardcode gooball cap)
    #overwrite_bytes(file, 0x14020eab5, bytes([0x0F, 0x1F, 0x80, 0x00, 0x00, 0x00, 0x00, 0x44, 0x39, 0xf7]))
