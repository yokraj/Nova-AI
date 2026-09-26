import sys
import os
import asyncio

sys.path.insert(0, '.')
from app.ai.kernel.capability_discovery import CapabilityDiscoveryEngine

async def main():
    engine = CapabilityDiscoveryEngine()
    # Index is already saved on disk, so load is warm
    print(f"Loaded persistent index. Count: {len(engine.index.capabilities)}")

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
        print("\n" + "="*80)
        print(f"QUERY: '{q}'")
        results = await engine.discover_capabilities_with_scores(q, top_k=5, min_score=0.40)
        if not results:
            print("  NO_SUITABLE_CAPABILITY")
        else:
            for item in results:
                cap = item['capability']
                print(f"  {cap.capability_id:<40} final={item['final_score']:.4f} sem={item['semantic_score']:.4f} lex={item['lexical_score']:.4f} dom={item['domain_score']:.2f} avail={item['availability_score']:.2f}")

if __name__ == '__main__':
    asyncio.run(main())
