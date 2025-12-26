import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser_js import Parser
from engine import LinterEngine
from fixer import Fixer
from config import Config

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.test_file = "temp_test_code.js"
        self.config_data = {
            "naming_pattern": r"^[a-z][a-zA-Z0-9]*$",
            "max_complexity": 2,
            "require_spaces_operators": True,
            "autofix": True
        }
        self.config = Config()
        self.config.settings.update(self.config_data)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_lint_disable_logic(self):
        """Проверка, что комментарии /* lint-disable */ работают"""
        code = """
        let validVar = 1;
        /* lint-disable */
        let Bad_Name = 2; 
        let unused = 3;
        /* lint-enable */
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        engine = LinterEngine(code, self.config)
        engine.run(tokens, ast)
        
        reports_str = "".join(engine.reports)
        self.assertNotIn("Bad_Name", reports_str)
        self.assertNotIn("unused", reports_str)

    def test_full_autofix_cycle(self):
        """Проверка полного цикла: обнаружение ошибки -> исправление -> запись в файл"""
        bad_code = "let x=10+y;"
        with open(self.test_file, "w") as f:
            f.write(bad_code)
            
        lexer = Lexer(bad_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        fixer = Fixer(bad_code)
        engine = LinterEngine(bad_code, self.config)
        
        engine.run(tokens, ast, fixer)
        
        fixed_code = fixer.apply()
        
        self.assertEqual(fixed_code, "let x = 10 + y;")
        self.assertIn("Line 1: Missing space around operator '='", engine.reports[0])

    def test_syntax_error_with_style_checks(self):
        """Проверка, что линтер находит стилевые ошибки даже рядом с синтаксическим мусором"""
        code = """
        let bad_name = 1; 
        if (x === ) { // Синтаксическая ошибка здесь
           console.log(1);
        }
        let another_Bad = 2;
        """
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        engine = LinterEngine(code, self.config)
        engine.run(tokens, ast)
        
        reports_str = "".join(engine.reports)
        self.assertIn("bad_name", reports_str)
        self.assertIn("another_Bad", reports_str)

if __name__ == "__main__":
    unittest.main()