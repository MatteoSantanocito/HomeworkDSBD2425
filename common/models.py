from sqlalchemy import Column, String, Float, DateTime, Integer
from .database import Base
from datetime import datetime, timezone

class User(Base):
    __tablename__ = 'users'
    email = Column(String, primary_key=True, index=True)
    ticker = Column(String)
    high_value = Column(Float, nullable=True)
    low_value = Column(Float, nullable=True)

class FinancialData(Base):
    __tablename__ = 'financial_data'
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    value = Column(Float)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

