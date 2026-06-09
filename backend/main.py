from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db import get_db, init_db, SessionLocal

app = FastAPI()

# This allows our React frontend to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables when the server starts
@app.on_event("startup")
def startup():
    init_db()

# Get all sites, optionally filtered by industry
@app.get("/sites")
def get_sites(industry: str = None, db: Session = Depends(get_db)):
    query = db.query(Site)
    if industry:
        query = query.filter(Site.industry == industry)
    return query.order_by(Site.performance_score.desc()).all()

# Get a single site by its ID
@app.get("/sites/{site_id}")
def get_site(site_id: int, db: Session = Depends(get_db)):
    return db.query(Site).filter(Site.id == site_id).first()

# Get all unique industries
@app.get("/industries")
def get_industries(db: Session = Depends(get_db)):
    results = db.query(Site.industry).distinct().all()
    return [r[0] for r in results]

@app.get("/status")
def get_status(db: Session = Depends(get_db)):
    import csv, os
    CSV_PATH = os.path.join(os.path.dirname(__file__), "../data/sites.csv")
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            total = sum(1 for row in csv.DictReader(f))
    except:
        total = 0
    scraped = db.query(Site).count()
    return {"scraped": scraped, "total": total}