import unittest
from interpreter import eval
from lisptypes import LispEmptyList, LispList, LispNumber, LispSymbol
from parser import parse
from scope import bind_to_static_scope
from screen import Screen, TestScreen


class ParserTests(unittest.TestCase):
    def test_basic_program(self):
        program = "(+ 5 3 2)"
        ast = parse(program)[0]
        self.assertEqual(ast, LispList.from_list([
            LispSymbol("+"),
            LispNumber(5),
            LispNumber(3),
            LispNumber(2),
        ]))

    def test_nested_program(self):
        program = "(+ (* 5 (f x y z)) 3 2)"
        ast = parse(program)[0]
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
        ast = parse(program)[0]
        self.assertEqual(ast, LispSymbol("a"))

    def test_number(self):
        program = "42"
        ast = parse(program)[0]
        self.assertEqual(ast, LispNumber(42))

    def test_number_negative(self):
        program = "-5"
        ast = parse(program)[0]
        self.assertEqual(ast, LispNumber(-5))

    def test_empty_list(self):
        program = "()"
        ast = parse(program)[0]
        self.assertEqual(ast, LispEmptyList())


class InterpreterTests(unittest.TestCase):
    def test_list_is_created(self):
        program = "(list 1 2 (3 4) x y)"

        ast = parse(program)
        result = eval(ast, Screen())
        self.assertEqual(result, LispList.from_list([
            LispNumber(1),
            LispNumber(2),
            LispList.from_list([LispNumber(3), LispNumber(4)]),
            LispSymbol("x"),
            LispSymbol("y"),
        ]))

    def test_function_is_applied(self):
        program = "(defun double (x) (+ x x)) (double 7)"

        ast = parse(program)
        result = eval(ast, Screen())
        self.assertEqual(result, LispNumber(14))

    def test_symbols_are_not_evaluated(self):
        program = "(let x 10) x"

        ast = parse(program)
        result = eval(ast, Screen())
        self.assertEqual(result, LispSymbol("x"))

    def test_symbols_are_coerced_when_summed(self):
        program = "(let x 10) (+ x 0)"

        ast = parse(program)
        result = eval(ast, Screen())
        self.assertEqual(result, LispNumber(10))

    def test_symbols_are_coerced_when_assigned(self):
        program = "(let x 10) (let y 20) (= x y) (+ x 0)"

        ast = parse(program)
        result = eval(ast, Screen())
        self.assertEqual(result, LispNumber(20))

    def test_symbols_are_coerced_when_assigned_via_declaration(self):
        program = "(let x 11) (let y x) (+ x 0)"

        ast = parse(program)
        result = eval(ast, Screen())
        self.assertEqual(result, LispNumber(11))


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
        ast = bind_to_static_scope(ast)
        eval(ast, screen)
        self.assertEqual(screen.get_contents(), "1\n3\n5\n8")


if __name__ == '__main__':
    unittest.main()
