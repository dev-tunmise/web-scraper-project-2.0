from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.site import Base
from dotenv import load_dotenv
import os

# Load the .env file so we can read DATABASE_URL
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create the database engine (this is the actual connection)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal is what we'll use to talk to the database in our code
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This creates all the tables defined in models/site.py if they don't exist yet
def init_db():
    Base.metadata.create_all(bind=engine)

# This gives us a database session to use in each API request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()