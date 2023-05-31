from TeslangSemanticChecker import TeslangSemanticChecker

class TypeChecker(TeslangSemanticChecker):
    def __init__(self, node, table):
        self.node = node
        self.table = table

    def variable_declaration_check(self):
        def extract_expected_type():
            # if self.is_terminal(self.node.expr):
            #     expected_type = self.node.type
            # elif self.node.expr.__class__.__name__ == 'ExprList':
            #     expected_type = 'vector'
            # elif self.node.expr.__class__.__name__ == 'FunctionCall':
            #     self.node.expr.accept(self.table)
            #     sym = self.table.get(self.node.expr.id)
            #     if sym.__class__.__name__ == 'FunctionSymbol':
            #         expected_type = sym.rettype  
            #     elif sym.__class__.__name__ == 'VariableSymbol':
            #         self.handle_error(self.node.pos, f'Variable {sym} used as function')   
            # return expected_type
            return self.node.type
        def extract_given_type():
            cast_var = {
                'NUMBER' : 'int',
                'STRING' : 'str',
            }
            if self.node.expr in ('NUMBER', 'STRING', 'ID'):
                actual_type = cast_var[]


    def assignment_check(self):
        def extract_expected_type():
    
        def extract_given_type():
        expected_type = table.get(node.id, current_scope=True).type

    def return_type_check(self):
        def extract_expected_type():
        
        def extract_given_type():
        expected_type = table.function.rettype

    def check_type_equality(self):
        if self.is_terminal(self.node.expr): 
            if self.node.expr.type == 'ID':
                id_search_res = table.get(self.node.expr.value)
                if id_search_res:
                    actual_type = table.get(self.node.expr.value).type
                else:
                    self.handle_error(self.node.pos, 'Variable \'' + self.node.expr.value + '\' not defined but used in ' + type_of_check)
            else:
                actual_type = cast_var(self.node.expr.type)
            if expected_type != actual_type:
                self.handle_error(self.node.pos, f'Type mismatch in {type_of_check}. Expected \'' + expected_type
                                + '\' but got \'' + actual_type + '\'')
        elif self.node.expr.__class__.__name__ == 'ExprList':
            if expected_type != 'vector':
                self.handle_error(self.node.pos, f'Type mismatch in {type_of_check}. Expected \'' + expected_type
                                + '\' but got \'vector\'')
        elif self.node.expr.__class__.__name__ == 'FunctionCall':
            self.node.expr.accept(table)
            sym = table.get(self.node.expr.id)
            if sym != None and sym.__class__.__name__ == 'FunctionSymbol':
                if sym.rettype != expected_type:
                    self.handle_error(self.node.pos, f'Type mismatch in {type_of_check}. Expected \'' + expected_type
                                    + '\' but function \'' + self.node.expr.id + '\' returns \'' + sym.rettype + '\'')

            elif sym.__class__.__name__ == 'VariableSymbol':
                self.handle_error(self.node.pos, f'Variable {sym} used as function')
