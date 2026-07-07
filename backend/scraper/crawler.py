import httpx
from bs4 import BeautifulSoup
import json
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

async def scrape_site(domain: str) -> dict:
    result = {
        "domain": domain,
        "page_title": None,
        "meta_description": None,
        "headers": "[]",
        "structured_data": "[]",
        "response_time": None,
        "error": None
    }

    # Try https first, then http
    urls_to_try = [f"https://{domain}", f"http://{domain}"]

    for url in urls_to_try:
        try:
            start = time.time()
            async with httpx.AsyncClient(
                timeout=20,
                follow_redirects=True,
                headers=HEADERS
            ) as client:
                response = await client.get(url)

            result["response_time"] = round(time.time() - start, 2)

            if response.status_code >= 400:
                continue

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract page title
            if soup.title and soup.title.string:
                result["page_title"] = soup.title.string.strip()

            # Extract meta description
            meta = soup.find("meta", attrs={"name": "description"})
            if not meta:
                meta = soup.find("meta", attrs={"property": "og:description"})
            if meta and meta.get("content"):
                result["meta_description"] = meta["content"].strip()

            # Extract headers H1 to H3
            headers = []
            for tag in ["h1", "h2", "h3"]:
                for h in soup.find_all(tag):
                    text = h.get_text(strip=True)
                    if text:
                        headers.append({"tag": tag, "text": text[:200]})
            result["headers"] = json.dumps(headers)

            # Extract structured data
            structured = []
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    if script.string:
                        structured.append(json.loads(script.string))
                except:
                    pass
            result["structured_data"] = json.dumps(structured)

            # If we got here successfully, break out of the loop
            if result["page_title"] or result["response_time"]:
                break

        except Exception as e:
            result["error"] = str(e)
            continue

    return result