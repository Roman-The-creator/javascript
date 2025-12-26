import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer

class TestLexer(unittest.TestCase):
    
    def test_basic_tokenization(self):
        """Проверка распознавания базовых типов токенов"""
        code = "const x = 42;"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        significant_tokens = [t for t in tokens if t.type != 'SKIP']
        
        self.assertEqual(significant_tokens[0].type, 'KEYWORD')
        self.assertEqual(significant_tokens[0].value, 'const')
        self.assertEqual(significant_tokens[1].type, 'ID')
        self.assertEqual(significant_tokens[1].value, 'x')
        self.assertEqual(significant_tokens[2].type, 'OP')
        self.assertEqual(significant_tokens[2].value, '=')
        self.assertEqual(significant_tokens[3].type, 'NUMBER')
        self.assertEqual(significant_tokens[4].type, 'PUNCT')

    def test_line_and_column_counting(self):
        """Проверка корректности строк и колонок"""
        code = "let a;\nlet b;"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        second_let = [t for t in tokens if t.line == 2 and t.value == 'let'][0]
        self.assertEqual(second_let.line, 2)
        self.assertEqual(second_let.column, 0)

    def test_string_and_comment_recognition(self):
        """Проверка строк и комментариев (включая многострочные)"""
        code = "'hello'; // line comment\n/* block \n comment */"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        types = [t.type for t in tokens if t.type != 'SKIP']
        self.assertIn('STRING', types)
        self.assertIn('COMMENT', types)
        
        # Проверяем, что многострочный комментарий распознан как один токен
        block_comment = [t for t in tokens if 'block' in t.value][0]
        self.assertEqual(block_comment.type, 'COMMENT')

    def test_operator_indices(self):
        """Важнейший тест для Fixer: проверка абсолютных индексов"""
        code = "a=b"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        op_token = [t for t in tokens if t.type == 'OP'][0]
        self.assertEqual(op_token.value, '=')
        self.assertEqual(op_token.start_idx, 1)
        self.assertEqual(op_token.end_idx, 2)

    def test_complex_identifiers(self):
        """Проверка имен с $, _ и цифрами"""
        code = "let $my_var1 = 1;"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        id_token = [t for t in tokens if t.type == 'ID'][0]
        self.assertEqual(id_token.value, "$my_var1")

    def test_error_handling_mismatch(self):
        """Проверка реакции на недопустимые символы (@, # вне строк)"""
        code = "let x = @;"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        self.assertEqual(tokens[-1].value, ';')

if __name__ == '__main__':
    unittest.main()