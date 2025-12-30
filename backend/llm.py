"""LLM integration wrapper
Supports Google Gemini (FREE), OpenAI and Anthropic (Claude).
Chooses provider based on env vars (priority order):
 - GEMINI_API_KEY -> uses Google Gemini (FREE, no credit card needed!)
 - OPENAI_API_KEY -> uses OpenAI Chat completions
 - ANTHROPIC_API_KEY -> uses Anthropic completions

Public API:
 - generate_llm_response(user_message: str, detection_context: dict, session_history: list) -> dict

Returns structured response with error handling.
"""
from __future__ import annotations

import os
import json
import time
import uuid
from typing import Optional, List, Dict

# Google Gemini (FREE!) - Priority #1
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

# OpenAI (Paid)
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Anthropic (Paid)
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-2.1")


def _build_system_prompt(detection_context: Optional[Dict]) -> str:
    """Build comprehensive Safety Copilot system prompt"""
    parts = [
        "You are HAZM TUWAIQ Safety Copilot - an advanced HSE (Health, Safety & Environment) AI assistant.",
        "",
        "CORE COMPETENCIES:",
        "- ISO 45001:2018 Occupational Health & Safety Management",
        "- OSHA regulations and compliance",
        "- Incident investigation and root cause analysis",
        "- Risk assessment (HAZOP, FMEA, Bow-Tie)",
        "- Safety culture and behavioral safety",
        "- Hazard identification and control hierarchy",
        "",
        "OUTPUT REQUIREMENTS:",
        "1. Be concise and actionable",
        "2. Prioritize recommendations (High/Medium/Low risk)",
        "3. Reference relevant standards when applicable",
        "4. Provide specific control measures (Elimination > Substitution > Engineering > Administrative > PPE)",
        "5. If information is missing, ask for it professionally",
        "6. Never hallucinate facts - admit when uncertain",
        "",
        "RESPONSE STRUCTURE:",
        "- Hazard Identification",
        "- Risk Level",
        "- Recommended Controls",
        "- Compliance Mapping (if applicable)",
        "- Next Steps",
    ]
    
    if detection_context:
        parts.append("\n=== CURRENT DETECTION CONTEXT ===")
        objs = detection_context.get("objects") if isinstance(detection_context, dict) else None
        if objs:
            parts.append(f"Detected {len(objs)} objects:")
            for o in objs[:5]:
                parts.append(f"  • {o.get('class', 'unknown')} (confidence: {o.get('confidence', 0):.2f})")
            parts.append("\nAnalyze these detections from a safety perspective.")
    
    return "\n".join(parts)


def generate_llm_response(user_message: str, detection_context: Optional[Dict], session_history: List[Dict]) -> Dict:
    """Generate LLM response with structured error handling
    
    Returns:
        dict with keys: answer, error, how_to_fix, confidence, trace_id
    """
    trace_id = str(uuid.uuid4())[:8]
    system_prompt = _build_system_prompt(detection_context)

    # Try Google Gemini first (FREE!)
    if GEMINI_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_KEY)
            
            model = genai.GenerativeModel(GEMINI_MODEL)
            
            # Build conversation history
            chat_history = []
            for item in (session_history or [])[-6:]:
                if item.get("user_message"):
                    chat_history.append({
                        "role": "user",
                        "parts": [item["user_message"]]
                    })
                if item.get("assistant_response"):
                    chat_history.append({
                        "role": "model",
                        "parts": [item["assistant_response"]]
                    })
            
            # Start chat with history
            chat = model.start_chat(history=chat_history)
            
            # Send message with system prompt context
            full_message = f"{system_prompt}\n\nUser Question: {user_message}"
            response = chat.send_message(
                full_message,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=600,
                )
            )
            
            answer = response.text.strip()
            return {
                "answer": answer,
                "sources": ["Google Gemini " + GEMINI_MODEL + " (FREE)"],
                "confidence": 0.85,
                "trace_id": trace_id,
                "model_used": GEMINI_MODEL,
                "provider": "gemini"
            }
        except Exception as e:
            return {
                "error": f"Gemini API error: {str(e)}",
                "how_to_fix": "Get FREE API key at https://aistudio.google.com/app/apikey and set GEMINI_API_KEY in Render environment variables.",
                "trace_id": trace_id
            }

    # Try OpenAI (Paid)
    if OPENAI_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_KEY)
            
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            
            # Include last few messages as context
            for item in (session_history or [])[-6:]:
                if item.get("assistant_response"):
                    messages.append({"role": "assistant", "content": item["assistant_response"]})
                if item.get("user_message"):
                    messages.append({"role": "user", "content": item["user_message"]})

            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                max_tokens=600,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content.strip()
            return {
                "answer": answer,
                "sources": ["OpenAI " + OPENAI_MODEL],
                "confidence": 0.85,
                "trace_id": trace_id,
                "model_used": OPENAI_MODEL
            }
        except Exception as e:
            return {
                "error": f"OpenAI API error: {str(e)}",
                "how_to_fix": "Verify OPENAI_API_KEY is set correctly in environment variables. Check API quota and network connectivity.",
                "trace_id": trace_id
            }

    # Try Anthropic
    if ANTHROPIC_KEY:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=ANTHROPIC_KEY)
            
            # Build conversation
            messages = []
            for item in (session_history or [])[-6:]:
                if item.get("user_message"):
                    messages.append({"role": "user", "content": item["user_message"]})
                if item.get("assistant_response"):
                    messages.append({"role": "assistant", "content": item["assistant_response"]})
            
            messages.append({"role": "user", "content": user_message})
            
            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=600,
                system=system_prompt,
                messages=messages
            )
            
            answer = response.content[0].text.strip()
            return {
                "answer": answer,
                "sources": ["Anthropic " + ANTHROPIC_MODEL],
                "confidence": 0.85,
                "trace_id": trace_id,
                "model_used": ANTHROPIC_MODEL
            }
        except Exception as e:
            return {
                "error": f"Anthropic API error: {str(e)}",
                "how_to_fix": "Verify ANTHROPIC_API_KEY is set correctly in environment variables.",
                "trace_id": trace_id
            }

    # No API keys configured
    return {
        "error": "No LLM API key configured",
        "how_to_fix": "Get FREE Google Gemini API key at https://aistudio.google.com/app/apikey and set GEMINI_API_KEY in Render environment variables. Alternative: Set OPENAI_API_KEY or ANTHROPIC_API_KEY (paid options).",
        "trace_id": trace_id
    }
