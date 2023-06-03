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
                id_search_res = table.get(expr.value)
                if id_search_res:
                    return id_search_res.type
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
            if funcSymbol and funcSymbol.__class__.__name__ == 'FunctionSymbol':
                return funcSymbol.rettype
            else:
                raise ExprNotFound
        elif expr_class_name == 'Assignment':
            expr.accept(table)
        elif expr_class_name == 'VectorAssignment':
            expr.accept(table)
            return 'vector'
        elif expr_class_name == 'TernaryExpr':
            pass
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
            self.handle_error(node.pos, 'Function \'' +
                              node.name + '\' already defined')
        child_table = SymbolTable(parent_table, funcSymbol)
        if node.fmlparams:
            for param in node.fmlparams.parameters:
                varSymbol = VariableSymbol(param.type, param.id)
                if not child_table.put(varSymbol):
                    self.handle_error(
                        node.pos, 'Parameter \'' + param.id + '\' already defined')
        if node.body:
            node.body.accept(child_table)
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

        elif symbol_table_search_res.__class__.__name__ == 'VariableSymbol':
            self.handle_error(node.pos, '\'' + node.id + '\' is not a function but used as function')
        else:
            funcSymbol = symbol_table_search_res
            params_count = len(funcSymbol.params.parameters) if funcSymbol.params else 0
            if len(node.args.exprs) != params_count:
                self.handle_error(
                    node.pos, 'Function \'' + node.id + '\' called with wrong number of arguments')
                
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
                if leftExprType != 'int' or rightExprType != 'int':
                    self.handle_error(node.pos, 'Type mismatch in binary expression. *, /, %, - can only be used with numbers')
            elif node.op == '+':
                if not (leftExprType == 'int' and rightExprType == 'int') or \
                not (leftExprType == 'str' and rightExprType == 'str'):
                    self.handle_error(node.pos, 'Type mismatch in binary expression. + can only be used with numbers or strings')
            else: 
                pass
        except ExprNotFound:
            pass

 
    

    def visit_VariableDecl(self, node, table):
        varSymbol = VariableSymbol(node.type, node.id)
        if not table.put(varSymbol):
            self.handle_error(node.pos, 'Variable \'' + node.id + '\' already defined')

        if node.expr is not None:
            expected_type = node.type
            try:
                given_type = self.extract_expr_type(node.expr, table)
                if given_type != expected_type:
                    self.handle_error(node.pos, f'Type mismatch in variable declaration. Expected \'' + expected_type
                                    + '\' but got \'' + given_type + '\'')
            except ExprNotFound:
                pass



    def visit_Assignment(self, node, table: SymbolTable):
        symbol = table.get(node.id)
        if symbol is None:
            self.handle_error(node.pos, 'Variable \'' + node.id + '\' not defined but used in assignment in function \'' 
                              + table.function.name + '\'')
        else:
            try:
                expected_type = symbol.type
                given_type = self.extract_expr_type(node.expr, table)
                if given_type != expected_type:
                    self.handle_error(node.pos, f'Type mismatch in assignment. Expected \'' + expected_type
                                    + '\' but got \'' + given_type + '\'')
            except ExprNotFound:
                pass

    def visit_VectorAssignment(self, node, table):
        try:
            if self.extract_expr_type(node.index_expr, table) != 'int':
                self.handle_error(node.pos, 'Invalid index type in vector assignment. Expected \'int\' but got \'' + self.extract_expr_type(node.index_expr) + '\'')
            
            # TODO - bug, because when we are using a vector which declared out of block, we can't find it in the table in the current scope
            symbol = table.get(node.id)
            if symbol is None:
                self.handle_error(node.pos, 'Vector \'' + node.id + '\' not defined but used in assignment in function \'' +
                                   table.function.name +'\'')
            else:
                id_type = symbol.type
                if id_type != 'vector':
                    self.handle_error(node.pos, 'Invalid expression type in vector assignment. Expected \'' + node.id + '\' to be \'vector\' but got \'' + id_type + '\'')
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
                self.handle_error(node.pos, 'Invalid expression type in for loop start range. Expected \'int\' but got \'' + self.extract_expr_type(node.start_expr, table) + '\'')    
            elif self.extract_expr_type(node.end_expr, table) != 'int':
                self.handle_error(node.pos, 'Invalid expression type in for loop end range. Expected \'int\' but got \'' + self.extract_expr_type(node.end_expr, table) + '\'')    
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
            if self.extract_expr_type(node.index_expr, table) != 'int':
                self.handle_error(node.pos, 'Invalid index type for \'' + symbol.name + '\'. Expected \'int\' but got \'' + self.extract_expr_type(node.index_expr, table) + '\'')        
    def visit_TernaryExpr(self, node, table):
        pass



