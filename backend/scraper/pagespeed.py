import httpx
import os
from dotenv import load_dotenv

load_dotenv()

PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY")

async def get_pagespeed_scores(domain: str) -> dict:
    url = f"https://{domain}"
    api_url = (
        f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        f"?url={url}&strategy=mobile&key={PAGESPEED_API_KEY}"
        f"&category=performance&category=seo&category=accessibility"
    )

    result = {
        "performance_score": None,
        "seo_score": None,
        "accessibility_score": None
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(api_url)
            data = response.json()

        # Extract the scores from the API response (scores are 0-1, we multiply by 100)
        categories = data.get("lighthouseResult", {}).get("categories", {})
        result["performance_score"] = round(categories.get("performance", {}).get("score", 0) * 100, 1)
        result["seo_score"] = round(categories.get("seo", {}).get("score", 0) * 100, 1)
        result["accessibility_score"] = round(categories.get("accessibility", {}).get("score", 0) * 100, 1)

    except Exception as e:
        print(f"PageSpeed error for {domain}: {e}")

    return result