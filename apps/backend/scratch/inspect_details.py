import sys
import os
import asyncio

sys.path.insert(0, '.')
from app.ai.kernel.capability_discovery import CapabilityDiscoveryEngine, SemanticCapabilityIndex, CapabilityExtractor

async def inspect_details():
    engine = CapabilityDiscoveryEngine()
    await engine.initialize()

    print("TOTAL INDEXED CAPABILITIES:", len(engine.index.capabilities))

    # Inspect subdivide_edges vs add_modifier vs convert_object_to_mesh
    target_ids = ["blender:subdivide_edges", "blender:add_modifier", "blender:convert_object_to_mesh", "blender:set_principled_metallic", "blender:create_camera", "blender:render_current_frame"]
    for cid in target_ids:
        cap = engine.index.capabilities.get(cid)
        if cap:
            print(f"\n--- {cid} ---")
            print("Name:", cap.name)
            print("Description:", cap.description)
            print("Keywords:", cap.keywords)
            print("Semantic Text:", cap.semantic_text)
        else:
            print(f"\n--- {cid} NOT FOUND ---")

if __name__ == '__main__':
    asyncio.run(inspect_details())
