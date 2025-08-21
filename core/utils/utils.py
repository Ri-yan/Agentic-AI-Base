import os
import json
import time
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import importlib
import inspect

from api.models.base_payload import BasePayload


# ------------------------------
# File & Directory Utilities
# ------------------------------

def read_json(filepath: str) -> Any:
    """
    Read a JSON file and return its contents as a Python object.

    Example:
        data = read_json("data.json")
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(data: Any, filepath: str, indent: int = 4) -> None:
    """
    Write a Python object to a file in JSON format.

    Example:
        write_json(data, "output.json")
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)


def ensure_dir(path: str) -> None:
    """
    Ensure a directory exists. If not, create it.

    Example:
        ensure_dir("logs/")
    """
    os.makedirs(path, exist_ok=True)


def list_files(directory: str, extension: Optional[str] = None) -> List[str]:
    """
    List all files in a directory. Optionally filter by file extension.

    Example:
        files = list_files("data", ".csv")
    """
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if extension:
        files = [f for f in files if f.endswith(extension)]
    return files


# ------------------------------
# String Utilities
# ------------------------------

def slugify(text: str) -> str:
    """
    Convert a string to a URL-friendly slug.

    Example:
        slug = slugify("Hello World!")  # hello-world
    """
    return ''.join(c if c.isalnum() else '-' for c in text.lower()).strip('-')


def truncate(text: str, max_length: int) -> str:
    """
    Truncate a string to a maximum length, adding ellipsis if needed.

    Example:
        short = truncate("This is a long string", 10)  # "This is..."
    """
    return text if len(text) <= max_length else text[:max_length - 3] + '...'


# ------------------------------
# Time Utilities
# ------------------------------

def current_timestamp() -> str:
    """
    Get the current timestamp as a string.

    Example:
        ts = current_timestamp()  # "2025-08-14 10:55:32"
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def measure_time(func):
    """
    Decorator to measure execution time of a function.

    Example:
        @measure_time
        def slow_function():
            time.sleep(1)
    """

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"[{func.__name__}] took {end - start:.4f} seconds")
        return result

    return wrapper


# ------------------------------
# Logging Utility
# ------------------------------

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Set up and return a logger with the specified name and level.

    Example:
        logger = setup_logger("my_app")
        logger.info("Started")
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


# ------------------------------
# Dictionary Utilities
# ------------------------------

def merge_dicts(a: Dict, b: Dict) -> Dict:
    """
    Recursively merge two dictionaries.

    Example:
        merged = merge_dicts({'a': 1}, {'b': 2})
    """
    result = a.copy()
    for key, value in b.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    Flatten a nested dictionary using dot notation.

    Example:
        flatten_dict({'a': {'b': 1}})  # {'a.b': 1}
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

# utils/importer.py

def import_from_path(dotted_path: str):
    """Dynamically import a class from a full dotted path string."""
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)



def import_payload_class(class_name: str, base_module: str = "models"):
    try:
        module = importlib.import_module(base_module)
        for name, obj in inspect.getmembers(module):
            if name == class_name:
                return obj
    except Exception as e:
        pass  # Optionally log error

    return BasePayload  # Fallback