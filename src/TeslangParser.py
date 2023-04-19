import ply.yacc as yacc
import logging
from TeslangLexer import *






def p_prog(p):
    '''prog : empty
            | func prog'''
    # p[0] = p[1]

def p_empty(p):
    '''empty :'''
    p[0] = []


def p_func(p):
    '''func : DEF type ID LPAREN flist RPAREN LBRACE body RBRACE
            | DEF type ID LPAREN flist RPAREN RETURN expr SEMI'''
    

def p_body(p):
    '''body : empty 
            | stmt body'''
    
def p_stmt(p):    
    '''stmt : expr SEMI                                
            | defvar SEMI                              
            | IF LPAREN expr RPAREN stmt               
            | IF LPAREN expr RPAREN stmt ELSE stmt     
            | WHILE LPAREN expr RPAREN stmt            
            | FOR LPAREN ID EQUALS expr TO expr RPAREN stmt
            | RETURN expr SEMI                         
            | LBRACE body RBRACE                   
            | func'''

def p_stmt_error(p: yacc.YaccProduction):
    '''stmt : error'''
    print("Syntax error in your statement at line %d!" % p.lineno(1)) 


def p_defvar(p):
    '''defvar : VAR type ID
              | VAR type ID EQUALS expr'''
    
def p_flist(p):
    '''flist : empty
             | type ID
             | type ID COMMA flist'''
    

def p_clist(p):
    '''clist : empty
             | expr
             | expr COMMA clist'''
    
def p_type(p):
    '''type : INT
            | STR
            | VECTOR
            | NULL'''

def p_expr(p):    
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

# def p_expr_error(p):
#     '''expr : error'''
#     print("Syntax error in print statement. Bad expression")
    
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





