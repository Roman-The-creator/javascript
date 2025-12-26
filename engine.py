from rules import FormattingRules, LogicRules

class LinterEngine:
    def __init__(self, code, config_obj):
        self.code = code
        self.config = config_obj
        self.reports = []
        # Собираем номера строк, которые нужно игнорировать
        self.disabled_lines = self._get_disabled_lines()
        # Инициализируем наборы правил
        self.fmt_rules = FormattingRules(self.config.settings)
        self.logic_rules = LogicRules(self.config.settings)

    def _get_disabled_lines(self):
        """Сканирует код на наличие комментариев управления линтером"""
        disabled = set()
        lines = self.code.split('\n')
        is_disabled = False
        
        for i, line in enumerate(lines, 1):
            if '/* lint-disable */' in line:
                is_disabled = True
            if '/* lint-enable */' in line:
                is_disabled = False
                # Саму строку с enable тоже исключаем из проверки
                disabled.add(i)
                continue
            
            if is_disabled:
                disabled.add(i)
        return disabled

    def add_report(self, line, message):
        """Добавляет ошибку в список, если строка не находится в блоке disable"""
        if line not in self.disabled_lines:
            self.reports.append(f"Line {line}: {message}")

    def run(self, tokens, ast, fixer=None):
        """Запускает все проверки по очереди"""
        
        # 1. Проверка нейминга (CamelCase и т.д.)
        for line, msg in self.fmt_rules.check_naming(tokens):
            self.add_report(line, msg)
            
        # 2. Проверка пробелов вокруг операторов (с поддержкой Fixer)
        for line, msg in self.fmt_rules.check_spacing(tokens, fixer):
            self.add_report(line, msg)
            
        # 3. Проверка избыточных пустых строк
        for line, msg in self.fmt_rules.check_blank_lines(tokens):
            self.add_report(line, msg)

        # 4. Проверка цикломатической сложности (анализ AST)
        # Передаем список напрямую, так как метод рекурсивный
        temp_reports = []
        self.logic_rules.check_complexity(ast, temp_reports)
        for line, msg in temp_reports:
            self.add_report(line, msg)
        
        # 5. Проверка неиспользуемых переменных
        for line, msg in self.logic_rules.check_unused(ast, tokens):
            self.add_report(line, msg)

        return self.reports