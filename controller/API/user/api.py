# api.py

import os
from datetime import datetime, date, timedelta
from typing import Optional
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from werkzeug.security import generate_password_hash, check_password_hash

# --- 1. Configuración ---
class Settings:
    SQLALCHEMY_DATABASE_URI: str = os.environ.get('DATABASE_URL') or 'sqlite:///./app.db'
    JWT_SECRET_KEY: str = os.environ.get('Key_JWT') or 'dev-secret-key-change-in-production'
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = 60

settings = Settings()

# --- 2. Modelos de Base de Datos SQLAlchemy ---
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
    registro = Column(DateTime, default=datetime.utcnow)
    
    edad = Column(Integer, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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

class UsuarioLogin(BaseModel):
    nombre_usuario: str
    password: str

class UsuarioPublic(UsuarioBase):
    id: int
    registro: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str



# --- 4. Lógica de Autenticación y JWT ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

# --- 5. Creación de la Aplicación y Endpoints ---
app = FastAPI(title="API de Registro y Nutrición", version="1.0.0")

@app.post("/register/", response_model=UsuarioPublic, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register_user(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_user = db.query(Usuario).filter(Usuario.nombre_usuario == usuario.nombre_usuario).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado."
        )
    
    hashed_password = generate_password_hash(usuario.password)
    nuevo_usuario = Usuario(
        nombre_usuario=usuario.nombre_usuario,
        password_hash=hashed_password,
        sexo=usuario.sexo,
        peso=usuario.peso,
        altura=usuario.altura,
        meta_calorias=usuario.meta_calorias,
        nivel_actividad=usuario.nivel_actividad,
        fecha_nacimiento=usuario.fecha_nacimiento,
        edad=usuario.edad
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario

@app.post("/login/", response_model=Token, tags=["Auth"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.nombre_usuario == form_data.username).first()
    if not user or not check_password_hash(user.password_hash, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    expire_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)
    access_token = create_access_token(data={"sub": user.nombre_usuario}, expires_delta=expire_delta)
    
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/", response_model=list[str], tags=["Users"])
def get_all_users(db: Session = Depends(get_db)):
    """
    Obtiene una lista de todos los nombres de usuario registrados.
    """
    usuarios = db.query(Usuario.nombre_usuario).all()
    # La consulta devuelve una lista de tuplas [('user1',), ('user2',)], la aplanamos.
    return [usuario[0] for usuario in usuarios]

@app.get("/users/me/", response_model=UsuarioPublic, tags=["Users"])
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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

# << MODIFICADO >>: Se cambia 'main:app' por 'api:app' para reflejar el nuevo nombre del archivo.
if __name__ == "__main__":
    print("Iniciando servidor FastAPI...")
    print("Accede a la documentación en http://127.0.0.1:8000/docs")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)