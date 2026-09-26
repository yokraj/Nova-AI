import urllib.request
import urllib.parse

def test_arxiv_query_formats():
    base = "https://export.arxiv.org/api/query"
    query = "Attention Is All You Need"

    # Clean query into individual terms
    words = [w for w in query.split() if len(w) > 1]
    term_query = " AND ".join([f"all:{w}" for w in words])

    tests = [
        ("Multi-term AND", f"{base}?search_query={urllib.parse.quote(term_query)}&start=0&max_results=3"),
        ("Single word", f"{base}?search_query=all:Attention&start=0&max_results=3"),
        ("Title single word", f"{base}?search_query=ti:Attention&start=0&max_results=3"),
    ]

    for label, url in tests:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=5)
            body = resp.read().decode('utf-8')
            print(f"[{label}] SUCCESS: Status={resp.status}, Len={len(body)}, Has 'Attention': {'Attention' in body}")
        except urllib.error.HTTPError as e:
            print(f"[{label}] HTTPError {e.code}: {e.reason}")
        except Exception as e:
            print(f"[{label}] Exception: {e}")

if __name__ == '__main__':
    test_arxiv_query_formats()
