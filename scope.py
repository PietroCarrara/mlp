from lisptypes import LispSymbol, LispValue


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


def bind_to_static_scope(ast: list[LispValue]) -> list[LispValue]:
    return ast  # TODO
