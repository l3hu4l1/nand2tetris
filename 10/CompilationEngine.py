class CompilationEngine:
    def __init__(self, tokenizer, output_file):
        self.tokenizer = tokenizer
        self.output = open(output_file, 'w')
        self.indent = 0

    def close(self):
        self.output.close()

    def _writeToken(self):
        type_ = self.tokenizer.tokenType()

        if type_ == "keyword":
            token = self.tokenizer.keyword()

        elif type_ == "symbol":
            token = self.tokenizer.symbol()
            # Escape special XML characters
            token = token.replace('&', '&amp;').replace('>', '&gt;').replace('<', '&lt;')

        elif type_ == "identifier":
            token = self.tokenizer.identifier()

        elif type_ == "integerConstant":
            token = self.tokenizer.intVal()

        elif type_ == "stringConstant":
            token = self.tokenizer.stringVal()

        self.output.write(f'<{type_}> {token} </{type_}>\n')
        # self._writeLine(f'<{type_}> {token} </{type_}>')

    def writeTokens(self):
        self.output.write('<tokens>' + '\n')
        while self.tokenizer.hasMoreTokens():
            self._writeToken()
            self.tokenizer.advance()
        self._writeToken()
        self.output.write('</tokens>' + '\n')

    def _writeLine(self, line):
        self.output.write("  " * self.indent + line + "\n")

    def _writeOpening(self, tag):
        self._writeLine(f"<{tag}>")
        self.indent += 1

    def _writeClosing(self, tag):
        self.indent -= 1
        self._writeLine(f"</{tag}>")

    def _eat(self):
        self._writeToken()
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()

    def compileClass(self):
        self._writeOpening("class")

        # class className
        self._eat()
        self._eat()

        # { classVarDec* subroutineDec* }
        self._eat()

        while self.tokenizer.tokenType() == "keyword":
            kw = self.tokenizer.keyword()
            if kw in {"static", "field"}:
                self.compileClassVarDec()
            elif kw in {"constructor", "function", "method"}:
                self.compileSubroutine()

        self._writeToken()

        self._writeClosing("class")

    def compileClassVarDec(self):
        self._writeOpening("classVarDec")

        self._eat() # static | field
        self._eat() # type (int | char | boolean | className)
        self._eat() # varName

        # (, varName)* ;
        while self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ",":
            self._eat()
            self._eat()
        self._eat()

        self._writeClosing("classVarDec")

    def compileSubroutine(self):
        self._writeOpening("subroutineDec")

        self._eat() # constructor | function | method
        self._eat() # type
        self._eat() # subroutineName

        self._eat() # (
        self.compileParameterList()
        self._eat() # )

        self.compileSubroutineBody()

        self._writeClosing("subroutineDec")

    def compileParameterList(self):
        self._writeOpening("parameterList")

        # is parameterList non-empty?
        if self.tokenizer.tokenType() != "symbol" or self.tokenizer.symbol() != ")":
            self._eat() # first type
            self._eat() # first varName

            while self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ",":
                self._eat()
                self._eat() # next type
                self._eat() # next varName

        self._writeClosing("parameterList")

    def compileSubroutineBody(self):
        self._writeOpening("subroutineBody")

        # { varDec* statements }
        self._eat()
        while self.tokenizer.tokenType() == "keyword" and self.tokenizer.keyword() == "var":
            self.compileVarDec()
        self.compileStatements()
        self._eat()

        self._writeClosing("subroutineBody")

    def compileVarDec(self):
        self._writeOpening("varDec")

        # var type varName
        self._eat()
        self._eat()
        self._eat()

        # (, varName)* ;
        while self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ",":
            self._eat()
            self._eat()
        self._eat()

        self._writeClosing("varDec")

    def compileStatements(self):
        self._writeOpening("statements")

        while self.tokenizer.tokenType() == "keyword":
            kw = self.tokenizer.keyword()
            if kw == 'do':
                self.compileDo()
            elif kw == 'let':
                self.compileLet()
            elif kw == 'while':
                self.compileWhile()
            elif kw == 'return':
                self.compileReturn()
            elif kw == 'if':
                self.compileIf()

        self._writeClosing("statements")

    def compileDo(self):
        self._writeOpening("doStatement")

        self._eat()
        self.compileSubroutineCall()
        self._eat()

        self._writeClosing("doStatement")

    def compileLet(self):
        self._writeOpening("letStatement")

        # let varName ([ expr ])?
        self._eat()
        self._eat() # varName
        if self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == "[":
            self.compileArray()

        # = expr ;
        self._eat()
        self.compileExpression()
        self._eat()

        self._writeClosing("letStatement")

    def compileIfWhile(self):
        # if | while ( expr )
        self._eat()
        self._eat()
        self.compileExpression()
        self._eat()

        # { statements }
        self._eat()
        self.compileStatements()
        self._eat()

    def compileIf(self):
        self._writeOpening("ifStatement")
        self.compileIfWhile()

        # (else { statements })?
        if self.tokenizer.tokenType() == "keyword" and self.tokenizer.keyword() == "else":
            self._eat()

            self._eat()
            self.compileStatements()
            self._eat()

        self._writeClosing("ifStatement")

    def compileWhile(self):
        self._writeOpening("whileStatement")
        self.compileIfWhile()
        self._writeClosing("whileStatement")

    def compileReturn(self):
        self._writeOpening("returnStatement")

        # return (expr)? ;
        self._eat()
        if self.tokenizer.tokenType() != "symbol" or self.tokenizer.symbol() != ";":
            self.compileExpression()
        self._eat()

        self._writeClosing("returnStatement")

    def compileArray(self):
        self._eat()
        self.compileExpression()
        self._eat()

    def compileExpression(self):
        self._writeOpening("expression")

        # term (op term)*
        self.compileTerm()
        while self.tokenizer.tokenType() == "symbol" and \
                self.tokenizer.symbol() in '+-*/&|<>=':
            self._eat()
            self.compileTerm()

        self._writeClosing("expression")

    def compileTerm(self):
        self._writeOpening("term")
        type_ = self.tokenizer.tokenType()

        if type_ in {"integerConstant", "stringConstant"} or \
                (type_ == "keyword" and self.tokenizer.keyword() in {"true", "false", "null", "this"}):
            self._eat()

        elif type_ == "symbol" and self.tokenizer.symbol() == '(':
            self._eat()
            self.compileExpression()
            self._eat()

        elif type_ == "symbol" and self.tokenizer.symbol() in '-~':
            self._eat()
            self.compileTerm()

        elif type_ == "identifier": # varName | varName [ ] | subroutineCall
            next_token = self.tokenizer.peek()

            if next_token == "[":
                self._eat()
                self.compileArray()
            elif next_token in {"(", "."}:
                self.compileSubroutineCall()
            else:
                self._eat()

        self._writeClosing("term")

    def compileSubroutineCall(self):
        self._eat() # subroutineName | className | varName

        # . subroutineName
        if self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ".":
            self._eat()
            self._eat()

        # ( exprList )
        self._eat()
        self.compileExpressionList()
        self._eat()

    def compileExpressionList(self):
        self._writeOpening("expressionList")

        # (expr(, expr)*)?
        if self.tokenizer.tokenType() != "symbol" or self.tokenizer.symbol() != ")":
            self.compileExpression()
            while self.tokenizer.tokenType() == "symbol" and self.tokenizer.symbol() == ",":
                self._eat()
                self.compileExpression()

        self._writeClosing("expressionList")