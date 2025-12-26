class Fixer:
    def __init__(self, code):
        self.code = code
        self.fixes = [] 

    def add_fix(self, start, end, replacement):
        self.fixes.append((start, end, replacement))

    def apply(self):
        sorted_fixes = sorted(self.fixes, key=lambda x: x[0], reverse=True)
        
        modified_code = self.code
        for start, end, replacement in sorted_fixes:
            modified_code = modified_code[:start] + replacement + modified_code[end:]
        
        return modified_code

