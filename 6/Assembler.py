import os
import sys
from Parser import Parser
from Code import Code
from SymbolTable import SymbolTable

def assemble_dir(directory):
    for f in os.listdir(directory):
        if f.endswith(".asm"):
            assemble_file(os.path.join(directory, f))

def assemble_file(input_file):
    parser = Parser(input_file)
    symbol_table = SymbolTable()

    rom_address = 0
    while parser.has_more_commands():
        parser.advance()
        if parser.command_type() == "L_COMMAND":
            symbol = parser.symbol()
            symbol_table.add_entry(symbol, rom_address)
        elif parser.command_type() in ("A_COMMAND", "C_COMMAND"):
            rom_address += 1

    output_file = os.path.splitext(input_file)[0] + ".hack"
    parser.reset()
    code = Code()
    ram_address = 16

    with open(output_file, 'w') as out:
        while parser.has_more_commands():
            parser.advance()
            cmd_type = parser.command_type()

            if cmd_type == "A_COMMAND":
                symbol = parser.symbol()
                if symbol.isdigit():
                    address = int(symbol)
                else:
                    if not symbol_table.contains(symbol):
                        symbol_table.add_entry(symbol, ram_address)
                        ram_address += 1
                    address = symbol_table.get_address(symbol)
                binary = format(address, '016b')
                out.write(binary + '\n')

            elif cmd_type == "C_COMMAND":
                dest = code.dest(parser.dest())
                comp = code.comp(parser.comp())
                jump = code.jump(parser.jump())
                binary = '111' + comp + dest + jump
                out.write(binary + '\n')

def assemble(argv):
    if len(argv) == 1:
        src = argv[0]
        if os.path.isdir(src):
            assemble_dir(src)
        elif src.endswith(".asm"):
            assemble_file(src)

    else:
        print("Usage: Assembler.py <filename>.asm | <directory>")
        sys.exit(1)

if __name__ == "__main__":
    assemble(sys.argv[1:])