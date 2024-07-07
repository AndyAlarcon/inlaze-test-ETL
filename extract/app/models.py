from sqlalchemy import Column, Integer, String
from database import Base

class Precipitaciones(Base):
    __tablename__='precipitaciones'

    codigoestacion = Column(String, primary_key=True, index=True)
    codigosensor = Column(String, index=True)
    valorobservado = Column(String)
    nombreestacion = Column(String)
    departamento = Column(String)
    municipio = Column(String)
    zonahidrografica = Column(String)
    latitud = Column(String)
    longitud = Column(String)
    descripcionsensor = Column(String)
    unidadmedida = Column(String)
    ano_obser = Column(Integer)
    mes_obser = Column(Integer)
    dia_obser = Column(Integer)