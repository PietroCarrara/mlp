import unittest
from interpreter import eval
from lisptypes import LispEmptyList, LispList, LispNumber, LispSymbol
from parser import parse


class ParserTests(unittest.TestCase):
    def test_basic_program(self):
        program = "(+ 5 3 2)"
        ast = parse(program)

        self.assertEqual(ast, LispList.from_list([
            LispSymbol("+"),
            LispNumber(5),
            LispNumber(3),
            LispNumber(2),
        ]))

    def test_nested_program(self):
        program = "(+ (* 5 (f x y z)) 3 2)"
        ast = parse(program)

        self.assertEqual(ast, LispList.from_list([
            LispSymbol("+"),
            LispList.from_list([
                LispSymbol("*"),
                LispNumber(5),
                LispList.from_list([
                    LispSymbol("f"),
                    LispSymbol("x"),
                    LispSymbol("y"),
                    LispSymbol("z"),
                ]),
            ]),
            LispNumber(3),
            LispNumber(2),
        ]))

    def test_symbol(self):
        program = "a"

        ast = parse(program)
        res = eval(ast)

        self.assertEqual(res, LispSymbol("a"))

    def test_number(self):
        program = "42"

        ast = parse(program)
        res = eval(ast)

        self.assertEqual(res, LispNumber(42))

    def test_number_negative(self):
        program = "-5"

        ast = parse(program)
        res = eval(ast)

        self.assertEqual(res, LispNumber(-5))

    def test_empty_list(self):
        program = "()"

        ast = parse(program)
        res = eval(ast)

        self.assertEqual(res, LispEmptyList())


if __name__ == '__main__':
    unittest.main()
