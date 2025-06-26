# peso_api.py

import os
import requests
from datetime import datetime, date
from typing import Optional, List
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

# --- 1. Configuración ---
class Settings:
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('PESO_DATABASE_URL') or 'sqlite:///./peso.db'
    JWT_SECRET_KEY: str = os.environ.get('Key_JWT') or 'dev-secret-key-change-in-production'
    JWT_ALGORITHM: str = "HS256"
    USER_API_URL: str = os.environ.get('USER_API_URL') or 'http://127.0.0.1:8000'

settings = Settings()

# --- 2. Modelos de Base de Datos SQLAlchemy ---
Base = declarative_base()

class RegistroPeso(Base):
    __tablename__ = 'registros_peso'
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False, index=True)  # ID del usuario desde la otra API
    fecha = Column(Date, nullable=False)
    peso = Column(Float, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow)

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

# --- 3. Esquemas Pydantic ---

class RegistroPesoBase(BaseModel):
    fecha: date = Field(..., description="Fecha en formato YYYY-MM-DD")
    peso: float = Field(..., gt=30, le=300, description="Peso en kilogramos")

    @field_validator('fecha')
    @classmethod
    def validar_fecha(cls, v):
        if v > date.today():
            raise ValueError("La fecha no puede ser futura")
        return v

class RegistroPesoCreate(RegistroPesoBase):
    pass

class RegistroPesoUpdate(BaseModel):
    peso: Optional[float] = Field(None, gt=30, le=300, description="Nuevo peso en kilogramos")
    fecha: Optional[date] = Field(None, description="Nueva fecha en formato YYYY-MM-DD")

    @field_validator('fecha')
    @classmethod
    def validar_fecha(cls, v):
        if v and v > date.today():
            raise ValueError("La fecha no puede ser futura")
        return v

class RegistroPesoPublic(RegistroPesoBase):
    id: int
    usuario_id: int
    creado_en: datetime

    class Config:
        orm_mode = True

class EstadisticasPeso(BaseModel):
    peso_actual: float
    peso_inicial: Optional[float]
    diferencia_peso: Optional[float]
    total_registros: int
    peso_promedio: float
    peso_minimo: float
    peso_maximo: float

# --- 4. Autenticación (usando el mismo sistema que la API de usuarios) ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.USER_API_URL}/login")

async def verificar_usuario_existe(usuario_id: int, token: str) -> bool:
    """
    Verifica si el usuario existe en la API de usuarios
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{settings.USER_API_URL}/users/me/", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            return user_data.get("id") == usuario_id
        return False
    except Exception:
        return False

async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Obtiene la información del usuario actual desde la API de usuarios
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token JWT para obtener el username
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Hacer llamada a la API de usuarios para obtener información completa
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{settings.USER_API_URL}/users/me/", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise credentials_exception
    except Exception:
        raise credentials_exception

# --- 5. Funciones auxiliares ---
async def actualizar_peso_en_api_usuarios(usuario_id: int, nuevo_peso: float, token: str):
    """
    Actualiza el peso del usuario en la API de usuarios (funcionalidad futura)
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        # Esta funcionalidad requeriría un endpoint en la API de usuarios para actualizar el peso
        # Por ahora solo registramos que se haría la llamada
        print(f"[INFO] Se actualizaría el peso del usuario {usuario_id} a {nuevo_peso} kg en la API de usuarios")
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo actualizar el peso en la API de usuarios: {e}")
        return False

# --- 6. Creación de la Aplicación y Endpoints ---
app = FastAPI(
    title="API de Registro de Peso", 
    version="1.0.0",
    description="API para el manejo de registros de peso de usuarios"
)

@app.post("/peso/", response_model=RegistroPesoPublic, status_code=status.HTTP_201_CREATED, tags=["Peso"])
async def crear_registro_peso(
    registro: RegistroPesoCreate, 
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    """
    Crea un nuevo registro de peso para el usuario autenticado
    """
    # Verificar si ya existe un registro para esta fecha
    registro_existente = db.query(RegistroPeso).filter(
        RegistroPeso.usuario_id == usuario_actual["id"],
        RegistroPeso.fecha == registro.fecha
    ).first()
    
    if registro_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un registro de peso para la fecha {registro.fecha.strftime('%d-%m-%Y')}"
        )
    
    nuevo_registro = RegistroPeso(
        usuario_id=usuario_actual["id"],
        fecha=registro.fecha,
        peso=registro.peso
    )
    
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    
    # Intentar actualizar el peso en la API de usuarios si es el registro más reciente
    registros_usuario = db.query(RegistroPeso).filter(
        RegistroPeso.usuario_id == usuario_actual["id"]
    ).order_by(RegistroPeso.fecha.desc()).all()
    
    if registros_usuario and registros_usuario[0].id == nuevo_registro.id:
        # Este es el registro más reciente, actualizar en API de usuarios
        # await actualizar_peso_en_api_usuarios(usuario_actual["id"], registro.peso, token)
        pass
    
    return nuevo_registro

@app.get("/peso/", response_model=List[RegistroPesoPublic], tags=["Peso"])
async def obtener_registros_peso(
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(obtener_usuario_actual),
    limite: int = Query(50, ge=1, le=100, description="Número máximo de registros a devolver"),
    saltar: int = Query(0, ge=0, description="Número de registros a saltar")
):
    """
    Obtiene todos los registros de peso del usuario autenticado
    """
    registros = db.query(RegistroPeso).filter(
        RegistroPeso.usuario_id == usuario_actual["id"]
    ).order_by(RegistroPeso.fecha.desc()).offset(saltar).limit(limite).all()
    
    return registros

@app.get("/peso/{registro_id}", response_model=RegistroPesoPublic, tags=["Peso"])
async def obtener_registro_peso(
    registro_id: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    """
    Obtiene un registro específico de peso
    """
    registro = db.query(RegistroPeso).filter(
        RegistroPeso.id == registro_id,
        RegistroPeso.usuario_id == usuario_actual["id"]
    ).first()
    
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de peso no encontrado"
        )
    
    return registro

@app.put("/peso/{registro_id}", response_model=RegistroPesoPublic, tags=["Peso"])
async def actualizar_registro_peso(
    registro_id: int,
    actualizacion: RegistroPesoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    """
    Actualiza un registro específico de peso
    """
    registro = db.query(RegistroPeso).filter(
        RegistroPeso.id == registro_id,
        RegistroPeso.usuario_id == usuario_actual["id"]
    ).first()
    
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de peso no encontrado"
        )
    
    # Verificar si la nueva fecha ya existe (si se está cambiando la fecha)
    if actualizacion.fecha and actualizacion.fecha != registro.fecha:
        registro_existente = db.query(RegistroPeso).filter(
            RegistroPeso.usuario_id == usuario_actual["id"],
            RegistroPeso.fecha == actualizacion.fecha,
            RegistroPeso.id != registro_id
        ).first()
        
        if registro_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un registro de peso para la fecha {actualizacion.fecha.strftime('%d-%m-%Y')}"
            )
    
    # Actualizar campos
    if actualizacion.peso is not None:
        registro.peso = actualizacion.peso
    if actualizacion.fecha is not None:
        registro.fecha = actualizacion.fecha
    
    db.commit()
    db.refresh(registro)
    
    return registro

@app.delete("/peso/{registro_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Peso"])
async def eliminar_registro_peso(
    registro_id: int,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    """
    Elimina un registro específico de peso
    """
    registro = db.query(RegistroPeso).filter(
        RegistroPeso.id == registro_id,
        RegistroPeso.usuario_id == usuario_actual["id"]
    ).first()
    
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de peso no encontrado"
        )
    
    db.delete(registro)
    db.commit()

@app.get("/peso/estadisticas/", response_model=EstadisticasPeso, tags=["Estadísticas"])
async def obtener_estadisticas_peso(
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    """
    Obtiene estadísticas del peso del usuario
    """
    registros = db.query(RegistroPeso).filter(
        RegistroPeso.usuario_id == usuario_actual["id"]
    ).order_by(RegistroPeso.fecha.asc()).all()
    
    if not registros:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron registros de peso"
        )
    
    pesos = [r.peso for r in registros]
    peso_actual = registros[-1].peso  # Último registro (más reciente)
    peso_inicial = registros[0].peso   # Primer registro
    
    return EstadisticasPeso(
        peso_actual=peso_actual,
        peso_inicial=peso_inicial,
        diferencia_peso=peso_actual - peso_inicial,
        total_registros=len(registros),
        peso_promedio=sum(pesos) / len(pesos),
        peso_minimo=min(pesos),
        peso_maximo=max(pesos)
    )

@app.get("/peso/por-fecha/{fecha}", response_model=RegistroPesoPublic, tags=["Peso"])
async def obtener_peso_por_fecha(
    fecha: date,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    """
    Obtiene el registro de peso para una fecha específica
    """
    registro = db.query(RegistroPeso).filter(
        RegistroPeso.usuario_id == usuario_actual["id"],
        RegistroPeso.fecha == fecha
    ).first()
    
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró registro de peso para la fecha {fecha.strftime('%d-%m-%Y')}"
        )
    
    return registro

@app.get("/health", tags=["Sistema"])
async def health_check():
    """
    Verifica el estado de la API
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

# Agregar el import que faltaba
from fastapi import Query

if __name__ == "__main__":
    print("Iniciando API de Peso...")
    print("Accede a la documentación en http://127.0.0.1:8001/docs")
    uvicorn.run("peso_api:app", host="127.0.0.1", port=8001, reload=True)