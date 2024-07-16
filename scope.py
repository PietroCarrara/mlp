from lisptypes import LispSymbol, LispValue


class Scope:
    """Represents a Dynamic Scope. In order to use the language with a static scope, see `bind_to_static_scope`"""

    def read_symbol(self, symbol: LispSymbol) -> LispValue | None:
        raise Exception("not implemented")

    def begin_block(self) -> None:
        raise Exception("not implemented")

    def end_block(self) -> None:
        raise Exception("not implemented")


def bind_to_static_scope(ast: list[LispValue]) -> list[LispValue]:
    return ast  # TODO
