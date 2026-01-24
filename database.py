from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Twoje dane logowania
DB_USER = "2024_szczudlo_kacper"
DB_PASS = "KacSzczud2115**"
DB_HOST = "195.150.230.208"
DB_PORT = "5432"
DB_NAME = "2024_szczudlo_kacper"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()