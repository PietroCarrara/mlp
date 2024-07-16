class LispValue():
    pass


class LispSymbol(LispValue):
    def __init__(self, symbolName: str) -> None:
        super().__init__()
        self.symbolName = symbolName

    def __eq__(self, value: object) -> bool:
        return isinstance(value, LispSymbol) and value.symbolName == self.symbolName


class LispNumber(LispValue):
    def __init__(self, numberValue: int) -> None:
        super().__init__()
        self.numberValue = numberValue

    def __eq__(self, value: object) -> bool:
        return isinstance(value, LispNumber) and value.numberValue == self.numberValue


class LispList(LispValue):
    @staticmethod
    def from_list(value: list[LispValue]) -> 'LispList':
        if len(value) == 0:
            return LispEmptyList()

        first, rest = value[0], value[1:]
        return LispNonEmptyList(first, LispList.from_list(rest))


class LispEmptyList(LispList):
    def __eq__(self, value: object) -> bool:
        return isinstance(value, LispEmptyList)


class LispNonEmptyList(LispList):
    def __init__(self, first: LispValue, rest: LispValue) -> None:
        super().__init__()
        self.first = first
        self.rest = rest

    def __eq__(self, value: object) -> bool:
        return isinstance(value, LispNonEmptyList) and value.first == self.first and value.rest == self.rest
