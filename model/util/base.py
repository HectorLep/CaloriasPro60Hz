import sqlite3
import os

class DBManager:
    @staticmethod
    def conectar_usuario(usuario):
        """Conecta a la base de datos del usuario con debugging."""
        # 1. Construir la ruta a la base de datos
        db_path = f"./users/{usuario}/alimentos.db"
        
        # Obtenemos la ruta absoluta para no tener dudas de dónde está buscando el archivo
        abs_path = os.path.abspath(db_path)
        print(f"DEBUG [DBManager]: Intentando conectar a la BD del usuario en: '{abs_path}'")

        # 2. Verificar si el archivo existe ANTES de intentar conectar
        if not os.path.exists(abs_path):
            print(f"DEBUG [DBManager]: ¡ERROR! El archivo de base de datos NO EXISTE en la ruta especificada.")
            print(f"DEBUG [DBManager]: Verifica que el usuario '{usuario}' se haya registrado correctamente y la carpeta/archivo se haya creado.")
            return None  # Devolver None para que el resto del código sepa que la conexión falló

        # 3. Intentar la conexión
        try:
            conexion = sqlite3.connect(abs_path)
            print(f"DEBUG [DBManager]: Conexión a la BD del usuario '{usuario}' establecida con éxito.")
            return conexion
        except sqlite3.Error as e:
            print(f"DEBUG [DBManager]: ¡FALLÓ LA CONEXIÓN! Error de SQLite al intentar conectar: {e}")
            return None

    @staticmethod
    def conectar_principal():
        """Conecta a la base de datos principal de usuarios con debugging."""
        db_path = "./usuarios.db"
        abs_path = os.path.abspath(db_path)
        print(f"DEBUG [DBManager]: Intentando conectar a la BD principal en: '{abs_path}'")

        if not os.path.exists(abs_path):
            print(f"DEBUG [DBManager]: ¡ADVERTENCIA! El archivo de BD principal no existe en la ruta. SQLite podría crear uno vacío.")
        
        try:
            conexion = sqlite3.connect(abs_path)
            print("DEBUG [DBManager]: Conexión a la BD principal establecida con éxito.")
            return conexion
        except sqlite3.Error as e:
            print(f"DEBUG [DBManager]: ¡FALLÓ LA CONEXIÓN PRINCIPAL! Error de SQLite: {e}")
            return None

    @staticmethod
    def ejecutar_query(conexion, query, params=(), fetch_all=False, commit=False):
        """Ejecuta una consulta en la base de datos con debugging."""
        if not conexion:
            print("DEBUG [DBManager]: ¡ERROR! Se intentó ejecutar una query sobre una conexión NULA. Abortando.")
            return None

        print(f"DEBUG [DBManager]: Ejecutando query: {query}")
        if params:
            print(f"DEBUG [DBManager]: Con parámetros: {params}")

        try:
            cursor = conexion.cursor()
            cursor.execute(query, params)
            
            resultado = None
            if fetch_all:
                resultado = cursor.fetchall()
            else:
                resultado = cursor.fetchone()
                
            if commit:
                conexion.commit()
                print("DEBUG [DBManager]: Commit realizado.")
            
            # Imprimimos solo una parte del resultado si es muy largo
            resultado_str = str(resultado)
            if len(resultado_str) > 150:
                resultado_str = resultado_str[:150] + "..."
            print(f"DEBUG [DBManager]: Query ejecutada con éxito. Resultado: {resultado_str}")
            return resultado
        except sqlite3.Error as e:
            # El error original ya es bastante claro
            print(f"Error en la consulta: {e}")
            return None

    @staticmethod
    def cerrar_conexion(conexion):
        """Cierra la conexión a la base de datos con debugging."""
        if conexion:
            print("DEBUG [DBManager]: Cerrando conexión a la base de datos.")
            conexion.close()
        else:
            print("DEBUG [DBManager]: Intento de cerrar una conexión que ya era NULA.")