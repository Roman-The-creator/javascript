import re

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
        self.start_idx = 0
        self.end_idx = 0

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        # Регулярные выражения для всех типов токенов JavaScript
        self.token_specification = [
            ('COMMENT',  r'//.*|/\*[\s\S]*?\*/'), # Однострочные и многострочные комментарии
            ('KEYWORD',  r'\b(let|const|var|function|if|else|while|for|return)\b'),
            ('ID',       r'[a-zA-Z_$][a-zA-Z0-9_$]*'), # Идентификаторы
            ('NUMBER',   r'\d+(\.\d*)?'),               # Числа
            ('STRING',   r'"[^"]*"|\'[^\']*\''),       # Строки
            ('OP',       r'[+\-*/%=<>!&|]+'),          # Операторы
            ('PUNCT',    r'[()\[\]{},.;]'),            # Пунктуация
            ('NEWLINE',  r'\n'),                       # Перенос строки
            ('SKIP',     r'[ \t\r]+'),                 # Пробелы и табы
            ('MISMATCH', r'.'),                        # Любой другой символ (ошибка)
        ]

    def tokenize(self):
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.token_specification)
        line_num = 1
        line_start = 0
        
        for mo in re.finditer(tok_regex, self.code):
            kind = mo.lastgroup
            value = mo.group()
            start_idx = mo.start()
            column = start_idx - line_start
            
            if kind == 'NEWLINE':
                line_start = start_idx + 1
                line_num += 1
                continue
            elif kind == 'SKIP':
                token = Token(kind, value, line_num, column)
                token.start_idx = start_idx
                token.end_idx = mo.end()
                self.tokens.append(token)
            elif kind == 'MISMATCH':
                print(f"Lexical Error: Unexpected character {repr(value)} at line {line_num}")
            else:
                # Основные токены
                token = Token(kind, value, line_num, column)
                token.start_idx = start_idx
                token.end_idx = mo.end()
                self.tokens.append(token)
        
        return self.tokens
