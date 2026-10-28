"""A small AI agent: one model, one calculator, and one loop."""

import math


# Step 1: The tool. Only these four operations can run;
def calculate(a, b, operation):
    for number in (a, b):
        if type(number) not in (int, float) or not math.isfinite(number):
            raise ValueError("Please use finite numbers.")

    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        result = a / b
    else:
        raise ValueError("Unknown operation.")

    if not math.isfinite(result):
        raise ValueError("The result is too large.")
    return result


# Step 2: Tell the model what the tool accepts.
CALCULATOR_TOOL = {
    "name": "calculate",
    "description": "Add, subtract, multiply, or divide two numbers.",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"},
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide"],
            },
        },
        "required": ["a", "b", "operation"],
        "additionalProperties": False,
    },
}

INSTRUCTIONS = """You are a helpful calculator assistant.
Use calculate for every arithmetic calculation, including intermediate steps.
Use tool results to answer clearly and briefly. If a tool reports an error,
explain it; do not invent a result. For non-math requests, answer normally.
"""
