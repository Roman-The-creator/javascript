import sys
import os
import argparse
from config import Config
from lexer import Lexer
from parser_js import Parser
from engine import LinterEngine
from fixer import Fixer

def main():
    parser = argparse.ArgumentParser(
        prog='js_linter',
        description='JS Linter: Анализ синтаксиса, стиля и сложности JavaScript кода', 
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '--fix', 
        action='store_true', 
        help='Включить автоматическое исправление ошибок'
    )

    args = parser.parse_args()

    if not args.path:
        parser.print_help()
        return

    js_file_path = args.path
    config_path = args.config

    if not os.path.exists(js_file_path):
        print(f"Error: File {js_file_path} not found.")
        return

    config = Config(config_path)
    
    if args.fix:
        config.data['autofix'] = True

    with open(js_file_path, 'r', encoding='utf-8') as f:
        original_code = f.read()

    lexer = Lexer(original_code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    fixer = None
    if config.get('autofix'):
        fixer = Fixer(original_code)

    engine = LinterEngine(original_code, config)
    
    for parse_error in parser.errors:
        engine.reports.append(f"[SYNTAX ERROR] {parse_error}")

    engine.run(tokens, ast, fixer)

    print(f"\nLinting Report for: {js_file_path}")
    if not engine.reports:
        print("Success: No style issues found.")
    else:
        for report in engine.reports:
            print(report)

    if fixer and config.get('autofix') and fixer.fixes:
        new_code = fixer.apply()
        try:
            with open(js_file_path, 'w', encoding='utf-8') as f:
                f.write(new_code)
            print(f"\n[FIXER] Applied {len(fixer.fixes)} fixes automatically.")
        except Exception as e:
            print(f"\n[FIXER] Error saving changes: {e}")

if __name__ == "__main__":
    main()
