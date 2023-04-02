from ply.lex import lex
import re


class Tokenizer:
    reserved = {
        'if' : 'IF',
        'else' : 'ELSE',
        'def' : 'DEF',
        'return' : 'RETURN',
        'int' : 'INT',
        'str' : 'STR',
        'vector' : 'VECTOR',
        'var' : 'VAR',
        'void' : 'VOID',
        'while' : 'WHILE',
        'for' : 'FOR',
        'break' : 'BREAK',
        'continue' : 'CONTINUE',
        'switch' : 'SWITCH',
        'length' : 'LENGTH',
        'case' : 'CASE',
        'default' : 'DEFAULT',
        'sizeof' : 'SIZEOF',
        'struct' : 'STRUCT',
        'static' : 'STATIC',
        'auto' : 'AUTO',
        'to' : 'TO',
        'const' : 'CONST',
        'class' : 'CLASS',
        'import' : 'IMPORT',
        'from' : 'FROM',
        'as' : 'AS',
        'pass' : 'PASS',
        'global' : 'GLOBAL',
        'nonlocal' : 'NONLOCAL',
        'lambda' : 'LAMBDA',
        'try' : 'TRY',
        'except' : 'EXCEPT',
        'raise' : 'RAISE',
        'with' : 'WITH',
        'del' : 'DEL',
        'in' : 'IN',
        'is' : 'IS',
        'True' : 'TRUE',
        'False' : 'FALSE',
        'None' : 'NONE',
        'print' : 'PRINT',
        'input' : 'INPUT',
        'range' : 'RANGE',
        'len' : 'LEN',
        'open' : 'OPEN',
        'close' : 'CLOSE',
        'read' : 'READ',
        'write' : 'WRITE',
        'type' : 'TYPE',
    }

    tokens = [
        # Literals (identifier, integer constant, float constant, string constant)
        'ID', 'TYPEID', 'NUMBER', 'STRING',

        # Operators (+,-,*,/,%,|,&,~,^,<<,>>, ||, &&, !, <, <=, >, >=, ==, !=)
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
        'OR', 'AND', 'NOT', 'XOR', 'LSHIFT', 'RSHIFT',
        'LOR', 'LAND', 'LNOT',
        'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',

        # Assignment (=, *=, /=, %=, +=, -=, 
        'EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL',

        # Increment/decrement (++,--)
        'INCREMENT', 'DECREMENT',

        # Delimeters ( ) [ ] { } , . ; :
        'LPAREN', 'RPAREN',
        'LBRACKET', 'RBRACKET',
        'LBRACE', 'RBRACE',
        'COMMA', 'PERIOD', 'SEMI', 'COLON',

    ] + list(reserved.values())

    t_ignore = ' \t'
    # Operators
    t_PLUS             = r'\+'
    t_MINUS            = r'-'
    t_TIMES            = r'\*'
    t_DIVIDE           = r'/'
    t_MODULO           = r'%'
    t_OR               = r'\|'
    t_AND              = r'&'
    t_NOT              = r'~'
    t_XOR              = r'\^'
    t_LSHIFT           = r'<<'
    t_RSHIFT           = r'>>'
    t_LOR              = r'\|\|'
    t_LAND             = r'&&'
    t_LNOT             = r'!'
    t_LT               = r'<'
    t_GT               = r'>'
    t_LE               = r'<='
    t_GE               = r'>='
    t_EQ               = r'=='
    t_NE               = r'!='

    # Assignment operators
    t_EQUALS           = r'='
    t_TIMESEQUAL       = r'\*='
    t_DIVEQUAL         = r'/='
    t_MODEQUAL         = r'%='
    t_PLUSEQUAL        = r'\+='
    t_MINUSEQUAL       = r'-='

    # Increment/decrement
    t_INCREMENT        = r'\+\+'
    t_DECREMENT        = r'--'


    # Delimeters
    t_LPAREN           = r'\('
    t_RPAREN           = r'\)'
    t_LBRACKET         = r'\['
    t_RBRACKET         = r'\]'
    t_LBRACE           = r'\{'
    t_RBRACE           = r'\}'
    t_COMMA            = r','
    t_PERIOD           = r'\.'
    t_SEMI             = r';'
    t_COLON            = r':'


    def __init__(self) -> None:
        self.lexer = lex(module=self)

    def tokenize(self, data):
        token_list = []
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            token_list.append(tok)
            print(tok)
        return token_list

    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t
    
    def t_STRING(self, t):
        # String literal - (x|y) where x shouldn't match \ , \n , ", '
        r'[\"\']([^\'\"\n\\]|(\\.))*?[\"\']'
        if t.value[0] != t.value[-1]:
            print(f'Illegal character {t.value[0]!r} at line {t.lineno}')
            t.lexer.skip(1)
        t.value = re.sub(r'\\', r'', t.value[1:-1])
        return t

    def t_ID(self, t):
        r'[A-Za-z_][A-Za-z0-9_]*'
        t.type = self.reserved.get(t.value, 'ID')    # Check for reserved words. If not reserved, it is an ID
        return t

    def t_COMMENT(self, t):
        r'\#.*'
        pass

    # Ignored token with an action associated with it
    def t_ignore_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')

    # Error handler for illegal characters
    def t_error(self, t):
        print(f'Illegal character {t.value[0]!r} at line {t.lineno}')
        t.lexer.skip(1)



data = """
    # int main (void) {
    #     int x = a546f;
    #     int A[54a] = 5;
    #     'A' = x;
    #     if (x 10 {
    #         retur 5;
    #     }
    # }
    # def int main() {
    #     var str text = "I was there. \\"yellow! I will be there\\" Sasha said. that was all."
    # }

    # def int sum(vector numList) {
    #     var int result = 0;

    #     for (i = 0 to length(numList)) {
    #         result = result + numList[i];
    #     }
    #     # returning the result.
    #     return result;
    # }

    # def str concatenate(int lengthOfString) {
    #     int i = 0;
    #     var vector b = [1, 2, 3, 4];
    #     while (i++ < lengthOfString) {
    #         print(x)
    #     }
    # }

    # recursive combination function
    # def void combination(int n, int r, int index, vector data, int i) { 
    #     # Current combination is ready to be printed, print it
    #     if (index == r) {
    #         for (j = 0 to r) {
    #             print(data[j]);
    #         }
    #         print("jjjj");
    #         return;
    #     }
    #     var str x = "hello";
    #     # When no more elements are there to put in data[]
    #     if (i >= n) {
    #         return;
    #     }
    #     # current is included, put next at next location
    #     data[index] = i;
    #     combination(n, r, index + 1, data, i + 1);
    #     # current is excluded, replace it with next (Note that
    #     # i+1 is passed, but index is not changed)
    #     combination(n, r, index, data, i + 1);
    # }

"""
tokenizer = Tokenizer()
token_list = tokenizer.tokenize(data)



