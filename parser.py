
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
    match reader.peek():
        case "-" | "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9":
            num = reader.next_number()
            if num is None:
                raise reader.with_location(Exception("expected number"))
            return LispNumber(num)
        case "(":
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
        case ")":
            raise reader.with_location(Exception("unexpected ')'"))
        case _:
            symbol = reader.next_word()
            if symbol is None:
                raise reader.with_location(Exception("expected symbol"))
            return LispSymbol(symbol)
