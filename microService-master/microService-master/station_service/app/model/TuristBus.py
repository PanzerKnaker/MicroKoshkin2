from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TuristBus(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    model: str
    direction: str
    datego: datetime
    seats: int
