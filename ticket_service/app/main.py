import os
from typing import Annotated
from database.schemas.TripTicketDB import TripTicket
from database.schemas.TuristBusDB import TuristBus
from database.database import engine, SessionLocal
from sqlalchemy.orm import Session
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Form
from database import database as database
import smtplib
from email.mime.text import MIMEText
from model.tripticket import TripTicket as tripticket_model

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



@app.get("/triptickets_all")
async def fetch_tickets(db: db_dependency):
        result = db.query(TripTicket).all()
        return result


@app.get("/find_bus")
def check_turistbus_existence(destinationbus: str, db: db_dependency):
        result=db.query(TuristBus).filter(
            TuristBus.destination == destinationbus
        ).first()
        return result

@app.get("/tripticket_by_id")
def fetch_ticket_id(id_ticket: int, db: db_dependency):
        return db.query(TripTicket).filter(
            TripTicket.id == id_ticket
        ).first()



@app.post("/buy_tripticket")
async def buy_tripticket( name_user: str,
                     last_name: str,
                     email: str,
                     destination: str,
                     db: db_dependency):
    try:
        turistbus = check_turistbus_existence(destination, db)
        if turistbus.seats > 0:
            tripticket = TripTicket(user_name=name_user,
                            user_last_name=last_name,
                            user_email=email,
                            turistbus_id=turistbus.id,
                            datego=turistbus.datego)
            Text = [
                str(turistbus.id),
                name_user,
                last_name,
                email,
                str(turistbus.datego)
            ]
            gen_file = open('data.txt', 'w')
            gen_file.writelines(Text)
            gen_file.close()
            turistbus.seats -= 1
            db.add(tripticket)
            db.commit()
            db.refresh(tripticket)
            db.refresh(turistbus)
            return print(tripticket)
    except HTTPException as e:
        print(f"Error: {e}")


@app.delete("/delete_tripticket_by_id")
def delete_ticket_id(id_ticket: int, db: db_dependency):
        try:
            tripticket = db.query(TripTicket).filter(TripTicket.id == id_ticket).first()
            db.delete(tripticket)
            db.commit()
        except Exception as _ex:
            raise HTTPException(status_code=404, detail='Ticket not found')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))