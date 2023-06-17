from SymbolTable import *
import AST
from colors import bcolors
import counters


class ExprNotFound(Exception):
    pass

      
class TeslangIRGenerator(object):
    cast_var = {
        'NUMBER' : 'int',
        'STRING' : 'str',
    }
    
    def __init__(self):
        pass


    def extract_expr_type(self, expr, table):
        expr_class_name = expr.__class__
        if expr_class_name.__name__ == 'LexToken':
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
        elif expr_class_name == AST.ExprList:
            return 'vector'
        elif expr_class_name == AST.FunctionCall:
            expr.accept_ir_generation(table)
            funcSymbol = table.get(expr.id)
            if funcSymbol and isinstance(funcSymbol, FunctionSymbol):
                funcSymbol.mark_as_used()
                return funcSymbol.rettype
            else:
                raise ExprNotFound
        elif expr_class_name == AST.Assignment:
            expr.accept_ir_generation(table)
        elif expr_class_name == AST.VectorAssignment:
            expr.accept_ir_generation(table)
            return 'vector'
        elif expr_class_name == AST.TernaryExpr:
            expr.accept_ir_generation(table)
        elif expr_class_name == AST.BinExpr:
            expr.accept_ir_generation(table)
            try:
                left_type = self.extract_expr_type(expr.left, table)
                right_type = self.extract_expr_type(expr.right, table)
                if left_type == right_type:
                    return left_type
            except ExprNotFound:
                pass
        elif expr_class_name == AST.OperationOnList:
            expr.accept_ir_generation(table)
            return 'int'
        return 'unknown'


    def handle_expr_register_allocation(self, expr, table) -> str:
        expr_register = None
        if hasattr(expr, 'accept_ir_generation'):
            expr_register = expr.accept_ir_generation(table)
        elif expr.__class__.__name__ == 'LexToken':
            if expr.type == 'NUMBER':
                expr_register = str(expr.value)
            elif expr.type == 'ID':
                exprSymbol = table.get(expr.value)
                expr_register = exprSymbol.register
        return expr_register


    def handle_error(self, pos, msg):
        print(bcolors.FAIL + 'Semantic error at line ' + str(pos.line) + bcolors.ENDC + ': ' + msg)

    def visit_Program(self, node, table):
        if table is None:
            table = SymbolTable(None, None)
        code = node.func.accept_ir_generation(table)
        if node.prog:
            code = node.prog.accept_ir_generation(table)
        # print(code)
        return code

    def visit_FunctionDef(self, node, parent_table: SymbolTable):
        print('proc ' + node.name + ':')
        counters.register_counter = 0
        funcSymbol = FunctionSymbol(node.rettype, node.name, node.fmlparams)
        parent_table.put(funcSymbol)
        child_table = SymbolTable(parent_table, funcSymbol)
        if node.fmlparams:
            node.fmlparams.parameters.reverse()
            for param in node.fmlparams.parameters:
                varSymbol = VariableSymbol(param.type, param.id, True)
                varSymbol.register = self.get_register()
                child_table.put(varSymbol)
        if node.body:
            node.body.accept_ir_generation(child_table)


    def visit_BodyLessFunctionDef(self, node, parent_table: SymbolTable):
        print('proc ' + node.name + ':')
        counters.register_counter = 0
        funcSymbol = FunctionSymbol(node.rettype, node.name, node.fmlparams)
        parent_table.put(funcSymbol)
        child_table = SymbolTable(parent_table, funcSymbol)
        if node.fmlparams:
            node.fmlparams.parameters.reverse()
            for param in node.fmlparams.parameters:
                varSymbol = VariableSymbol(param.type, param.id, True)
                varSymbol.register = self.get_register()
                child_table.put(varSymbol)
        return_reg = self.handle_expr_register_allocation(node.expr, child_table)
        return return_reg


    def visit_Body(self, node, table):
        if node.statement:
            if hasattr(node.statement, 'accept_ir_generation'):
                node.statement.accept_ir_generation(table)
        if node.body:
            node.body.accept_ir_generation(table)

    def visit_FunctionCall(self, node, table):
        intermediate_code = ''

        intermediate_code += '\tcall '
        if node.id == 'printInt':
            intermediate_code += 'iput' + ', '
        elif node.id == 'scan':
            intermediate_code += 'iget' + ', '
        else:
            intermediate_code += node.id + ', '

        node.args.exprs.reverse()

        if node.args.exprs:
            # return register is the first argument of call
            return_register = self.handle_expr_register_allocation(node.args.exprs[0], table)
        else:
            return_register = self.get_register()

        intermediate_code += return_register

        for i, expr in enumerate(node.args.exprs[1:]):
            expr_register = self.handle_expr_register_allocation(expr, table)
            intermediate_code += ', ' + expr_register

        print(intermediate_code)
        return return_register

    def visit_BinExpr(self, node, table):
        intermediate_code = ''
        op_intermediate_equivalent = {
            '>': '\tcmp>',
            '<': '\tcmp<',
            '>=': '\tcmp>=',
            '<=': '\tcmp<=',
            '==': '\tcmp==',
            '*': '\tmul',
            '/': '\tdiv',
            '%': '\tmod',
            '-': '\tsub',
            '+': '\tadd',
        }

        result_register = self.get_register()
        intermediate_code += op_intermediate_equivalent[node.op] + ' ' + result_register + ', '
        left_expr = self.handle_expr_register_allocation(node.left, table)
        intermediate_code += left_expr + ', '
        right_expr = self.handle_expr_register_allocation(node.right, table)
        intermediate_code += right_expr
        print(intermediate_code)
        return result_register

 
    

    def visit_VariableDecl(self, node, table):
        varSymbol = None
        if node.type == 'vector':
            try:
                rightSideExprType = self.extract_expr_type(node.expr, table)
                if rightSideExprType != 'vector':
                    varSymbol = VectorSymbol(node.id, 0)
                else:
                    if node.expr.__class__ == AST.ExprList:
                        exprsListNode = node.expr
                        varSymbol = VectorSymbol(node.id, len(exprsListNode.exprs))
                    elif node.expr.__class__ == AST.FunctionCall and node.expr.id == 'list':
                        node.expr.accept(table)
                        varSymbol = VectorSymbol(node.id, node.expr.args.exprs[0].value)
            except ExprNotFound:
                pass
        else:
            varSymbol = VariableSymbol(node.type, node.id, False)
        intermediate_code = ''
        if varSymbol is not None and varSymbol.__class__ == VariableSymbol:
            varSymbol.assigned = True
            register = self.get_register()
            varSymbol.set_register(register)
            if node.expr is None:
                intermediate_code += '\tmov ' + register + ', 0'
            else:
                expr_register = self.handle_expr_register_allocation(node.expr, table)
                intermediate_code += '\tmov ' + register + ', ' + expr_register

        print(intermediate_code)
        table.put(varSymbol)
        return intermediate_code


    def visit_Assignment(self, node, table: SymbolTable):
        intermediate_code = ''
        symbol = table.get(node.id)
        if isinstance(symbol, VariableSymbol):
            intermediate_code += '\tmov ' + symbol.register + ', '
            expr_register = self.handle_expr_register_allocation(node.expr, table)
            intermediate_code += expr_register
        elif isinstance(symbol, VectorSymbol):
            pass
            # rightSideExprType = self.extract_expr_type(node.expr, table)
            # if rightSideExprType != 'vector':
            #     self.handle_error(node.pos, 'Type mismatch in vector assignment. Expected \'vector\' but got \''
            #                     + rightSideExprType + '\'')
            # else:
            #     if node.expr.__class__ == AST.ExprList:
            #         exprsListNode = node.expr
            #         symbol.length = len(exprsListNode.exprs)
            #     elif node.expr.__class__ == AST.FunctionCall and node.expr.id == 'list':
            #         node.expr.accept_ir_generation(table)
            #         symbol.length = node.expr.args.exprs[0].value
        print(intermediate_code)

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
        expr_register = self.handle_expr_register_allocation(node.expr, table)
        intermediate_code = '\tmov r0, ' + expr_register
        print(intermediate_code)
        print('\tret')



    def visit_IfOrIfElseInstruction(self, node, table):
        intermediate_code = ''
        def is_if_with_else():
            return node.else_statement is not None

        after_else_label = self.get_label()
        else_label  = self.get_label()
        if hasattr(node.cond, 'accept_ir_generation'):
            # node.cond is an expression
            result_register = self.handle_expr_register_allocation(node.cond, table)
            intermediate_code += '\tjz ' + result_register + ', '
            intermediate_code += else_label if is_if_with_else() else after_else_label
            print(intermediate_code)
        if is_if_with_else():
            if hasattr(node.if_statement, 'accept_ir_generation'):
                node.if_statement.accept_ir_generation(table)
                print('\tjmp ' + after_else_label)

            if hasattr(node.else_statement, 'accept_ir_generation'):
                print(else_label + ':')
                node.else_statement.accept_ir_generation(table)
                print(after_else_label + ':')
        else:
            if hasattr(node.if_statement, 'accept_ir_generation'):
                ''' exec the if statement '''
                node.if_statement.accept_ir_generation(table)
                print(after_else_label + ':')

    def visit_Block(self, node, table):
        child_table = SymbolTable(parent=table, function=table.function)
        if hasattr(node.body, 'accept_ir_generation'):
            node.body.accept_ir_generation(child_table)

    def visit_WhileInstruction(self, node, table):
        while_loop_label = self.get_label()
        out_of_while_label = self.get_label()
        print(while_loop_label + ':')
        if hasattr(node.cond, 'accept_ir_generation'):
            # node.cond is an expression
            cond_register = self.handle_expr_register_allocation(node.cond, table)
            print(f'\tjz {cond_register}, {out_of_while_label}')
        if hasattr(node.while_statement, 'accept_ir_generation'):
            node.while_statement.accept_ir_generation(table)
            print(f'\tjmp {while_loop_label}')
        print(out_of_while_label + ':')

    def visit_ForInstruction(self, node, table):
        for_loop = self.get_label()
        out_of_for_loop = self.get_label()
        for_loop_id_register = table.get(node.id).register
        res_register = self.get_register()
        start_expr = self.handle_expr_register_allocation(node.start_expr, table)
        end_register = self.handle_expr_register_allocation(node.end_expr, table)
        print(f'\tmov {for_loop_id_register}, {start_expr}')
        print(for_loop + ':')
        print(f'\tcmp< {res_register}, {for_loop_id_register}, {end_register}')
        print(f'\tjz {res_register}, {out_of_for_loop}')
        self.handle_expr_register_allocation(node.end_expr, table)
        if hasattr(node.for_statement, 'accept_ir_generation'):
            node.for_statement.accept_ir_generation(table)
        print(f'\tadd {for_loop_id_register}, {for_loop_id_register}, 1')
        print(f'\tjmp {for_loop}')
        print(out_of_for_loop + ':')


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
        if hasattr(node.cond, 'accept_ir_generation'):
            node.cond.accept_ir_generation(table)
        if hasattr(node.first_expr, 'accept_ir_generation'):
            node.first_expr.accept_ir_generation(table)
        if hasattr(node.second_expr, 'accept_ir_generation'):
            node.second_expr.accept_ir_generation(table)


    def get_register(self)-> str:
        rg_n = f'r{counters.register_counter}'
        counters.register_counter += 1
        return rg_n

    def get_label(self)-> str:
        l_n = f'L{counters.label_counter}'
        counters.label_counter += 1
        return l_n

    def get_temp(self)-> str:
        tmp_n = f't{counters.temp_counter}'
        counters.temp_counter += 1
        return tmp_n

