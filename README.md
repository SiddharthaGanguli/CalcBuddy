# CalcBuddy

This example uses plain Python and a shared Chat Completions API format for
OpenAI, Ollama, and other compatible local servers. There is no agent
framework: you can read the entire system in `calculator_agent.py`.

## 1. Start with the tool

`calculate(a, b, operation)` takes two numbers and performs one operation.
For example, `calculate(12, 8, "add")` returns `20`.

The `if` statements allow only addition, subtraction, multiplication, and
division. We never run model-generated Python or use `eval()`. The function
also rejects division by zero and non-finite values. It uses ordinary Python
numbers; decimal fractions can have the usual floating-point rounding.

## 2. Describe the tool to the model

`CALCULATOR_TOOL` is the tool's instruction card. It explains the name,
arguments, and allowed operations. The Python function validates the inputs
even if a local model sends incorrect arguments.

The model can request a call such as:

```json
{"a": 12, "b": 8, "operation": "add"}
```

The model requests the action. Our Python code actually executes it.

## 3. Add the model and loop

`run_agent()` starts with the user's request and repeats these steps:

1. Send the conversation and tool description to the model.
2. If the model returns an answer, return that answer.
3. If it requests a tool, print the call and run the calculator.
4. Print the result and send it back using the call's ID.
5. Let the model continue with that result.

Keeping the previous response in `messages` lets the model follow its earlier
steps. The call ID connects each result to the correct tool request. A limit of
10 model turns prevents an endless loop. Tool errors are sent back too, so the
model can explain them.

For `(12 + 8) * 3`, it can add first, receive `20`, then multiply `20` by `3`.
The prompt asks it to use the calculator for arithmetic; choosing when to call
the tool is still the model's decision.

## 4. Run it

Use Python 3.10 or newer. In PowerShell, from this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:OPENAI_API_KEY = "your-api-key"
.\.venv\Scripts\python.exe calculator_agent.py
```

You need an OpenAI API key with API billing/access. The key stays outside the
source code. Optionally set `OPENAI_MODEL` to another model available to your
account that supports Chat Completions function calling.

### Use a local model with Ollama

Install [Ollama](https://ollama.com/download), then download a model that supports
tools. For example, in PowerShell:

```powershell
ollama pull llama3.1:8b
ollama list
.\.venv\Scripts\python.exe calculator_agent.py --provider ollama --model llama3.1:8b
```

If you already downloaded a tool-capable model, use its exact name from
`ollama list`; you don't need to download it again. Ollama must be running.
If the app isn't running, run `ollama serve` in another terminal.
No OpenAI API key is needed for local Ollama models.

### Use another local server

Start your model runner's OpenAI-compatible server and load a model that
supports tool calling. Use the URL and model ID shown by that server:

```powershell
.\.venv\Scripts\python.exe calculator_agent.py --provider local --base-url http://localhost:1234/v1 --model YOUR_MODEL_ID
```

The URL above is an example; replace the port if your server uses another one.
If the server requires authentication, set `$env:LOCAL_API_KEY = "your-key"`.
The same calculator and agent loop work for every provider; only the connection
and model name change. The `openai` Python package is also used as the local
API client, which does not mean requests are sent to OpenAI in local mode.

A downloaded model alone isn't enough: both the model and its server must
support tool calling. Embedding models such as `nomic-embed-text` cannot run
this agent. If the model answers without calling a tool, no calculator trace
will appear; try a tool-capable model. If a request fails, check the server,
model name, URL, and tool support. Use `--help` to see the options.

An illustrative session (wording and number formatting may vary):

```text
You: What is 12 plus 8?
Using tool: calculate({"a":12,"b":8,"operation":"add"})
Tool result: {"result": 20}
Agent: 12 plus 8 is 20.
```

Try `What is (12 + 8) * 3?`, `Divide 10 by zero`, or `Hello!` next.
Each new prompt starts fresh; intermediate steps within a prompt share context.

The printed trace shows real tool calls and results, not the model's private
reasoning.

Official reference: [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling).
Local setup: [Ollama OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility).

installed Ollama model worked: it called the calculator twice for (12 + 8) × 3 and returned 60.

Run it with:
python calculator_agent.py --provider ollama --model llama3.1:8b
For another local server:
python calculator_agent.py --provider local --base-url http://localhost:1234/v1 --model YOUR_MODEL_ID