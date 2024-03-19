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

app = FastAPI()
database.Base.metadata.create_all(bind=engine)

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import  TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from keycloak import KeycloakOpenID

from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)


KEYCLOAK_URL = "http://keycloak:8080/"
KEYCLOAK_CLIENT_ID = "koshkin"
KEYCLOAK_REALM = "koshkinrealm"
KEYCLOAK_CLIENT_SECRET = "wIYhDqHAudxL6xtcp8zrdRk0yDnw1fuo"

keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_URL,
                                  client_id=KEYCLOAK_CLIENT_ID,
                                  realm_name=KEYCLOAK_REALM,
                                  client_secret_key=KEYCLOAK_CLIENT_SECRET)

user_token =""

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.post("/Login")
async def get_token(username: str = Form(...), password: str = Form(...)):
    try:
        # Получение токена
        token = keycloak_openid.token(grant_type=["password"],
                                      username=username,
                                      password=password)
        global user_token
        user_token = token
        return token
    except Exception as e:
        print(e)  # Логирование для диагностики
        raise HTTPException(status_code=400, detail="Не удалось получить токен")

def check_user_roles():
    global user_token
    token = user_token
    try:
        userinfo = keycloak_openid.userinfo(token["access_token"])
        token_info = keycloak_openid.introspect(token["access_token"])
        if "testRole" not in token_info["realm_access"]["roles"]:
            raise HTTPException(status_code=403, detail="Access denied")
        return "Autorization success!!!"
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or access denied")

@app.get("/alive", status_code=status.HTTP_200_OK)
async def ticket_alive():
    if (check_user_roles()):
        return {'message' : 'service alive'}
    else:
        return C


@app.get("/triptickets_all")
async def fetch_tickets(db: db_dependency):
    if (check_user_roles()):
        result = db.query(TripTicket).all()
        return result
    else:
        return C

@app.get("/find_bus")
def check_turistbus_existence(destinationbus: str, db: db_dependency):
    if (check_user_roles()):
        result=db.query(TuristBus).filter(
            TuristBus.destination == destinationbus
        ).first()
        return result
    else:
        return C

@app.get("/tripticket_by_id")
def fetch_ticket_id(id_ticket: int, db: db_dependency):
    if (check_user_roles()):
        return db.query(TripTicket).filter(
            TripTicket.id == id_ticket
        ).first()
    else:
        return C

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