import os
from fastapi import FastAPI, Depends, HTTPException, status, Form
from pydantic import BaseModel
import uvicorn
from typing import List, Annotated
from database.schemas.TuristBusDB import TuristBus
from database.database import engine, SessionLocal
from sqlalchemy.orm import Session
from model.TuristBus import TuristBus as turist_bus_model
import database.database as database

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
async def station_alive():
    return {'message' : 'service alive'}


@app.get("/TuristBuses")
async def fetch_turistbuses(db: db_dependency):
    result = db.query(TuristBus).all()
    return result


@app.post("/add_TuristBus")
async def add_turistbus(turistBus: turist_bus_model, db: db_dependency):
        db_turistbus = TuristBus(modelbus=turistBus.modelbus,
                        destination=turistBus.destination,
                        datego=turistBus.datego,
                        seats=turistBus.seats)
        db.add(db_turistbus)
        db.commit()
        db.refresh(db_turistbus)


@app.post("/delete_TuristBus")
async def delete_turistbus(turistbus_id: int, db: db_dependency):
        try:
            turistbus = db.query(TuristBus).filter(
                TuristBus.id == turistbus_id,
            ).first()
            db.delete(turistbus)
            db.commit()
        except Exception as _ex:
            raise HTTPException(status_code=404, detail='Bus not found')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))
