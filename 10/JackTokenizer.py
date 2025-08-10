import re

KEYWORDS = {
    "class", "constructor", "function", "method", "field", "static", "var",
    "int", "char", "boolean", "void", "true", "false", "null", "this",
    "let", "do", "if", "else", "while", "return"
}

SYMBOLS = set('{}()[].,;+-*/&|<>=~')

class JackTokenizer:
    def __init__(self, input_file):
        with open(input_file, 'r') as f:
            code = f.read()

        clean_code = self._clean(code)
        self.tokens = self._tokenize(clean_code)
        self.index = 1
        self.current_token = self.tokens[0]
        self.tokens_len = len(self.tokens)

    def hasMoreTokens(self):
        return self.index < self.tokens_len

    def advance(self):
        self.current_token = self.tokens[self.index]
        self.index += 1

    def peek(self):
        if self.hasMoreTokens():
            return self.tokens[self.index]
        return None

    def tokenType(self):
        token = self.current_token
        if token in KEYWORDS:
            return "keyword"
        elif token in SYMBOLS:
            return "symbol"
        elif token.isdigit():
            return "integerConstant"
        elif token.startswith('"') and token.endswith('"'):
            return "stringConstant"
        else:
            return "identifier"

    def keyword(self):
        return self.current_token

    def symbol(self):
        return self.current_token

    def identifier(self):
        return self.current_token

    def intVal(self):
        return int(self.current_token)

    def stringVal(self):
        return self.current_token.strip('"')

    def _tokenize(self, code):
        """ Returns list of tokens, ignoring whitespace """

        pattern = re.compile(
            r'"[^"\n]*"' # stringConstant
            r'|[\{\}\(\)\[\]\.\,\;\+\-\*\/\&\|\<\>\=\~]' # symbol
            r'|[A-Za-z_]\w*' # identifier & keyword
            r'|\d+' # integerConstant
        )
        return pattern.findall(code)

    def _clean(self, code):
        # /* ... */ and /** ... */ comments
        code = re.sub(r'/\*\*?.*?\*/', '', code, flags=re.DOTALL)
        # // comments
        code = re.sub(r'//.*', '', code)
        return code