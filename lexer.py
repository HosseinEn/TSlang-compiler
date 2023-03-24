from ply.lex import lex
from ply.yacc import yacc
import re



data = """

    def int main() {
        var str x = "hel\"lo";
    }

    # def int sum(vector numList) {
    #     var int result = 0;

    #     for (i = 0 to length(numList)) {
    #         result = result + numList[i];
    #     }
    #     # returning the result.
    #     return result;
    # }

    # def str concatinate(int lenghtOfString) {
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

print(data)







# --- Tokenizer

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
    #'List' : 'LIST',
    # 'or' : 'OR',
    # 'and' : 'AND',
    # 'not' : 'NOT',
}

tokens = [
    # Literals (identifier, integer constant, float constant, string constant, char const)
    'ID', 'TYPEID', 'NUMBER', 'STRING', 'CHARACTER',

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

# Identifiers
# t_ID = r'[A-Za-z_][A-Za-z0-9_]*'

# Integer literal
# t_INTEGER = r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'

# Floating literal
# t_FLOAT = r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'

# String literal - (x|y) where x shouldn't match \ , \n , "
t_STRING = r'\"([^\\\n]|(\\.))*?\"'
# t_STRING = r'\"([^\\\n\"]|(\\.))*\"'
# print("hel\"lo")

# def t_STRING(t):
#     r'"([^"\\]|\\.)*"'
#     t.value = re.sub(r'\\(")', r'\1', t.value[1:-1])
#     return t

# Character constant 'c' or L'c'
#t_CHARACTER = r'(L)?\'([^\\\n]|(\\.))*?\''

"""
def t_FLOAT(t):
    r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t
"""
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'ID')    # Check for reserved words. If not reserved, it is an ID
    return t

def t_COMMENT(t):
    r'\#.*'
    pass

# Ignored token with an action associated with it
def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

# Error handler for illegal characters
def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)

# Build the lexer object
lexer = lex()



lexer.input(data)

for tok in lexer:
    print(tok)





