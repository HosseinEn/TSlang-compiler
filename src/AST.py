
class Node(object):

  def __init__(self, node_info):
      #if len(node_info) == 3:
      self.lineno = node_info['lno']
         #self.columnno = node_info['cno']
         #self.ptype = node_info['ptype']
    
  def accept(self, visitor, table = None):
      className = self.__class__.__name__
      # return visitor.visit_<className>(self)
      meth = getattr(visitor, 'visit_' + className, None)
      if meth!=None:
          return meth(self, table)

  def iaccept(self, visitor):
    result = visitor.visit(self)
    if isinstance(result, list):
        if result:
            return result[0]
        else:
            return None
    else:
        return result


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
  def __init__(self, id, params, pos):
    self.id = id
    self.params = params
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

# class InstructionList(Node):
#   def __init__(self, instrs):
#     self.instrs = instrs

class Statement(Node):
    def __init__(self, statement):
      self.statement = statement

class PrintInstruction(Node):
  def __init__(self, expr):
    self.expr = expr

class ReturnInstruction(Node):
  def __init__(self, expr, pos):
    self.expr = expr
    self.pos = pos

class DeclarationList(Node):
  def __init__(self, decls):
    self.decls = decls

class Declaration(Node):
  def __init__(self, type, inits, pos):
    self.type = type
    self.inits = inits
    self.pos = pos

class InitList(Node):
  def __init__(self, inits):
    self.inits = inits

class Init(Node):
  def __init__(self, id, expr):
    self.id = id
    self.expr = expr

class IfOrIfElseInstruction(Node):
  def __init__(self, cond, if_statement, pos, else_statement = None):
    self.cond = cond
    self.if_statement = if_statement
    self.else_statement = else_statement
    self.pos = pos

class WhileInstruction(Node):
  def __init__(self, cond, while_statement):
    self.cond = cond
    self.while_statement = while_statement

class ForInstruction(Node):
  def __init__(self, start_expr, end_expr, for_statement, pos):
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

# class CompoundInstructions(Node):
#   def __init__(self, decls, instrs):
#     self.decls = decls
#     self.instrs = instrs

class Body(Node):
    def __init__(self, statement, body):
        self.statement = statement
        self.body = body

class Assignment(Node):
  def __init__(self, id, expr, pos):
    self.id = id
    self.expr = expr
    self.pos = pos

class LabeledInstruction(Node):
  def __init__(self, kw, instr):
    self.keyword = kw
    self.instr = instr

class RepeatInstruction(Node):
  def __init__(self, kw_1, instrs, kw_2, cond ):
      self.kw_1 = kw_1
      self.kw_2 = kw_2
      self.instrs = instrs
      self.cond = cond

      
class ArgsList(Node):
  def __init__(self, exprs):
    self.exprs = exprs

class ParametersList(Node):
  def __init__(self, parameters):
    self.parameters = parameters

class Parameter(Node):
  def __init__(self, type, id):
    self.type = type
    self.id = id