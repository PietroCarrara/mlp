import unittest
from interpreter import eval
from lisptypes import LispEmptyList, LispList, LispNumber, LispSymbol
from parser import parse
from screen import Screen, TestScreen


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
        self.assertEqual(ast, LispSymbol("a"))

    def test_number(self):
        program = "42"
        ast = parse(program)
        self.assertEqual(ast, LispNumber(42))

    def test_number_negative(self):
        program = "-5"
        ast = parse(program)
        self.assertEqual(ast, LispNumber(-5))

    def test_empty_list(self):
        program = "()"
        ast = parse(program)
        self.assertEqual(ast, LispEmptyList())


class InterpreterTests(unittest.TestCase):
    def test_symbols_are_not_evaluated(self):
        program = "(let x 10) x"

        ast = parse(program)
        result = eval(ast, Screen())
        self.assertEqual(result, LispSymbol("x"))

    def test_symbols_are_coerced_when_needed(self):
        program = "(let x 10) (+ x 0)"

        ast = parse(program)
        result = eval(ast, Screen())
        self.assertEqual(result, LispNumber(10))


class FinalInterpreterTests(unittest.TestCase):
    def test_static_scope(self):
        program = ""
        with open("example.lisp") as f:
            program = f.read()
        screen = TestScreen()

        ast = parse(program)
        eval(ast, screen)
        self.assertEqual(screen.get_contents(), "3\n11\n3\n11")

    def test_dynamic_scope(self):
        program = ""
        with open("example.lisp") as f:
            program = f.read()
        screen = TestScreen()

        ast = parse(program)
        eval(ast, screen)
        self.assertEqual(screen.get_contents(), "1\n3\n5\n8")


if __name__ == '__main__':
    unittest.main()
