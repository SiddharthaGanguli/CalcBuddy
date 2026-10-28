"""A small AI agent: one model, one calculator, and one loop."""

import argparse
import json
import math
import os


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


# Step 3: The loop. Ask the model, run its tool calls, send results back.
def run_agent(request, client, model):
    messages = [
        {"role": "system", "content": INSTRUCTIONS},
        {"role": "user", "content": request},
    ]

    for _ in range(10):
        response = client.chat.completions.create(
            model=model,
            tools=[{"type": "function", "function": CALCULATOR_TOOL}],
            messages=messages,
        )
        message = response.choices[0].message
        tool_calls = message.tool_calls or []

        if not tool_calls:
            return message.content or "No answer was returned."

        messages.append(message.model_dump(exclude_none=True))

        for call in tool_calls:
            function = call.function
            print(f"Using tool: {function.name}({function.arguments})")
            try:
                if function.name != "calculate":
                    raise ValueError("Unknown tool.")
                arguments = json.loads(function.arguments)
                result = {"result": calculate(**arguments)}
            except (ValueError, TypeError, OverflowError) as error:
                result = {"error": str(error)}

            print(f"Tool result: {json.dumps(result)}")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })

    return "Stopped after 10 model turns. Try a simpler request."


# Step 4: A tiny command-line interface. Each request starts a fresh conversation.
def main():
    from openai import APIError, OpenAI

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["openai", "ollama", "local"], default="openai")
    parser.add_argument("--model", help="Exact model name from your provider or local server")
    parser.add_argument("--base-url", help="OpenAI-compatible API URL, including /v1")
    args = parser.parse_args()

    if args.provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise SystemExit("Set OPENAI_API_KEY before using OpenAI.")
        client = OpenAI(base_url=args.base_url or "https://api.openai.com/v1")
        model = args.model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    else:
        if not args.model:
            parser.error("--model is required for Ollama and other local servers.")
        if args.provider == "local" and not args.base_url:
            parser.error("--base-url is required for other local servers.")
        client = OpenAI(
            base_url=args.base_url or "http://localhost:11434/v1",
            # Ollama ignores this placeholder; other servers may require a key.
            api_key=os.getenv("LOCAL_API_KEY", "local"),
            timeout=120.0,
            max_retries=0,
        )
        model = args.model
    print(f"Provider: {args.provider} | Model: {model}")
    print("Calculator agent. Type 'quit' to exit.")

    while True:
        try:
            request = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if request.lower() in ("quit", "exit"):
            break
        if not request:
            continue
        try:
            print("Agent:", run_agent(request, client, model))
        except APIError as error:
            print(f"API request failed: {error}")


if __name__ == "__main__":
    main()
