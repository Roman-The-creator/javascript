import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser_js import Parser
from rules import FormattingRules, LogicRules
from config import Config

class TestRules(unittest.TestCase):

    def setUp(self):
        self.config = Config() 
        self.fmt_rules = FormattingRules(self.config)
        self.logic_rules = LogicRules(self.config)

    def _prepare(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        return tokens, ast

    def test_naming_camel_case(self):
        """Проверка соблюдения camelCase для переменных"""
        code = "let bad_variable_name = 1; let goodVariableName = 2;"
        tokens, _ = self._prepare(code)
        
        errors = self.fmt_rules.check_naming(tokens)
        
        self.assertEqual(len(errors), 1)
        self.assertIn("bad_variable_name", errors[0][1])

    def test_spacing_around_operators(self):
        """Проверка наличия пробелов вокруг операторов"""
        code = "let x=10+y;"
        tokens, _ = self._prepare(code)
        
        errors = self.fmt_rules.check_spacing(tokens)
        
        self.assertEqual(len(errors), 2)

    def test_unused_variables(self):
        """Проверка поиска объявленных, но не использованных переменных"""
        code = """
        let usedVar = 10;
        let unusedVar = 20;
        console.log(usedVar);
        """
        tokens, ast = self._prepare(code)
        
        errors = self.logic_rules.check_unused(ast, tokens)
        
        self.assertEqual(len(errors), 1)
        self.assertIn("unusedVar", errors[0][1])

    def test_cyclomatic_complexity(self):
        """Проверка расчета сложности (V(G))"""
        code = """
        function complexFunc(x) {
            if (x > 0) {            // +1
                while (x < 10) {    // +1
                    x++;
                }
            } else {                // else не увеличивает сложность в базовом подсчете
                return 0;
            }
            return x;
        }
        """
        tokens, ast = self._prepare(code)
        reports = []
        
        self.config.settings['max_complexity'] = 1
        self.logic_rules.check_complexity(ast, reports)
        
        self.assertTrue(any("complexity too high: 3" in r[1] for r in reports))

    def test_blank_lines_limit(self):
        """Проверка ограничения на пустые строки"""
        code = "let a = 1;\n\n\n\nlet b = 2;" # 3 пустые строки
        tokens, _ = self._prepare(code)
        
        self.config.settings['max_empty_lines'] = 1
        errors = self.fmt_rules.check_blank_lines(tokens)
        
        self.assertGreater(len(errors), 0)
        self.assertIn("Too many blank lines", errors[0][1])

if __name__ == '__main__':
    unittest.main()