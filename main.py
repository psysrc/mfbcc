from lexer import Lexer
from parser import Parser

if __name__ == "__main__":
    source_code = """
    int main(void) {
        int a = 10;
        float b = 3.14;
        char c = 'A';
        if (a > b) {
            printf("a is greater than b\\n");
        } else {
            printf("a is not greater than b\\n");
        }

        return 0;
    }
    """
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    # Optionally, you can print or inspect the AST
    print(ast)
