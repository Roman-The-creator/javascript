import unittest
import sys
import os

# Добавляем путь к корневой директории, чтобы импорты работали
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser_js import Parser  # Убедитесь, что файл называется parser_js.py или измените на parser

class TestParser(unittest.TestCase):

    def parse_code(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        return parser, parser.parse()

    def test_empty_program(self):
        """Проверка работы с пустым вводом"""
        _, root = self.parse_code("")
        self.assertEqual(root.type, 'Program')
        self.assertEqual(len(root.children), 0)

    def test_variable_declarations(self):
        """Проверка распознавания переменных let/const/var"""
        _, root = self.parse_code("let x = 10; const y; var z = 'test';")
        # Должно быть 3 узла VariableDeclaration
        decls = [n for n in root.children if n.type == 'VariableDeclaration']
        self.assertEqual(len(decls), 3)
        self.assertEqual(decls[0].value, 'x')
        self.assertEqual(decls[1].value, 'y')
        self.assertEqual(decls[2].value, 'z')

    def test_syntax_error_recovery(self):
        """Тест на выживаемость парсера при синтаксических ошибках"""
        # Ошибка: после let нет имени. Но парсер должен выжить и найти вторую переменную.
        parser, root = self.parse_code("let ; let validVar = 10;")
        
        # Должна быть зафиксирована как минимум одна ошибка в списке parser.errors
        self.assertGreater(len(parser.errors), 0)
        
        # Несмотря на ошибку, validVar должна быть в дереве
        decls = [n for n in root.children if n.type == 'VariableDeclaration']
        self.assertTrue(any(d.value == 'validVar' for d in decls))

    def test_function_parsing(self):
        """Проверка парсинга объявления функции и её структуры"""
        code = "function myFunc(a, b) { let x = 1; }"
        _, root = self.parse_code(code)
        
        func_node = root.children[0]
        self.assertEqual(func_node.type, 'Function')
        self.assertEqual(func_node.value, 'myFunc')
        
        # Проверяем параметры
        params = [n for n in func_node.children if n.type == 'Param']
        self.assertEqual(len(params), 2)
        self.assertEqual(params[0].value, 'a')

    def test_nested_complexity_nodes(self):
        """Проверка вложенности для расчета цикломатической сложности"""
        code = """
        function complex() {
            if (true) {
                while (false) { }
            }
        }
        """
        _, root = self.parse_code(code)
        func_node = root.children[0]
        
        # Рекурсивно ищем все узлы ControlStructure внутри функции
        def count_control(node):
            count = 1 if node.type == 'ControlStructure' else 0
            for child in node.children:
                count += count_control(child)
            return count

        control_count = count_control(func_node)
        # Ожидаем 2: if и while
        self.assertEqual(control_count, 2)



    def test_control_structures_standalone(self):
        """Проверка распознавания if/while вне функций"""
        code = "if (x) { } while (y) { }"
        _, root = self.parse_code(code)
        
        control_nodes = [n for n in root.children if n.type == 'ControlStructure']
        self.assertEqual(len(control_nodes), 2)
        self.assertIn(control_nodes[0].value, ['if', 'while'])

if __name__ == '__main__':
    unittest.main()