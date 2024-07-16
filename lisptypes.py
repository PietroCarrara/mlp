class LispValue():
    pass


class LispSymbol(LispValue):
    def __init__(self, symbolName: str) -> None:
        super().__init__()
        self.symbolName = symbolName

    def __eq__(self, value: object) -> bool:
        return isinstance(value, LispSymbol) and value.symbolName == self.symbolName

    def __str__(self) -> str:
        return self.symbolName

    def __repr__(self) -> str:
        return self.__str__()


class LispNumber(LispValue):
    def __init__(self, numberValue: int) -> None:
        super().__init__()
        self.numberValue = numberValue

    def __eq__(self, value: object) -> bool:
        return isinstance(value, LispNumber) and value.numberValue == self.numberValue

    def __str__(self) -> str:
        return self.numberValue.__str__()

    def __repr__(self) -> str:
        return self.__str__()


class LispList(LispValue):
    @staticmethod
    def from_list(value: list[LispValue]) -> 'LispList':
        if len(value) == 0:
            return LispEmptyList()

        first, rest = value[0], value[1:]
        return LispNonEmptyList(first, LispList.from_list(rest))

    def to_python_list(self) -> list[LispValue]:
        raise Exception("not implemented")


class LispEmptyList(LispList):
    def to_python_list(self) -> list[LispValue]:
        return []

    def __eq__(self, value: object) -> bool:
        return isinstance(value, LispEmptyList)

    def __str__(self) -> str:
        return "()"

    def __repr__(self) -> str:
        return self.__str__()


class LispNonEmptyList(LispList):
    def __init__(self, first: LispValue, rest: LispValue) -> None:
        super().__init__()
        self.first = first
        self.rest = rest

    def to_python_list(self) -> list[LispValue]:
        values = [self.first]
        if isinstance(self.rest, LispList):
            values.extend(self.rest.to_python_list())
        else:
            values.append(self.rest)

        return values

    def __eq__(self, value: object) -> bool:
        return isinstance(value, LispNonEmptyList) and value.first == self.first and value.rest == self.rest

    def __str__(self) -> str:
        return f"({self.first} {self.rest})"

    def __repr__(self) -> str:
        return self.__str__()
