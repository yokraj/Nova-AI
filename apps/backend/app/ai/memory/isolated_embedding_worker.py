"""Isolated Embedding Worker Script.

Runs inside isolated Python 3.11 environment (.venv-stt) using fastembed ONNX runtime.
Generates real local semantic embedding vectors and outputs JSON to stdout.
"""

import sys
import json
import argparse
import os

try:
    from fastembed import TextEmbedding
except ImportError:
    print(json.dumps({"error": "fastembed is not installed in isolated environment.", "success": False}))
    sys.exit(1)

# Global lazy cached model
_MODEL_CACHE = None


def get_model(model_name: str = "BAAI/bge-small-en-v1.5"):
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        _MODEL_CACHE = TextEmbedding(model_name=model_name)
    return _MODEL_CACHE


def main():
    parser = argparse.ArgumentParser(description="Isolated Embedding Worker")
    parser.add_argument("--text", help="Single text input to embed")
    parser.add_argument("--batch_file", help="Path to JSON file containing list of texts")
    parser.add_argument("--model", default="BAAI/bge-small-en-v1.5", help="Embedding model name")
    args = parser.parse_args()

    try:
        model = get_model(args.model)

        if args.text:
            embeddings = list(model.embed([args.text]))
            vec = [float(x) for x in embeddings[0]]
            print(json.dumps({"embedding": vec, "dimension": len(vec), "success": True}))
        elif args.batch_file and os.path.exists(args.batch_file):
            with open(args.batch_file, "r", encoding="utf-8") as f:
                texts = json.load(f)
            embeddings = list(model.embed(texts))
            vecs = [[float(x) for x in emb] for emb in embeddings]
            print(json.dumps({"embeddings": vecs, "dimension": len(vecs[0]) if vecs else 0, "success": True}))
        else:
            print(json.dumps({"error": "No valid text or batch file provided.", "success": False}))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Embedding generation failed: {str(e)}", "success": False}))
        sys.exit(1)


if __name__ == "__main__":
    main()
