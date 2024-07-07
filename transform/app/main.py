from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from redis import Redis
import httpx
import pandas as pd
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis(host='localhost', port=6379)
    app.state.http_client = httpx.AsyncClient()
    yield
    app.state.redis.close()

app = FastAPI(lifespan=lifespan)


@app.get("/precipitacion_trans")
async def get_precipitacion_trans():
    value = app.state.redis.get('precipitacion')
    if value is None:
        raise HTTPException(status_code=404, detail='Sin registros para transformar')
    precipitacion_trans(json.loads(value))
    return {"result": "ok"}

def precipitacion_trans(redis_json):
    df = pd.DataFrame.from_records(redis_json)
    return df.info()