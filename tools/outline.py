import os
import re
import requests


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.environ['OUTLINE_API_KEY']}",
        "Content-Type": "application/json",
    }


def _extract_doc_id(url: str) -> str:
    """Extract document ID from an Outline URL.
    Supports: https://outline.example.com/doc/my-doc-abc123def456
    """
    match = re.search(r"/doc/[^/]+-([a-f0-9\-]{36}|[a-f0-9]{8,})", url)
    if match:
        return match.group(0).split("/doc/")[-1]
    # fallback: use last path segment
    return url.rstrip("/").split("/")[-1]


def fetch_doc(doc_url: str) -> dict:
    """Fetch an Outline document by URL. Returns title and full text content."""
    base_url = os.environ["OUTLINE_BASE_URL"].rstrip("/")
    doc_id = _extract_doc_id(doc_url)

    resp = requests.post(
        f"{base_url}/api/documents.info",
        headers=_headers(),
        json={"id": doc_id}
    )
    resp.raise_for_status()
    doc = resp.json()["data"]["document"]
    return {
        "id": doc["id"],
        "title": doc["title"],
        "text": doc.get("text", ""),
    }
