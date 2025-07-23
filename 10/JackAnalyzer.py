import os
import sys
from JackTokenizer import JackTokenizer as Tokenizer
from CompilationEngine import CompilationEngine as Engine

def is_jack_file(path):
    return os.path.isfile(path) and path.endswith(".jack")

def get_jack_files(path):
    if os.path.isdir(path):
        return [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".jack")]
    elif is_jack_file(path):
        return [path]
    else:
        return []

def analyze():
    if len(sys.argv) != 2:
        print("Usage: JackAnalyzer.py <filename.jack> | <directory>")
        return

    input_path = sys.argv[1]
    jack_files = get_jack_files(input_path)

    for jack_file in jack_files:
        base_name = os.path.splitext(jack_file)[0]
        output_file = base_name + "T.xml"

        tokenizer = Tokenizer(jack_file)
        engine = Engine(tokenizer, output_file)
        engine.writeTokens()
        # engine.compileClass()
        engine.close()

if __name__ == "__main__":
    analyze()