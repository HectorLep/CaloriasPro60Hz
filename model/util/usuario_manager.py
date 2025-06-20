# model/util/usuario_manager.py
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox

class UsuarioManager:
    """Clase para manejar la gestión de usuarios y mensajes en PyQt6"""
    
    @staticmethod
    def obtener_usuario_actual():
        """Obtiene el usuario actual desde el archivo de configuración"""
        try:
            if os.path.exists('usuario_actual.txt'):
                with open('usuario_actual.txt', 'r') as file:
                    usuario = file.readline().strip()
                    return usuario if usuario else None
            return None
        except Exception as e:
            print(f"Error al obtener usuario actual: {e}")
            return None
    
    @staticmethod
    def establecer_usuario_actual(usuario):
        """Establece el usuario actual en el archivo de configuración"""
        try:
            with open('usuario_actual.txt', 'w') as file:
                file.write(usuario)
            return True
        except Exception as e:
            print(f"Error al establecer usuario actual: {e}")
            return False
    
    @staticmethod
    def conectar_bd_usuario(usuario):
        """Conecta a la base de datos específica del usuario"""
        try:
            db_path = f"./users/{usuario}/alimentos.db"
            if not os.path.exists(db_path):
                # Crear directorio si no existe
                os.makedirs(f"./users/{usuario}", exist_ok=True)
                conn = sqlite3.connect(db_path)
                UsuarioManager._crear_tablas_iniciales(conn, usuario)
            else:
                conn = sqlite3.connect(db_path)
            return conn
        except Exception as e:
            print(f"Error al conectar a BD del usuario {usuario}: {e}")
            return None
    
    @staticmethod
    def _crear_tablas_iniciales(conn, usuario):
        """Crea las tablas iniciales necesarias para un nuevo usuario"""
        cursor = conn.cursor()
        try:
            # Tabla de mensajes para controlar qué mensajes se han mostrado
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY,
                    salud INTEGER DEFAULT 1,
                    peso INTEGER DEFAULT 1,
                    pulsaciones INTEGER DEFAULT 1,
                    recordatorios INTEGER DEFAULT 1,
                    agua INTEGER DEFAULT 1
                )
            ''')
            
            # Tabla de peso
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS peso (
                    num INTEGER PRIMARY KEY AUTOINCREMENT,
                    peso REAL NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insertar registro inicial en mensajes
            cursor.execute('INSERT OR IGNORE INTO mensajes (id) VALUES (1)')
            
            conn.commit()
            print(f"Tablas iniciales creadas para usuario: {usuario}")
            
        except Exception as e:
            print(f"Error al crear tablas iniciales: {e}")
    
    @staticmethod
    def mostrar_mensaje_una_vez(parent, nombre_ventana, mensaje, titulo):
        """
        Muestra un mensaje solo una vez por sesión/usuario
        
        Args:
            parent: Widget padre para el mensaje
            nombre_ventana: Nombre de la ventana/módulo (columna en tabla mensajes)
            mensaje: Texto del mensaje
            titulo: Título del mensaje
        """
        usuario = UsuarioManager.obtener_usuario_actual()
        if not usuario:
            return
        
        conn = UsuarioManager.conectar_bd_usuario(usuario)
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Verificar si existe la columna
            cursor.execute("PRAGMA table_info(mensajes)")
            columnas = [col[1] for col in cursor.fetchall()]
            
            if nombre_ventana not in columnas:
                # Agregar columna si no existe
                cursor.execute(f"ALTER TABLE mensajes ADD COLUMN {nombre_ventana} INTEGER DEFAULT 1")
                conn.commit()
            
            # Verificar si el mensaje debe mostrarse
            cursor.execute(f"SELECT {nombre_ventana} FROM mensajes WHERE id = 1")
            resultado = cursor.fetchone()
            
            if resultado and resultado[0] == 1:
                # Mostrar mensaje
                msg_box = QMessageBox(parent)
                msg_box.setWindowTitle(titulo)
                msg_box.setText(mensaje)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.exec()
                
                # Marcar como mostrado
                cursor.execute(f"UPDATE mensajes SET {nombre_ventana} = 0 WHERE id = 1")
                conn.commit()
                
        except Exception as e:
            print(f"Error al manejar mensaje: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def resetear_mensajes(usuario=None):
        """Resetea todos los mensajes para que se vuelvan a mostrar"""
        if not usuario:
            usuario = UsuarioManager.obtener_usuario_actual()
        
        if not usuario:
            return False
        
        conn = UsuarioManager.conectar_bd_usuario(usuario)
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE mensajes SET salud = 1, peso = 1, pulsaciones = 1, recordatorios = 1, agua = 1 WHERE id = 1")
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al resetear mensajes: {e}")
            return False
        finally:
            conn.close()

class BaseWidget:
    """Clase base para widgets que necesitan acceso a usuario y mensajes"""
    
    def __init__(self, parent=None, usuario=None):
        self.parent = parent
        self.usuario = usuario if usuario else UsuarioManager.obtener_usuario_actual()
        
        if not self.usuario:
            raise ValueError("No se ha proporcionado un usuario válido y no hay usuario actual configurado")
    
    def mostrar_mensaje_bienvenida(self, nombre_modulo, mensaje, titulo="Información"):
        """Muestra mensaje de bienvenida del módulo una sola vez"""
        UsuarioManager.mostrar_mensaje_una_vez(
            self.parent, 
            nombre_modulo, 
            mensaje, 
            titulo
        )
    
    def conectar_bd_usuario(self):
        """Conecta a la base de datos del usuario actual"""
        return UsuarioManager.conectar_bd_usuario(self.usuario)
    
    def mostrar_error(self, mensaje, titulo="Error"):
        """Muestra un mensaje de error"""
        if hasattr(self, 'parent') and self.parent:
            parent = self.parent
        else:
            parent = None
            
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.exec()
    
    def mostrar_info(self, mensaje, titulo="Información"):
        """Muestra un mensaje informativo"""
        if hasattr(self, 'parent') and self.parent:
            parent = self.parent
        else:
            parent = None
            
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()