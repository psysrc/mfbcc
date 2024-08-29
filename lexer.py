import re
from enum import Enum, auto

class TokenType(Enum):
    KEYWORD = auto()
    OPERATOR = auto()
    IDENTIFIER = auto()
    INTEGER_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    CHAR_LITERAL = auto()
    PUNCTUATOR = auto()
    COMMENT = auto()
    WHITESPACE = auto()
    EOF = auto()

KEYWORDS = {
        "auto", "break", "case", "char", "const", "continue", "default", "do", "double",
        "else", "enum", "extern", "float", "for", "goto", "if", "int", "long", "register",
        "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef", "union",
        "unsigned", "void", "volatile", "while"
}

OPERATORS = {
        "+", "-", "*", "/", "%", "++", "--", "==", "!=", ">", "<", ">=", "<=", "&&", "||", "!", "&", "|", "^",
        "~", "<<", ">>", "=", "+=", "-=", "*=", "/="
}

PUNCTUATORS = {
        ";", ",", "(", ")", "{", "}", "[", "]"
}

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
        self.position = 0
        self.length = len(source_code)
    
    def next_char(self):
        if self.position < self.length:
            return self.source_code[self.position]
        return None

    def advance(self):
        self.position += 1

    def peek(self):
        if self.position + 1 < self.length:
            return self.source_code[self.position + 1]
        return None

    def skip_whitespace(self):
        while self.next_char() and self.next_char().isspace():
            self.advance()

    def skip_comment(self):
        if self.next_char() == '/' and self.peek() == '/':
            while self.next_char() != '\n':
                self.advance()
            self.advance()
        elif self.next_char() == '/' and self.peek() == '*':
            self.advance()
            self.advance()
            while not (self.next_char() == '*' and self.peek() == '/'):
                self.advance()
            self.advance()
            self.advance()

    def match_regex(self, pattern):
        match = re.match(pattern, self.source_code[self.position:])
        if match:
            self.position += match.end()
            return match.group(0)
        return None

    def tokenize(self):
        tokens = []
        while self.position < self.length:
            self.skip_whitespace()
            if self.next_char() is None:
                break

            if self.next_char() == '/' and (self.peek() == '/' or self.peek() == '*'):
                self.skip_comment()
                continue

            word = self.match_regex(r'[a-zA-Z_]\w*')
            if word:
                if word in KEYWORDS:
                    tokens.append((TokenType.KEYWORD, word))
                else:
                    tokens.append((TokenType.IDENTIFIER, word))
                continue

            number = self.match_regex(r'\d+(\.\d+)?')
            if number:
                if '.' in number:
                    tokens.append((TokenType.FLOAT_LITERAL, number))
                else:
                    tokens.append((TokenType.INTEGER_LITERAL, number))
                continue

            string = self.match_regex(r'"(\\.|[^"])*"')
            if string:
                tokens.append((TokenType.STRING_LITERAL, string))
                continue

            char_literal = self.match_regex(r"'(\\.|[^'])'")
            if char_literal:
                tokens.append((TokenType.CHAR_LITERAL, char_literal))
                continue

            for op in sorted(OPERATORS, key=len, reverse=True):
                if self.source_code.startswith(op, self.position):
                    tokens.append((TokenType.OPERATOR, op))
                    self.position += len(op)
                    break

            else:
                if self.next_char() in PUNCTUATORS:
                 tokens.append((TokenType.PUNCTUATOR, self.next_char()))
                 self.advance()
                else:
                    raise Exception(f"Unknown token: {self.next_char()}")

        tokens.append((TokenType.EOF, ""))
        return tokens
