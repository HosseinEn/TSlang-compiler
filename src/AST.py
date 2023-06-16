from TeslangSemanticChecker import TeslangSemanticChecker
from preParser import PreParser
from TeslangIRGenerator import TeslangIRGenerator
import counters

class Node(object):

    def __init__(self, node_info):
        self.lineno = node_info['lno']
        
    def accept(self, table = None, pre_parse=False):
        className = self.__class__.__name__
        if pre_parse:
            meth = getattr(PreParser(), 'visit_' + className, None)
        else:
            meth = getattr(TeslangSemanticChecker(), 'visit_' + className, None)
        if meth!=None:
            return meth(self, table)

    def accept_ir_generation(self, table):
        className = self.__class__.__name__
        meth = getattr(TeslangIRGenerator(), 'visit_' + className, None)
        if meth!=None:
            return meth(self, table)



class ErrorNode(Node):
    pass

class Program(Node):
  def __init__(self, func, prog, pos):  
    self.func = func
    self.prog = prog
    self.pos = pos
    
class Const(Node):
  def __init__(self, value):
    self.value = value

class Integer(Const):
    pass

class Float(Const):
    pass

class String(Const):
    pass

class VariableDecl(Node):
  def __init__(self, id, type, pos, expr=None):
    self.id = id
    self.type = type
    self.expr = expr
    self.pos = pos

class BinExpr(Node):
  def __init__(self, left, op, right, pos):
    self.left = left
    self.op = op
    self.right = right
    self.pos = pos
    #sprint(left, op, right)

class ExprList(Node):
  def __init__(self, exprs):
    self.exprs = exprs

class FunctionCall(Node):
  def __init__(self, id, args, pos):
    self.id = id
    self.args = args
    self.pos = pos

class FunctionDefList(Node):
  def __init__(self, fundefs):
    self.fundefs = fundefs

class FunctionDef(Node):
  def __init__(self, rettype, name, fmlparams, body, pos):
    self.rettype = rettype
    self.name = name
    self.fmlparams = fmlparams
    self.body = body
    self.pos = pos

class BodyLessFunctionDef(Node):
  def __init__(self, rettype, name, fmlparams, expr, pos):
    self.rettype = rettype
    self.name = name
    self.fmlparams = fmlparams
    self.expr = expr
    self.pos = pos

class Statement(Node):
    def __init__(self, statement):
      self.statement = statement

class ReturnInstruction(Node):
  def __init__(self, expr, pos):
    self.expr = expr
    self.pos = pos


class IfOrIfElseInstruction(Node):
    def __init__(self, cond, if_statement, pos, else_statement = None):
        self.cond = cond
        self.if_statement = if_statement
        self.else_statement = else_statement
        self.pos = pos

class WhileInstruction(Node):
    def __init__(self, cond, while_statement, pos):
        self.cond = cond
        self.while_statement = while_statement
        self.pos = pos

class ForInstruction(Node):
    def __init__(self, id, start_expr, end_expr, for_statement, pos):
        self.id = id
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.for_statement = for_statement
        self.pos = pos


class ContinueInstruction(Node):
    def __init__(self):
        pass

class BreakInstruction(Node):
    def __init__(self):
        pass


class Body(Node):
    def __init__(self, statement, body):
        self.statement = statement
        self.body = body


class Assignment(Node):
    def __init__(self, id, expr, pos):
        self.id = id
        self.expr = expr
        self.pos = pos

class VectorAssignment(Node):
    def __init__(self, id, index_expr, expr, pos):
        self.id = id
        self.index_expr = index_expr
        self.expr = expr
        self.pos = pos
       


class OperationOnList(Node):
    def __init__(self, expr, index_expr, pos):
        self.expr = expr
        self.index_expr = index_expr
        self.pos = pos

class ParametersList(Node):
    def __init__(self, parameters):
        self.parameters = parameters
    def __str__(self) -> str:
       return str(self.parameters)

class Parameter(Node):
    def __init__(self, type, id):
        self.type = type
        self.id = id


class TernaryExpr(Node):
    def __init__(self, cond, first_expr, second_expr, pos):
        self.cond = cond
        self.first_expr = first_expr
        self.second_expr = second_expr
        self.pos = pos

class Block(Node):
   def __init__(self, body):
         self.body = body
