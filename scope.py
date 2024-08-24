from lisptypes import LispSymbol, LispValue, LispList, LispNonEmptyList


class Scope:
    """Represents a Dynamic Scope. In order to use the language with a static scope, see `bind_to_static_scope`"""

    def __init__(self) -> None:
        # Already begins in one level
        self.scopes: list[list[tuple[LispSymbol, LispValue]]] = [[]]

    def read_symbol(self, symbol: LispSymbol) -> LispValue | None:
        # From most specific scope to least specific
        for scope in reversed(self.scopes):
            for (name, value) in scope:
                if symbol == name:
                    return value
        return None

    def create_symbol(self, symbol: LispSymbol, value: LispValue):
        self.scopes[-1].insert(0, (symbol, value))

    def set_symbol(self, symbol: LispSymbol, value: LispValue):
        # From most specific scope to least specific
        for scope in reversed(self.scopes):
            for i in range(len(scope)):
                (name, _) = scope[i]
                if symbol == name:
                    scope[i] = (symbol, value)
                    return

        raise Exception(f"unknown symbol {symbol}")

    def begin_block(self) -> None:
        self.scopes.append([])

    def end_block(self) -> None:
        self.scopes.pop()

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
            var = args[1]
            expr = args[2]

            if not isinstance(var, LispSymbol):
                    raise Exception(
                        f"can't perform attribution using '{var}' as variable")
            new_var: LispSymbol = make_var_name(var)
            scope.create_symbol(var, new_var)
    
            something = LispList.from_list([args[0], new_var] + bind_to_static_scope([expr], scope))
            result_ast.append(something)
        
        # Function declaration
        elif isinstance(node, LispNonEmptyList) and isinstance(node.first, LispSymbol) and node.first.symbolName == "defun":
            scope.begin_block()
            args = node.to_python_list()
            [_, function_name, args_list, *function_body] = args
            
            if not isinstance(args_list, LispList):
                    raise Exception(
                        f"function declaration expects list of arguments, given {args_list}")
            
            new_args_list: list[LispValue] = []

            for function_arg in args_list.to_python_list():
                    if not isinstance(function_arg, LispSymbol):
                        raise Exception(
                            f"bad argument {function_arg} from function {function_name}, all arguments must be symbols") 
                    new_var = make_var_name(function_arg)
                    new_args_list.append(new_var)
                    scope.create_symbol(function_arg, new_var)

            something = LispList.from_list([args[0], function_name, LispList.from_list(new_args_list)] + bind_to_static_scope(function_body, scope))
            result_ast.append(something)
            scope.end_block()

        # Function application
        elif isinstance(node, LispNonEmptyList) and isinstance(node.first, LispSymbol):
            args = node.to_python_list()
            [function_name, *args_list] = args
            renamed_application = [function_name]

            for function_arg in args_list:
                # This is a function application, the user can pass values or variables as parameters
                # We must check if is a variable and replace it
                if isinstance(function_arg, LispSymbol):
                    replaced_name = scope.read_symbol(function_arg)

                    if replaced_name is None:
                        raise Exception(f"variable name {function_arg} not defined")
                    
                    renamed_application.append(replaced_name)
                else:
                    # I have absolutely no ideia why I need to use indexing for this, I'm too tired bro...
                    renamed_application.append(bind_to_static_scope([function_arg], scope)[0])
            result_ast.append(LispList.from_list(renamed_application))
            
        else:
             result_ast.append(node)
    return result_ast
                