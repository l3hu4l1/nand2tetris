import os
import sys
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
from VMWriter import VMWriter
from SymbolTable import SymbolTable

def is_jack_file(path):
    return os.path.isfile(path) and path.endswith(".jack")

def get_jack_files(path):
    if os.path.isdir(path):
        return [
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.endswith(".jack")
        ]
    elif is_jack_file(path):
        return [path]
    else:
        return []

def compile_file(jack_file):
    base_name = os.path.splitext(jack_file)[0]
    vm_file = base_name + ".vm"

    tokenizer = JackTokenizer(jack_file)
    vm_writer = VMWriter(vm_file)
    symbol_table = SymbolTable()
    engine = CompilationEngine(tokenizer, vm_writer, symbol_table)
    engine.compileClass()
    vm_writer.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: JackCompiler.py <path>")
        return

    input_path = sys.argv[1]
    jack_files = get_jack_files(input_path)

    if not jack_files:
        print("No .jack files found.")
        return

    for jack_file in jack_files:
        compile_file(jack_file)

if __name__ == "__main__":
    main()