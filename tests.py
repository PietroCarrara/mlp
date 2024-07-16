import unittest
from interpreter import eval
from lisptypes import LispEmptyList, LispList, LispNumber, LispSymbol
from parser import parse
from scope import Scope, bind_to_static_scope
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

    def test_basic_subtraction(self):
        program = "(- 5 3 2)"
        ast = parse(program)[0]
        self.assertEqual(ast, LispList.from_list([
            LispSymbol("-"),
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
        program = "(list 1 2 (list 3 4) x y)"

        ast = parse(program)
        result = eval(ast, Scope(), Screen())
        self.assertEqual(result, LispList.from_list([
            LispNumber(1),
            LispNumber(2),
            LispList.from_list([LispNumber(3), LispNumber(4)]),
            LispSymbol("x"),
            LispSymbol("y"),
        ]))

    def test_list_is_created_with_cons(self):
        program = "(cons 1 (cons 2 (cons (cons 3 (cons 4 ())) (cons 5 (cons 6 ())))))"

        ast = parse(program)
        result = eval(ast, Scope(), Screen())
        self.assertEqual(result, LispList.from_list([
            LispNumber(1),
            LispNumber(2),
            LispList.from_list([LispNumber(3), LispNumber(4)]),
            LispNumber(5),
            LispNumber(6),
        ]))

    def test_list_is_created_with_cons_using_symbols(self):
        program = "(let x 5) (let y 6) (cons 1 (cons 2 (cons (cons 3 (cons 4 ())) (cons x (cons y ())))))"

        ast = parse(program)
        result = eval(ast, Scope(), Screen())
        self.assertEqual(result, LispList.from_list([
            LispNumber(1),
            LispNumber(2),
            LispList.from_list([LispNumber(3), LispNumber(4)]),
            LispNumber(5),
            LispNumber(6),
        ]))

    def test_function_is_applied(self):
        program = "(defun double (x) (+ x x)) (double 7)"

        ast = parse(program)
        result = eval(ast, Scope(), Screen())
        self.assertEqual(result, LispNumber(14))

    def test_symbols_are_evaluated(self):
        program = "(let x 10) (let y 11) (let z (+ x y)) z"

        ast = parse(program)
        result = eval(ast, Scope(), Screen())
        self.assertEqual(result, LispNumber(21))

    def test_sum_with_symbols(self):
        program = "(let x 10) (+ x 2)"

        ast = parse(program)
        result = eval(ast, Scope(), Screen())
        self.assertEqual(result, LispNumber(12))

    def test_assignment(self):
        program = "(let x 10) (let y 20) (= x y) x"

        ast = parse(program)
        result = eval(ast, Scope(), Screen())
        self.assertEqual(result, LispNumber(20))

    def test_empty_list_evals_to_itself(self):
        program = "()"

        ast = parse(program)
        result = eval(ast, Scope(), Screen())
        self.assertEqual(result, LispEmptyList())

    def test_scope_is_respected(self):
        program = "(let x (+ 2 2)) (defun foo () (let x 10) (= x 11)) (foo) x"

        ast = parse(program)
        result = eval(ast, Scope(), Screen())
        self.assertEqual(result, LispNumber(4))


class FinalInterpreterTests(unittest.TestCase):
    def test_static_scope(self):
        program = ""
        with open("example.lisp") as f:
            program = f.read()
        screen = TestScreen()

        ast = parse(program)
        eval(ast, Scope(), screen)
        self.assertEqual(screen.get_contents(), "3\n11\n3\n11")

    def test_dynamic_scope(self):
        program = ""
        with open("example.lisp") as f:
            program = f.read()
        screen = TestScreen()

        ast = parse(program)
        ast = bind_to_static_scope(ast)
        eval(ast, Scope(), screen)
        self.assertEqual(screen.get_contents(), "1\n3\n5\n8")


if __name__ == '__main__':
    unittest.main()
