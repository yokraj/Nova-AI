import sys
import asyncio
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.session import SessionLocal
from app.database.models.inference import InferenceLog
from sqlalchemy import select

async def dump_logs():
    async with SessionLocal() as session:
        result = await session.execute(select(InferenceLog).order_by(InferenceLog.created_at.desc()).limit(5))
        logs = result.scalars().all()
        for idx, log in enumerate(logs):
            print(f"=== LOG {idx+1}: {log.prompt[:50]} ===")
            print(f"Model: {log.model_name}, Provider: {log.provider}, Total tokens: {log.total_tokens}")
            out_path = backend_dir / "tests" / f"inference_output_{idx+1}.txt"
            out_path.write_text(log.response_content or "", encoding="utf-8")
            print(f"Wrote {len(log.response_content or '')} chars to {out_path.name}")

if __name__ == "__main__":
    asyncio.run(dump_logs())
