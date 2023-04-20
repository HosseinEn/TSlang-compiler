import ply.yacc as yacc
import logging
from TeslangLexer import *


precedence = (
    ('left', 'LOR'),
    ('left', 'LAND'),
    ('left', 'OR', 'XOR', 'AND'),
    ('left', 'EQ', 'NE', 'GT', 'LT', 'GE', 'LE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('left', 'LBRACKET'),
    ('left', 'LPAREN'),
    ('left', 'QUESTIONMARK', 'COLON'),
    ('left', 'EQUALS', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL'),
    ('left', 'COMMA'),
    ('right', 'LNOT', 'NOT', 'INCREMENT', 'DECREMENT'),
)


# Rule 1
def p_prog(p: yacc.YaccProduction):
    '''prog : empty
            | func prog'''
    # if len(3):
    #     p[0] = p[1] + [p[2]]

# def p_prog_error(p: yacc.YaccProduction):
#     '''prog : error'''
#     print("Syntax error in your program at line %d!" % p.lineno(1))

# Rule 2
def p_func(p: yacc.YaccProduction):
    '''func : DEF type ID LPAREN flist RPAREN LBRACE body RBRACE
            | DEF type ID LPAREN flist RPAREN RETURN expr SEMI'''

# def p_func_error(p: yacc.YaccProduction):
#     '''func : error'''
#     print("Syntax error in your function declaration  at line %d!" % p.lineno(1))

# Rule 3
def p_body(p: yacc.YaccProduction):
    '''body : empty 
            | stmt body'''
    
# def p_body_error(p: yacc.YaccProduction):
#     '''body : error'''
#     print("Syntax error in your function body at line %d!" % p.lineno(1))
    
# Rule 4
def p_stmt(p: yacc.YaccProduction):    
    '''stmt : expr SEMI                                
            | defvar SEMI                              
            | IF LPAREN expr RPAREN stmt               
            | IF LPAREN expr RPAREN stmt ELSE stmt     
            | WHILE LPAREN expr RPAREN stmt            
            | FOR LPAREN ID EQUALS expr TO expr RPAREN stmt
            | RETURN expr SEMI                         
            | LBRACE body RBRACE                   
            | func'''

# def p_stmt_error(p: yacc.YaccProduction):
#     '''stmt : error'''
#     print("Syntax error in your statement at line %d!" % p.lineno(1)) 

# Rule 5
def p_defvar(p: yacc.YaccProduction):
    '''defvar : VAR type ID
              | VAR type ID EQUALS expr'''

# def p_defvar_error(p: yacc.YaccProduction):
#     '''defvar : error'''
#     print("Syntax error in your variable declaration at line %d!" % p.lineno(1))
    
# Rule 6
def p_flist(p: yacc.YaccProduction):
    '''flist : empty
             | type ID
             | type ID COMMA flist'''
    
# def p_flist_error(p: yacc.YaccProduction):
#     '''flist : error'''
#     print("Syntax error in your function parameter list at line %d!" % p.lineno(1))

# Rule 7
def p_clist(p: yacc.YaccProduction):
    '''clist : empty
             | expr
             | expr COMMA clist'''
    
# def p_clist_error(p: yacc.YaccProduction):
#     '''clist : error'''
#     print("Syntax error in your function call parameter list at line %d!" % p.lineno(1))

# Rule 8 
def p_type(p: yacc.YaccProduction):
    '''type : INT
            | STR
            | VECTOR
            | NULL'''

# def p_type_error(p: yacc.YaccProduction):
#     '''type : error'''
#     print("Invalid type declaration at line %d!" % p.lineno(1))

# Rule 9
def p_expr(p: yacc.YaccProduction):    
    '''expr : expr LBRACKET expr RBRACKET                
            | LBRACKET clist RBRACKET                    
            | expr QUESTIONMARK expr COLON expr
            | expr PLUS expr                   
            | expr MINUS expr                  
            | expr TIMES expr                  
            | expr DIVIDE expr                 
            | expr MODULO expr                 
            | expr GT expr                     
            | expr LT expr                     
            | expr EQ expr                     
            | expr LE expr                     
            | expr GE expr                     
            | expr NE expr                     
            | expr LOR expr                    
            | expr LAND expr                   
            | LNOT expr                        
            | PLUS expr                        
            | MINUS expr                       
            | ID                               
            | ID EQUALS expr                   
            | ID LPAREN clist RPAREN  
            | NUMBER                           
            | STRING                                    
        '''

# def p_expr_error(p: yacc.YaccProduction):
#     '''expr : error'''
#     print("Syntax error in your expression at line %d!" % p.lineno(1))

# Rule 10
def p_empty(p: yacc.YaccProduction):
    '''empty :'''
    p[0] = []


def p_error(p):
    print(f'Syntax error at line {p.lineno} with token {p}')



data = open('../tests/test_input_file.txt', 'r').read()


logging.basicConfig(
    level=logging.DEBUG,
    filename="../logs/parselog.txt",
    filemode="w",
    format="%(filename)10s:%(lineno)4d:%(message)s"
)

log = logging.getLogger()



lexer = lex()
parser = yacc.yacc(debug=True, debuglog=log)

parser.parse(data, lexer)





