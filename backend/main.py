from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db import get_db, init_db, SessionLocal
from models.site import Site, RetryLog
import csv
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scraping_progress = {"current": 0, "total": 0, "domain": "", "pass": "Idle", "retry_count": 0, "complete": 0}

@app.on_event("startup")
def startup():
    init_db()
    scraping_progress.update({"current": 0, "total": 0, "domain": "", "pass": "Idle", "retry_count": 0, "complete": 0})

@app.get("/sites")
def get_sites(industry: str = None, db: Session = Depends(get_db)):
    query = db.query(Site)
    if industry:
        query = query.filter(Site.industry == industry)
    return query.order_by(Site.performance_score.desc()).all()

@app.get("/sites/{site_id}")
def get_site(site_id: int, db: Session = Depends(get_db)):
    return db.query(Site).filter(Site.id == site_id).first()

@app.get("/industries")
def get_industries(db: Session = Depends(get_db)):
    results = db.query(Site.industry).distinct().all()
    return [r[0] for r in results]

@app.get("/status")
def get_status(db: Session = Depends(get_db)):
    CSV_PATH = os.path.join(os.path.dirname(__file__), "../data/sites.csv")
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            total = sum(1 for row in csv.DictReader(f))
    except:
        total = 0
    scraped = db.query(Site).count()
    complete = db.query(Site).filter(
        Site.performance_score != None,
        Site.performance_score > 0
    ).count()
    return {"scraped": scraped, "total": total, "complete": complete}

@app.post("/progress")
def update_progress(data: dict):
    scraping_progress.update(data)
    return {"ok": True}

@app.get("/progress")
def get_progress(db: Session = Depends(get_db)):
    retry_logs = db.query(RetryLog).order_by(RetryLog.retry_number).all()
    return {
        **scraping_progress,
        "retries": [
            {
                "retry_number": r.retry_number,
                "total": r.total_retried,
                "got_data": r.got_data
            }
            for r in retry_logs
        ]
    }