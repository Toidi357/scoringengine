import configparser
import os
import importlib.util
import sys
from typing import Callable, Dict
from pprint import pprint
from termcolor import colored, cprint
from colorama import init
init()

"""
DO NOT TOUCH
"""

class Check:
    """Represents a single scoring task."""
    def __init__(self, name: str, host: str, exec_func: Callable, metadata: Dict):
        self.name = name
        self.host = host
        self.exec = exec_func  # The 'run' function from the script
        self.metadata = metadata
        self.last_result = None

    def run(self):
        """Executes the check and captures the result."""
        try:
            # We pass host and metadata into the imported 'run' function
            self.last_result = self.exec(self.host, self.metadata)
            return self.last_result
        except Exception as e:
            cprint(f"Error executing {self.name}: {e}", "red")
            self.last_result = False
            return False

    def __repr__(self):
        return f"<Check {self.name} target={self.host} metadata={self.metadata}>"

class ScoringEngine:
    def __init__(self, config_path, checks_dir="checks"):
        self.config_path = config_path
        self.checks_dir = checks_dir
        self.registry = {}  # Stores { 'check-name': run_function_pointer }
        self.active_checks = []

        self._load_plugins()

    def _load_plugins(self):
        """Dynamically imports .py files and grabs their 'run' functions."""
        subfolders = ['default', 'custom']
        
        for sub in subfolders:
            folder_path = os.path.join(self.checks_dir, sub)
            if not os.path.exists(folder_path):
                continue

            for filename in os.listdir(folder_path):
                if filename.endswith(".py"):
                    script_name = filename[:-3]
                    file_path = os.path.join(folder_path, filename)

                    # Dynamic Import Magic
                    spec = importlib.util.spec_from_file_location(script_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    
                    # Add to sys.modules to allow relative imports within the plugin if needed
                    sys.modules[script_name] = module
                    
                    try:
                        spec.loader.exec_module(module)
                        
                        # Verify the 'run' function exists
                        if hasattr(module, 'run'):
                            self.registry[script_name] = module.run
                        else:
                            cprint(f"Logic Error: {filename} has no 'run' function. Skipping.", "red")
                    except Exception as e:
                        cprint(f"Load Error: Could not import {filename}: {e}", "red")

        cprint(f"Engine initialized. {len(self.registry)} possible check scripts loaded.", 'yellow')


    def parse_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError("Config file missing.")

        config = configparser.ConfigParser()
        config.read(self.config_path)

        for section in config.sections():
            check_key = config.get(section, 'Check', fallback=None)
            host = config.get(section, 'Host', fallback=None)

            if check_key in self.registry:
                # Get everything else as metadata
                metadata = {k: v for k, v in config.items(section) if k not in ['host', 'check']}
                
                new_check = Check(
                    name=section,
                    host=host,
                    exec_func=self.registry[check_key],
                    metadata=metadata
                )
                
                self.active_checks.append(new_check)
        return self.active_checks

# --- Execution ---
if __name__ == "__main__":
    engine = ScoringEngine("scoring.conf")
    checks = engine.parse_config()
    
    pprint(checks)