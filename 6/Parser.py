class Parser:
    def __init__(self, filepath):
        with open(filepath, 'r') as f:
            lines = f.readlines()
        self.commands = [self.clean(line) for line in lines if self.clean(line)]
        self.current_index = -1
        self.current_command = None

    def clean(self, line):
        return line.split('//')[0].strip() # remove comments and whitespace

    def has_more_commands(self):
        return self.current_index + 1 < len(self.commands)

    def advance(self):
        self.current_index += 1
        self.current_command = self.commands[self.current_index]

    def reset(self):
        self.current_index = -1
        self.current_command = None

    def command_type(self):
        if self.current_command.startswith('@'):
            return "A_COMMAND"
        elif self.current_command.startswith('('):
            return "L_COMMAND"
        else:
            return "C_COMMAND"

    def symbol(self):
        if self.command_type() == "A_COMMAND":
            return self.current_command[1:]
        elif self.command_type() == "L_COMMAND":
            return self.current_command[1:-1]

    def dest(self):
        if '=' in self.current_command:
            return self.current_command.split('=')[0]
        return 'null'

    def comp(self):
        parts = self.current_command.split('=')
        comp_jump = parts[-1]
        if ';' in comp_jump:
            return comp_jump.split(';')[0]
        return comp_jump

    def jump(self):
        if ';' in self.current_command:
            return self.current_command.split(';')[1]
        return 'null'