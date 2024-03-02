from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class TuristBus(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    modelbus: str
    destination: str
    datego: datetime
    seats: int
