from TeslangParser import TeslangParser
import logging
import sys
import ply.yacc as yacc


logging.basicConfig(
    level = logging.DEBUG,
    filename = "parselog.txt",
    filemode = "w",
    format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

data = open(sys.argv[1] if len(sys.argv) == 2 else '../tests/test_input_file2.txt', 'r').read()
tParser = TeslangParser()
# parser = yacc.yacc(debug=True, debuglog=log)
parser = yacc.yacc(module=tParser, debug=True, write_tables=True)

ast = parser.parse(data, lexer=tParser.scanner)

table = ast.accept()
table.show_unused_warning()
breakpoint()
