from sqlalchemy import Column, String, DateTime, Integer
from ..database import Base


class TripTicket(Base):
    __tablename__ = 'triptickets'

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    user_last_name = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    turistbus_id = Column(Integer, nullable=False)
    datego = Column(DateTime, nullable=False)
