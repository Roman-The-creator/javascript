import unittest
import os
import sys


def run_unit_tests():
    print("Поиск тесты в папке 'tests'...")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='tests', pattern='test_*.py')
    
    print(f"Найдено тестов: {suite.countTestCases()}")
    
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

if __name__ == "__main__":
    try:
        res = run_unit_tests()
        print("Тестирование завершено")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
