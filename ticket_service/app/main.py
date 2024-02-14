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


@app.post("/get-token")
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
        return "Autorization success!"
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or access denied")

@app.get("/alive", status_code=status.HTTP_200_OK)
async def ticket_alive():
    if (check_user_roles()):
        return {'message' : 'service alive'}
    else:
        return C


@app.get("/tripticket/{tripticket_id}")
async def fetch_tickets(tripticket_id: int, db: db_dependency):
    try:
        result = db.query(TripTicket).filter(TripTicket.id == tripticket_id).first()
    except Exception:
        raise HTTPException(status_code=404, detail='Tickets not found')
    return result


def check_turistbus_existence(direction: str, db: db_dependency):
    if (check_user_roles()):
        return db.query(TuristBus).filter(
            TuristBus.direction == direction
        ).first()
    else:
        return "Wrong User Token"


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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))