import json
import os

class Config:
    DEFAULT_CONFIG = {
        "naming_pattern": r"^[a-z][a-zA-Z0-9]*$",
        "max_empty_lines": 2,
        "max_complexity": 10,
        "indentation_size": 4,
        "require_spaces_operators": True,
        "no_unused_vars": True,
        "autofix": False
    }

    def __init__(self, config_path=None):
        self.settings = self.DEFAULT_CONFIG.copy()
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_settings = json.load(f)
                    self.settings.update(user_settings)
            except Exception as e:
                print(f"Warning: Could not read config file, using defaults. Error: {e}")

    def get(self, key):
        return self.settings.get(key)