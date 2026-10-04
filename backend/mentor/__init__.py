"""AI mentor: explains a finished plan in English or Roman Urdu. It never calculates.

Pipeline (Member 5's design, ported from TypeScript):

    finished plan -> numbered facts -> model writes text with [[F#]] tokens
                  -> digit guard -> one retry -> template fallback

The model is never shown a way to type a number: it can only reference fact
IDs, and code swaps in the verified value and its source.
"""
from .mentor import CHAT_FALLBACK_PREFIX, run_chat, run_explain, run_mentor  # noqa: F401
