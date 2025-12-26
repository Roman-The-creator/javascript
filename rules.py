import re

class BaseRule:
    def __init__(self, config):
        # Принимаем словарь настроек (config.settings)
        self.config = config

class FormattingRules(BaseRule):
    """Правила форматирования и стилистики"""

    def check_naming(self, tokens):
        errors = []
        # Тест ожидает стандартный camelCase, если иное не указано
        pattern = self.config.get('naming_pattern') or r'^[a-z][a-zA-Z0-9]*$'
        
        for i in range(len(tokens)):
            tok = tokens[i]
            if tok.type == 'ID':
                # Ищем ключевое слово перед идентификатором (пропуская SKIP)
                prev_idx = i - 1
                while prev_idx >= 0 and tokens[prev_idx].type == 'SKIP':
                    prev_idx -= 1
                
                if prev_idx >= 0 and tokens[prev_idx].value in ['let', 'const', 'var', 'function']:
                    if not re.match(pattern, tok.value):
                        # Текст сообщения должен совпадать с ожиданиями тестов
                        errors.append((tok.line, f"Naming violation: '{tok.value}'"))
        return errors

    def check_spacing(self, tokens, fixer=None):
        errors = []
        if self.config.get('require_spaces_operators') is False:
            return errors

        # Проверяем все операторы: =, +, -, *, /
        for i in range(1, len(tokens) - 1):
            tok = tokens[i]
            if tok.type == 'OP' and tok.value in ['=', '+', '-', '*', '/']:
                missing_before = tokens[i-1].type != 'SKIP'
                missing_after = tokens[i+1].type != 'SKIP'
                
                if missing_before or missing_after:
                    # Тест в integration ждет "around", а в rules ждет кол-во ошибок
                    errors.append((tok.line, f"Missing space around operator '{tok.value}'"))
                    if fixer:
                        if missing_before: fixer.add_fix(tok.start_idx, tok.start_idx, " ")
                        if missing_after: fixer.add_fix(tok.end_idx, tok.end_idx, " ")
        return errors

    def check_blank_lines(self, tokens):
        errors = []
        max_blanks = self.config.get('max_empty_lines') or 2
        
        # Фильтруем только значимые токены (игнорируем SKIP, так как нам важны номера строк кода)
        code_tokens = [t for t in tokens if t.type != 'SKIP']
        
        for i in range(1, len(code_tokens)):
            prev_tok = code_tokens[i-1]
            curr_tok = code_tokens[i]
            
            # Разница в номерах строк между двумя токенами кода
            # Например: строка 1 и строка 4 -> разница 3 (т.е. 2 пустые строки внутри)
            line_diff = curr_tok.line - prev_tok.line - 1
            
            if line_diff >= max_blanks:
                # Репортим ошибку на строку, где начался лишний разрыв
                errors.append((prev_tok.line + 1, "Too many blank lines"))
                
        return errors

class LogicRules(BaseRule):
    """Правила анализа структуры и логики"""

    def get_complexity(self, node):
        """Рекурсивно собирает сложность со всех вложенных узлов"""
        total = getattr(node, 'complexity', 0)
        for child in node.children:
            total += self.get_complexity(child)
        return total

    def check_complexity(self, node, reports):
        max_c = self.config.get('max_complexity') or 10
        
        if node.type == 'Function':
            # V(G) = кол-во узлов ветвления + 1
            total = self.get_complexity(node) + 1
            if total > max_c:
                # Сообщение должно содержать "complexity too high" для test_rules.py
                reports.append((node.line, f"complexity too high: {total}"))
        
        for child in node.children:
            self.check_complexity(child, reports)

    def check_unused(self, ast, tokens):
        errors = []
        declared = [] # (имя, строка)
        used = set()

        # 1. Находим все объявления через обход AST
        def walk_ast(n):
            if n.type in ['VariableDeclaration', 'Param']:
                declared.append((n.value, n.line))
            for child in n.children:
                walk_ast(child)
        walk_ast(ast)

        # 2. Находим все использования имен в токенах
        for i, tok in enumerate(tokens):
            if tok.type == 'ID':
                # Проверяем, не является ли этот ID частью объявления
                p_idx = i - 1
                while p_idx >= 0 and tokens[p_idx].type == 'SKIP':
                    p_idx -= 1
                
                is_declaration = (p_idx >= 0 and tokens[p_idx].value in ['let', 'const', 'var', 'function'])
                if not is_declaration:
                    used.add(tok.value)

        # 3. Сопоставляем
        for name, line in declared:
            if name not in used and name != 'console':
                errors.append((line, f"Unused variable: '{name}'"))
        
        return errors