# function_call_demo.py
import json
from client import client
from config import MODEL
from tools.registry import TOOL_SCHEMAS, handle_tool_calls

messages = [
    {"role":"system","content":"You are a precise industrial assistant."},
    {"role":"user","content":"Area of a circle with radius 3 (cm), then fault steps for F07?"}
]

# First round: allow the model to request tool calls
res = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=TOOL_SCHEMAS,
    tool_choice="auto",
    temperature=0
)
msg = res.choices[0].message

# Execute requested tools
tool_msgs = handle_tool_calls(msg)
if tool_msgs:
    messages.append(msg)        # include the function_call message
    messages.extend(tool_msgs)  # include tool results

    # Second round: let model compose the final answer using tool outputs
    final = client.chat.completions.create(model=MODEL, messages=messages, temperature=0.2)
    print(final.choices[0].message.content)
else:
    # Model answered directly
    print(msg.content)
