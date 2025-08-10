class Parser:
    """ Parses VM commands from a file. """

    def __init__(self, file_path):
        self.file = open(file_path, "r")
        self.commands = self._clean_lines(self.file.readlines())
        self.current_command = None
        self.index = 0

    def _clean_lines(self, lines):
        cleaned = []
        for line in lines:
            line = line.split("//")[0].strip()
            if line:
                cleaned.append(line)
        return cleaned

    def has_more_commands(self):
        return self.index < len(self.commands)

    def advance(self):
        if self.has_more_commands():
            self.current_command = self.commands[self.index]
            self.index += 1

    def command_type(self):
        if self.current_command.startswith("push"):
            return "C_PUSH"
        elif self.current_command.startswith("pop"):
            return "C_POP"
        elif self.current_command.split()[0] in ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]:
            return "C_ARITHMETIC"
        elif self.current_command.startswith("label"):
            return "C_LABEL"
        elif self.current_command.startswith("goto"):
            return "C_GOTO"
        elif self.current_command.startswith("if-goto"):
            return "C_IF"
        elif self.current_command.startswith("function"):
            return "C_FUNCTION"
        elif self.current_command.startswith("call"):
            return "C_CALL"
        elif self.current_command.startswith("return"):
            return "C_RETURN"

    def arg1(self):
        if self.command_type() == "C_ARITHMETIC":
            return self.current_command
        return self.current_command.split()[1]

    def arg2(self):
        return int(self.current_command.split()[2])