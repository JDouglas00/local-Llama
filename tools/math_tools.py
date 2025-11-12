# tools/math_tools.py
import math
from typing import Dict, Any

SCHEMA = {
  "type": "function",
  "function": {
    "name": "circle_area",
    "description": "Compute area of a circle (cm^2).",
    "parameters": {
      "type": "object",
      "properties": {
        "radius": {"type":"number", "minimum":0}
      },
      "required": ["radius"]
    }
  }
}

def circle_area(args: Dict[str, Any]) -> Dict[str, Any]:
    r = float(args["radius"])
    return {"area_cm2": math.pi * r * r}
