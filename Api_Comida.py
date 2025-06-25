from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, date
import requests
import os
from dotenv import load_dotenv
from enum import Enum

load_dotenv()
app = FastAPI(title="API para Registrar Comidas", version="1.0.0")

EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")

# Base de datos en memoria (en producción usar una base de datos real)
alimentos_registrados = []
comidas_diarias = []

class TipoAlimento(str, Enum):
    DESAYUNO = "desayuno"
    ALMUERZO = "almuerzo"
    CENA = "cena"
    SNACK = "snack"
    BEBIDA = "bebida"

class CategoriaAlimento(str, Enum):
    PROTEINA = "proteina"
    CARBOHIDRATO = "carbohidrato"
    GRASA = "grasa"
    FRUTA = "fruta"
    VERDURA = "verdura"
    LACTEO = "lacteo"
    CEREAL = "cereal"
    LEGUMBRE = "legumbre"
    OTRO = "otro"

class AlimentoBase(BaseModel):
    nombre: str
    cantidad: float = 100
    unidad: str = "g"

class AlimentoRegistrado(BaseModel):
    nombre: str
    calorias_por_100g: float
    proteinas: float = 0
    carbohidratos: float = 0
    grasas: float = 0
    categoria: CategoriaAlimento
    tipo_comida: TipoAlimento
    cantidad: float
    unidad: str = "g"
    fecha: date = None

class MenuRequest(BaseModel):
    items: List[AlimentoBase]

class RegistroComidaRequest(BaseModel):
    alimentos: List[AlimentoRegistrado]
    fecha: Optional[date] = None

class ResumenDiario(BaseModel):
    fecha: date
    total_calorias: float
    total_proteinas: float
    total_carbohidratos: float
    total_grasas: float
    comidas: List[AlimentoRegistrado]

def buscar_calorias_edamam(alimento: str):
    """Busca información nutricional usando la API de Edamam"""
    url = "https://api.edamam.com/api/food-database/v2/parser"
    params = {
        "ingr": alimento,
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_APP_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("parsed") and len(data["parsed"]) > 0:
            food = data["parsed"][0]["food"]
            nutrients = food.get("nutrients", {})
            
            return {
                "nombre": food["label"],
                "calorias": nutrients.get("ENERC_KCAL", 0),
                "proteinas": nutrients.get("PROCNT", 0),
                "carbohidratos": nutrients.get("CHOCDF", 0),
                "grasas": nutrients.get("FAT", 0)
            }
    except requests.RequestException:
        pass
    
    raise HTTPException(
        status_code=404, 
        detail=f"No se encontró información nutricional para '{alimento}'"
    )

@app.post("/consultar-alimento")
def consultar_alimento(alimento: AlimentoBase):
    """Consulta información nutricional de un alimento"""
    info = buscar_calorias_edamam(alimento.nombre)
    
    # Calcular valores según la cantidad especificada
    factor = alimento.cantidad / 100
    
    return {
        "nombre": info["nombre"],
        "cantidad": alimento.cantidad,
        "unidad": alimento.unidad,
        "calorias": round(info["calorias"] * factor, 2),
        "proteinas": round(info["proteinas"] * factor, 2),
        "carbohidratos": round(info["carbohidratos"] * factor, 2),
        "grasas": round(info["grasas"] * factor, 2),
        "calorias_por_100g": info["calorias"]
    }

@app.post("/registrar-comida")
def registrar_comida(registro: RegistroComidaRequest):
    """Registra una comida completa con múltiples alimentos"""
    fecha_registro = registro.fecha or date.today()
    
    total_calorias = 0
    total_proteinas = 0
    total_carbohidratos = 0
    total_grasas = 0
    
    alimentos_procesados = []
    
    for alimento in registro.alimentos:
        # Calcular valores nutricionales según la cantidad
        factor = alimento.cantidad / 100
        
        calorias = alimento.calorias_por_100g * factor
        proteinas = alimento.proteinas * factor
        carbohidratos = alimento.carbohidratos * factor
        grasas = alimento.grasas * factor
        
        # Crear registro completo
        alimento_completo = {
            **alimento.dict(),
            "fecha": fecha_registro,
            "calorias_calculadas": round(calorias, 2),
            "proteinas_calculadas": round(proteinas, 2),
            "carbohidratos_calculados": round(carbohidratos, 2),
            "grasas_calculadas": round(grasas, 2)
        }
        
        alimentos_procesados.append(alimento_completo)
        comidas_diarias.append(alimento_completo)
        
        total_calorias += calorias
        total_proteinas += proteinas
        total_carbohidratos += carbohidratos
        total_grasas += grasas
    
    return {
        "mensaje": "Comida registrada exitosamente",
        "fecha": fecha_registro,
        "alimentos": alimentos_procesados,
        "resumen": {
            "total_calorias": round(total_calorias, 2),
            "total_proteinas": round(total_proteinas, 2),
            "total_carbohidratos": round(total_carbohidratos, 2),
            "total_grasas": round(total_grasas, 2)
        }
    }

@app.get("/resumen-diario/{fecha}")
def obtener_resumen_diario(fecha: date):
    """Obtiene el resumen nutricional de un día específico"""
    comidas_del_dia = [c for c in comidas_diarias if c["fecha"] == fecha]
    
    if not comidas_del_dia:
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontraron registros para la fecha {fecha}"
        )
    
    total_calorias = sum(c["calorias_calculadas"] for c in comidas_del_dia)
    total_proteinas = sum(c["proteinas_calculadas"] for c in comidas_del_dia)
    total_carbohidratos = sum(c["carbohidratos_calculados"] for c in comidas_del_dia)
    total_grasas = sum(c["grasas_calculadas"] for c in comidas_del_dia)
    
    # Agrupar por tipo de comida
    comidas_por_tipo = {}
    for comida in comidas_del_dia:
        tipo = comida["tipo_comida"]
        if tipo not in comidas_por_tipo:
            comidas_por_tipo[tipo] = []
        comidas_por_tipo[tipo].append(comida)
    
    return {
        "fecha": fecha,
        "resumen_total": {
            "calorias": round(total_calorias, 2),
            "proteinas": round(total_proteinas, 2),
            "carbohidratos": round(total_carbohidratos, 2),
            "grasas": round(total_grasas, 2)
        },
        "comidas_por_tipo": comidas_por_tipo,
        "total_alimentos": len(comidas_del_dia)
    }

@app.get("/historial/{dias}")
def obtener_historial(dias: int = 7):
    """Obtiene el historial de los últimos N días"""
    from datetime import timedelta
    
    fecha_inicio = date.today() - timedelta(days=dias-1)
    
    historial = {}
    for i in range(dias):
        fecha_actual = fecha_inicio + timedelta(days=i)
        comidas_del_dia = [c for c in comidas_diarias if c["fecha"] == fecha_actual]
        
        if comidas_del_dia:
            total_calorias = sum(c["calorias_calculadas"] for c in comidas_del_dia)
            historial[str(fecha_actual)] = {
                "calorias": round(total_calorias, 2),
                "num_alimentos": len(comidas_del_dia)
            }
        else:
            historial[str(fecha_actual)] = {
                "calorias": 0,
                "num_alimentos": 0
            }
    
    return {
        "periodo": f"Últimos {dias} días",
        "historial": historial
    }

@app.delete("/limpiar-registros")
def limpiar_registros():
    """Limpia todos los registros (solo para desarrollo)"""
    global comidas_diarias, alimentos_registrados
    comidas_diarias.clear()
    alimentos_registrados.clear()
    return {"mensaje": "Todos los registros han sido eliminados"}

@app.get("/")
def root():
    return {
        "mensaje": "API de Registro de Calorías",
        "version": "1.0.0",
        "endpoints": {
            "consultar_alimento": "POST /consultar-alimento",
            "registrar_comida": "POST /registrar-comida", 
            "resumen_diario": "GET /resumen-diario/{fecha}",
            "historial": "GET /historial/{dias}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)