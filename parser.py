from lexer import TokenType

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class VariableDeclaration(ASTNode):
    def __init__(self, var_type, identifier, initializer):
        self.var_type = var_type
        self.identifier = identifier
        self.initializer = initializer

class Assignment(ASTNode):
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

class IfStatement(ASTNode):
    def __init__(self, condition, true_branch, false_branch=None):
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

class BinaryOperation(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value

class FunctionCall(ASTNode):
    def __init__(self, identifier, arguments):
        self.identifier = identifier
        self.arguments = arguments

    def __repr__(self):
        return f"FunctionCall(identifier={self.identifier}, arguments={self.arguments})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def peek_token(self):
        if self.position + 1 < len(self.tokens):
            return self.tokens[self.position + 1]
        return None

    def advance(self):
        self.position += 1

    def match(self, *token_types):
        if self.current_token() and self.current_token()[0] in token_types:
            self.advance()
            return True
        return False

    def parse(self):
        statements = []
        while self.current_token()[0] != TokenType.EOF:
            statement = self.parse_statement()
            if statement is not None:  # Only add non-None statements
                statements.append(statement)
            else:
                self.advance()  # Ensure we advance if no statement is returned
        return Program(statements)

    def parse_statement(self):
        # Check for block end
        if self.current_token() and self.current_token()[0] == TokenType.PUNCTUATOR and self.current_token()[1] == '}':
            self.advance()  # Skip '}'
            return None

        # Variable declaration
        if self.match(TokenType.KEYWORD) and self.current_token()[1] == 'int':
            return self.parse_variable_declaration()

        # If statement
        elif self.match(TokenType.KEYWORD) and self.current_token()[1] == 'if':
            return self.parse_if_statement()

        # Assignment or function call
        elif self.current_token() and self.current_token()[0] == TokenType.IDENTIFIER:
            if self.peek_token() and self.peek_token()[0] == TokenType.PUNCTUATOR and self.peek_token()[1] == '(':
                return self.parse_function_call()
            else:
                return self.parse_assignment()

        # Unexpected token
        else:
            raise Exception(f"Unexpected token in statement: {self.current_token()}")

    def parse_variable_declaration(self):
        var_type = self.tokens[self.position - 1][1]
        identifier = self.tokens[self.position][1]
        self.advance()
        self.match(TokenType.OPERATOR)  # Skip '='
        initializer = self.parse_expression()
        self.match(TokenType.PUNCTUATOR)  # Skip ';'
        return VariableDeclaration(var_type, identifier, initializer)

    def parse_assignment(self):
        # Save the identifier
        identifier = self.tokens[self.position - 1][1]

        # Expect '=' operator
        if not self.match(TokenType.OPERATOR) or self.current_token()[1] != '=':
            raise Exception(f"Expected '=', got {self.current_token()}")

        self.advance()  # Skip '='

        # Parse the value expression
        value = self.parse_expression()

        # Expect a semicolon to terminate the assignment statement
        if not self.match(TokenType.PUNCTUATOR) or self.current_token()[1] != ';':
            raise Exception(f"Expected ';' after assignment, got {self.current_token()}")

        self.advance()  # Skip ';'

        return Assignment(identifier, value)

    def parse_if_statement(self):
        self.match(TokenType.PUNCTUATOR)  # Skip '('
        condition = self.parse_expression()
        self.match(TokenType.PUNCTUATOR)  # Skip ')'
        true_branch = self.parse_block()
        false_branch = None
        if self.match(TokenType.KEYWORD) and self.current_token()[1] == 'else':
            false_branch = self.parse_block()
        return IfStatement(condition, true_branch, false_branch)

    def parse_block(self):
        statements = []
        self.match(TokenType.PUNCTUATOR)  # Skip '{'

        while not (self.current_token()[0] == TokenType.PUNCTUATOR and self.current_token()[1] == '}'):
            statement = self.parse_statement()
            if statement is not None:
                statements.append(statement)

            # Check for EOF to avoid infinite loop
            if self.current_token()[0] == TokenType.EOF:
                raise Exception("Unexpected end of file while parsing block")

        self.match(TokenType.PUNCTUATOR)  # Skip '}'
        return statements

    def parse_expression(self):
        # Start with parsing the primary expression
        left = self.parse_primary()

        while self.current_token() and self.current_token()[0] == TokenType.OPERATOR:
            operator = self.current_token()[1]
            self.advance()
            right = self.parse_primary()  # Continue parsing the right-hand side of the operation
            left = BinaryOperation(left, operator, right)

        return left

    def parse_function_call(self):
        identifier = self.tokens[self.position - 1][1]  # Identifier should be the token before '('
        self.advance()  # Skip '('
        arguments = []

        while self.current_token() and not (self.current_token()[0] == TokenType.PUNCTUATOR and self.current_token()[1] == ')'):
            print(f"DEBUG: Parsing argument in function call: {self.current_token()}")
            arguments.append(self.parse_expression())

            # Handle commas between arguments
            if self.current_token() and self.current_token()[0] == TokenType.PUNCTUATOR and self.current_token()[1] == ',':
                self.advance()  # Skip ','

        if self.current_token() and self.current_token()[0] == TokenType.PUNCTUATOR and self.current_token()[1] == ')':
            self.advance()  # Skip ')'
        else:
            raise Exception(f"Expected closing parenthesis, got {self.current_token()}")

        return FunctionCall(identifier, arguments)

        return FunctionCall(identifier, arguments)

    def parse_primary(self):
        token = self.current_token()
        print(f"DEBUG: Entering parse_primary with token: {token}")

        if token[0] == TokenType.INTEGER_LITERAL or token[0] == TokenType.FLOAT_LITERAL:
            self.advance()
            return Literal(token[1])

        elif token[0] == TokenType.IDENTIFIER:
            identifier = token[1]
            self.advance()
            # Check for function call after identifier
            if self.current_token() and self.current_token()[0] == TokenType.PUNCTUATOR and self.current_token()[1] == '(':
                return self.parse_function_call()
            return Literal(identifier)  # Return identifier wrapped in a Literal for consistency

        elif token[0] == TokenType.STRING_LITERAL or token[0] == TokenType.CHAR_LITERAL:
            self.advance()
            return Literal(token[1])

        elif token[0] == TokenType.PUNCTUATOR and token[1] == '(':
            self.advance()  # Skip '('
            expr = self.parse_expression()
            if self.current_token() and self.current_token()[0] == TokenType.PUNCTUATOR and self.current_token()[1] == ')':
                self.advance()  # Skip ')'
                return expr
            else:
                raise Exception(f"Expected closing parenthesis, got {self.current_token()}")

        else:
            raise Exception(f"Unexpected token: {token}")
