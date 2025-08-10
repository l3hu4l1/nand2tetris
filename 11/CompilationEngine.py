class CompilationEngine:
    def __init__(self, tokenizer, vm_writer, symbol_table):
        self.tokenizer = tokenizer
        self.vm_writer = vm_writer
        self.class_name = ""
        self.symbol_table = symbol_table
        self.label_counter = 0

    def _eat(self, expected=None):
        token = self.tokenizer.current_token
        if expected and token != expected:
            raise ValueError(f"Expected {expected}, got {token}")
        self.tokenizer.advance()

    def new_label(self, base):
        label = f"{base}{self.label_counter}"
        self.label_counter += 1
        return label

    def kindToSegment(self, kind):
        if kind == "STATIC": return "static"
        if kind == "FIELD": return "this"
        if kind == "ARG": return "argument"
        if kind == "VAR": return "local"
        return "none"

    def compileArithmetic(self, op):
        command_map = {
            "+": "add",
            "-": "sub",
            "*": "call Math.multiply 2",
            "/": "call Math.divide 2",
            "&": "and",
            "|": "or",
            "<": "lt",
            ">": "gt",
            "=": "eq"
        }
        command = command_map[op]
        if command.startswith("call"):
            fn, n = command.split()[1], int(command.split()[2])
            self.vm_writer.writeCall(fn, n)
        else:
            self.vm_writer.writeArithmetic(command)

    def compileClass(self):
        self._eat("class")
        self.class_name = self.tokenizer.identifier()
        self._eat(self.class_name)
        self._eat("{")

        while self.tokenizer.current_token in ("static", "field"):
            self.compileClassVarDec()

        while self.tokenizer.current_token in ("constructor", "function", "method"):
            self.compileSubroutine()

        self._eat("}")

    def compileClassVarDec(self):
        kind = self.tokenizer.current_token  # static or field
        self._eat(kind)
        var_type = self.tokenizer.current_token
        self._eat(var_type)
        name = self.tokenizer.current_token
        self.symbol_table.define(name, var_type, kind)
        self._eat(name)

        while self.tokenizer.current_token == ",":
            self._eat(",")
            name = self.tokenizer.current_token
            self.symbol_table.define(name, var_type, kind)
            self._eat(name)

        self._eat(";")

    def compileSubroutine(self):
        self.symbol_table.startSubroutine()
        subroutine_type = self.tokenizer.current_token
        self._eat(subroutine_type)
        self._eat()  # return type
        subroutine_name = self.tokenizer.identifier()
        full_name = f"{self.class_name}.{subroutine_name}"
        self._eat(subroutine_name)
        self._eat("(")
        if subroutine_type == "method":
            # Add 'this' as the 0th argument
            self.symbol_table.define("this", self.class_name, "arg")
        self.compileParameterList()
        self._eat(")")
        self._eat("{")

        while self.tokenizer.current_token == "var":
            self.compileVarDec()

        n_locals = self.symbol_table.varCount("var")
        self.vm_writer.writeFunction(full_name, n_locals)

        if subroutine_type == "constructor":
            field_count = self.symbol_table.varCount("field")
            self.vm_writer.writePush("constant", field_count)
            self.vm_writer.writeCall("Memory.alloc", 1)
            self.vm_writer.writePop("pointer", 0)  # set this = base address
        elif subroutine_type == "method":
            self.vm_writer.writePush("argument", 0)
            self.vm_writer.writePop("pointer", 0)  # set this = argument 0

        self.compileStatements()
        self._eat("}")

    def compileParameterList(self):
        if self.tokenizer.current_token != ")":
            var_type = self.tokenizer.current_token
            self._eat(var_type)
            name = self.tokenizer.current_token
            self.symbol_table.define(name, var_type, "arg")
            self._eat(name)
            while self.tokenizer.current_token == ",":
                self._eat(",")
                var_type = self.tokenizer.current_token
                self._eat(var_type)
                name = self.tokenizer.current_token
                self.symbol_table.define(name, var_type, "arg")
                self._eat(name)

    def compileVarDec(self):
        self._eat("var")
        var_type = self.tokenizer.current_token
        self._eat(var_type)
        name = self.tokenizer.current_token
        self.symbol_table.define(name, var_type, "var")
        self._eat(name)
        while self.tokenizer.current_token == ",":
            self._eat(",")
            name = self.tokenizer.current_token
            self.symbol_table.define(name, var_type, "var")
            self._eat(name)
        self._eat(";")

    def compileStatements(self):
        while self.tokenizer.current_token in ("let", "if", "while", "do", "return"):
            if self.tokenizer.current_token == "let":
                self.compileLet()
            elif self.tokenizer.current_token == "do":
                self.compileDo()
            elif self.tokenizer.current_token == "return":
                self.compileReturn()
            elif self.tokenizer.current_token == "if":
                self.compileIf()
            elif self.tokenizer.current_token == "while":
                self.compileWhile()

    def compileLet(self):
        self._eat("let")
        var_name = self.tokenizer.identifier()
        self._eat(var_name)

        is_array = False
        if self.tokenizer.current_token == "[":
            is_array = True
            self._eat("[")
            self.compileExpression()  # push index
            self._eat("]")

            kind = self.symbol_table.kindOf(var_name)
            index = self.symbol_table.indexOf(var_name)
            segment = self.kindToSegment(kind)
            self.vm_writer.writePush(segment, index)  # push base addr
            self.vm_writer.writeArithmetic("add")  # base + index

        self._eat("=")
        self.compileExpression()
        self._eat(";")

        if is_array:
            # For array: save value to temp, pop pointer 1, pop that 0
            self.vm_writer.writePop("temp", 0)  # save value
            self.vm_writer.writePop("pointer", 1)  # that = base+index
            self.vm_writer.writePush("temp", 0)  # value
            self.vm_writer.writePop("that", 0)
        else:
            kind = self.symbol_table.kindOf(var_name)
            index = self.symbol_table.indexOf(var_name)
            segment = self.kindToSegment(kind)
            self.vm_writer.writePop(segment, index)

    def compileDo(self):
        self._eat("do")
        self.compileSubroutineCall()
        self._eat(";")
        self.vm_writer.writePop("temp", 0)

    def compileReturn(self):
        self._eat("return")
        if self.tokenizer.current_token != ";":
            self.compileExpression()
        else:
            self.vm_writer.writePush("constant", 0)
        self._eat(";")
        self.vm_writer.writeReturn()

    def compileWhile(self):
        label_exp = self.new_label("WHILE_EXP")
        label_end = self.new_label("WHILE_END")

        self.vm_writer.writeLabel(label_exp)

        self._eat("while")
        self._eat("(")
        self.compileExpression()
        self._eat(")")

        self.vm_writer.writeArithmetic("not")
        self.vm_writer.writeIf(label_end)

        self._eat("{")
        self.compileStatements()
        self._eat("}")

        self.vm_writer.writeGoto(label_exp)
        self.vm_writer.writeLabel(label_end)

    def compileIf(self):
        label_else = self.new_label("IF_ELSE")
        label_end = self.new_label("IF_END")

        self._eat("if")
        self._eat("(")
        self.compileExpression()
        self._eat(")")

        self.vm_writer.writeArithmetic("not")
        self.vm_writer.writeIf(label_else)

        self._eat("{")
        self.compileStatements()  # IF body
        self._eat("}")

        self.vm_writer.writeGoto(label_end)
        self.vm_writer.writeLabel(label_else)

        if self.tokenizer.current_token == "else":
            self._eat("else")
            self._eat("{")
            self.compileStatements()
            self._eat("}")

        self.vm_writer.writeLabel(label_end)

    def compileExpression(self):
        self.compileTerm()
        while self.tokenizer.current_token in ('+', '-', '*', '/', '&', '|', '<', '>', '='):
            op = self.tokenizer.current_token
            self._eat(op)
            self.compileTerm()
            self.compileArithmetic(op)

    def compileTerm(self):
        token_type = self.tokenizer.tokenType()
        token = self.tokenizer.current_token

        if token_type == "integerConstant":
            self.vm_writer.writePush("constant", int(token))
            self._eat(token)

        elif token_type == "stringConstant":
            value = self.tokenizer.stringVal()
            self._eat(token)
            self.vm_writer.writePush("constant", len(value))
            self.vm_writer.writeCall("String.new", 1)
            for c in value:
                self.vm_writer.writePush("constant", ord(c))
                self.vm_writer.writeCall("String.appendChar", 2)

        elif token_type == "keyword" and token in {"true", "false", "null", "this"}:
            self._eat(token)
            if token == "true":
                self.vm_writer.writePush("constant", 0)
                self.vm_writer.writeArithmetic("not")
            elif token in {"false", "null"}:
                self.vm_writer.writePush("constant", 0)
            elif token == "this":
                self.vm_writer.writePush("pointer", 0)

        elif token_type == "symbol" and token == "(":
            self._eat("(")
            self.compileExpression()
            self._eat(")")

        elif token_type == "symbol" and token in {"-", "~"}:
            op = token
            self._eat(op)
            self.compileTerm()
            if op == "-":
                self.vm_writer.writeArithmetic("neg")
            else:
                self.vm_writer.writeArithmetic("not")

        elif token_type == "identifier":
            next_token = self.tokenizer.peek()

            if next_token == "[":
                var_name = token
                self._eat(var_name)
                self._eat("[")
                self.compileExpression()
                self._eat("]")

                kind = self.symbol_table.kindOf(var_name)
                index = self.symbol_table.indexOf(var_name)
                segment = self.kindToSegment(kind)
                self.vm_writer.writePush(segment, index)
                self.vm_writer.writeArithmetic("add")
                self.vm_writer.writePop("pointer", 1)
                self.vm_writer.writePush("that", 0)

            elif next_token in {"(", "."}:
                self.compileSubroutineCall()
            else:
                kind = self.symbol_table.kindOf(token)
                index = self.symbol_table.indexOf(token)
                segment = self.kindToSegment(kind)
                self.vm_writer.writePush(segment, index)
                self._eat(token)

    def compileSubroutineCall(self):
        n_args = 0
        name = self.tokenizer.identifier()
        self._eat(name)

        if self.tokenizer.current_token == ".":
            self._eat(".")
            subroutine_name = self.tokenizer.identifier()
            self._eat(subroutine_name)

            kind = self.symbol_table.kindOf(name)
            if kind is not None:
                # 'name' is a variable referring to an object instance
                type_name = self.symbol_table.typeOf(name)
                segment = self.kindToSegment(kind)
                index = self.symbol_table.indexOf(name)
                self.vm_writer.writePush(segment, index)
                full_name = f"{type_name}.{subroutine_name}"
                n_args += 1
            else:
                # 'name' is a class name
                full_name = f"{name}.{subroutine_name}"
        else:
            # method call
            full_name = f"{self.class_name}.{name}"
            self.vm_writer.writePush("pointer", 0)
            n_args += 1

        self._eat("(")
        n_args += self.compileExpressionList()
        self._eat(")")
        self.vm_writer.writeCall(full_name, n_args)

    def compileExpressionList(self):
        n_args = 0
        if self.tokenizer.current_token != ")":
            self.compileExpression()
            n_args += 1
            while self.tokenizer.current_token == ",":
                self._eat(",")
                self.compileExpression()
                n_args += 1
        return n_args
