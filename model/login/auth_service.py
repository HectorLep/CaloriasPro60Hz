import sqlite3
from abc import ABC, abstractmethod


class IAuthService(ABC):
    @abstractmethod
    def verificar_credenciales(self, usuario, contrasena):
        pass
    
    @abstractmethod
    def registrar_usuario(self, datos_usuario):
        pass
    
    @abstractmethod
    def obtener_usuarios(self):
        pass
    
    @abstractmethod
    def guardar_usuario_actual(self, usuario):
        pass
    
    @abstractmethod
    def limpiar_usuario_actual(self):
        pass

    # --- AÑADE ESTE MÉTODO AQUÍ ---
    @abstractmethod
    def obtener_usuario_actual(self):
        pass

class AuthService(IAuthService):
    def __init__(self, db_file='usuarios.db'):
        self.db_file = db_file
        self._inicializar_db()
        
    def _inicializar_db(self):
        """Inicializa la base de datos si no existe."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    nombre TEXT PRIMARY KEY,
                    contra TEXT NOT NULL
                )
            """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error al inicializar la base de datos: {e}")
        finally:
            if conn:
                conn.close()
    
    def verificar_credenciales(self, usuario, contrasena):
        """Verifica las credenciales del usuario."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT contra FROM users WHERE nombre = ?", (usuario,))
            resultado = cursor.fetchone()
            
            return resultado is not None and contrasena == resultado[0]
        except sqlite3.Error as e:
            print(f"Error al verificar credenciales: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def registrar_usuario(self, datos_usuario):
        """Registra un nuevo usuario en la base de datos."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (nombre, contra) VALUES (?, ?)", 
                          (datos_usuario['nombre'], datos_usuario['contra']))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error as e:
            print(f"Error al registrar usuario: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def obtener_usuarios(self):
        """Obtiene la lista de usuarios registrados."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM users")
            usuarios = cursor.fetchall()
            return [usuario[0] for usuario in usuarios]
        except sqlite3.Error as e:
            print(f"Error al obtener los usuarios: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def guardar_usuario_actual(self, usuario):
        """Guarda el usuario actual en un archivo."""
        try:
            with open('usuario_actual.txt', 'w') as file:
                file.write(usuario)
            return True
        except Exception as e:
            print(f"Error al guardar usuario actual: {e}")
            return False
    
    def limpiar_usuario_actual(self):
        """Limpia el archivo de usuario actual."""
        try:
            with open('usuario_actual.txt', 'w') as file:
                file.write('')
            return True
        except Exception as e:
            print(f"Error al limpiar usuario actual: {e}")
            return False
        
    # --- AÑADE ESTE MÉTODO COMPLETO AL FINAL DE LA CLASE ---
    def obtener_usuario_actual(self):
        """
        Lee el nombre del usuario actual desde el archivo 'usuario_actual.txt'.
        """
        try:
            with open('usuario_actual.txt', 'r') as file:
                # .strip() elimina espacios en blanco o saltos de línea
                return file.read().strip()
        except FileNotFoundError:
            # Si el archivo no existe, no hay usuario logueado
            return None
        except Exception as e:
            print(f"Error al obtener usuario actual: {e}")
            return None