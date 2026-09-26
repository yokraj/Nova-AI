import sys
import os
import asyncio
import re

sys.path.insert(0, '.')

# Stop words to exclude from lexical intent tokens
STOP_WORDS = {"to", "a", "an", "the", "of", "for", "in", "on", "with", "and", "or", "is", "at", "by", "from", "it", "this", "that"}

# Generic action verbs that should not carry primary lexical specificity unless part of exact name match
GENERIC_VERBS = {"add", "make", "create", "set", "get", "do", "run", "perform", "apply", "start", "use"}

def extract_lexical_tokens(query: str) -> set:
    """Extracts clean, un-expanded lexical intent tokens from user query."""
    words = re.findall(r'\b[a-zA-Z0-9_]+\b', query.lower())
    tokens = {w for w in words if w not in STOP_WORDS}
    return tokens

def get_intent_technical_tokens(query: str) -> set:
    """Extracts specific non-generic technical tokens from query."""
    tokens = extract_lexical_tokens(query)
    tech = {t for t in tokens if t not in GENERIC_VERBS and t != "object"}
    return tech

print("Test query 'make an object metallic':")
print("  Lexical tokens:", extract_lexical_tokens("make an object metallic"))
print("  Technical tokens:", get_intent_technical_tokens("make an object metallic"))

print("\nTest query 'add subdivision to a mesh':")
print("  Lexical tokens:", extract_lexical_tokens("add subdivision to a mesh"))
print("  Technical tokens:", get_intent_technical_tokens("add subdivision to a mesh"))
