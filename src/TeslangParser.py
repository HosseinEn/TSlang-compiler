import ply.yacc as yacc
import logging
from TeslangLexer import *
from AST  import *
import sys




class FilePosition(object):
  def __init__(self, line):
    self.line = line

def getPosition(p):
    return FilePosition(p.lexer.lexer.lineno - 1)


class TeslangParser(object):
    def __init__(self):
        self.scanner = TeslangLexer()
        self.scanner.build()
    
    tokens = TeslangLexer.tokens


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
    def p_prog(self, p: yacc.YaccProduction):
        '''prog : empty
                | func prog'''
        if len(p) == 3:
            p[0] = Program(func=p[1], prog=p[2], pos=getPosition(p))

    # Rule 2
    def p_func(self, p: yacc.YaccProduction):
        '''func : DEF TYPE ID LPAREN flist RPAREN LBRACE body RBRACE
                | DEF TYPE ID LPAREN flist RPAREN RETURN expr SEMI'''
        # TODO  - potential bug , How about second rule? I'm just passing the expr as body
        p[0] = FunctionDef(rettype=p[2], name=p[3], fmlparams=p[5], body=p[8], pos=getPosition(p))

    # Rule 3
    def p_body(self, p: yacc.YaccProduction):
        '''body : empty 
                | stmt body'''
        if len(p) == 3:
            p[0] = Body(statement=p[1], body=p[2])

    # Rule 4
    def p_stmt(self, p: yacc.YaccProduction):    
        # '''stmt : expr SEMI                                
        #         | defvar SEMI                              
        #         | IF LPAREN expr RPAREN stmt               
        #         | IF LPAREN expr RPAREN stmt ELSE stmt     
        #         | WHILE LPAREN expr RPAREN stmt            
        #         | FOR LPAREN ID EQUALS expr TO expr RPAREN stmt
        #         | RETURN expr SEMI                         
        #         | LBRACE body RBRACE                   
        #         | func'''
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
        p[0] = ForInstruction(start_expr=p[5], end_expr=p[7], \
                                for_statement=p[9], pos=getPosition(p))

    def p_block(self, p: yacc.YaccProduction):
        '''block : LBRACE body RBRACE'''
        # TODO why not Body()?
        p[0] = p[2]

    def p_return_instr(self, p: yacc.YaccProduction):
        '''return_instr : RETURN expr'''
        # breakpoint()
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
        # TODO - potential bug
        if len(p) == 3:
            p[0] = ParametersList(parameters=[Parameter(type=p[1], id=p[2])])
        elif len(p) == 5:
            p[0] = ParametersList(parameters=p[4].parameters + [Parameter(type=p[1], id=p[2])])


    # Rule 7
    def p_clist(self, p: yacc.YaccProduction):
        '''clist : empty
                 | expr
                 | expr COMMA clist'''
        # TODO check this out after defining functionCall
        # this is same as expr list
        if len(p) == 2:
            exprs = [] if p[1] == [] else [p[1]]
            p[0] = ArgsList(exprs=exprs)
        elif len(p) == 4:
            p[0] = ArgsList(exprs=p[3].exprs + [p[1]])

        

    # Rule 9
    def p_expr(self, p: yacc.YaccProduction):    
        # '''expr : expr LBRACKET expr RBRACKET                
        #         | LBRACKET clist RBRACKET                    
        #         | expr QUESTIONMARK expr COLON expr
        #         | expr PLUS expr                   
        #         | expr MINUS expr                  
        #         | expr TIMES expr                  
        #         | expr DIVIDE expr                 
        #         | expr MODULO expr                 
        #         | expr GT expr                     
        #         | expr LT expr                     
        #         | expr EQ expr                     
        #         | expr LE expr                     
        #         | expr GE expr                     
        #         | expr NE expr                     
        #         | expr LOR expr                    
        #         | expr LAND expr                   
        #         | LNOT expr                        
        #         | PLUS expr                        
        #         | MINUS expr                       
        #         | ID                               
        #         | ID EQUALS expr                   
        #         | ID LPAREN clist RPAREN  
        #         | NUMBER                           
        #         | STRING                                    
        #     '''
        '''expr : vector_index               
                | expr_list                   
                | ternary_expr                
                | LNOT expr                        
                | PLUS expr                        
                | MINUS expr  
                | binary_expr                     
                | ID                               
                | assignment                   
                | function_call 
                | NUMBER                           
                | STRING'''
        # TODO what should be done for vector declaration?
        # TODO check vector out - expr [expr] and [clist]
        # breakpoint()
        if len(p) == 4 or len(p) == 3:
            p[0] = p[2]
        else:
            # TODO - potential bug
            if p.slice[1].type in ('NUMBER', 'STRING', 'ID'):
                p[0] = p.slice[1]
            else:
                p[0] = p[1]

    def p_expr_list(self, p: yacc.YaccProduction):
        '''expr_list : LBRACKET clist RBRACKET'''
        p[0] = ExprList(p[2])

    def p_vector_index(self, p: yacc.YaccProduction):
        '''vector_index : expr LBRACKET expr RBRACKET'''
        p[0] = VectorIndex(expr=p[1], index_expr=p[3], pos=getPosition(p))

    def p_assignment(self, p: yacc.YaccProduction):
        '''assignment : ID EQUALS expr'''
        p[0] = Assignment(id=p[1], expr=p[3], pos=getPosition(p))
        
    def p_ternary_expr(self, p: yacc.YaccProduction):
        '''ternary_expr : expr QUESTIONMARK expr COLON expr  '''
        p[0] = TernaryExpr(first_expr=p[1], second_expr=p[3], pos=getPosition(p))

    def p_function_call(self, p: yacc.YaccProduction):
        '''function_call : ID LPAREN clist RPAREN'''
        p[0] = FunctionCall(id=p[1], args=p[3], pos=getPosition(p))


    def p_binary_expr(self, p: yacc.YaccProduction):
        '''binary_expr : expr PLUS expr                   
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
                       | expr LAND expr'''
        p[0] = BinExpr(left=p[1], op=p[2], right=p[3], pos=getPosition(p))
        # logging.debug("Parsing function %s", p[2])

    # Rule 10
    def p_empty(self, p: yacc.YaccProduction):
        '''empty :'''
        p[0] = []


    def p_error(self, p):
        if p is not None:
            print(f'Syntax error at line {p.lineno} with token {p}')
        else:
            print('Unexpected end of input')


# if __name__ == "__main__":


    # # Set up a logging object
    # import logging
    # logging.basicConfig(
    #     level = logging.DEBUG,
    #     filename = "parselog.txt",
    #     filemode = "w",
    #     format = "%(filename)10s:%(lineno)4d:%(message)s"
    # )
    # log = logging.getLogger()

    # data = open(sys.argv[1] if len(sys.argv) == 2 else '../tests/test_input_file1.txt', 'r').read()
    # tParser = TeslangParser()
    # # parser = yacc.yacc(debug=True, debuglog=log)
    # parser = yacc.yacc(module=tParser, debug=True, write_tables=True)

    # ast = parser.parse(data, lexer=tParser.scanner)







