import ply.yacc as yacc
from TeslangLexer import *
from AST import *
from colors import bcolors
import control_flags

class FilePosition(object):
    def __init__(self, line):
        self.line = line


def getPosition(p):
    return FilePosition(p.lexer.lexer.lineno - 1)


class TeslangParser(object):
    def __init__(self, pre_parse=False):
        self.pre_parse = pre_parse
        self.scanner = TeslangLexer()
        self.scanner.build()

    tokens = TeslangLexer.tokens

    precedence = (
        ('nonassoc', 'ASSEXPR'),
        ('left', 'LOR'),
        ('left', 'LAND'),
        ('left', 'OR', 'XOR', 'AND'),
        ('left', 'EQ', 'NE', 'GT', 'LT', 'GE', 'LE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'MODULO'),
        ('right', 'UMINUS'),
        ('left', 'QUESTIONMARK', 'COLON'),
        ('nonassoc', 'DBLEQ'),
        ('left', 'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL'),
        ('left', 'COMMA'),
        ('right', 'EQUALS', 'LNOT', 'NOT', 'INCREMENT', 'DECREMENT'),  # EQUALS: =, EQ: ==
    )

    # Rule 1
    def p_prog(self, p: yacc.YaccProduction):
        '''prog : empty
                | func prog'''
        if len(p) == 3:
            p[0] = Program(func=p[1], prog=p[2], pos=getPosition(p))

    # Rule 2
    def p_func(self, p: yacc.YaccProduction):
        '''func : DEF TYPE ID LPAREN flist RPAREN LBRACE body RBRACE
                | DEF TYPE ID LPAREN flist RPAREN RETURN expr SEMI'''
        if isinstance(p[8], Body) or p[8] is None:
            p[0] = FunctionDef(rettype=p[2], name=p[3], fmlparams=p[5], body=p[8], pos=getPosition(p))
        else:
            p[0] = BodyLessFunctionDef(rettype=p[2], name=p[3], fmlparams=p[5], expr=p[8], pos=getPosition(p))

    def p_func_parameter_error(self, p):
        '''func : DEF TYPE ID LPAREN error RPAREN LBRACE body RBRACE'''
        p[0] = FunctionDef(rettype=p[2], name=p[3], fmlparams=None, body=p[8], pos=getPosition(p))
        self.handle_error('function definition', p[5])

    def p_func_missing_return_type_error(self, p):
        '''func : DEF error ID LPAREN flist RPAREN LBRACE body RBRACE'''
        p[0] = FunctionDef(rettype='int', name=p[3], fmlparams=p[5], body=p[8], pos=getPosition(p))
        self.handle_error('function return type', p[2])

    # Rule 3
    def p_body(self, p: yacc.YaccProduction):
        '''body : empty 
                | stmt body'''
        if len(p) == 3:
            p[0] = Body(statement=p[1], body=p[2])

    # Rule 4
    def p_stmt(self, p: yacc.YaccProduction):
        '''stmt : expr SEMI                                
                | defvar SEMI
                | return_instr SEMI
                | single_if             
                | if_with_else
                | while_loop             
                | for_loop 
                | block                  
                | func'''
        p[0] = p[1]

    def p_stmt_error(self, p):
        '''stmt : error SEMI
                | error'''
        self.handle_error('statement', p[1])

    def p_single_if(self, p: yacc.YaccProduction):
        '''single_if : IF LPAREN expr RPAREN stmt'''
        p[0] = IfOrIfElseInstruction(cond=p[3], if_statement=p[5], \
                                     else_statement=None, pos=getPosition(p))

    def p_if_with_else(self, p: yacc.YaccProduction):
        '''if_with_else : IF LPAREN expr RPAREN stmt ELSE stmt'''
        p[0] = IfOrIfElseInstruction(cond=p[3], if_statement=p[5], \
                                     else_statement=p[7], pos=getPosition(p))

    def p_while_loop(self, p: yacc.YaccProduction):
        '''while_loop : WHILE LPAREN expr RPAREN stmt'''
        p[0] = WhileInstruction(cond=p[3], while_statement=p[5], pos=getPosition(p))

    def p_for_loop(self, p: yacc.YaccProduction):
        '''for_loop : FOR LPAREN ID EQUALS expr TO expr RPAREN stmt'''
        p[0] = ForInstruction(id=p[3], start_expr=p[5], end_expr=p[7], \
                              for_statement=p[9], pos=getPosition(p))

    def p_block(self, p: yacc.YaccProduction):
        '''block : LBRACE body RBRACE'''
        p[0] = Block(body=p[2])

    def p_return_instr(self, p: yacc.YaccProduction):
        '''return_instr : RETURN expr'''
        p[0] = ReturnInstruction(expr=p[2], pos=getPosition(p))

    # Rule 5
    def p_defvar(self, p: yacc.YaccProduction):
        '''defvar : VAR TYPE ID
                  | VAR TYPE ID EQUALS expr'''
        if len(p) == 4:
            p[0] = VariableDecl(type=p[2], id=p[3], expr=None, pos=getPosition(p))
        elif len(p) == 6:
            p[0] = VariableDecl(type=p[2], id=p[3], expr=p[5], pos=getPosition(p))

    # Rule 6
    def p_flist(self, p: yacc.YaccProduction):
        '''flist : empty
                | TYPE ID
                | TYPE ID COMMA flist'''
        if len(p) == 3:
            p[0] = ParametersList(parameters=[Parameter(type=p[1], id=p[2])])
        elif len(p) == 5:
            p[0] = ParametersList(parameters=p[4].parameters + [Parameter(type=p[1], id=p[2])])

    def p_flist_error(self, p):
        '''flist : error ID COMMA flist
                 | TYPE error COMMA flist
                 | TYPE ID COMMA error'''
        p[0] = ParametersList(parameters=[])
        for i in range(1, len(p)):
            if p[i].__class__.__name__ == 'LexToken':
                self.handle_error('function parameters list', p[i])
                break

    # Rule 7
    def p_clist(self, p: yacc.YaccProduction):
        '''clist : empty
                 | expr
                 | expr COMMA clist'''
        if len(p) == 2:
            exprs = [] if p[1] == [] else [p[1]]
            p[0] = ExprList(exprs=exprs)
        elif len(p) == 4:
            p[0] = ExprList(exprs=p[3].exprs + [p[1]])

    # Rule 9
    def p_expr(self, p: yacc.YaccProduction):
        '''expr : operation_on_list               
                | expr_list                   
                | ternary_expr                
                | LNOT expr                        
                | PLUS expr                        
                | MINUS expr %prec UMINUS
                | binary_expr                     
                | ID                               
                | assignment                   
                | function_call 
                | NUMBER                           
                | STRING'''
        if len(p) == 4 or len(p) == 3:
            if p[1] == '-':
                p[2].value = -p[2].value
            elif p[1] == '!':
                p[2].value = 0 if p[2].value else 1
            p[0] = p[2]
        else:
            if p.slice[1].type in ('NUMBER', 'STRING', 'ID'):
                p[0] = p.slice[1]
            else:
                p[0] = p[1]

    def p_expr_list(self, p: yacc.YaccProduction):
        '''expr_list : LBRACKET clist RBRACKET'''
        p[0] = p[2]

    def p_operation_on_list(self, p: yacc.YaccProduction):
        '''operation_on_list : expr LBRACKET expr RBRACKET
                             | ID LBRACKET expr RBRACKET'''
        p[0] = OperationOnList(expr=p[1], index_expr=p[3], pos=getPosition(p))

    def p_assignment(self, p: yacc.YaccProduction):
        '''assignment : ID EQUALS expr %prec ASSEXPR
                      | ID LBRACKET expr RBRACKET EQUALS expr'''
        if len(p) == 4:
            p[0] = Assignment(id=p[1], expr=p[3], pos=getPosition(p))
        else:
            p[0] = VectorAssignment(id=p[1], index_expr=p[3], expr=p[6], pos=getPosition(p))

    def p_ternary_expr(self, p: yacc.YaccProduction):
        '''ternary_expr : expr QUESTIONMARK expr COLON expr  '''
        p[0] = TernaryExpr(cond=p[1], first_expr=p[3], second_expr=p[5], pos=getPosition(p))

    def p_function_call(self, p: yacc.YaccProduction):
        '''function_call : ID LPAREN clist RPAREN'''
        p[0] = FunctionCall(id=p[1], args=p[3], pos=getPosition(p))

    def p_function_call_error(self, p):
        '''function_call : ID LPAREN error RPAREN'''
        self.handle_error('function call', p[3])

    def p_binary_expr(self, p: yacc.YaccProduction):
        '''binary_expr : expr PLUS expr                   
                       | expr MINUS expr                  
                       | expr TIMES expr                  
                       | expr DIVIDE expr                 
                       | expr MODULO expr                 
                       | expr GT expr                     
                       | expr LT expr                     
                       | expr EQ expr %prec DBLEQ                
                       | expr LE expr                     
                       | expr GE expr                     
                       | expr NE expr                     
                       | expr LOR expr                    
                       | expr LAND expr'''
        p[0] = BinExpr(left=p[1], op=p[2], right=p[3], pos=getPosition(p))
        # logging.debug("Parsing function %s", p[2])

    # Rule 10
    def p_empty(self, p: yacc.YaccProduction):
        '''empty :'''
        p[0] = []

    def handle_error(self, where, p):
        if not self.pre_parse:
            print(bcolors.FAIL + f'Syntax error' + f' at line {p.lineno}, column {self.scanner.find_token_column(p)}' +
                  bcolors.ENDC + f' in {where} with token {p}')

    def p_error(self, p):
        control_flags.parser_failed = True
        if p is not None:
            pass
        else:
            print('Unexpected end of input')
