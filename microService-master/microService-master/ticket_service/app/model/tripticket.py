from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TripTicket(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_name: str
    user_last_name: str
    user_email: str
    turistbus_id: int
    datego: datetime
