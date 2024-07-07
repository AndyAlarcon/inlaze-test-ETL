from typing import Annotated
from fastapi import FastAPI, Depends, Response
import requests
from database import SessionLocal
import models
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from redis import Redis
import httpx
import json


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis(host='redis', port=6379)
    app.state.http_client = httpx.AsyncClient()
    yield
    app.state.redis.close()

app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/precipitacion")
async def get_precipitacion():

    value = app.state.redis.get('precipitacion')
    if value is None:
        # params = {'$limit': 1}
        # response = await app.state.http_client.get('https://www.datos.gov.co/resource/s54a-sgyg.json', params = params)
        response = await app.state.http_client.get('https://www.datos.gov.co/resource/s54a-sgyg.json')
        value = response.json()
        data_str = json.dumps(value)
        app.state.redis.set("precipitacion", data_str)
        response = requests.get('http://transform:70/precipitacion_trans/')
        if response.status_code == 204:
            return json.loads(data_str)
        else:
            return Response(content='f{"result": {response.text}}', media_type="application/json", status_code=207)
    return json.loads(value)

@app.get("/precipitaciones_tran/")
async def get_precipitaciones_tran(db: db_dependency):
    return db.query(models.Precipitaciones).all()