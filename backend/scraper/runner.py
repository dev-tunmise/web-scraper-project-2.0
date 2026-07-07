import asyncio
import csv
import os
import sys
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.crawler import scrape_site
from scraper.pagespeed import get_pagespeed_scores
from db import SessionLocal, init_db
from models.site import Site, RetryLog

CSV_PATH = os.path.join(os.path.dirname(__file__), "../../data/sites.csv")
BACKEND_URL = "http://127.0.0.1:8000"

def update_progress(current, total, domain, pass_name, retry_count, complete):
    try:
        requests.post(f"{BACKEND_URL}/progress", json={
            "current": current,
            "total": total,
            "domain": domain,
            "pass": pass_name,
            "retry_count": retry_count,
            "complete": complete,
        }, timeout=2)
    except:
        pass

def count_with_data(db, sites):
    count = 0
    for row in sites:
        domain = row["domain"].strip()
        site = db.query(Site).filter(Site.domain == domain).first()
        if site and site.performance_score and site.performance_score > 0:
            count += 1
    return count

async def scrape_one(db, domain, industry):
    try:
        scraped = await scrape_site(domain)
    except Exception as e:
        print(f"Crawler error for {domain}: {e}")
        scraped = {"page_title": None, "meta_description": None, "headers": "[]", "structured_data": "[]", "response_time": None}
    
    try:
        scores = await get_pagespeed_scores(domain)
    except Exception as e:
        print(f"PageSpeed error for {domain}: {e}")
        scores = {"performance_score": 0, "seo_score": 0, "accessibility_score": 0}

    existing = db.query(Site).filter(Site.domain == domain).first()
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

async def run_scraper():
    init_db()
    db = SessionLocal()

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        all_sites = list(csv.DictReader(f))

    total = len(all_sites)
    print(f"Total sites in CSV: {total}")

    # PASS 1 — scrape brand new sites only
    print("=== PASS 1: Scraping new sites only ===")
    new_sites = [row for row in all_sites if not db.query(Site).filter(Site.domain == row["domain"].strip()).first()]
    print(f"Found {len(new_sites)} new sites to scrape")

    for i, row in enumerate(new_sites):
        domain = row["domain"].strip()
        industry = row["industry"].strip()
        complete = count_with_data(db, all_sites)
        print(f"[Pass 1][{i+1}/{len(new_sites)}] Scraping {domain}...")
        update_progress(i+1, len(new_sites), domain, "Pass 1", 0, complete)
        await scrape_one(db, domain, industry)

    # RETRY LOOP — only starts after every site in CSV is saved
    retry_count = db.query(RetryLog).count()

    while True:
        # First finish any unsaved sites
        unsaved = [row for row in all_sites if not db.query(Site).filter(Site.domain == row["domain"].strip()).first()]

        if unsaved:
            print(f"=== {len(unsaved)} sites still unsaved, scraping them first ===")
            for i, row in enumerate(unsaved):
                domain = row["domain"].strip()
                industry = row["industry"].strip()
                complete = count_with_data(db, all_sites)
                print(f"[Finishing][{i+1}/{len(unsaved)}] Scraping {domain}...")
                update_progress(i+1, len(unsaved), domain, "Finishing Pass 1", retry_count, complete)
                await scrape_one(db, domain, industry)

        # Now check for incomplete sites
        incomplete = []
        for row in all_sites:
            domain = row["domain"].strip()
            site = db.query(Site).filter(Site.domain == domain).first()
            if site and (not site.performance_score or site.performance_score == 0):
                incomplete.append(row)

        complete = count_with_data(db, all_sites)

        if not incomplete:
            print("=== All sites complete! ===")
            update_progress(0, 0, "", "Complete!", retry_count, complete)
            break

        retry_count += 1
        retry_total = len(incomplete)
        print(f"=== Retry #{retry_count}: {retry_total} incomplete sites ===")

        got_data_before = count_with_data(db, incomplete)

        for i, row in enumerate(incomplete):
            domain = row["domain"].strip()
            industry = row["industry"].strip()
            complete = count_with_data(db, all_sites)
            print(f"[Retry #{retry_count}][{i+1}/{retry_total}] Retrying {domain}...")
            update_progress(i+1, retry_total, domain, f"Retry #{retry_count}", retry_count, complete)
            await scrape_one(db, domain, industry)

        got_data_after = count_with_data(db, incomplete)
        newly_got = got_data_after - got_data_before

        log = RetryLog(
            retry_number=retry_count,
            total_retried=retry_total,
            got_data=newly_got
        )
        db.add(log)
        db.commit()

        print(f"Retry #{retry_count} done — got data from {newly_got}/{retry_total}")

    db.close()
    print("=== Scraping fully complete! ===")

if __name__ == "__main__":
    asyncio.run(run_scraper())