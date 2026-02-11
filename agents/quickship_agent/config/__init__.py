"""
Configuration package for QuickShip AI Agent
"""

# Import all variables from the main config.py file to maintain backward compatibility
import os
import importlib.util

# Get the path to the main config.py file (one level up)
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.py')

# Load the main config module
spec = importlib.util.spec_from_file_location("main_config", config_path)
main_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_config)

# Export all variables from main config
for attr in dir(main_config):
    if not attr.startswith('_') and not callable(getattr(main_config, attr)):
        globals()[attr] = getattr(main_config, attr)