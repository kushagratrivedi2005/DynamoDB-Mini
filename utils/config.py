import json
import os
import logging

# Get the absolute path to the project root (assuming utils/ is one level deep)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config.json')

_config = None

def load_config():
    global _config
    if _config is None:
        try:
            with open(CONFIG_PATH, 'r') as f:
                _config = json.load(f)
        except Exception as e:
            logging.error(f"Failed to load config from {CONFIG_PATH}: {e}")
            raise e
    return _config

def get_port(service_name):
    config = load_config()
    return config['ports'].get(service_name)

def get_nodes():
    config = load_config()
    return config['nodes']

def get_timeout(name):
    config = load_config()
    return config['timeouts'].get(name)

def get_quorum(name):
    config = load_config()
    return config['quorum'].get(name)

def get_retry(name):
    config = load_config()
    return config['retries'].get(name)
