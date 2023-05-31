from colors import bcolors

class Symbol(object):
    def __init__(self, name):
        self.name = name
        self.used = False

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

    def get(self, name, current_scope=False):
        symbol = self.table.get(name)
        if symbol is not None:
            symbol.used = True
            return symbol
        elif not current_scope and self.getParent() is not None:
            return self.getParent().get(name)
        return symbol

    def getTable(self):
        return self.table

    def getParent(self):
        return self.parent
    
    def print_symbols(self):
        for key in self.table:
            print(key, self.table[key])

    def show_unused(self):
        for key in self.table:
            if not self.table[key].used:
                symbolType = 'variable' if isinstance(self.table[key], VariableSymbol) else 'function'
                if isinstance(self.table[key], VariableSymbol) and self.parent.function:
                    position = ' in function \'' + self.parent.function.name + '\''
                elif isinstance(self.table[key], VariableSymbol) and self.function:
                    position = ' at function \'' + self.function.name + '\' parameter list'
                else:
                    position = ''
                print(bcolors.WARNING + f'WARNING - Unused {symbolType} \'{self.table[key].name}\'' + position + bcolors.ENDC)
                self.table[key].used = True


