import os
from datetime import datetime, date, timedelta
from typing import Optional, List

import uvicorn
import requests
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

# --- 1. Configuración Centralizada ---
class Settings:
    # --- Configuración de la Base de Datos ---
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('DATABASE_URL') or 'sqlite:///./app_integrada.db'
    
    # --- Configuración de JWT ---
    JWT_SECRET_KEY: str = os.environ.get('Key_JWT') or 'dev-secret-key-change-in-production'
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = 60
    
    # --- Configuración de API Externa (Edamam) ---
    EDAMAM_APP_ID: str = os.environ.get('EDAMAM_APP_ID')
    EDAMAM_APP_KEY: str = os.environ.get('EDAMAM_APP_KEY')

settings = Settings()

# --- 2. Modelos de Base de Datos SQLAlchemy (Unificados) ---
Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(80), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    sexo = Column(String(10), nullable=False)
    peso = Column(Float, nullable=False)
    altura = Column(Integer, nullable=False)
    meta_calorias = Column(Integer, nullable=False)
    nivel_actividad = Column(String(15), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    edad = Column(Integer, nullable=False)
    registro = Column(DateTime, default=datetime.utcnow)

    # Relación con la tabla de consumo
    consumos = relationship("Consumo", back_populates="propietario")

class AlimentoPersonalizado(Base):
    __tablename__ = 'alimentos_personalizados'
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    calorias_100gr = Column(Float, nullable=True)
    calorias_porcion = Column(Float, nullable=True)
    # ID del usuario que creó este alimento (opcional, si quisieras que fueran privados)
    # user_id = Column(Integer, ForeignKey("usuarios.id"))

class Consumo(Base):
    __tablename__ = 'consumo_diario'
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_alimento = Column(String, index=True, nullable=False)
    cantidad = Column(Float, nullable=False)
    calorias_totales = Column(Float, nullable=False)
    fecha_consumo = Column(Date, nullable=False, default=date.today)
    hora_consumo = Column(String, nullable=False, default=lambda: datetime.now().strftime("%H:%M:%S"))
    
    # Clave foránea para vincular el consumo con un usuario
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    propietario = relationship("Usuario", back_populates="consumos")

# --- Configuración de la Base de Datos ---
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 3. Esquemas Pydantic (Unificados) ---

# --- Esquemas de Usuario y Auth ---
class UsuarioBase(BaseModel):
    nombre_usuario: str = Field(..., min_length=3, max_length=80)
    sexo: str
    peso: float = Field(..., gt=30, le=300)
    altura: int = Field(..., gt=100, le=250)
    meta_calorias: int = Field(..., gt=1000, le=5000)
    nivel_actividad: str
    fecha_nacimiento: date
    edad: int = Field(..., gt=12, le=120)

    @field_validator('sexo')
    @classmethod
    def sexo_valido(cls, v):
        if v not in ['Masculino', 'Femenino']:
            raise ValueError("El sexo debe ser 'Masculino' o 'Femenino'")
        return v

    @field_validator('nivel_actividad')
    @classmethod
    def nivel_actividad_valido(cls, v):
        if v not in ['Sedentario', 'Ligero', 'Moderado', 'Intenso']:
            raise ValueError("El nivel de actividad no es válido")
        return v

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)

class UsuarioPublic(UsuarioBase):
    id: int
    registro: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Esquemas de Alimentos y Consumo ---
class AlimentoBase(BaseModel):
    nombre: str
    calorias_100gr: Optional[float] = None
    calorias_porcion: Optional[float] = None

class AlimentoCreate(AlimentoBase):
    pass

class AlimentoPublic(AlimentoBase):
    id: int
    class Config:
        from_attributes = True
        
class AlimentoRespuesta(AlimentoBase):
    fuente: str

class ConsumoCreate(BaseModel):
    nombre_alimento: str
    cantidad: float
    calorias_totales: float
    
class ConsumoPublic(ConsumoCreate):
    id: int
    fecha_consumo: date
    hora_consumo: str
    user_id: int
    class Config:
        from_attributes = True

# --- 4. Lógica de Autenticación y Dependencias ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # Cambiado de "auth/login" a "login"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
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
    except JWTError:
        raise credentials_exception
        
    user = db.query(Usuario).filter(Usuario.nombre_usuario == username).first()
    if user is None:
        raise credentials_exception
    return user

# --- 5. Creación de la Aplicación FastAPI ---
app = FastAPI(
    title="API de Registro y Nutrición Integrada",
    version="5.0.0",
    description="Una API que combina registro de usuarios con seguimiento de consumo de alimentos."
)

# --- Rutas de Autenticación (sin prefijo) ---
@app.post("/register", response_model=UsuarioPublic, status_code=status.HTTP_201_CREATED, tags=["Autenticación"])
def register_user(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.nombre_usuario == usuario.nombre_usuario).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario ya está registrado.")
    
    hashed_password = generate_password_hash(usuario.password)
    nuevo_usuario = Usuario(**usuario.model_dump(exclude={'password'}), password_hash=hashed_password)
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@app.post("/login", response_model=Token, tags=["Autenticación"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.nombre_usuario == form_data.username).first()
    if not user or not check_password_hash(user.password_hash, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
        )
    
    access_token = create_access_token(data={"sub": user.nombre_usuario})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Rutas de Usuario ---
@app.get("/users/me", response_model=UsuarioPublic, tags=["Usuarios"])
def read_users_me(current_user: Usuario = Depends(get_current_user)):
    return current_user

# Ruta adicional para obtener todos los usuarios (si la necesitas)
@app.get("/users", response_model=List[UsuarioPublic], tags=["Usuarios"])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

# --- Router para Alimentos y Consumo ---
alimentos_router = APIRouter(prefix="/alimentos", tags=["Alimentos y Consumo"])

@alimentos_router.post("/personalizados", response_model=AlimentoPublic, status_code=201)
def agregar_alimento_personalizado(alimento: AlimentoCreate, db: Session = Depends(get_db)):
    db_alimento = AlimentoPersonalizado(**alimento.model_dump())
    if db.query(AlimentoPersonalizado).filter(AlimentoPersonalizado.nombre == alimento.nombre).first():
        raise HTTPException(status_code=409, detail=f"El alimento '{alimento.nombre}' ya existe.")
    db.add(db_alimento)
    db.commit()
    db.refresh(db_alimento)
    return db_alimento

@alimentos_router.get("/personalizados", response_model=List[AlimentoPublic])
def obtener_alimentos_personalizados(db: Session = Depends(get_db)):
    return db.query(AlimentoPersonalizado).order_by(AlimentoPersonalizado.nombre).all()

@alimentos_router.post("/consultar", response_model=AlimentoRespuesta)
def consultar_alimento(alimento: AlimentoBase):
    # 1. Buscar en la base de datos local (SQLAlchemy)
    db_alimento = SessionLocal().query(AlimentoPersonalizado).filter(AlimentoPersonalizado.nombre.ilike(f"%{alimento.nombre}%")).first()
    if db_alimento:
        return AlimentoRespuesta(**db_alimento.__dict__, fuente='local')

    # 2. Buscar en la API externa (Edamam)
    if not settings.EDAMAM_APP_ID or not settings.EDAMAM_APP_KEY:
         raise HTTPException(status_code=500, detail="La API externa no está configurada en el servidor.")
    
    url = "https://api.edamam.com/api/food-database/v2/parser"
    params = {"ingr": alimento.nombre, "app_id": settings.EDAMAM_APP_ID, "app_key": settings.EDAMAM_APP_KEY}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("parsed"):
            food = data["parsed"][0]["food"]
            nutrients = food.get("nutrients", {})
            return AlimentoRespuesta(nombre=food.get("label", alimento.nombre), calorias_100gr=nutrients.get("ENERC_KCAL", 0), fuente='externa')
    except requests.RequestException:
        pass # Ignorar errores de red para dar el mensaje final

    raise HTTPException(status_code=404, detail=f"No se encontró información para '{alimento.nombre}'.")

@alimentos_router.post("/consumo", response_model=ConsumoPublic)
def registrar_consumo(consumo: ConsumoCreate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    nuevo_consumo = Consumo(**consumo.model_dump(), user_id=current_user.id)
    db.add(nuevo_consumo)
    db.commit()
    db.refresh(nuevo_consumo)
    return nuevo_consumo

@alimentos_router.get("/consumo/{fecha_str}", response_model=List[ConsumoPublic])
def obtener_resumen_diario(fecha_str: str, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Use AAAA-MM-DD.")
        
    consumos = db.query(Consumo).filter(Consumo.user_id == current_user.id, Consumo.fecha_consumo == fecha).all()
    if not consumos:
        raise HTTPException(status_code=404, detail=f"No se encontraron registros para la fecha {fecha_str}")
    return consumos

@alimentos_router.get("/historial", response_model=List[ConsumoPublic])
def obtener_historial_completo(fecha_desde: date, fecha_hasta: date, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    registros = db.query(Consumo).filter(
        Consumo.user_id == current_user.id,
        Consumo.fecha_consumo.between(fecha_desde, fecha_hasta)
    ).order_by(Consumo.fecha_consumo.desc(), Consumo.hora_consumo.desc()).all()
    return registros

# Incluir el router de alimentos
app.include_router(alimentos_router)

@app.on_event("startup")
def on_startup():
    # Crea todas las tablas al iniciar la aplicación
    Base.metadata.create_all(bind=engine)
    print("Base de datos y tablas creadas (si no existían).")
    if not settings.EDAMAM_APP_ID or not settings.EDAMAM_APP_KEY:
        print("ADVERTENCIA: Las credenciales de la API de Edamam no están configuradas. El endpoint /consultar solo funcionará para alimentos locales.")

@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "Bienvenido a la API de Nutrición Integrada. Visita /docs para la documentación."}

if __name__ == "__main__":
    print("Iniciando servidor FastAPI...")
    print("Accede a la documentación en http://127.0.0.1:8000/docs")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)