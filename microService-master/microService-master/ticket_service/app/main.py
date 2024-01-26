from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated
from app.database.schemas.TripTicketDB import TripTicket
from app.database.schemas.TuristBusDB import TuristBus
from app.database.database import engine, SessionLocal
from sqlalchemy.orm import Session
from app.database import database as database
import smtplib
from email.mime.text import MIMEText

app = FastAPI()
database.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/alive", status_code=status.HTTP_200_OK)
async def ticket_alive():
    return {'message' : 'service alive'}

@app.get("/tripticket/{tripticket_id}")
async def fetch_tickets(tripticket_id: int, db: db_dependency):
    try:
        result = db.query(TripTicket).filter(TripTicket.id == tripticket_id).first()
    except Exception:
        raise HTTPException(status_code=404, detail='Tickets not found')
    return result


def check_turistbus_existence(direction: str, db: db_dependency):
    return db.query(TuristBus).filter(
        TuristBus.direction == direction
    ).first()



@app.post("/buy_tripticket")
async def buy_tripticket(direction: str,
                     name: str,
                     last_name: str,
                     email: str,
                     db: db_dependency):
    try:
        turistbus = check_turistbus_existence(direction, db)
        if turistbus.seats > 0:
            tripticket = TripTicket(user_name=name,
                            user_last_name=last_name,
                            user_email=email,
                            turistbus_id=turistbus.id,
                            datego=turistbus.datego)
            gen_file = open('data.txt', 'w')
            gen_file.write(tripticket)
            tripticket.seats -= 1
            db.add(tripticket)
            db.commit()
            db.refresh(tripticket)
    except HTTPException as e:
        print(f"Error: {e}")

