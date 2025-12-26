class Node:
    """Узел абстрактного синтаксического дерева (AST)"""
    def __init__(self, type, value=None, line=None):
        self.type = type
        self.value = value
        self.line = line
        self.children = []
        self.complexity = 0  # Вес для цикломатической сложности

    def add_child(self, node):
        self.children.append(node)

class Parser:
    def __init__(self, tokens):
        # Фильтруем SKIP токены (пробелы), они не нужны для построения структуры
        self.tokens = [t for t in tokens if t.type != 'SKIP']
        self.current = 0
        self.errors = []
        self.root = Node('Program', line=1)

    def peek(self, offset=0):
        """Посмотреть токен впереди без сдвига указателя"""
        idx = self.current + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    def consume(self, expected_value=None):
        """Забрать текущий токен и перейти к следующему"""
        token = self.peek()
        if not token:
            raise Exception("Unexpected end of input")
        if expected_value and token.value != expected_value:
            raise Exception(f"Expected '{expected_value}', got '{token.value}' at line {token.line}")
        self.current += 1
        return token

    def parse(self):
        while self.current < len(self.tokens):
            token = self.peek()
            try:
                if token.value in ['let', 'const', 'var']:
                    self.root.add_child(self.parse_variable())
                elif token.value == 'function':
                    self.root.add_child(self.parse_function())
                elif token.value in ['if', 'while', 'for']:
                    # Добавляем вызов парсинга структур в основной цикл
                    self.root.add_child(self.parse_control_structure())
                else:
                    self.current += 1
            except Exception as e:
                # Для теста Recovery нужно, чтобы ошибки попадали в self.errors
                self.errors.append(str(e))
                # Ищем точку синхронизации (;) или конец блока (})
                while self.current < len(self.tokens) and self.tokens[self.current].value not in [';', '}']:
                    self.current += 1
                self.current += 1
        return self.root

    def parse_variable(self):
        start_tok = self.peek()
        line = start_tok.line
        self.consume() # keyword
        
        # ВАЖНО для теста Recovery: если дальше не ID, это ошибка!
        if not self.peek() or self.peek().type != 'ID':
            raise Exception(f"Expected identifier at line {line}")
            
        name_tok = self.consume()
        node = Node('VariableDeclaration', value=name_tok.value, line=line)
        
        # Если есть присваивание
        if self.peek() and self.peek().value == '=':
            self.consume('=')
            # Упрощенно: пропускаем всё до точки с запятой
            while self.peek() and self.peek().value != ';':
                self.consume()
        
        if self.peek() and self.peek().value == ';':
            self.consume(';')
        return node

    def parse_function(self):
        token = self.consume('function')
        name_token = self.consume()
        func_node = Node('Function', value=name_token.value, line=token.line)
        
        self.consume('(')
        while self.peek() and self.peek().value != ')':
            p = self.consume()
            if p.type == 'ID': func_node.add_child(Node('Param', value=p.value, line=p.line))
            if self.peek() and self.peek().value == ',': self.consume(',')
        self.consume(')')
        
        if self.peek() and self.peek().value == '{':
            self.consume('{')
            # Рекурсивно парсим содержимое функции, чтобы ControlStructure попали в func_node.children
            while self.peek() and self.peek().value != '}':
                t = self.peek()
                if t.value in ['if', 'while', 'for']:
                    func_node.add_child(self.parse_control_structure())
                elif t.value in ['let', 'const', 'var']:
                    func_node.add_child(self.parse_variable())
                else:
                    self.current += 1
            if self.peek(): self.consume('}')
        return func_node

    def parse_control_structure(self):
        token = self.consume() # if/while/for
        node = Node('ControlStructure', value=token.value, line=token.line)
        node.complexity = 1
        
        # Обработка условия (...)
        if self.peek() and self.peek().value == '(':
            self.consume('(')
            d = 1
            while self.current < len(self.tokens) and d > 0:
                t = self.consume()
                if t.value == '(': d += 1
                elif t.value == ')': d -= 1
        
        # Обработка тела { ... }
        if self.peek() and self.peek().value == '{':
            self.consume('{')
            while self.peek() and self.peek().value != '}':
                t = self.peek()
                if t.value in ['if', 'while', 'for']:
                    node.add_child(self.parse_control_structure()) # Вложенность!
                else:
                    self.current += 1
            if self.peek(): self.consume('}')
        return node