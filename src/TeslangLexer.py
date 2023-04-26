from ply.lex import lex
import re


class TeslangLexer(object):
    def find_token_column(self, token):
        last_cr = self.lexer.lexdata.rfind('\n', 0, token.lexpos)
        if last_cr < 0:
            last_cr = 0
        return token.lexpos - last_cr

    def build(self):
        self.lexer = lex(object=self)

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        self.last_token = self.lexer.token()
        return self.last_token

    reserved = {
        'as': 'AS',
        'auto': 'AUTO',
        'break': 'BREAK',
        'case': 'CASE',
        'class': 'CLASS',
        'close': 'CLOSE',
        'const': 'CONST',
        'continue': 'CONTINUE',
        'def': 'DEF',
        'default': 'DEFAULT',
        'del': 'DEL',
        'else': 'ELSE',
        'except': 'EXCEPT',
        'False': 'ALSE',
        'for': 'FOR',
        'from': 'FROM',
        'global': 'GLOBAL',
        'if': 'IF',
        'import': 'IMPORT',
        'in': 'IN',
        'input': 'INPUT',
        'int': 'INT',
        'is': 'IS',
        'lambda': 'LAMBDA',
        'len': 'LEN',
        'length': 'LENGTH',
        'None': 'ONE',
        'nonlocal': 'NONLOCAL',
        'null': 'NULL',
        'open': 'OPEN',
        'pass': 'PASS',
        'raise': 'RAISE',
        'range': 'RANGE',
        'read': 'READ',
        'return': 'RETURN',
        'sizeof': 'SIZEOF',
        'static': 'STATIC',
        'str': 'STR',
        'struct': 'STRUCT',
        'switch': 'SWITCH',
        'to': 'TO',
        'True': 'RUE',
        'try': 'TRY',
        # 'type' : 'TYPE',
        'var': 'VAR',
        'vector': 'VECTOR',
        'void': 'VOID',
        'while': 'WHILE',
        'with': 'WITH',
        'write': 'WRITE'
    }

    tokens = [
        # Literals (identifier, integer constant, float constant, string constant)
        'ID', 'TYPE', 'NUMBER', 'STRING',

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
        'COMMA', 'PERIOD', 'SEMI', 'COLON', 'QUESTIONMARK'

    ] + list(reserved.values())

    t_ignore = ' \t'
    # Operators
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MODULO = r'%'
    t_OR = r'\|'
    t_AND = r'&'
    t_NOT = r'~'
    t_XOR = r'\^'
    t_LSHIFT = r'<<'
    t_RSHIFT = r'>>'
    t_LOR = r'\|\|'
    t_LAND = r'&&'
    t_LNOT = r'!'
    t_QUESTIONMARK = r'\?'
    t_LT = r'<'
    t_GT = r'>'
    t_LE = r'<='
    t_GE = r'>='
    t_EQ = r'=='
    t_NE = r'!='

    # Assignment operators
    t_EQUALS = r'='
    t_TIMESEQUAL = r'\*='
    t_DIVEQUAL = r'/='
    t_MODEQUAL = r'%='
    t_PLUSEQUAL = r'\+='
    t_MINUSEQUAL = r'-='

    # Increment/decrement
    t_INCREMENT = r'\+\+'
    t_DECREMENT = r'--'

    # Delimeters
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_COMMA = r','
    t_PERIOD = r'\.'
    t_SEMI = r';'
    t_COLON = r':'

    # def __init__(self) -> None:
    #     self.lexer = lex(module=self)

    # def tokenize(lexer, data):
    #     token_list = []
    #     lexer.input(data)
    #     while True:
    #         tok = lexer.token()
    #         if not tok:
    #             break
    #         token_list.append(tok)
    #         print(tok)
    #     return token_list

    def t_TYPE(self, t):
        r'\b(int|str|vector|null)\b'
        return t

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
        # Check for reserved words. If not reserved, it is an ID
        t.type = self.reserved.get(t.value, 'ID')
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
