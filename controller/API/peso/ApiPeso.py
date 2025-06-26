# peso_api.py

import os
from datetime import datetime
from typing import List
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- Configuración ---
class Settings:
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('PESO_DATABASE_URL') or 'sqlite:///./peso.db'
    JWT_SECRET_KEY: str = os.environ.get('Key_JWT') or 'dev-secret-key-change-in-production'
    JWT_ALGORITHM: str = "HS256"

settings = Settings()

# --- Modelo de Base de Datos ---
Base = declarative_base()

class Peso(Base):
    __tablename__ = 'peso'
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String(8), nullable=False)  # DD-MM-YY
    peso = Column(Float, nullable=False)

# --- Configuración de la Base de Datos ---
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Esquemas Pydantic ---
class PesoBase(BaseModel):
    fecha: str = Field(..., description="Fecha en formato DD-MM-YY")
    peso: float = Field(..., gt=0, description="Peso en kilogramos")

    @field_validator('fecha')
    @classmethod
    def validar_fecha(cls, v):
        try:
            datetime.strptime(v, '%d-%m-%y')
            return v
        except ValueError:
            raise ValueError("La fecha debe estar en formato DD-MM-YY")

class PesoCreate(PesoBase):
    pass

class PesoPublic(PesoBase):
    id: int

    class Config:
        orm_mode = True

# --- Autenticación ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8000/login")

async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

# --- API ---
app = FastAPI(title="API de Peso", version="1.0.0")

@app.post("/peso/", response_model=PesoPublic, status_code=status.HTTP_201_CREATED)
async def crear_peso(
    peso: PesoCreate, 
    db: Session = Depends(get_db),
    usuario: str = Depends(obtener_usuario_actual)
):
    nuevo_peso = Peso(fecha=peso.fecha, peso=peso.peso)
    db.add(nuevo_peso)
    db.commit()
    db.refresh(nuevo_peso)
    return nuevo_peso

@app.get("/peso/", response_model=List[PesoPublic])
async def obtener_pesos(
    db: Session = Depends(get_db),
    usuario: str = Depends(obtener_usuario_actual)
):
    return db.query(Peso).all()

@app.get("/peso/{peso_id}", response_model=PesoPublic)
async def obtener_peso(
    peso_id: int,
    db: Session = Depends(get_db),
    usuario: str = Depends(obtener_usuario_actual)
):
    peso = db.query(Peso).filter(Peso.id == peso_id).first()
    if not peso:
        raise HTTPException(status_code=404, detail="Peso no encontrado")
    return peso

@app.put("/peso/{peso_id}", response_model=PesoPublic)
async def actualizar_peso(
    peso_id: int,
    peso_actualizado: PesoCreate,
    db: Session = Depends(get_db),
    usuario: str = Depends(obtener_usuario_actual)
):
    peso = db.query(Peso).filter(Peso.id == peso_id).first()
    if not peso:
        raise HTTPException(status_code=404, detail="Peso no encontrado")
    
    peso.fecha = peso_actualizado.fecha
    peso.peso = peso_actualizado.peso
    db.commit()
    db.refresh(peso)
    return peso

@app.delete("/peso/{peso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_peso(
    peso_id: int,
    db: Session = Depends(get_db),
    usuario: str = Depends(obtener_usuario_actual)
):
    peso = db.query(Peso).filter(Peso.id == peso_id).first()
    if not peso:
        raise HTTPException(status_code=404, detail="Peso no encontrado")
    
    db.delete(peso)
    db.commit()

if __name__ == "__main__":
    print("Iniciando API de Peso...")
    print("Accede a la documentación en http://127.0.0.1:8001/docs")
    uvicorn.run("peso_api:app", host="127.0.0.1", port=8001, reload=True)