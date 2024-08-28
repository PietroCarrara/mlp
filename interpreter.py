from lisptypes import LispEmptyList, LispList, LispNonEmptyList, LispNumber, LispSymbol
from parser import LispValue
from scope import Scope, SymbolType
from screen import Screen, TestScreen
from functools import reduce

saved: bool = False
ast_backup: list[LispValue]
current_state: LispSymbol

hash_code: dict[str, list[LispValue]] = {}


def eval(ast: list[LispValue], scope: Scope, screen: Screen, code: str = "") -> LispValue:
    result = eval_recursive(ast, scope, screen, code)
    if isinstance(screen, TestScreen):
        print_ast(LispSymbol("global"), LispEmptyList(), scope, screen)

    return result


def eval_recursive(ast: list[LispValue], scope: Scope, screen: Screen, code: str = "") -> LispValue:
    global ast_backup
    global saved
    global current_state

    if not saved:
        ast_backup = ast
        current_state = LispSymbol("global")
        hash_code[current_state.symbolName] = ast
        saved = True

    last_value = eval_expression(ast[0], scope, screen)
    for expression in ast[1:]:
        last_value = eval_expression(expression, scope, screen)

    return last_value


def eval_expression(expr: LispValue, scope: Scope, screen: Screen) -> LispValue:
    if isinstance(expr, LispNumber):
        return expr  # A number evals to itself

    if isinstance(expr, LispSymbol):
        # A symbol evals to whatever was in the scope
        value = scope.read_symbol(expr)
        if value is None:
            raise Exception(f"unknown symbol {expr}")
        return value

    if isinstance(expr, LispEmptyList):
        return expr  # An empty list evals to itself

    if isinstance(expr, LispNonEmptyList):
        # A list evals to a funcion application, where the first item must be a symbol (the function name),
        # and all the other items are the function arguments
        if not isinstance(expr.first, LispSymbol):
            raise Exception(
                f"can't perform function application using '{expr.first}' as a function")

        return eval_function_application(expr.first, expr.rest, scope, screen)

    raise Exception(f"unexpected value {expr}")


def eval_function_application(name: LispSymbol, arguments: LispList, scope: Scope, screen: Screen) -> LispValue:
    if isinstance(screen, TestScreen):
        print_ast(name, arguments, scope, screen)

    match name.symbolName:
        case "+":
            operators = arithmetic_helper("addition", arguments, scope, screen)
            return LispNumber(sum(operators))

        case "-":
            operators = arithmetic_helper(
                "subtraction", arguments, scope, screen)
            return LispNumber(reduce((lambda x, y: x - y), operators))

        case "*":
            operators = arithmetic_helper(
                "multiplication", arguments, scope, screen)
            return LispNumber(reduce((lambda x, y: x * y), operators))

        case "/":
            args = arguments.to_python_list()
            if len(args) != 2:
                raise Exception(
                    f"division needs exactly two arguments, but was called with {args}")
            [op1, op2] = args
            dividend = eval_expression(op1, scope, screen)
            divisor = eval_expression(op2, scope, screen)

            if not isinstance(dividend, LispNumber) or not isinstance(divisor, LispNumber):
                raise Exception(
                    f"can't perform division using non num values, attempted: {dividend}/{divisor}")
            if divisor.numberValue == 0:
                raise Exception(
                    f"can't divide a number by zero")
            # Implementing only integer division
            return LispNumber(dividend.numberValue//divisor.numberValue)

        case "defun":
            # Not dealing with duplicated function names
            args = arguments.to_python_list()
            if len(args) < 3:
                raise Exception(
                    f"function definition expects at least three arguments (foo_name, arguments, body), given {args}")

            [foo_name, *foo_body] = args
            if not isinstance(foo_name, LispSymbol):
                raise Exception(
                    f"function name must be a symbol, given {foo_name}")

            scope.create_symbol(foo_name, LispList.from_list(
                foo_body), SymbolType.FUNCTION)
            hash_code[foo_name.symbolName] = foo_body
            return LispEmptyList()

        case "let":
            args = arguments.to_python_list()
            if len(args) != 2:
                raise Exception(
                    f"let needs exactly two arguments, but was called with {args}")
            [symbol, value] = args
            if not isinstance(symbol, LispSymbol):
                raise Exception(
                    f"can't perform attribution using '{symbol}' as a variable")
            value = eval_expression(value, scope, screen)
            scope.create_symbol(symbol, value, SymbolType.VARIABLE)
            return value

        case "=":
            args = arguments.to_python_list()
            if len(args) != 2:
                raise Exception(
                    f"= needs exactly two arguments, but was called with {args}")
            [symbol, value] = args
            if not isinstance(symbol, LispSymbol):
                raise Exception(
                    f"can't perform attribution using '{symbol}' as a variable")
            value = eval_expression(value, scope, screen)
            scope.set_symbol(symbol, value, SymbolType.VARIABLE)
            return value

        case "cons":
            args = arguments.to_python_list()
            if len(args) != 2:
                raise Exception(
                    f"cons needs exactly two arguments, but was called with {args}")
            [first, rest] = args
            first = eval_expression(first, scope, screen)
            rest = eval_expression(rest, scope, screen)

            if not isinstance(rest, LispList):
                raise Exception(
                    f"cons expects the second argument to be a list, found {rest}")

            return LispNonEmptyList(first, rest)

        case "list":
            items: list[LispValue] = []
            for item in arguments.to_python_list():
                items.append(eval_expression(item, scope, screen))
            return LispList.from_list(items)

        case "print":
            for arg in arguments.to_python_list():
                screen.print(str(eval_expression(arg, scope, screen)))
            return LispEmptyList()

        case _:
            global current_state
            foo = scope.read_symbol(name)
            given_args = arguments.to_python_list()
            scope.begin_block(name.symbolName)

            if not isinstance(foo, LispList):
                raise Exception(
                    f"Function {name} not defined")

            foo_args, *foo_body = foo.to_python_list()
            current_state = name

            # TODO: right now, the test of the function syntax is done here
            #       not in the definition of the function 'defun'
            if not isinstance(foo_args, LispList):
                raise Exception(
                    f"Bad definition of function {
                        name}, the syntax for defun is: "
                    + "(defun name (parameter-list) body)")
            foo_args = foo_args.to_python_list()

            # Check if user passed the needed number of parameters
            if len(foo_args) != len(given_args):
                raise Exception(
                    f"{name} expects {len(foo_args)} arguments, were given {len(given_args)}")

            for i in range(len(foo_args)):
                arg = foo_args[i]  # scope only works if I do this
                if not isinstance(arg, LispSymbol):
                    raise Exception(
                        f"Bad argument {arg} from function {name}, all arguments must be symbols")

                eval_arg = eval_expression(given_args[i], scope, screen)
                scope.create_symbol(arg, eval_arg, SymbolType.VARIABLE)

            result = eval(foo_body, scope, screen)
            scope.end_block()
            return result

# Returns a list of the n operands for addition, subtraction and multiplication


def arithmetic_helper(operation: str, arguments: LispList, scope: Scope, screen: Screen) -> list[int]:
    operators: list[int] = []
    for expr in arguments.to_python_list():
        operator = eval_expression(expr, scope, screen)
        if not isinstance(operator, LispNumber):
            raise Exception(
                f"tried to perform {operation} with a non num types: {operator}")
        operators.append(operator.numberValue)
    return operators


def print_ast(name: LispSymbol, arguments: LispList, scope: Scope, screen: TestScreen):
    global ast_backup
    global current_state
    temp = LispNonEmptyList(name, arguments)

    result = ""
    result += f"Expression:    {temp}\n"
    result += f"Current Scope: {" ".join(scope.names)}\n\n\n"
    for node in ast_backup:
        result += node.__str__() + "\n"

    print("\n"*30)
    print_side_by_side_by_side(
        result,
        "Output:\n\n" + screen.get_contents(),
        str(scope),
    )
    input()  # Pause


def print_side_by_side_by_side(left: str, middle: str, right: str):
    leftLines = left.split("\n")
    middleLines = middle.split("\n")
    rightLines = right.split("\n")

    maxLeftWidth = max(map(lambda line: len(line), leftLines))
    maxMiddleWidth = max(map(lambda line: len(line), middleLines))

    for i in range(max(len(leftLines), len(middleLines))):
        if i < len(leftLines):
            neededPadding = maxLeftWidth - len(leftLines[i])
            print(leftLines[i] + " " * neededPadding, end="")
        else:
            print(" " * maxLeftWidth, end="")

        print(" | ", end="")

        if i < len(middleLines):
            neededPadding = maxMiddleWidth - len(middleLines[i])
            print(middleLines[i] + " " * neededPadding, end="")
        else:
            print(" " * maxMiddleWidth, end="")

        print(" | ", end="")

        if i < len(rightLines):
            print(rightLines[i], end="")

        print()  # Break line
