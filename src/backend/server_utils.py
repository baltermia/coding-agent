"""
server_utils.py  –  Shared utilities for AISE501 Prompting Exercises
======================================================================
Connects to the vLLM inference server at silicon.fhgr.ch via the
OpenAI-compatible API.

This file is complete — no TODOs here.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ── Server configuration ──────────────────────────────────────────────────────
HOST    = os.getenv("HOST", "silicon.fhgr.ch")
PORT    = int(os.getenv("PORT", "7080"))
API_KEY = os.getenv("API_KEY", "EMPTY")
MODEL   = os.getenv("MODEL", "qwen3.5-35b-a3b")   # model ID served on silicon.fhgr.ch


def get_client() -> OpenAI:
    """Return an OpenAI-compatible client pointing at the vLLM server."""
    base_url = f"http://{HOST}:{PORT}/v1"
    return OpenAI(base_url=base_url, api_key=API_KEY)


def list_models(client: OpenAI) -> list[str]:
    """Return all model IDs available on the server."""
    return [m.id for m in client.models.list().data]


def chat(
    client: OpenAI,
    messages: list[dict],
    model: str = MODEL,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> str:
    """
    Send a list of chat messages to the LLM and return the response text.

    Qwen3's built-in chain-of-thought "think" mode is disabled via
    ``extra_body`` so that replies are direct and not wrapped in
    <think>…</think> blocks.

    Parameters
    ----------
    client      : OpenAI client returned by get_client()
    messages    : List of {"role": ..., "content": ...} dicts
    model       : Model ID (default: module-level MODEL constant)
    temperature : Sampling temperature (0 = deterministic, 1 = creative)
    max_tokens  : Maximum number of tokens in the response
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )
    return response.choices[0].message.content


def chat_json(
    client: OpenAI,
    messages: list[dict],
    model: str = MODEL,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> str:
    """
    Like chat(), but forces the model to emit syntactically valid JSON via
    response_format={"type": "json_object"}.

    The server constrains token sampling so the output is always parseable
    by json.loads() — no post-processing needed.  Use this whenever you
    need structured JSON output (Exercises 3 and 4).

    Parameters are the same as chat(); temperature defaults to 0.2 because
    deterministic output is usually preferable for structured data.
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        response_format={"type": "json_object"},
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )
    return response.choices[0].message.content


def _repair_json_strings(text: str) -> str:
    """
    Replace unescaped control characters (newline, tab, carriage return)
    inside JSON string values with their proper escape sequences.

    LLMs frequently emit literal newlines inside long string values, which
    is invalid JSON. This function fixes that without touching structural
    whitespace outside strings.
    """
    result: list[str] = []
    in_string = False
    escape = False
    _escapes = {'\n': '\\n', '\r': '\\r', '\t': '\\t'}
    for ch in text:
        if escape:
            result.append(ch)
            escape = False
            continue
        if ch == '\\' and in_string:
            result.append(ch)
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            result.append(ch)
            continue
        if in_string and ch in _escapes:
            result.append(_escapes[ch])
            continue
        result.append(ch)
    return ''.join(result)


def extract_json(text: str) -> str:
    """
    Extract and repair a JSON object or array from an LLM response that may
    contain extra prose, markdown code fences, or unescaped control characters.

    Strategy:
      1. Strip markdown ```json ... ``` or ``` ... ``` fences.
      2. Find the first '{' or '[' and extract to the matching closing bracket.
      3. Repair unescaped newlines/tabs inside string values.

    Returns the cleaned JSON string, or the original text as a fallback
    (so json.loads can raise a meaningful error with context).
    """
    import re

    # 1. Strip markdown fences
    fenced = re.sub(r"```(?:json)?\s*([\s\S]*?)\s*```", r"\1", text.strip())
    if fenced != text.strip():
        return _repair_json_strings(fenced.strip())

    # 2. Find first JSON container and extract to matching close
    extracted = text
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        idx = text.find(start_char)
        if idx == -1:
            continue
        depth = 0
        in_string = False
        escape = False
        for i, ch in enumerate(text[idx:], start=idx):
            if escape:
                escape = False
                continue
            if ch == '\\' and in_string:
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == start_char:
                depth += 1
            elif ch == end_char:
                depth -= 1
                if depth == 0:
                    extracted = text[idx: i + 1]
                    break
        break

    # 3. Repair unescaped control characters inside string values
    return _repair_json_strings(extracted)


def strip_code_fences(text: str) -> str:
    """Remove markdown code fences (```python ... ```) from LLM output.

    LLMs often wrap code in fences even when told not to. Call this before
    writing LLM-generated code to a .py file so it is directly executable.
    """
    import re
    text = text.strip()
    text = re.sub(r"^```\w*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def print_messages(messages: list[dict]) -> None:
    """Print the full messages list before sending it to the LLM.

    Call this before chat() or chat_json() to inspect the exact prompt
    hierarchy (system + user + assistant turns) that the model receives.
    This is the primary debugging and learning tool for prompt engineering.
    """
    width = 64
    print("\n" + "═" * width)
    print("  PROMPT SENT TO LLM")
    print("═" * width)
    for msg in messages:
        role = msg["role"].upper()
        print(f"\n── [{role}] " + "─" * max(0, width - len(role) - 6))
        print(msg["content"])
    print("\n" + "═" * width)


def print_separator(title: str = "") -> None:
    """Print a visual separator with an optional title."""
    width = 64
    print("\n" + "─" * width)
    if title:
        print(f"  {title}")
        print("─" * width)
