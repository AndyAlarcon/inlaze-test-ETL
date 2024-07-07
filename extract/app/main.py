from typing import Annotated
from fastapi import FastAPI, BackgroundTasks, Depends
from database import engine, SessionLocal
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import asynccontextmanager
from redis import Redis
import httpx
import json


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis(host='localhost', port=6379)
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
        #
        # Código para llamar al microservicio de transformación
        #
        return json.loads(data_str)
    
    return json.loads(value)