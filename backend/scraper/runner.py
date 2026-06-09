import asyncio
import csv
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.crawler import scrape_site
from scraper.pagespeed import get_pagespeed_scores
from db import SessionLocal, init_db
from models.site import Site

CSV_PATH = os.path.join(os.path.dirname(__file__), "../../data/sites.csv")

async def run_scraper():
    init_db()
    db = SessionLocal()

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        sites = list(reader)

    print(f"Total sites in CSV: {len(sites)}")

    for i, row in enumerate(sites):
        domain = row["domain"].strip()
        industry = row["industry"].strip()

        # Skip if already scraped
        existing = db.query(Site).filter(Site.domain == domain).first()
        if existing and existing.page_title is not None:
            print(f"[{i+1}/{len(sites)}] Skipping {domain} (already scraped)")
            continue

        print(f"[{i+1}/{len(sites)}] Scraping {domain}...")

        scraped = await scrape_site(domain)
        scores = await get_pagespeed_scores(domain)

        if existing:
            site = existing
        else:
            site = Site(domain=domain, industry=industry)
            db.add(site)

        site.page_title = scraped.get("page_title")
        site.meta_description = scraped.get("meta_description")
        site.headers = scraped.get("headers")
        site.structured_data = scraped.get("structured_data")
        site.response_time = scraped.get("response_time")
        site.performance_score = scores.get("performance_score")
        site.seo_score = scores.get("seo_score")
        site.accessibility_score = scores.get("accessibility_score")
        site.ai_summary = None

        db.commit()
        print(f"✓ Saved {domain}")

    db.close()
    print("Scraping complete!")

if __name__ == "__main__":
    asyncio.run(run_scraper())