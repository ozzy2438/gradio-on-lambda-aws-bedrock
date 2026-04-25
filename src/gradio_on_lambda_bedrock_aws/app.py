from __future__ import annotations

import os
from typing import Any

import gradio as gr
from litellm import completion


DEFAULT_BEDROCK_MODEL = "bedrock/deepseek.v3.2"
DEFAULT_BEDROCK_MANTLE_MODEL = "bedrock_mantle/deepseek.v3.2"
DEFAULT_REGION = "us-east-1"
DEFAULT_SYSTEM_PROMPT = "You are a concise, helpful assistant."


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _optional_env_int(*names: str) -> int | None:
    for name in names:
        value = os.getenv(name)
        if not value:
            continue
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _model_name() -> str:
    if model := os.getenv("LITELLM_MODEL") or os.getenv("BEDROCK_MODEL"):
        return model
    if os.getenv("BEDROCK_MANTLE_API_KEY"):
        return DEFAULT_BEDROCK_MANTLE_MODEL
    return DEFAULT_BEDROCK_MODEL


def _aws_region() -> str:
    return (
        os.getenv("AWS_REGION_NAME")
        or os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or DEFAULT_REGION
    )


def _text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, dict):
        if content.get("type") == "text":
            return str(content.get("text") or "")
        if "text" in content:
            return str(content.get("text") or "")
        return ""

    if isinstance(content, list):
        parts = [_text_from_content(part) for part in content]
        return "\n".join(part for part in parts if part)

    return ""


def _messages_from_history(history: list[Any] | None) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []

    for item in history or []:
        if isinstance(item, dict):
            role = item.get("role")
            content = _text_from_content(item.get("content"))
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})
            continue

        if isinstance(item, (list, tuple)) and len(item) == 2:
            user_message = _text_from_content(item[0])
            assistant_message = _text_from_content(item[1])
            if user_message:
                messages.append({"role": "user", "content": user_message})
            if assistant_message:
                messages.append({"role": "assistant", "content": assistant_message})

    return messages


def _stream_delta_content(chunk: Any) -> str:
    try:
        delta = chunk.choices[0].delta
    except (AttributeError, IndexError, KeyError, TypeError):
        return ""

    if isinstance(delta, dict):
        return str(delta.get("content") or "")

    return str(getattr(delta, "content", "") or "")


def deepseek_response(message: str, history: list[Any] | None):
    messages = [
        {"role": "system", "content": os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)},
        *_messages_from_history(history),
        {"role": "user", "content": message},
    ]

    model = _model_name()
    request_kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": _env_float("BEDROCK_TEMPERATURE", 0.7),
        "max_tokens": _env_int("BEDROCK_MAX_TOKENS", 1024),
        "stream": True,
    }

    if model.startswith("bedrock/"):
        request_kwargs["aws_region_name"] = _aws_region()

    try:
        stream = completion(**request_kwargs)
        response = ""
        for chunk in stream:
            response += _stream_delta_content(chunk)
            if response:
                yield response
    except Exception as exc:
        yield f"Bedrock request failed: {exc}"


demo = gr.ChatInterface(
    fn=deepseek_response,
    title="DeepSeek V3.2",
    fill_height=True,
)


if __name__ == "__main__":
    launch_kwargs: dict[str, Any] = {}

    if server_name := os.getenv("GRADIO_SERVER_NAME"):
        launch_kwargs["server_name"] = server_name

    if server_port := _optional_env_int("GRADIO_SERVER_PORT", "PORT"):
        launch_kwargs["server_port"] = server_port

    demo.launch(**launch_kwargs)
