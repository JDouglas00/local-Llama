# tools/registry.py
from typing import Dict, Any, Callable, List
from tools import parts_tools

# Describe callable tools (simple schema for now)
TOOLS: Dict[str, Dict[str, Any]] = {
    "low_stock": {
        "description": "Get low-stock items across locations.",
        "params": {"limit": {"type": "integer", "default": 20}},
        "fn": parts_tools.low_stock,
    },
    "bom_explosion": {
        "description": "One-level BOM explosion for a parent SKU and quantity.",
        "params": {
            "parent_sku": {"type": "string"},
            "qty": {"type": "number", "default": 1.0},
        },
        "fn": parts_tools.bom_explosion,
    },
    "value_on_hand_main": {
        "description": "Inventory value by category in MAIN location.",
        "params": {},
        "fn": parts_tools.value_on_hand_main,
    },
}

def call_tool(name: str, **kwargs):
    spec = TOOLS[name]
    return spec["fn"](**kwargs)

