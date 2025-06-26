import sqlite3
import os
import requests

class DBManager:
    # Configuración API
    API_URL = "http://127.0.0.1:8000"
    _token = None
    
    @classmethod
    def set_token(cls, token):
        """Establece el token JWT para las consultas API."""
        cls._token = token
    
    @classmethod
    def api_request(cls, method, endpoint, data=None):
        """Realiza peticiones a la API de forma optimizada."""
        url = f"{cls.API_URL}{endpoint}"
        headers = {"Authorization": f"Bearer {cls._token}"} if cls._token else {}
        
        try:
            response = requests.request(method, url, json=data, headers=headers)
            return response.json() if response.status_code == 200 else None
        except:
            return None
    
    @classmethod
    def obtener_usuario_actual(cls):
        """Obtiene datos del usuario autenticado desde la API."""
        return cls.api_request("GET", "/users/me/")
    
    @classmethod
    def login_api(cls, username, password):
        """Login y guarda el token automáticamente."""
        try:
            response = requests.post(f"{cls.API_URL}/login/", 
                                   data={"username": username, "password": password})
            if response.status_code == 200:
                token = response.json()["access_token"]
                cls.set_token(token)
                return True
            return False
        except:
            return False
    
    @classmethod
    def eliminar_cuenta_api(cls):
        """Elimina la cuenta del usuario autenticado."""
        result = cls.api_request("DELETE", "/users/me/")
        return result is not None
    
    # Métodos legacy mantenidos para compatibilidad
    @staticmethod
    def conectar_usuario(usuario):
        """Conecta a la base de datos del usuario."""
        db_path = f"{usuario}/app.db"
        abs_path = os.path.abspath(db_path)
        
        if not os.path.exists(abs_path):
            return None
        
        try:
            return sqlite3.connect(abs_path)
        except sqlite3.Error:
            return None

    @staticmethod
    def conectar_principal():
        """Conecta a la base de datos principal."""
        try:
            return sqlite3.connect("./app.db")
        except sqlite3.Error:
            return None

    @staticmethod
    def ejecutar_query(conexion, query, params=(), fetch_all=False, commit=False):
        """Ejecuta consulta en BD local."""
        if not conexion:
            return None
        
        try:
            cursor = conexion.cursor()
            cursor.execute(query, params)
            
            resultado = cursor.fetchall() if fetch_all else cursor.fetchone()
            
            if commit:
                conexion.commit()
            
            return resultado
        except sqlite3.Error:
            return None

    @staticmethod
    def cerrar_conexion(conexion):
        """Cierra conexión a BD."""
        if conexion:
            conexion.close()