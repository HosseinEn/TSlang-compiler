from SymbolTable import *
from AST import *
from enum import Enum

# class VarType(Enum):
#     NUMBER = 'int'
#     STRING = 'str'

#     def cast_var(self, var):
#         if var == VarType.NUMBER:
#             return 'int'
#         elif var == VarType.STRING:
#             return 'str'

def cast_var(var):
    if var == 'NUMBER':
        return 'int'
    elif var == 'STRING':
        return 'str'

class TeslangSemanticChecker(object):
    def __init__(self):
        pass
        # self.ttype = Ttype()

    def handle_error(self, pos, msg):
        print('Line ' + str(pos.line) + ': ' + msg)

    def visit_Program(self, node, table):
        if table is None:
            table = SymbolTable(None, None)
        # node.ext_decls.accept(self, table)
        node.func.accept(table)
        if node.prog:
            node.prog.accept(table)

    def visit_FunctionDef(self, node, parent_table):
        funcSymbol = FunctionSymbol(node.rettype, node.name, node.fmlparams)

        if not parent_table.put(funcSymbol):
            self.handle_error(node.pos, 'Function \'' +
                              node.name + '\' already defined')
        # breakpoint()
        # table.print_symbols()
        # print('-----------')

        child_table = SymbolTable(parent_table, funcSymbol)
        # breakpoint()
        if node.fmlparams:
            for param in node.fmlparams.parameters:
                varSymbol = VariableSymbol(param.type, param.id)
                if not child_table.put(varSymbol):
                    self.handle_error(
                        node.pos, 'Parameter \'' + param.id + '\' already defined')

        node.body.accept(child_table)

    def visit_Body(self, node, table):
        # className = node.statement.__class__.__name__
        # meth = getattr(TeslangSemanticChecker(), 'visit_' + className, None)

        if node.statement:
            node.statement.accept(table)
        if node.body:
            node.body.accept(table)

    def visit_FunctionCall(self, node, table):
        # Searching for the called function in the symbol table
        symbol_table_search_res = table.get(node.id)
        if symbol_table_search_res is None:
            self.handle_error(node.pos, 'Function \'' +
                              node.id + '\' not defined but called')

        elif symbol_table_search_res.__class__.__name__ == 'VariableSymbol':
            self.handle_error(node.pos, 'Variable \'' +
                              node.id + '\' used as function')
        else:
            funcSymbol = symbol_table_search_res
            if len(node.args.exprs) != len(funcSymbol.params.parameters):
                self.handle_error(
                    node.pos, 'Function \'' + node.id + '\' called with wrong number of arguments')
            else:
                for i, expr in enumerate(node.args.exprs):
                    param = funcSymbol.params.parameters[i]
                    # arg.accept(table)
                    # breakpoint()
                    if expr.__class__.__name__ == 'LexToken':
                        if expr.type == 'ID':
                            arg_id_search_res = table.get(expr.value)
                            if arg_id_search_res is None:
                                self.handle_error(
                                    node.pos, 'Variable \'' + expr.value + '\' not defined but used as argument')
                            else:
                                # TODO - test this
                                if arg_id_search_res.type != param.type:
                                    self.handle_error(node.pos, 'Function \'' + node.id + '\' called with wrong type of arguments in ' +
                                                    str(len(node.args.exprs)-i) + '. expected \'' + param.type + '\' but got \'' + arg_id_search_res.type + '\'')
                        elif expr.type == 'NUMBER':
                            if param.type != 'int':
                                self.handle_error(node.pos, 'Function \'' + node.id + '\' called with wrong type of arguments in ' +
                                                  str(len(node.args.exprs)-i) + '. expected \'' + param.type + '\' but got \'int\'')
                        else:
                            if param.type != 'str':
                                self.handle_error(node.pos, 'Function \'' + node.id + '\' called with wrong type of arguments in ' +
                                                  str(len(node.args.exprs)-i) + '. expected \'' + param.type + '\' but got \'str\'')
                    elif expr.__class__.__name__ == 'ExprList':
                        if param.type != 'vector':
                            self.handle_error(node.pos, 'Function \'' + node.id + '\' called with wrong type of arguments in ' +
                                              str(len(node.args.exprs)-i) + '. expected \'' + param.type + '\' but got \'vector\'')
                    else:
                        expr.accept(table)

    def visit_BinExpr(self, node, table):
        leftClassName = node.left.__class__.__name__
        rightClassName = node.right.__class__.__name__
        if leftClassName != 'LexToken' and leftClassName != 'ExprList':
            node.left.accept(table)
        if rightClassName != 'LexToken' and rightClassName != 'ExprList':
            node.right.accept(table)            
        if leftClassName == 'ExprList' or rightClassName == 'ExprList':
            self.handle_error(node.pos, 'Vector operations not supported')
        if leftClassName == 'LexToken' and rightClassName == 'LexToken':
            if node.op in ('*', '/', '%', '+', '-'): # , '<', '>', '<=', '>=', '==', '!=', '&&', '||'):
                if node.left.type == 'NUMBER' and node.right.type == 'NUMBER':
                    pass
                elif node.left.type == 'ID' or node.right.type == 'ID':
                    leftIsNumber = False if node.left.type != 'NUMBER' else True
                    rightIsNumber = False if node.right.type != 'NUMBER' else True
                    if node.left.type == 'ID':
                        leftSymbol = table.get(node.left.value)
                        if leftSymbol is None:
                            self.handle_error(node.pos, 'Variable \'' + node.left.value + '\' not defined but used in binary expression')
                        elif leftSymbol.type == 'int':
                            leftIsNumber = True
                    if node.right.type == 'ID':
                        rightSymbol = table.get(node.right.value)
                        if rightSymbol is None:
                            self.handle_error(node.pos, 'Variable \'' + node.right.value + '\' not defined but used in binary expression')
                        elif rightSymbol.type == 'int':
                            rightIsNumber = True
                    if leftIsNumber and rightIsNumber:
                        pass
                    else:
                        self.handle_error(node.pos, 'Type mismatch in binary expression. *, /, %, +, - can only be used with numbers')                          
                else:
                    self.handle_error(node.pos, 'Type mismatch in binary expression. *, /, %, +, - can only be used with numbers')
            elif node.op in ('<', '>', '<=', '>=', '==', '!='):
                ################################################# handle this 
                pass


    def visit_VariableDecl(self, node, table):
        varSymbol = VariableSymbol(node.id, node.type)

        if not table.put(varSymbol):
            self.handle_error(node.pos, 'Variable \'' + node.id + '\' already defined')

        if node.expr.__class__.__name__ == 'LexToken':
            if node.type != cast_var(node.expr.type):
                self.handle_error(node.pos, 'Type mismatch in variable declaration. Expected \'' + node.type 
                                  + '\' but got \'' + cast_var(node.expr.type) + '\'')
        elif node.expr.__class__.__name__ == 'ExprList':
            if node.type != 'vector':
                self.handle_error(node.pos, 'Type mismatch in variable declaration. Expected \'' + node.type 
                                  + '\' but got \'vector\'')
        elif node.expr.__class__.__name__ == 'FunctionCall':
            node.expr.accept(table)
            funcSymbol = table.get(node.expr.id)
            if funcSymbol:
                if funcSymbol.rettype != node.type:
                    self.handle_error(node.pos, 'Type mismatch in variable declaration. Expected \'' + node.type 
                                      + '\' but function \'' + node.expr.id + '\' returns \'' + funcSymbol.rettype + '\'')
    
    def visit_Assignment(self, node, table):
        pass






    def visit_ExprList(self, node, table):
        pass

    def visit_FunctionDefList(self, node, table):
        pass

    def visit_Statement(self, node, table):
        pass

    def visit_ReturnInstruction(self, node, table):
        pass

    def visit_IfOrIfElseInstruction(self, node, table):
        pass

    def visit_WhileInstruction(self, node, table):
        pass

    def visit_ForInstruction(self, node, table):
        pass

    def visit_ContinueInstruction(self, node, table):
        pass    
    
    def visit_BreakInstruction(self, node, table):
        pass    
    
    # def visit_CompoundInstructions(self, node, table):
        # pass

    def visit_Assignment(self, node, table):
        pass

    def visit_VectorIndex(self, node, table):
        pass
        
    def visit_ArgsList(self, node, table):
        pass
    
    def visit_ParametersList(self, node, table):
        pass

    def visit_Parameter(self, node, table):
            pass

    def visit_TernaryExpr(self, node, table):
        pass

    # def visit_VectorDecl():


