from datetime import date
from sqlalchemy import Column, Integer, String, Date, Text
from .database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String, nullable=False)
    role = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Applied")
    job_url = Column(String)
    applied_on = Column(Date, default=date.today)
    notes = Column(Text)