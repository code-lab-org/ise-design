from sqlalchemy import Boolean, Column, DateTime, Integer, Float, String

from ..database import Base

class Design(Base):
    __tablename__ = "designs"
    id = Column(Integer, primary_key=True, index=True)
    design_id = Column(String, unique=True, index=True)
    name = Column(String)
    timestamp = Column(DateTime)
    designer = Column(String)
    name = Column(String)
    thumbnail = Column(String)
    mass = Column(Float)
    width = Column(Float)
    length = Column(Float)
    height = Column(Float)
    wheelbase = Column(Float)
    track = Column(Float)
    volume = Column(Float)
    number_seats = Column(Float)
    cargo_volume = Column(Float)
    dsm_json = Column(String)
    requirements_json = Column(String)
    cost_json = Column(String)
    value_json = Column(String)
    is_valid = Column(Boolean)
    total_cost = Column(Float)
    total_revenue = Column(Float)
    total_profit = Column(Float)
    total_roi = Column(Float)
