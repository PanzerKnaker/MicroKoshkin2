import os
from fastapi import FastAPI, Depends, HTTPException, status, Form
from pydantic import BaseModel
import uvicorn
from typing import List, Annotated
from database.schemas.TuristBusDB import TuristBus
from database.database import engine, SessionLocal
from sqlalchemy.orm import Session
from model.TuristBus import TuristBus as turist_bus_model
from keycloak import KeycloakOpenID
import database.database as database

app = FastAPI()
database.Base.metadata.create_all(bind=engine)

from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import  TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


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
async def station_alive():
    if (check_user_roles()):
        return {'message' : 'service alive'}
    else:
        return "Wrong User Token"

@app.get("/TuristBuses")
async def fetch_turistbuses(db: db_dependency):
    if (check_user_roles()):
        result = db.query(TuristBus).all()
        return result
    else:
        return "Wrong User Token"

@app.post("/add_TuristBus")
async def add_turistbus(turistBus: turist_bus_model, db: db_dependency):
    if (check_user_roles()):
        db_turistbus = TuristBus(modelbus=turistBus.modelbus,
                        destination=turistBus.destination,
                        datego=turistBus.datego,
                        seats=turistBus.seats)
        db.add(db_turistbus)
        db.commit()
        db.refresh(db_turistbus)
    else:
        return "Wrong User Token"

@app.post("/delete_TuristBus")
async def delete_turistbus(turistbus_id: int, db: db_dependency):
    if (check_user_roles()):
        try:
            turistbus = db.query(TuristBus).filter(
                TuristBus.id == turistbus_id,
            ).first()
            db.delete(turistbus)
            db.commit()
        except Exception as _ex:
            raise HTTPException(status_code=404, detail='Bus not found')
    else:
        return "Wrong User Token"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))