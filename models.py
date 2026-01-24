from sqlalchemy import Column, Integer, String, DateTime
from database import Base
import datetime

class Auditor(Base):
    __tablename__ = "cli_auditors"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    two_factor_secret = Column(String)

class WhistleblowerReport(Base):
    __tablename__ = "cli_reports"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    encrypted_content = Column(String) # To pole będzie zawierać szyfr AES
    status = Column(String, default="NEW")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AccessLog(Base):
    __tablename__ = "cli_access_logs"
    id = Column(Integer, primary_key=True, index=True)
    auditor_username = Column(String)
    report_id = Column(Integer)
    action = Column(String) # Np. DECRYPT_SUCCESS, DECRYPT_FAILED
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)