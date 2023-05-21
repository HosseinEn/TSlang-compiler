from SymbolTable import *
from ply.lex import LexToken
from AST import *
from enum import Enum


def cast_var(var):
    if var == 'NUMBER':
        return 'int'
    elif var == 'STRING':
        return 'str'

class TeslangSemanticChecker(object):
    def __init__(self):
        pass
        # self.ttype = Ttype()

    def is_terminal(self, node):
        return isinstance(node, LexToken)
    
    
    def both_exprs_are_numbers(self, left, right):
        return left.type == 'NUMBER' and right.type == 'NUMBER'
    

    def type_checker(self, node, table, type_of_check):
        expected_type = None
        if type_of_check == 'variable_declaration':
            if self.is_terminal(node.expr):
                expected_type = node.type
            elif node.expr.__class__.__name__ == 'ExprList':
                expected_type = 'vector'
            elif node.expr.__class__.__name__ == 'FunctionCall':
                node.expr.accept(table)
                sym = table.get(node.expr.id)
                if sym.__class__.__name__ == 'FunctionSymbol':
                    expected_type = funcSymbol.rettype  
                elif sym.__class__.__name__ == 'VariableSymbol':
                    self.handle_error(node.pos, f'Variable {sym} used as function')   
        elif type_of_check == 'assignment':
            expected_type = table.get(node.id, current_scope=True).type
        elif type_of_check == 'return_type':
            expected_type = table.function.rettype
            
        if self.is_terminal(node.expr): 
            if expected_type != cast_var(node.expr.type):
                self.handle_error(node.pos, f'Type mismatch in {type_of_check}. Expected \'' + expected_type
                                + '\' but got \'' + cast_var(node.expr.type) + '\'')
        elif node.expr.__class__.__name__ == 'ExprList':
            if expected_type != 'vector':
                self.handle_error(node.pos, f'Type mismatch in {type_of_check}. Expected \'' + expected_type
                                + '\' but got \'vector\'')
        elif node.expr.__class__.__name__ == 'FunctionCall':
            node.expr.accept(table)
            sym = table.get(node.expr.id)
            if sym != None and sym.__class__.__name__ == 'FunctionSymbol':
                if sym.rettype != expected_type:
                    self.handle_error(node.pos, f'Type mismatch in {type_of_check}. Expected \'' + expected_type
                                    + '\' but function \'' + node.expr.id + '\' returns \'' + sym.rettype + '\'')

            elif sym.__class__.__name__ == 'VariableSymbol':
                self.handle_error(node.pos, f'Variable {sym} used as function')



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
            params_count = len(funcSymbol.params.parameters) if funcSymbol.params else 0
            if len(node.args.exprs) != params_count:
                self.handle_error(
                    node.pos, 'Function \'' + node.id + '\' called with wrong number of arguments')
            else:
                for i, expr in enumerate(node.args.exprs):
                    param = funcSymbol.params.parameters[i]
                    # arg.accept(table)
                    # breakpoint()
                    # TODO - these codes can be refactored with cast_var()
                    if self.is_terminal(expr):
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
        if leftClassName == 'ExprList' or leftClassName == 'ExprList':
            self.handle_error(node.pos, 'Vector operations not supported')

        if node.op in ('*', '/', '%', '+', '-'):
            le_ri_nodes = (node.left, node.right)
            for node_item in le_ri_nodes:
                if not self.is_terminal(node_item):
                    node_item.accept(table)
                    if node_item.__class__.__name__ == 'FunctionCall':
                        sym = table.get(node_item.id)
                        if sym != None and sym.__class__.__name__ == 'FunctionSymbol':
                            if sym.rettype != 'int':
                                self.handle_error(node.pos, 'Type mismatch in binary expression. *, /, %, +, - can only be used with numbers. Function \'' + 
                                                    node_item.id + '\' called in binary expression does not return int')
                                break
                        elif sym.__class__.__name__ == 'VariableSymbol':
                            self.handle_error(node.pos, f'Variable {sym} used as function')
                else:
                    if node_item.type == 'NUMBER':
                        pass
                    elif node_item.type == 'ID':
                        left_id_search_res = table.get(node_item.value)
                        if left_id_search_res is None:
                            self.handle_error(
                                node.pos, 'Variable \'' + node_item.value + '\' not defined but used in expression')
                            break
                        else:
                            if left_id_search_res.type != 'int':
                                self.handle_error(node.pos, 'Variable \'' + node_item.value + '\' used in expression is not of type \'int\'')
                                break
                    elif node_item.type == 'STRING':
                            self.handle_error(node.pos, 'Variable \'' + node_item.value + '\' used in expression is not of type \'int\'')

        elif node.op in ('==', '!=', '<', '>', '<=', '>='):
            pass
    


    def visit_VariableDecl(self, node, table):
        varSymbol = VariableSymbol(node.type, node.id)
        if not table.put(varSymbol):
            self.handle_error(node.pos, 'Variable \'' + node.id + '\' already defined')

        if node.expr is not None:
            self.type_checker(node, table, 'variable_declaration')

    def visit_Assignment(self, node, table):
        if table.get(node.id, current_scope=True) is None:
            self.handle_error(node.pos, 'Variable \'' + node.id + '\' not defined but used in assignment')
        else:
            self.type_checker(node, table, 'assignment')

    def visit_VectorAssignment(self, node, table):
        if table.get(node.id, current_scope=True) is None:
            self.handle_error(node.pos, 'Vector \'' + node.id + '\' not defined but used in assignment')
        # else:
        #     self.type_checker(node, table, 'assignment')
     

    def visit_ReturnInstruction(self, node, table):
        self.type_checker(node, table, 'return_type')



    def visit_IfOrIfElseInstruction(self, node, table):
        def is_if_with_else():
            return node.else_statement is not None

        if node.cond.__class__.__name__ in ('Assignment'):
            self.handle_error(node.pos, 'Invalid condition type in if statement')
        if hasattr(node.cond, 'accept'):
            node.cond.accept(table)
        node.if_statement.accept(table)
        if is_if_with_else():
            node.else_statement.accept(table)


    # def visit_Statement(self, node, table):
    #     pass


    def visit_Block(self, node, table):
        child_table = SymbolTable(parent=table, function=None)
        if hasattr(node.body, 'accept'):
            node.body.accept(child_table)

    def visit_WhileInstruction(self, node, table):
        if hasattr(node.cond, 'accept'):
            node.cond.accept(table)
        # breakpoint()
        if hasattr(node.while_statement, 'accept'):
            node.while_statement.accept(table)

    def visit_ForInstruction(self, node, table):
        def check_exprs_as_for_range(expr):
            expr_class_name = expr.__class__.__name__
            is_assignment = expr_class_name == 'Assignment'
            is_vector = expr_class_name == 'ExprList'
            is_identifier_a_number = True
            is_return_type_a_number = True

            if expr_class_name == 'LexToken':
                if expr.type == 'STRING':
                    is_identifier_a_number = False
                elif expr.type == 'ID':
                    decl_iden = table.get(expr.value, current_scope=True)
                    if decl_iden:
                        is_return_type_a_number = decl_iden.type == 'int'
                    else:
                        self.handle_error(node.pos, 'Variable \'' + expr.value + '\' not defined but used in for loop range')
            if expr_class_name == 'FunctionCall':
                sym = table.get(expr.id)
                if sym.__class__.__name__ == 'FunctionSymbol':
                    is_return_type_a_number = sym.rettype == 'int'
                elif sym.__class__.__name__ == 'VariableSymbol':
                    self.handle_error(node.pos, f'Variable {sym} used as function')

            if is_assignment:
                self.handle_error(node.pos, 'Invalid expression type in for loop range. cannot use assignment as range')
            elif is_vector:
                self.handle_error(node.pos, 'Invalid expression type in for loop range. cannot use vector as range')
            elif not is_identifier_a_number:
                self.handle_error(node.pos, 'Invalid expression type in for loop range. cannot use string as range')
            elif not is_return_type_a_number:
                self.handle_error(node.pos, 'Invalid expression type in for loop range. cannot use function call that returns string as range')
        
        check_exprs_as_for_range(node.start_expr)
        check_exprs_as_for_range(node.end_expr)
        if hasattr(node.start_expr, 'accept'):
            node.start_expr.accept(table)
        if hasattr(node.end_expr, 'accept'):
            node.end_expr.accept(table)
        
            
        
    

    def visit_OperationOnList(self, node, table):
        # check that the expr operated on list is the correct type
        # breakpoint()
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


