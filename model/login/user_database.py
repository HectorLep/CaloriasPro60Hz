import sqlite3
import os
from abc import ABC, abstractmethod

class IUserDatabase(ABC):
    @abstractmethod
    def crear_db_usuario(self, nombre_usuario):
        pass


class UserDatabase(IUserDatabase):
    def crear_db_usuario(self, nombre_usuario):
        """Crea la base de datos para un nuevo usuario."""
        directorio = f'./users/{nombre_usuario}'
        os.makedirs(directorio, exist_ok=True)
        
        try:
            conn = sqlite3.connect(f"{directorio}/alimentos.db")
            cursor = conn.cursor()
            
            tablas = {
                'alimento': '''
                    CREATE TABLE IF NOT EXISTS alimento (
                        nombre TEXT NOT NULL,
                        calorias_100gr INTEGER,
                        calorias_porcion INTEGER
                    )
                ''',
                'consumo_diario': '''
                    CREATE TABLE IF NOT EXISTS consumo_diario (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        fecha TEXT NOT NULL,
                        hora TEXT NOT NULL,
                        cantidad INTEGER NOT NULL,
                        total_cal REAL NOT NULL
                    )
                ''',
                'peso': '''
                    CREATE TABLE IF NOT EXISTS peso (
                        num INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT,
                        peso REAL
                    )
                ''',
                'agua': '''
                    CREATE TABLE IF NOT EXISTS agua (
                        num INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT,
                        cant INTEGER
                    )
                ''',
                'datos': '''
                    CREATE TABLE IF NOT EXISTS datos (
                        nombre TEXT PRIMARY KEY,
                        estatura INTEGER,
                        nivel_actividad TEXT,
                        genero TEXT,
                        meta_cal INTEGER,
                        edad INTEGER,
                        recordatorio TEXT,
                        cantidad_dias VARCHAR,
                        ultimo_msj TEXT 
                    )
                ''',
                'mensajes': '''
                    CREATE TABLE IF NOT EXISTS mensajes (
                        registrar_alimento INTEGER DEFAULT 0,
                        agregar_alimento INTEGER DEFAULT 0,
                        graficos INTEGER DEFAULT 0,
                        configuracion INTEGER DEFAULT 0,
                        salud INTEGER DEFAULT 0,
                        admin_alimentos INTEGER DEFAULT 0,
                        historial INTEGER DEFAULT 0
                    )
                ''',
                'recordatorios': '''
                    CREATE TABLE IF NOT EXISTS recordatorios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Titulo TEXT,
                        Fecha TEXT,
                        Hora TEXT,
                        Usuario TEXT
                    )
                '''
            }
            
            for tabla in tablas.values():
                cursor.execute(tabla)
                
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al crear base de datos: {e}")
            return False
        finally:
            if conn:
                conn.close()