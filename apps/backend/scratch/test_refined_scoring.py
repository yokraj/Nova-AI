import sys
import os
import asyncio
import re

sys.path.insert(0, '.')
from app.ai.kernel.capability_discovery import CapabilityDiscoveryEngine, DiscoverableCapability, DiscoveryRankingWeights

STOP_WORDS = {"to", "a", "an", "the", "of", "for", "in", "on", "with", "and", "or", "is", "at", "by", "from", "it", "this", "that"}

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
    # 1. Clean query words
    query_words = [w for w in re.findall(r'\b[a-zA-Z0-9_]+\b', raw_query) if w not in STOP_WORDS]
    if not query_words:
        return 0.0

    cap_name = cap.name.lower()
    cap_name_tokens = set(cap_name.split("_"))
    cap_keywords = {k.lower() for k in cap.keywords}

    # Exact full match
    if cap_name == raw_query.replace(" ", "_"):
        return 1.0

    # Count how many query words match in action name vs keywords
    name_matches = 0
    kw_matches = 0
    
    for qw in query_words:
        equivs = get_expanded_terms(qw)
        if any(e in cap_name_tokens for e in equivs):
            name_matches += 1
        elif any(e in cap_keywords for e in equivs):
            kw_matches += 1

    total_q = len(query_words)
    
    # Specificity calculation
    name_ratio = name_matches / total_q
    kw_ratio = kw_matches / total_q
    
    # Check for direct conflicts (e.g. query asks for 'import', cap is 'export')
    conflict = False
    if "import" in query_words and "export" in cap_name_tokens:
        conflict = True
    if "export" in query_words and "import" in cap_name_tokens:
        conflict = True

    if name_ratio == 1.0:
        # All query words matched capability name!
        score = 0.95
    elif name_matches > 0:
        score = 0.50 + (0.35 * name_ratio) + (0.10 * kw_ratio)
    elif kw_matches > 0:
        score = 0.20 + (0.40 * kw_ratio)
    else:
        score = 0.0

    if conflict:
        score *= 0.5

    return min(1.0, score)

async def run_test():
    engine = CapabilityDiscoveryEngine()
    caps = engine.extractor.extract_all_capabilities()
    await engine.index.build_index(caps, force_rebuild=True)

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
        print("\n" + "="*70)
        print(f"QUERY: '{q}'")
        
        vector_results = await engine.index.search_vector_candidates(q, limit=100)
        vector_scores = {cap.capability_id: sem for cap, sem in vector_results}
        
        scored = []
        for cap in caps:
            sem = vector_scores.get(cap.capability_id, 0.0)
            lex = compute_lexical_score(q, cap)
            
            # Inferred domain
            raw_words = set(q.lower().split())
            inferred_domain = "blender" if any(w in raw_words for w in ["mesh", "3d", "render", "camera", "modifier", "subdivision", "material", "metallic", "gltf"]) else "windows"
            dom = 1.0 if cap.domain == inferred_domain else 0.5
            avail = 1.0
            
            final = (sem * 0.40) + (lex * 0.45) + (dom * 0.10) + (avail * 0.05)
            scored.append((cap, final, sem, lex, dom, avail))
            
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Check thresholding
        filtered = [x for x in scored if x[1] >= 0.40]
        if not filtered:
            print("  -> NO_SUITABLE_CAPABILITY")
        else:
            for cap, final, sem, lex, dom, avail in filtered[:5]:
                print(f"  {cap.capability_id:<40} final={final:.4f} sem={sem:.4f} lex={lex:.4f}")

if __name__ == '__main__':
    asyncio.run(run_test())
