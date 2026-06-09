import httpx
from bs4 import BeautifulSoup
import json
import time

async def scrape_site(domain: str) -> dict:
    url = f"https://{domain}"
    result = {
        "domain": domain,
        "page_title": None,
        "meta_description": None,
        "headers": "[]",
        "structured_data": "[]",
        "response_time": None,
        "error": None
    }

    try:
        # Visit the website and measure how long it takes to respond
        start = time.time()
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.get(url)
        result["response_time"] = round(time.time() - start, 2)

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract page title
        result["page_title"] = soup.title.string.strip() if soup.title else None

        # Extract meta description
        meta = soup.find("meta", attrs={"name": "description"})
        result["meta_description"] = meta["content"].strip() if meta else None

        # Extract all headers (H1 to H3)
        headers = []
        for tag in ["h1", "h2", "h3"]:
            for h in soup.find_all(tag):
                headers.append({"tag": tag, "text": h.get_text(strip=True)})
        result["headers"] = json.dumps(headers)

        # Extract structured data (JSON-LD schema.org tags)
        structured = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                structured.append(json.loads(script.string))
            except:
                pass
        result["structured_data"] = json.dumps(structured)

    except Exception as e:
        result["error"] = str(e)

    return result