from dotenv import load_dotenv
from pathlib import Path
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"base directory for resource {BASE_DIR}")


def load_environs():
    config_path =BASE_DIR+ "/resources/config.env"
    try:
        """loading the file for environment configurtaion"""
        env_path = Path(config_path)
        envrinment = load_dotenv(dotenv_path=env_path)
        return envrinment

    except Exception as ex:
        print(ex)

