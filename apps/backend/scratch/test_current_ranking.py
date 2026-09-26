import sys
import os
import asyncio

sys.path.insert(0, '.')
from app.ai.kernel.capability_discovery import CapabilityDiscoveryEngine

async def main():
    engine = CapabilityDiscoveryEngine()
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
        print('='*70)
        print(f"QUERY: '{q}'")
        # Let's inspect vector candidates and scoring
        norm_query = engine._normalize_query(q)
        vector_results = await engine.index.search_vector_candidates(q, limit=100)
        vector_scores = {cap.capability_id: sem_score for cap, sem_score in vector_results}
        
        raw_words = set(q.lower().replace("_", " ").split())
        inferred_domain = None
        if any(w in raw_words for w in ["mesh", "3d", "render", "camera", "modifier", "subdivision", "material", "metallic", "gltf", "fbx", "obj"]):
            inferred_domain = "blender"
        elif any(w in raw_words for w in ["screenshot", "window", "terminal", "desktop"]):
            inferred_domain = "windows"

        scored = []
        for cap in engine.index.capabilities.values():
            sem_score = vector_scores.get(cap.capability_id, 0.0)
            
            # Lexical
            lex_score = 0.0
            name_lower = cap.name.lower()
            name_clean = name_lower.replace("_", " ")
            desc_clean = cap.description.lower()

            if name_lower == q.lower().strip() or name_lower == norm_query:
                lex_score = 1.0
            elif name_lower in q.lower() or q.lower() in name_lower:
                lex_score = 0.9
            elif name_clean in norm_query or any(word in name_clean or word in desc_clean for word in raw_words if len(word) > 2):
                lex_score = 0.7

            kw_matches = sum(1 for kw in cap.keywords if kw.lower() in norm_query or kw.lower() in raw_words)
            if kw_matches > 0:
                lex_score = max(lex_score, min(0.95, 0.3 + (kw_matches * 0.15)))

            if "metallic" in raw_words and "metallic" in cap.keywords:
                lex_score = max(lex_score, 0.9)
            if ("subdivision" in raw_words or "subdivide" in raw_words) and ("subdivision" in cap.keywords or "subdivide" in cap.keywords):
                lex_score = max(lex_score, 0.9)
            if "gltf" in raw_words and "gltf" in cap.keywords:
                lex_score = max(lex_score, 0.95)

            domain_score = 0.5
            if inferred_domain and cap.domain.lower() == inferred_domain:
                domain_score = 1.0
            elif cap.domain.lower() == "blender":
                domain_score = 0.7

            avail_score = 0.8

            final_score = (
                (sem_score * engine.weights.semantic_weight)
                + (lex_score * engine.weights.lexical_weight)
                + (domain_score * engine.weights.domain_weight)
                + (avail_score * engine.weights.availability_weight)
            )
            scored.append((cap, final_score, sem_score, lex_score, domain_score, avail_score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        top5 = scored[:5]
        for cap, final, sem, lex, dom, avail in top5:
            print(f"  {cap.capability_id:<40} final={final:.4f} sem={sem:.4f} lex={lex:.4f} dom={dom:.2f}")

if __name__ == '__main__':
    asyncio.run(main())
