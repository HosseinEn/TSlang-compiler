from SymbolTable import *
from ply.lex import LexToken
import AST
from colors import bcolors


class ExprNotFound(Exception):
    pass

      
class PreParser(object):


    cast_var = {
        'NUMBER' : 'int',
        'STRING' : 'str',
    }

    def push_builtins_to_table(self, table):
        def create_list_func():
            return FunctionSymbol('vector', 'list', AST.ParametersList([AST.Parameter('int', 'size')]))
        def create_print_func():
            return FunctionSymbol('null', 'print', AST.ParametersList([AST.Parameter('str', 'string_to_print')]))
        def create_int_print_func():
            return FunctionSymbol('null', 'printInt', AST.ParametersList([AST.Parameter('int', 'int_to_print')]))
        def create_length_func():
            return FunctionSymbol('int', 'length', AST.ParametersList([AST.Parameter('vector', 'vector_to_count')]))
        def create_scan_func():
            return FunctionSymbol('int', 'scan', AST.ParametersList([]))
        table.put(create_list_func())
        table.put(create_print_func())
        table.put(create_length_func())
        table.put(create_scan_func())
        table.put(create_int_print_func())

        

    def handle_error(self, pos, msg):
        print(bcolors.FAIL + 'Semantic error at line ' + str(pos.line) + bcolors.ENDC + ': ' + msg)


    def visit_Program(self, node, table):
        if table is None:
            table = SymbolTable(None, None)
        node.func.accept(table, pre_parse=True)
        if node.prog:
            table = node.prog.accept(table, pre_parse=True)
        return table

    def visit_FunctionDef(self, node, parent_table: SymbolTable):
        funcSymbol = FunctionSymbol(node.rettype, node.name, node.fmlparams)
        if not parent_table.put(funcSymbol):
            parent_table.mark_as_defined(node.name)
        child_table = SymbolTable(parent_table, funcSymbol)
        if node.body:
            node.body.accept(child_table, pre_parse=True)

    def visit_Body(self, node, table):
        if node.statement:
            if hasattr(node.statement, 'accept'):
                node.statement.accept(table, pre_parse=True)
        if node.body:
            node.body.accept(table, pre_parse=True)



