from parser import LispValue
from screen import Screen


def eval(ast: list[LispValue], screen: Screen) -> LispValue:
    # TODO: Receive somethin like a scope?
    return ast[-1]
