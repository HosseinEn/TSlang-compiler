from TeslangParser import TeslangParser
import logging
import sys
import ply.yacc as yacc
from preParser import PreParser



def up_and_run_compiler():
    def start(pre_parse, table=None):
        tParser = TeslangParser(pre_parse=pre_parse)
        parser = yacc.yacc(module=tParser, debug=True, write_tables=True)
        ast = parser.parse(data, lexer=tParser.scanner)
        table = ast.accept(pre_parse=pre_parse, table=table if not pre_parse else None)
        if pre_parse:
            PreParser().push_builtins_to_table(table)
        else:
            table.show_unused_warning()
        return table
    table = start(pre_parse=True)
    start(pre_parse=False, table=table)



logging.basicConfig(
    level = logging.DEBUG,
    filename = "parselog.txt",
    filemode = "w",
    format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

data = open(('../tests/' +sys.argv[1]) if len(sys.argv) == 2 else '../tests/input1.txt', 'r').read()

up_and_run_compiler()

