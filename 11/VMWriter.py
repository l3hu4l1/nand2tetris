class VMWriter:
    def __init__(self, output_file):
        self.out = open(output_file, 'w')

    def writePush(self, segment, index):
        if segment is None or index is None:
            raise ValueError(f"Invalid push: segment={segment}, index={index}")
        self.out.write(f'push {segment.lower()} {index}\n')

    def writePop(self, segment, index):
        self.out.write(f'pop {segment.lower()} {index}\n')

    def writeArithmetic(self, command):
        self.out.write(f'{command.lower()}\n')

    def writeLabel(self, label):
        self.out.write(f'label {label}\n')

    def writeGoto(self, label):
        self.out.write(f'goto {label}\n')

    def writeIf(self, label):
        self.out.write(f'if-goto {label}\n')

    def writeCall(self, name, n_args):
        self.out.write(f'call {name} {n_args}\n')

    def writeFunction(self, name, n_locals):
        self.out.write(f'function {name} {n_locals}\n')

    def writeReturn(self):
        self.out.write('return\n')

    def close(self):
        self.out.close()