from lisptypes import LispEmptyList, LispList, LispNonEmptyList, LispNumber, LispSymbol
from parser import LispValue
from scope import Scope
from screen import Screen


def eval(ast: list[LispValue], scope: Scope, screen: Screen) -> LispValue:
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
        if not isinstance(expr.rest, LispList):
            raise Exception(
                f"can't perform function application using '{expr.rest}' as arguments")

        return eval_function_application(expr.first, expr.rest, scope, screen)

    raise Exception(f"unexpected value {expr}")


def eval_function_application(name: LispSymbol, arguments: LispList, scope: Scope, screen: Screen) -> LispValue:
    match name.symbolName:
        case "+":
            return LispNumber(0)  # TODO
        case "-":
            return LispNumber(0)  # TODO
        case "*":
            return LispNumber(0)  # TODO
        case "/":
            return LispNumber(0)  # TODO
        case "defun":
            return LispEmptyList()  # TODO
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
            scope.create_symbol(symbol, value)
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
            scope.set_symbol(symbol, value)
            return value

        case "cons":
            args = arguments.to_python_list()
            if len(args) != 2:
                raise Exception(
                    f"cons needs exactly two arguments, but was called with {args}")
            [first, rest] = args
            return LispNonEmptyList(eval_expression(first, scope, screen), eval_expression(rest, scope, screen))

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
            # TODO: User-defined function
            scope.begin_block()
            result = LispEmptyList()
            scope.end_block()
            return result
