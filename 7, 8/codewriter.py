import os

class CodeWriter:
    """ Translates VM commands into Hack assembly code and writes them to output file. """

    SYMBOLS = {
            # Arithmetic Operators
            'add': 'M=D+M',
            'sub': 'M=M-D',
            'and': 'M=D&M',
            'or': 'M=D|M',
            'neg': 'M=-M',
            'not': 'M=!M',
            'eq': 'D;JEQ',
            'gt': 'D;JGT',
            'lt': 'D;JLT',

	        # Assembly Symbols
            'local': '@LCL',
            'argument': '@ARG',
            'this': '@THIS',
            'that': '@THAT'
    }
    POINTER_ID = 3
    TEMP_ID = 5

    def __init__(self, output_path):
        self.file = open(output_path, 'w')
        self.filename = ''
        self.static_prefix = ''
        self.label_count = 0
        self.function_prefix = ''
        self.function_stack = []

    def set_file_name(self, file_path):
        self.filename = os.path.splitext(os.path.basename(file_path))[0]
        self.static_prefix = self.filename + '.'

    def _write(self, block):
        self.file.write('\n'.join(block) + '\n')

    def _pushd(self):
        return ['@SP', 'A=M', 'M=D', '@SP', 'M=M+1']

    def _popd(self):
        return ['@SP', 'AM=M-1', 'D=M']

    def _push_constant(self, value):
        if value in {0, 1}:
            asm = ['D=' + str(value)]
        else:
            asm = ['@' + str(value), 'D=A']
        return asm + self._pushd()

    def _push_register(self, register):
        return ['@' + register, 'D=M'] + self._pushd()

    def _push_segment(self, segment, index):
        if index == 0:
            asm = [self.SYMBOLS[segment], 'A=M']
        else: asm = [self.SYMBOLS[segment], 'D=M', '@' + str(index), 'A=D+A']
        return asm + ['D=M'] + self._pushd()

    def _push_segment_addr(self, segment):
        return [self.SYMBOLS[segment], 'D=M'] + self._pushd()

    def _pop_register(self, register):
        return self._popd() + ['@' + register, 'M=D']

    def _pop_segment(self, segment, index):
        asm = ['@' + str(index), 'D=A', # get i
            self.SYMBOLS[segment], # get base addr of segment
            'D=D+M', # addr = base + i
            '@R13', # store addr for use later
            'M=D']
        asm += self._popd()
        asm += ['@R13', 'A=M', 'M=D']

        return asm

    def _get_label_count(self):
        self.label_count += 1
        return self.label_count

    def write_label(self, label):
        self._write(['(' + label + ')'])

    def write_goto(self, label):
        asm = ['@' + label, '0;JMP']
        self._write(asm)

    def write_if(self, label):
        asm = self._popd() + ['@' + label, 'D;JNE']
        self._write(asm)

    def write_function(self, function_name, num_locals):
        """ Commands to declare function """

        self.function_prefix = self.filename + '$'
        self.function_stack.append(self.function_prefix) # PUSH current function prefix
        self.write_label(function_name)

        if num_locals != 0:
            asm = []
            for _ in range(num_locals):
                asm += self._push_constant(0)
            self._write(asm)

    def write_return(self):
        """ Commands to save return value and restore caller's state """

        asm = ['@LCL', 'D=M', '@R13', 'M=D']
        asm += ['@5', 'A=D-A', 'D=M', '@R14', 'M=D']  # get return addr
        asm += self._popd() + ['@ARG', 'A=M', 'M=D'] # get return value
        asm += ['@ARG', 'D=M+1', '@SP', 'M=D'] # reposition SP
        for segment in ['that', 'this', 'argument', 'local']:
            asm += ['@R13', 'AM=M-1', 'D=M', self.SYMBOLS[segment], 'M=D'] # restore segments
        asm += ['@R14', 'A=M', '0;JMP'] # jump to return addr

        self._write(asm)

        # POP back to previous function context
        if self.function_stack:
            self.function_prefix = self.function_stack.pop()
        else:
            self.function_prefix = ''

    def write_call(self, function_name, num_args):
        """ Commands to save caller's state and transfer control to callee """

        return_suffix = 'ret.' + str(self._get_label_count())
        label = self.function_prefix + return_suffix

        asm = ['@' + label, 'D=A'] + self._pushd() # push return addr
        for segment in ['local', 'argument', 'this', 'that']:
            asm += self._push_segment_addr(segment)

        asm += ['@SP', 'D=M', '@' + str(num_args+5), 'D=D-A', '@ARG', 'M=D'] # reposition ARG
        asm += ['@SP', 'D=M', '@LCL', 'M=D'] # reposition LCL

        self._write(asm)
        self.function_stack.append(self.function_prefix) # PUSH current function prefix
        self.write_goto(function_name)
        self.write_label(label)

    def write_init(self):
        """ Init virtual segments and start execution"""

        asm = ['@256', 'D=A', '@SP', 'M=D']
        for i, seg in enumerate(['local', 'argument', 'this', 'that'], 1):
            asm += ['@' + str(i), 'D=A', self.SYMBOLS[seg], 'M=D']
        self._write(asm)
        self.write_call('Sys.init', 0)

    def write_arithmetic(self, command):
        if command in {'add', 'sub', 'and', 'or'}:
            asm = ['@SP', 'AM=M-1', 'D=M', 'A=A-1', self.SYMBOLS[command]]
        elif command in {'neg', 'not'}:
            asm = ['@SP', 'A=M-1', self.SYMBOLS[command]]
        elif command in {'eq', 'gt', 'lt'}:
            jump_label = 'label' + str(self._get_label_count())
            sym1 = '@' + jump_label
            sym2 = '(' + jump_label + ')' # symbol for the true state

            asm = ['@SP', 'AM=M-1', 'D=M', 'A=A-1', 'D=M-D',
                   'M=-1', # set true first
                   sym1, self.SYMBOLS[command], # to jump if true
                   '@SP', 'A=M-1', 'M=0', # else set *SP to false
                   sym2]

        self._write(asm)

    def write_push(self, segment, index):
        if segment == 'constant':
            asm = self._push_constant(index)
        elif segment in {'local', 'argument', 'this', 'that'}:
            # addr = segptr + i, then get *addr
            asm = self._push_segment(segment, index)
        elif segment == 'pointer':
            asm = self._push_register('R' + str(self.POINTER_ID + index))
        elif segment == 'temp':
            asm = self._push_register('R' + str(self.TEMP_ID + index))
        elif segment == 'static':
            asm = self._push_register(self.static_prefix + str(index))

        self._write(asm)

    def write_pop(self, segment, index):
        if segment in {'local','argument','this','that'}:
            asm = self._pop_segment(segment, index)
        elif segment == 'pointer':
            asm = self._pop_register('R' + str(self.POINTER_ID + index))
        elif segment == 'temp':
            asm = self._pop_register('R' + str(self.TEMP_ID + index))
        elif segment == 'static':
            asm = self._pop_register(self.static_prefix + str(index))

        self._write(asm)

    def close(self):
        self.file.close()