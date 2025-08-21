# analytics_platform/agent_builder/agent_config_loader.py

import json
from pathlib import Path

def load_agent_config(agent_name: str, config_dir="config/agents/"):
    config_path = Path(config_dir) / f"{agent_name}_config.json"
    with open(config_path) as f:
        return json.load(f)
