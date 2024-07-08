from fastapi import FastAPI, Response, HTTPException
import requests
from contextlib import asynccontextmanager
from redis import Redis
import httpx
import pandas as pd
import numpy as np
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis(host='redis', port=6379)
    app.state.http_client = httpx.AsyncClient()
    yield
    app.state.redis.close()

app = FastAPI(lifespan=lifespan)


@app.get("/precipitacion_trans")
async def get_precipitacion_trans():
    value = app.state.redis.get('precipitacion')
    if value is None:
        raise HTTPException(status_code=404, detail='Sin registros para transformar')
    df_json = precipitacion_trans(json.loads(value)).to_json(orient='split')
    result = app.state.redis.set('precipitacion_trans', df_json)

    if result:
        response = requests.get('http://load:9000/load/')
        if response.status_code == 204:
            return Response(status_code=204)
        else:
            return Response(content='f{"result": {response.text}}', media_type="application/json", status_code=207)
    else:
        return Response(content='{"result": "Recibido, pero no procesado"}', media_type="application/json", status_code=207)

def precipitacion_trans(redis_json):
    df = pd.DataFrame.from_records(redis_json)
    #Reemplazar valores <nil> por NaN, para borrar las filas posteriormente
    df.replace('<nil>', np.nan, inplace=True)
    df = df.dropna(axis=0, how='any')
    
    #Generación de columnas nuevas, para separar en año, mes y día, a partir de la columna fecha
    df['fechaobservacion'] = pd.to_datetime(df['fechaobservacion'])

    df['ano_obser'] = df['fechaobservacion'].dt.year
    df['mes_obser'] = df['fechaobservacion'].dt.month
    df['dia_obser'] = df['fechaobservacion'].dt.day

    #Se elimina la columna fecha
    df.drop(columns=['fechaobservacion'], inplace=True)
    return df