
from lisptypes import LispList, LispNumber, LispSymbol, LispValue
from utils import StringReader


def parse(code: str) -> list[LispValue]:
    reader = StringReader(code)
    result: list[LispValue] = []
    while True:
        reader.skip_whitespaces()
        if reader.size() > 0:
            result.append(parse_single_expression(reader))
        else:
            break

    return result


def parse_single_expression(reader: StringReader) -> LispValue:
    reader.skip_whitespaces()

    if reader.peek() == "(":
        expression_list: list[LispValue] = []
        reader.advance()
        reader.skip_whitespaces()
        while True:
            char = reader.peek()
            if char is None:
                raise reader.with_location(Exception("expected ')'"))
            if char == ")":
                break
            expression_list.append(parse_single_expression(reader))
            reader.skip_whitespaces()
        reader.advance()
        return LispList.from_list(expression_list)

    if reader.peek() == ")":
        raise reader.with_location(Exception("unexpected ')'"))

    if (number := reader.next_number()) is not None:
        return LispNumber(number)

    if (symbol := reader.next_word()) is not None:
        return LispSymbol(symbol)
    else:
        raise reader.with_location(Exception("expected symbol"))
