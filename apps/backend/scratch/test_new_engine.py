import sys
import os
import asyncio
import re

sys.path.insert(0, '.')
from app.ai.kernel.capability_discovery import CapabilityDiscoveryEngine, DiscoverableCapability

STOP_WORDS = {"to", "a", "an", "the", "of", "for", "in", "on", "with", "and", "or", "is", "at", "by", "from", "it", "this", "that"}
GENERIC_VERBS = {"add", "make", "create", "set", "get", "do", "run", "perform", "apply", "start", "use"}

TERM_EQUIVALENTS = {
    "subdivision": {"subdivision", "subdivide", "subsurf"},
    "subdivide": {"subdivision", "subdivide", "subsurf"},
    "metallic": {"metallic", "metal", "metalness"},
    "metal": {"metallic", "metal", "metalness"},
    "gltf": {"gltf", "glb"},
    "glb": {"gltf", "glb"},
    "camera": {"camera", "cameras"},
    "render": {"render", "rendering"},
    "rendering": {"render", "rendering"},
    "screenshot": {"screenshot", "snapshot", "screen_capture", "printscreen"},
}

def get_expanded_terms(token: str) -> set:
    return TERM_EQUIVALENTS.get(token.lower(), {token.lower()})

def compute_lexical_score(query: str, cap: DiscoverableCapability) -> float:
    raw_query = query.lower().strip()
    words = [w for w in re.findall(r'\b[a-zA-Z0-9_]+\b', raw_query) if w not in STOP_WORDS]
    tech_words = [w for w in words if w not in GENERIC_VERBS and w != "object"]
    
    if not words:
        return 0.0

    cap_name = cap.name.lower()
    cap_name_tokens = set(cap_name.split("_"))
    cap_keywords = {k.lower() for k in cap.keywords}

    # 1. Exact name match
    if cap_name == raw_query.replace(" ", "_"):
        return 1.0

    # 2. Technical token matches in capability name
    name_tech_matches = 0
    kw_tech_matches = 0
    for tw in tech_words:
        equivs = get_expanded_terms(tw)
        if any(e in cap_name_tokens for e in equivs):
            name_tech_matches += 1
        elif any(e in cap_keywords for e in equivs):
            kw_tech_matches += 1

    total_tech = len(tech_words)
    if total_tech > 0:
        if name_tech_matches == total_tech:
            # All technical intent words match the action name directly!
            return 0.95
        elif name_tech_matches > 0:
            # Partial name match + kw match
            score = 0.60 + (0.25 * (name_tech_matches / total_tech)) + (0.10 * (kw_tech_matches / total_tech))
            return min(0.90, score)
        elif kw_tech_matches == total_tech:
            # All tech words match keywords (e.g. add_modifier for subdivision)
            return 0.75
        elif kw_tech_matches > 0:
            # Some tech words match keywords
            return 0.40 * (kw_tech_matches / total_tech)
        else:
            # No technical words matched
            return 0.0
    else:
        # Query only had generic verbs/words (e.g. "make object")
        verb_matches = sum(1 for w in words if w in cap_name_tokens)
        return min(0.5, 0.2 * verb_matches)

async def test():
    engine = CapabilityDiscoveryEngine()
    # Re-extract with clean keywords
    caps = engine.extractor.extract_all_capabilities()
    
    queries = [
        "add subdivision to a mesh",
        "make an object metallic",
        "import a glTF model",
        "create a camera",
        "render the scene",
        "take a screenshot",
        "create a camera and render"
    ]

    for q in queries:
        print("="*70)
        print(f"QUERY: '{q}'")
        scored = []
        for cap in caps:
            lex = compute_lexical_score(q, cap)
            scored.append((cap, lex))
        scored.sort(key=lambda x: x[1], reverse=True)
        for cap, lex in scored[:5]:
            if lex > 0:
                print(f"  {cap.capability_id:<40} lex={lex:.4f}")

if __name__ == '__main__':
    asyncio.run(test())
