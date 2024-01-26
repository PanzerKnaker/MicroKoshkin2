from sqlalchemy import Column, String, DateTime, Integer
from ..database import Base


class TuristBus(Base):
    __tablename__ = 'TuristBus'

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    datego = Column(DateTime, nullable=False)
    seats = Column(Integer, nullable=False)
