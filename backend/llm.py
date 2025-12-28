"""LLM integration wrapper
Supports OpenAI and Anthropic (Claude). Chooses provider based on env vars:
 - OPENAI_API_KEY -> uses OpenAI Chat completions
 - ANTHROPIC_API_KEY -> uses Anthropic completions

Public API:
 - generate_llm_response(user_message: str, detection_context: dict, session_history: list) -> str

This wrapper is defensive: if no API key is configured it returns None so caller
can fall back to a local/mock response.
"""
from __future__ import annotations

import os
import json
import time
from typing import Optional, List, Dict

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-2.1")


def _build_system_prompt(detection_context: Optional[Dict]) -> str:
    parts = [
        "You are a concise safety assistant for Hazm Tuwaiq.",
        "Use available detection context to provide actionable, prioritized recommendations.",
    ]
    if detection_context:
        parts.append("Recent detection summary:\n")
        # summarize basic info
        objs = detection_context.get("objects") if isinstance(detection_context, dict) else None
        if objs:
            parts.append(f"- {len(objs)} detected objects; top 3: \n")
            for o in objs[:3]:
                parts.append(f"  - {o.get('class')} (conf={o.get('confidence')}) bbox={o.get('bbox')}\n")
    return "\n".join(parts)


def generate_llm_response(user_message: str, detection_context: Optional[Dict], session_history: List[Dict]) -> Optional[str]:
    # Try OpenAI first
    system_prompt = _build_system_prompt(detection_context)

    if OPENAI_KEY:
        try:
            import openai
            openai.api_key = OPENAI_KEY
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            # include last few messages as context
            for item in (session_history or [])[-6:]:
                role = "assistant" if item.get("assistant_response") else "user"
                content = item.get("assistant_response") or item.get("user_message")
                messages.append({"role": role, "content": content})

            messages.append({"role": "user", "content": user_message})

            resp = openai.ChatCompletion.create(model=OPENAI_MODEL, messages=messages, max_tokens=400, temperature=0.2)
            text = resp.choices[0].message.content.strip()
            return text
        except Exception:
            pass

    if ANTHROPIC_KEY:
        try:
            from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
            client = Anthropic(api_key=ANTHROPIC_KEY)
            # Build prompt
            prompt_parts = ["Assistant is concise and gives safety recommendations.", "\n\n"]
            prompt_parts.append(system_prompt)
            prompt_parts.append("\n\nUser: ")
            prompt_parts.append(user_message)
            prompt = "".join(prompt_parts)
            resp = client.completions.create(model=ANTHROPIC_MODEL, prompt=prompt, max_tokens_to_sample=400)
            return resp.get("completion", "").strip()
        except Exception:
            pass

    return None
