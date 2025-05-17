"""
Database models for AutoXpress
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# Database setup
DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///autoxpress.db")
engine = create_engine(DATABASE_URI)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class CallRecord(Base):
    """Model for storing call records from Dialpad"""
    __tablename__ = 'call_records'
    
    id = Column(String, primary_key=True)
    dialpad_id = Column(String, unique=True, nullable=True)
    call_type = Column(String)  # inbound/outbound
    date = Column(String)
    time = Column(String)
    timestamp = Column(DateTime)
    agent = Column(String)
    agent_id = Column(String, nullable=True)
    customer = Column(String)
    phone = Column(String)
    duration = Column(Float)
    status = Column(String)  # completed/pending/missed
    notes = Column(Text, nullable=True)
    vehicle_info = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    product = Column(String, nullable=True)
    followup_required = Column(Boolean, default=False)
    followup_date = Column(String, nullable=True)
    followup_time = Column(String, nullable=True)
    raw_data = Column(Text, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": self.id,
            "call_type": self.call_type,  # The field name in the database
            "date": self.date,
            "time": self.time,
            "agent": self.agent,
            "agent_id": self.agent_id,
            "customer": self.customer,
            "phone": self.phone,
            "duration": self.duration,
            "status": self.status,
            "notes": self.notes,
            "vehicle_info": self.vehicle_info,
            "year": self.year,
            "product": self.product,
            "followup_required": self.followup_required,
            "followup_date": self.followup_date,
            "followup_time": self.followup_time
        }

def init_db():
    """Initialize the database with tables"""
    Base.metadata.create_all(bind=engine)

# Run init_db() if this file is run directly
if __name__ == "__main__":
    init_db()