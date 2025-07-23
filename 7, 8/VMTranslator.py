import sys
import os
from vmparser import Parser
from codewriter import CodeWriter

def main():
    if len(sys.argv) != 2:
        print("Usage: VMTranslator.py <path>")
        sys.exit(1)

    source = sys.argv[1]

    if os.path.isdir(source):
        vm_files = [os.path.join(source, f) for f in os.listdir(source) if f.endswith(".vm")]
        dir_name = os.path.basename(os.path.normpath(source))
        output_path = os.path.join(source, dir_name + ".asm")
    elif source.endswith(".vm"):
        vm_files = [source]
        output_path = source.replace(".vm", ".asm")
    else:
        sys.exit(1)

    code_writer = CodeWriter(output_path)

    if any(os.path.basename(f) == "Sys.vm" for f in vm_files):
        code_writer.write_init()

    for vm_file in vm_files:
        parser = Parser(vm_file)
        code_writer.set_file_name(vm_file)

        while parser.has_more_commands():
            parser.advance()
            cmd_type = parser.command_type()

            if cmd_type == "C_ARITHMETIC":
                code_writer.write_arithmetic(parser.arg1())
            elif cmd_type == "C_PUSH":
                code_writer.write_push(parser.arg1(), parser.arg2())
            elif cmd_type == "C_POP":
                code_writer.write_pop(parser.arg1(), parser.arg2())
            elif cmd_type == "C_LABEL":
                code_writer.write_label(parser.arg1())
            elif cmd_type == "C_GOTO":
                code_writer.write_goto(parser.arg1())
            elif cmd_type == "C_IF":
                code_writer.write_if(parser.arg1())
            elif cmd_type == "C_FUNCTION":
                code_writer.write_function(parser.arg1(), parser.arg2())
            elif cmd_type == "C_RETURN":
                code_writer.write_return()
            elif cmd_type == "C_CALL":
                code_writer.write_call(parser.arg1(), parser.arg2())

    code_writer.close()

if __name__ == "__main__":
    main()