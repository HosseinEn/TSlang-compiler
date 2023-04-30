class Symbol(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return '<{name}>'.format(name=self.name)

class VariableSymbol(Symbol):

    def __init__(self, type, name):
        super(VariableSymbol, self).__init__(name)
        self.type = type

class FunctionSymbol(Symbol):

    def __init__(self, rettype, name, params):
        super(FunctionSymbol, self).__init__(name)
        self.rettype = rettype
        self.params = params
    #     self.local_vars = dict()

    # def put_into_local_vars(self, symbol):
    #     if not symbol.name in self.local_vars:
    #         self.local_vars[symbol.name] = symbol
    #         return True
    #     return False
    
    # def get_from_local_vars(self, name):
    #     symbol = self.local_vars.get(name)
    #     if symbol is not None:
    #         return symbol
    #     return symbol

    def __str__(self):
        return '<{name} : {rettype}({params})>'.format(name=self.name, rettype=self.rettype, params=self.params)
    

class SymbolTable(object):

    def __init__(self, parent, function):
        self.parent = parent
        self.function = function
        self.table = dict()

    def put(self, symbol):
        if not symbol.name in self.table:
            self.table[symbol.name] = symbol
            return True
        return False

    def get(self, name):
        symbol = self.table.get(name)
        if symbol is not None:
            return symbol
        elif self.getParent() is not None:
            return self.getParent().get(name)
        return symbol

    def getTable(self):
        return self.table

    def getParent(self):
        return self.parent
    
    def print_symbols(self):
        for key in self.table:
            print(key, self.table[key])

