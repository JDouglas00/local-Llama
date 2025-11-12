# tools/plc_tools.py
# Fill with real I/O later (OPC UA, pymodbus, HTTP bridge, etc.)
from typing import Dict, Any

SCHEMA = {
  "type": "function",
  "function": {
    "name": "get_fault_instructions",
    "description": "Return SOP steps for a given fault code.",
    "parameters": {
      "type": "object",
      "properties": {
        "fault_code": {"type":"string", "description":"e.g., F07"}
      },
      "required": ["fault_code"]
    }
  }
}

_FAULTS = {
  "F07": "Clear jam at sensor S2; verify belt tension; reset via HMI.",
  "F11": "VFD overcurrent: inspect mechanical binding; check current limit."
}

def get_fault_instructions(args: Dict[str, Any]) -> Dict[str, Any]:
    code = str(args["fault_code"]).upper()
    return {"fault_code": code, "instructions": _FAULTS.get(code, "No entry found.")}
