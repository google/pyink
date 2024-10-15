import importlib.resources
import json
from typing import Any


def get_schema(tool_name: str = "pyink") -> Any:
    """Get the stored complete schema for black's settings."""
    assert tool_name == "pyink", "Only black is supported."

    pkg = "pyink.resources"
    fname = "pyink.schema.json"

    schema = importlib.resources.files(pkg).joinpath(fname)
    with schema.open(encoding="utf-8") as f:
        return json.load(f)
