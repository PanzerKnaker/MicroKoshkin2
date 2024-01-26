from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TuristBus(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    modelbus: str
    destination: str
    datego: datetime
    seats: int
