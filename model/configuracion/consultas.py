from model.util.base import DBManager
from .mensajes import MessageHandler  # Importamos nuestro manejador de mensajes
import os
import shutil
import requests
import json

# Configuración de la API
API_BASE_URL = "http://127.0.0.1:8000"  # Ajusta según tu configuración

def obtener_datos_usuario(nombre_usuario):
    """Obtiene edad, género, meta calórica, nivel de actividad, estatura y peso actual del usuario."""
    try:
        conn = DBManager.conectar_usuario(nombre_usuario)
        query_user = "SELECT edad, genero, meta_cal, nivel_actividad, estatura FROM datos WHERE nombre = ?"
        user_data = DBManager.ejecutar_query(conn, query_user, (nombre_usuario,))

        query_peso = """
            SELECT peso, fecha 
            FROM peso 
            ORDER BY 
                SUBSTR(fecha, 7, 4) DESC, -- Año (YYYY)
                SUBSTR(fecha, 4, 2) DESC, -- Mes (MM)
                SUBSTR(fecha, 1, 2) DESC  -- Día (DD)
            LIMIT 1
        """
        peso_data = DBManager.ejecutar_query(conn, query_peso)

        DBManager.cerrar_conexion(conn)

        if user_data and peso_data:
            edad, genero, meta_cal, nivel_actividad, estatura = user_data
            peso, fecha = peso_data
            return edad, genero, peso, nivel_actividad, meta_cal, estatura
        else:
            return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
    except Exception as e:
        # Usamos nuestro MessageHandler en lugar de CTkMessagebox
        MessageHandler.mostrar_advertencia("Error", f"Error al acceder a la base de datos: {e}")
        return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

def guardar_peso(nombre_usuario, nuevo_peso):
    """Guarda un nuevo peso para el usuario con la fecha actual en formato DD-MM-YYYY."""
    try:
        conn = DBManager.conectar_usuario(nombre_usuario)
        query = "INSERT INTO peso (peso, fecha) VALUES (?, strftime('%d-%m-%Y', 'now'))"
        DBManager.ejecutar_query(conn, query, (nuevo_peso,), commit=True)
        DBManager.cerrar_conexion(conn)
        return True
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al guardar peso: {e}")
        return False

def actualizar_datos_usuario(nombre_usuario, nueva_estatura, nueva_meta_cal, nuevo_nivel_act):
    """Actualiza estatura, objetivo de calorías y nivel de actividad del usuario."""
    try:
        conexion = DBManager.conectar_usuario(nombre_usuario)
        query = """
            UPDATE datos
            SET estatura = ?, meta_cal = ?, nivel_actividad = ?
            WHERE nombre = ?
        """
        DBManager.ejecutar_query(conexion, query, (nueva_estatura, nueva_meta_cal, nuevo_nivel_act, nombre_usuario), commit=True)
        DBManager.cerrar_conexion(conexion)
        return True
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al guardar datos: {e}")
        return False

def actualizar_contrasena(nombre_usuario, contra_actual, nueva_contra):
    """Verifica y actualiza la contraseña de un usuario."""
    try:
        conexion = DBManager.conectar_principal()
        query_verificar = "SELECT contra FROM users WHERE nombre = ?"
        resultado = DBManager.ejecutar_query(conexion, query_verificar, (nombre_usuario,))
        
        if resultado and resultado[0] == contra_actual:
            query_actualizar = "UPDATE users SET contra = ? WHERE nombre = ?"
            DBManager.ejecutar_query(conexion, query_actualizar, (nueva_contra, nombre_usuario), commit=True)
            DBManager.cerrar_conexion(conexion)
            return True
        else:
            DBManager.cerrar_conexion(conexion)
            return False
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al actualizar contraseña: {e}")
        return False

def obtener_configuracion_recordatorio(nombre_usuario):
    """Obtiene el estado y frecuencia del recordatorio de peso."""
    try:
        conn = DBManager.conectar_usuario(nombre_usuario)
        query = "SELECT recordatorio, cantidad_dias FROM datos WHERE nombre = ?"
        config = DBManager.ejecutar_query(conn, query, (nombre_usuario,))
        DBManager.cerrar_conexion(conn)
        return config if config else ("off", "1 día")
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al cargar configuración: {e}")
        return "off", "1 día"

def guardar_configuracion_recordatorio(nombre_usuario, estado, frecuencia):
    """Guarda la configuración del recordatorio del usuario."""
    try:
        conn = DBManager.conectar_usuario(nombre_usuario)
        query = """
            UPDATE datos 
            SET recordatorio = ?, cantidad_dias = ? 
            WHERE nombre = ?
        """
        DBManager.ejecutar_query(conn, query, (estado, frecuencia, nombre_usuario), commit=True)
        DBManager.cerrar_conexion(conn)
        return True
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al guardar configuración: {e}")
        return False

def login_usuario_api(nombre_usuario, contraseña):
    """Autentica al usuario en la API y devuelve el token de acceso."""
    try:
        login_data = {
            "username": nombre_usuario,
            "password": contraseña
        }
        
        response = requests.post(
            f"{API_BASE_URL}/login/",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            return None
            
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al conectar con la API: {e}")
        return None

def eliminar_usuario_api(token):
    """Elimina la cuenta del usuario usando la API con el token JWT."""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.delete(
            f"{API_BASE_URL}/users/me/",
            headers=headers
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            error_detail = response.json().get("detail", "Error desconocido") if response.content else "Error de conexión"
            return False, error_detail
            
    except Exception as e:
        return False, f"Error al conectar con la API: {e}"

def eliminar_usuario(nombre_usuario, contraseña):
    """
    Elimina la cuenta del usuario usando la nueva API.
    Mantiene compatibilidad con el código existente.
    """
    try:
        # 1. Autenticar usuario y obtener token
        token = login_usuario_api(nombre_usuario, contraseña)
        if not token:
            MessageHandler.mostrar_advertencia("Error", "Credenciales incorrectas")
            return False
        
        # 2. Eliminar usuario usando la API
        success, result = eliminar_usuario_api(token)
        
        if success:
            # 3. Limpiar archivos locales si existen (compatibilidad con sistema anterior)
            usuario_path = f'./users/{nombre_usuario}'
            if os.path.exists(usuario_path):
                try:
                    shutil.rmtree(usuario_path)
                except Exception as e:
                    # No es crítico si no se pueden eliminar los archivos locales
                    print(f"Advertencia: No se pudieron eliminar archivos locales: {e}")
            
            MessageHandler.mostrar_info("Éxito", f"Cuenta eliminada exitosamente: {result.get('deleted_user', nombre_usuario)}")
            return True
        else:
            MessageHandler.mostrar_advertencia("Error", f"Error al eliminar cuenta: {result}")
            return False
            
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al eliminar cuenta: {e}")
        return False

# Función auxiliar para verificar si la API está disponible
def verificar_api_disponible():
    """Verifica si la API está funcionando."""
    try:
        response = requests.get(f"{API_BASE_URL}/users/", timeout=5)
        return response.status_code == 200
    except:
        return False

def eliminar_usuario_legacy(nombre_usuario, contraseña):
    """
    Versión legacy de eliminar usuario (por si la API no está disponible).
    Mantiene la funcionalidad original como respaldo.
    """
    try:
        conexion = DBManager.conectar_principal()
        query_verificar = "SELECT contra FROM users WHERE nombre = ?"
        resultado = DBManager.ejecutar_query(conexion, query_verificar, (nombre_usuario,))

        if resultado and resultado[0] == contraseña:
            usuario_path = f'./users/{nombre_usuario}'
            if os.path.exists(usuario_path):
                shutil.rmtree(usuario_path)

            DBManager.ejecutar_query(conexion, "DELETE FROM users WHERE nombre = ?", (nombre_usuario,), commit=True)
            DBManager.cerrar_conexion(conexion)
            return True
        else:
            DBManager.cerrar_conexion(conexion)
            return False
    except Exception as e:
        MessageHandler.mostrar_advertencia("Error", f"Error al eliminar cuenta: {e}")
        return False