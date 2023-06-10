from SymbolTable import *
from ply.lex import LexToken
from AST import *
from colors import bcolors


class ExprNotFound(Exception):
    pass

      
class TeslangSemanticChecker(object):
    cast_var = {
        'NUMBER' : 'int',
        'STRING' : 'str',
    }
    
    def __init__(self):
        pass
    
    def both_exprs_are_numbers(self, left, right):
        return left.type == 'NUMBER' and right.type == 'NUMBER'


    def extract_expr_type(self, expr, table):
        expr_class_name = expr.__class__.__name__
        if expr_class_name == 'LexToken':
            if expr.type == 'ID':
                symbol = table.get(expr.value)
                if isinstance(symbol, VariableSymbol) and not symbol.assigned:
                    file_pos_simulation_obj = type('obj', (object,), {'line' : expr.lineno})
                    self.handle_error(file_pos_simulation_obj, '\'' + expr.value + '\' not assigned but used in a expression in function \''
                                       + table.function.name + '\'')
                if symbol:
                    symbol.mark_as_used()
                    if isinstance(symbol, VariableSymbol):
                        return symbol.type
                else:
                    file_pos_simulation_obj = type('obj', (object,), {'line' : expr.lineno})
                    self.handle_error(file_pos_simulation_obj, 'Variable \'' + expr.value +
                                       '\' not defined but used in expression in function \'' + table.function.name + '\'')
                    raise ExprNotFound
            else:
                return self.cast_var[expr.type]
        elif expr_class_name == 'ExprList':
            return 'vector'
        elif expr_class_name == 'FunctionCall':
            expr.accept(table)
            funcSymbol = table.get(expr.id)
            if funcSymbol and isinstance(funcSymbol, FunctionSymbol):
                funcSymbol.mark_as_used()
                return funcSymbol.rettype
            else:
                raise ExprNotFound
        elif expr_class_name == 'Assignment':
            expr.accept(table)
        elif expr_class_name == 'VectorAssignment':
            expr.accept(table)
            return 'vector'
        elif expr_class_name == 'TernaryExpr':
            expr.accept(table)
        elif expr_class_name == 'BinExpr':
            expr.accept(table)
            try:
                left_type = self.extract_expr_type(expr.left, table)
                right_type = self.extract_expr_type(expr.right, table)
                if left_type == right_type:
                    return left_type
            except ExprNotFound:
                pass
        elif expr_class_name == 'OperationOnList':
            expr.accept(table)
            return 'int'
        return 'unknown'


    def handle_error(self, pos, msg):
        print(bcolors.FAIL + 'Semantic error at line ' + str(pos.line) + bcolors.ENDC + ': ' + msg)

    def visit_Program(self, node, table):
        if table is None:
            table = SymbolTable(None, None)
        node.func.accept(table)
        if node.prog:
            table = node.prog.accept(table)
        return table

    def visit_FunctionDef(self, node, parent_table: SymbolTable):
        funcSymbol = FunctionSymbol(node.rettype, node.name, node.fmlparams)
        if not parent_table.put(funcSymbol):
            if parent_table.get(node.name).redefined:
                self.handle_error(node.pos, 'Function \'' +
                                node.name + '\' already defined')
        child_table = SymbolTable(parent_table, funcSymbol)
        if node.fmlparams:
            for param in node.fmlparams.parameters:
                varSymbol = VariableSymbol(param.type, param.id, True)
                if not child_table.put(varSymbol):
                    self.handle_error(
                        node.pos, 'Parameter \'' + param.id + '\' already defined' + ' in function \'' + node.name + '\'')
        if node.body:
            node.body.accept(child_table)
        child_table.show_unused_warning()

    def visit_BodyLessFunctionDef(self, node, parent_table: SymbolTable):
        funcSymbol = FunctionSymbol(node.rettype, node.name, node.fmlparams)
        if not parent_table.put(funcSymbol):
            if parent_table.get(node.name).redefined:
                self.handle_error(node.pos, 'Function \'' +
                                node.name + '\' already defined')
        child_table = SymbolTable(parent_table, funcSymbol)
        if node.fmlparams:
            for param in node.fmlparams.parameters:
                varSymbol = VariableSymbol(param.type, param.id, True)
                if not child_table.put(varSymbol):
                    self.handle_error(
                        node.pos, 'Parameter \'' + param.id + '\' already defined' + ' in function \'' + node.name + '\'')
        try:
            expr_type = self.extract_expr_type(node.expr, child_table)
            if expr_type != funcSymbol.rettype:
                if funcSymbol.rettype == 'null':
                    self.handle_error(node.pos, 'Function \'' + node.name + '\'' + ' doesn\'t return any thing but got \'' +
                                       expr_type + '\'')
                else:
                    self.handle_error(node.pos, 'Function \'' + node.name + '\' returns \'' + funcSymbol.rettype
                                  + '\' but got \'' + expr_type + '\'')
        except ExprNotFound:
            pass
        child_table.show_unused_warning()

    def visit_Body(self, node, table):
        if node.statement:
            if hasattr(node.statement, 'accept'):
                node.statement.accept(table)
        if node.body:
            node.body.accept(table)

    def visit_FunctionCall(self, node, table):
        # Searching for the called function in the symbol table
        symbol_table_search_res = table.get(node.id)
        if symbol_table_search_res is None:
            self.handle_error(node.pos, 'Function \'' +
                            node.id + '\' not defined but called')
        elif not isinstance(symbol_table_search_res, FunctionSymbol):
            self.handle_error(node.pos, '\'' + node.id + '\' is not a function but called as function in \'' +
                               table.function.name + '\'')
        else:
            funcSymbol = symbol_table_search_res
            funcSymbol.mark_as_used()
            params_count = len(funcSymbol.params.parameters) if funcSymbol.params else 0
            if len(node.args.exprs) != params_count:
                self.handle_error(
                    node.pos, 'Function \'' + node.id + '\' called with wrong number of arguments. Expected ' + 
                    str(params_count) + ' but got ' + str(len(node.args.exprs)) + '.')
            else:
                for i, expr in enumerate(node.args.exprs):
                    try: 
                        param = funcSymbol.params.parameters[i]
                        arg_type = self.extract_expr_type(expr, table)

                        if arg_type != param.type:
                            self.handle_error(node.pos, 'Function \'' + node.id + '\' called with wrong type of arguments in ' +
                                            str(len(node.args.exprs)-i) + '. expected \'' + param.type + '\' but got \'' + arg_type + '\'')
                    except ExprNotFound:
                        pass
            

    def visit_BinExpr(self, node, table):
        try: 
            leftExprType = self.extract_expr_type(node.left, table)
            rightExprType = self.extract_expr_type(node.right, table)

            if leftExprType == 'vector' or rightExprType == 'vector':
                self.handle_error(node.pos, 'Vector operations not supported')

            if node.op in ('*', '/', '%', '-'):
                both_are_int = (leftExprType == 'int' and rightExprType == 'int')
                if not both_are_int:
                    self.handle_error(node.pos, 'Type mismatch in binary expression. *, /, %, - can only be used with numbers')
            elif node.op == '+':
                both_are_int = (leftExprType == 'int' and rightExprType == 'int')
                both_are_str = (leftExprType == 'str' and rightExprType == 'str')
                if not both_are_int and not both_are_str:
                    self.handle_error(node.pos, 'Type mismatch in binary expression. + can only be used with numbers or strings')
            else: 
                pass
        except ExprNotFound:
            pass

 
    

    def visit_VariableDecl(self, node, table):
        varSymbol = None
        if node.type == 'vector':
            try:
                rightSideExprType = self.extract_expr_type(node.expr, table)
                if rightSideExprType != 'vector':
                    self.handle_error(node.pos, 'Type mismatch in vector declaration. Expected \'vector\' but got \''
                                    + rightSideExprType + '\'')
                    # Handling error by passing vector length as zero to show more errors
                    varSymbol = VectorSymbol(node.id, 0)
                else:
                    if node.expr.__class__.__name__ == 'ExprList':
                        exprsListNode = node.expr
                        varSymbol = VectorSymbol(node.id, len(exprsListNode.exprs))
                    elif node.expr.__class__.__name__ == 'FunctionCall' and node.expr.id == 'list':
                        node.expr.accept(table)
                        varSymbol = VectorSymbol(node.id, node.expr.args.exprs[0].value)                        
            except ExprNotFound:
                pass
        else:
            varSymbol = VariableSymbol(node.type, node.id, False)

        if not table.put(varSymbol):
            self.handle_error(node.pos, 'Symbol \'' + node.id + '\' of type \''
                               + node.type + '\' already defined')

        if node.expr is not None:
            if node.type != 'vector':
                varSymbol.assigned = True
                expected_type = node.type
                try:
                    given_type = self.extract_expr_type(node.expr, table)
                    if given_type != expected_type:
                        self.handle_error(node.pos, f'Type mismatch in variable declaration. Expected \'' + expected_type
                                        + '\' but got \'' + given_type + '\'')
                except ExprNotFound:
                    pass
                
    # def handle_list_function_error(self, node, table):
    #     # if len(node.expr.args) != 1:
    #     #     self.handle_error(node.pos, 'Function \'list\' called with wrong number of arguments. Expected 1 but got ' 
    #     #                       + str(len(node.expr.args)) + '.')
    #     #     return True
    #     # elif self.extract_expr_type(node.exprs.args.exprs[0], table) != 'int':
    #     #     self.handle_error(node.pos, 'Function \'list\' called with wrong type of arguments. Expected \'int\' but got \'' 
    #     #                       + self.extract_expr_type(node.exprs.args.exprs[0], table) + '\'')
    #     #     return True
    #     # else:
    #     return False

    def visit_Assignment(self, node, table: SymbolTable):
        symbol = table.get(node.id)
        if symbol is None:
            self.handle_error(node.pos, 'Variable \'' + node.id + '\' not defined but used in assignment in function \'' 
                              + table.function.name + '\'')
        else:
            try:
                symbol.mark_as_used()
                if isinstance(symbol, VariableSymbol):
                    expected_type = symbol.type
                    given_type = self.extract_expr_type(node.expr, table)
                    if given_type != expected_type:
                        self.handle_error(node.pos, f'Type mismatch in assignment. Expected \'' + expected_type
                                        + '\' but got \'' + given_type + '\'')
                    symbol.assigned = True
                elif isinstance(symbol, VectorSymbol):
                    rightSideExprType = self.extract_expr_type(node.expr, table)
                    if rightSideExprType != 'vector':
                        self.handle_error(node.pos, 'Type mismatch in vector assignment. Expected \'vector\' but got \''
                                        + rightSideExprType + '\'')
                    else:
                        if node.expr.__class__.__name__ == 'ExprList':
                            exprsListNode = node.expr
                            symbol.length = len(exprsListNode.exprs)
                        elif node.expr.__class__.__name__ == 'FunctionCall' and node.expr.id == 'list':
                            node.expr.accept(table)
                            symbol.length = node.expr.args.exprs[0].value
                else:
                    self.handle_error(node.pos, 'Can not use ' 
                                      + symbol.__class__.__name__ + ' \'' + symbol.name + '\' in assignment')
            except ExprNotFound:
                pass

    def visit_VectorAssignment(self, node, table):
        try:
            index_type = self.extract_expr_type(node.index_expr, table)
            if index_type != 'int':
                self.handle_error(node.pos, 'Invalid index type in vector assignment. Expected \'int\' but got \'' + index_type + '\'')
            
            symbol = table.get(node.id)
            if symbol is None:
                self.handle_error(node.pos, 'Vector \'' + node.id + '\' not defined but used in assignment in function \'' +
                                   table.function.name +'\'')
            else:
                symbol.mark_as_used()
                if not isinstance(symbol, VectorSymbol):
                    self.handle_error(node.pos, 'Can not use ' 
                        + symbol.__class__.__name__ + ' \'' + symbol.name + '\' in vector assignment')  

                else:
                    if symbol.length <= node.index_expr.value or node.index_expr.value < 0:
                        self.handle_error(node.pos, 'Index out of range in vector assignment. Vector \'' 
                                          + node.id + '\' can hold only ' + str(symbol.length) + ' values')
                    rightSideExprType = self.extract_expr_type(node.expr, table)
                    if rightSideExprType != 'int':
                        self.handle_error(node.pos, 'Invalid expression type in vector assignment. Vector can hold only \'int\' values but got \''
                                           + rightSideExprType + '\'' + ' in function \'' + table.function.name + '\'')
        except ExprNotFound:
            pass

    def visit_ReturnInstruction(self, node, table):
        try:
            expected_type = table.function.rettype
            given_return_type = self.extract_expr_type(node.expr, table)
            if expected_type != given_return_type:
                self.handle_error(node.pos, f'Type mismatch in return statement. Expected \'' + expected_type
                                + '\' but got \'' + given_return_type + '\'')
        except ExprNotFound:
            pass


    def visit_IfOrIfElseInstruction(self, node, table):
        def is_if_with_else():
            return node.else_statement is not None

        if node.cond.__class__.__name__ in ('Assignment'):
            self.handle_error(node.pos, 'Invalid condition type in if statement')
        if hasattr(node.cond, 'accept'):
            node.cond.accept(table)
        if hasattr(node.if_statement, 'accept'):
            node.if_statement.accept(table)
        if is_if_with_else():
            if hasattr(node.else_statement, 'accept'):
                node.else_statement.accept(table)

    def visit_Block(self, node, table):
        child_table = SymbolTable(parent=table, function=table.function)
        if hasattr(node.body, 'accept'):
            node.body.accept(child_table)

    def visit_WhileInstruction(self, node, table):
        if hasattr(node.cond, 'accept'):
            node.cond.accept(table)
        if hasattr(node.while_statement, 'accept'):
            node.while_statement.accept(table)

    def visit_ForInstruction(self, node, table):
        try:
            if self.extract_expr_type(node.start_expr, table) != 'int':
                self.handle_error(node.pos, 'Invalid expression type in for loop start range. Expected \'int\' but got \'' 
                                  + self.extract_expr_type(node.start_expr, table) + '\'')    
            elif self.extract_expr_type(node.end_expr, table) != 'int':
                self.handle_error(node.pos, 'Invalid expression type in for loop end range. Expected \'int\' but got \'' 
                                  + self.extract_expr_type(node.end_expr, table) + '\'')    
            if hasattr(node.for_statement, 'accept'):
                node.for_statement.accept(table)
        except ExprNotFound:
            pass


    def visit_OperationOnList(self, node, table):
        symbol = table.get(node.expr)
        if symbol is None:
            self.handle_error(node.pos, 'Vector \'' + node.expr + '\' not defined but used in operation in function \'' +
                               table.function.name +'\'')
        else:
            id_type = symbol.type
            if id_type != 'vector':
                self.handle_error(node.pos, 'Identifier \'' +
                                 node.expr + '\' expected to be \'vector\' but got \'' + id_type + '\'')
            try:
                if self.extract_expr_type(node.index_expr, table) != 'int':
                    self.handle_error(node.pos, 'Invalid index type for \'' + symbol.name + '\'. Expected \'int\' but got \'' + self.extract_expr_type(node.index_expr, table) + '\'')        
            except ExprNotFound:
                pass

    def visit_TernaryExpr(self, node, table):
        if hasattr(node.cond, 'accept'):
            node.cond.accept(table)
        if hasattr(node.first_expr, 'accept'):
            node.first_expr.accept(table)
        if hasattr(node.second_expr, 'accept'):
            node.second_expr.accept(table)
