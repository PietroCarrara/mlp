from lisptypes import LispSymbol, LispValue, LispList, LispNonEmptyList, LispNumber, LispEmptyList
from enum import Enum

class SymbolType(Enum):
    VARIABLE = 0
    FUNCTION = 1

class Scope:
    """Represents a Dynamic Scope. In order to use the language with a static scope, see `bind_to_static_scope`"""

    def __init__(self) -> None:
        # Already begins in one level
        self.scopes: list[list[tuple[LispSymbol, LispValue, SymbolType]]] = [[]]

    def read_symbol(self, symbol: LispSymbol) -> LispValue | None:
        # From most specific scope to least specific
        for scope in reversed(self.scopes):
            for (name, value, _) in scope:
                if symbol == name:
                    return value
        return None

    def create_symbol(self, symbol: LispSymbol, value: LispValue, symbol_type: SymbolType):
        self.scopes[-1].insert(0, (symbol, value, symbol_type))

    def set_symbol(self, symbol: LispSymbol, value: LispValue, symbol_type: SymbolType):
        # From most specific scope to least specific
        for scope in reversed(self.scopes):
            for i in range(len(scope)):
                (name, _, _) = scope[i]
                if symbol == name:
                    scope[i] = (symbol, value, symbol_type)
                    return

        raise Exception(f"unknown symbol {symbol}")

    def begin_block(self) -> None:
        self.scopes.append([])

    def end_block(self) -> None:
        self.scopes.pop()

    def __str__(self) -> str:
        i: int = 0
        result = ""# + "---------- SCOPE: ----------\n"
        for scope in reversed(self.scopes):
            #result += f"LEVEL {i}\n"
            for var, value, symbol_type in scope:
                result += f"{var}" + (f" = {value}" if symbol_type == SymbolType.VARIABLE else "()") + "\n"
            result += "-----------------------------\n"
            i += 1
        return result
    
var_count: int = 0

def make_var_name(var: LispSymbol):
      global var_count      
      new_var_name = var.symbolName + "_" + str(var_count)
      var_count += 1 
      return LispSymbol(new_var_name)

def bind_to_static_scope(ast: list[LispValue], scope: Scope) -> list[LispValue]:
    result_ast: list[LispValue] = []

    for node in ast:
        # Variable declaration
        if isinstance(node, LispNonEmptyList) and isinstance(node.first, LispSymbol) and node.first.symbolName == "let":
            args = node.to_python_list()
            # Well-formed variable declaration structure is (let var expr)
            operator = args[0] 
            var = args[1]
            expr = args[2]

            if not isinstance(var, LispSymbol):
                    raise Exception(
                        f"can't perform attribution using '{var}' as variable")
            
            # Creates a new name for the variable
            # everytime the same variable is found program must replace by the new one
            new_var: LispSymbol = make_var_name(var)
            scope.create_symbol(var, new_var, SymbolType.VARIABLE)
    
            # Replace the node by the new modified one
            new_node = LispList.from_list([operator, new_var] + bind_to_static_scope([expr], scope))
            result_ast.append(new_node)
        
        # Function declaration
        elif isinstance(node, LispNonEmptyList) and isinstance(node.first, LispSymbol) and node.first.symbolName == "defun":
            scope.begin_block()
            args = node.to_python_list()
            # Well-formed function declaration is (defun name (args) (body))
            [operator, function_name, args_list, *function_body] = args
            
            if not isinstance(args_list, LispList):
                    raise Exception(
                        f"function declaration expects list of arguments, given {args_list}")
            new_args_list: list[LispValue] = []

            # Creates a new variable name for every argument in the function
            for function_arg in args_list.to_python_list():
                    if not isinstance(function_arg, LispSymbol):
                        raise Exception(
                            f"bad argument {function_arg} from function {function_name}, all arguments must be symbols") 
                    new_var = make_var_name(function_arg)
                    new_args_list.append(new_var)
                    scope.create_symbol(function_arg, new_var, SymbolType.VARIABLE)

            new_node = LispList.from_list([operator, function_name, LispList.from_list(new_args_list)] + bind_to_static_scope(function_body, scope))
            result_ast.append(new_node)
            scope.end_block()

        # Function application
        elif isinstance(node, LispNonEmptyList) and isinstance(node.first, LispSymbol):
            args = node.to_python_list()
            # Well-formed function application is (name arguments)
            [function_name, *args_list] = args
            renamed_application = [function_name]

            renamed_application.extend(bind_to_static_scope(args_list, scope))
            result_ast.append(LispList.from_list(renamed_application))
        
        elif isinstance(node, LispSymbol):
            replaced_name = scope.read_symbol(node)
            if replaced_name is None:
                    raise Exception(f"variable name {node} not defined")
            result_ast.append(replaced_name)

        elif isinstance(node, LispNumber):
            result_ast.append(node)
        
        elif isinstance(node, LispEmptyList):
            result_ast.append(node)

        else:
            raise Exception(f"unexpected syntax {node}")

    return result_ast
    
                