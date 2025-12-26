import sys
import os
from config import Config
from lexer import Lexer
from parser_js import Parser
from engine import LinterEngine
from fixer import Fixer

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_js_file> [path_to_config.json]")
        return

    js_file_path = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else 'style_config.json'

    if not os.path.exists(js_file_path):
        print(f"Error: File {js_file_path} not found.")
        return

    config = Config(config_path)

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

    print(f"\n--- Linting Report for: {js_file_path} ---")
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