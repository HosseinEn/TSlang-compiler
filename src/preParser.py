from SymbolTable import *
from ply.lex import LexToken
from AST import *
from colors import bcolors


class ExprNotFound(Exception):
    pass

      
class PreParser(object):
    cast_var = {
        'NUMBER' : 'int',
        'STRING' : 'str',
    }
    
    def __init__(self):
        pass

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



