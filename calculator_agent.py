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
