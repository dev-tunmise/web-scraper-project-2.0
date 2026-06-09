from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True)
    industry = Column(String, index=True)
    
    # Scraped data
    page_title = Column(String, nullable=True)
    meta_description = Column(Text, nullable=True)
    headers = Column(Text, nullable=True)        # stored as JSON string
    structured_data = Column(Text, nullable=True) # stored as JSON string
    response_time = Column(Float, nullable=True)  # in seconds
    
    # Scores
    performance_score = Column(Float, nullable=True)
    seo_score = Column(Float, nullable=True)
    accessibility_score = Column(Float, nullable=True)
    
    # AI summary
    ai_summary = Column(Text, nullable=True)
    
    # Timestamp
    scraped_at = Column(DateTime, default=datetime.datetime.utcnow)