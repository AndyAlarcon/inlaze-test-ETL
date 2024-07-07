from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Response
from database import engine, SessionLocal
import models
from sqlalchemy import func
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from redis import Redis
import pandas as pd
import httpx
import json
import io


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

@app.get("/load/")
async def load_precipitacion(db: db_dependency):
    value = app.state.redis.get('precipitacion_trans')
    if value is None:
        raise HTTPException(status_code=404, detail='Sin registros para cargar')
    jsonio = io.BytesIO(value)
    df = pd.read_json(jsonio, orient='split')
    df.to_sql('precipitaciones', con=engine, if_exists='replace', index=False)
    return Response(status_code=204)

@app.get("/precipitaciones_tran/")
async def get_precipitaciones_tran(db: db_dependency):
    return db.query(models.Precipitaciones).all()

