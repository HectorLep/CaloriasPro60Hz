import sqlite3

class DBManager:
    @staticmethod
    def conectar_usuario(usuario):
        """Conecta a la base de datos del usuario"""
        return sqlite3.connect(f"./users/{usuario}/alimentos.db")
    
    @staticmethod
    def conectar_principal():
        """Conecta a la base de datos principal de usuarios"""
        return sqlite3.connect("./usuarios.db")
        
    @staticmethod
    def ejecutar_query(conexion, query, params=(), fetch_all=False, commit=False):
        """Ejecuta una consulta en la base de datos"""
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
                
            return resultado
        except sqlite3.Error as e:
            # La clase no muestra pop-ups, solo imprime el error en la consola.
            # Esto es correcto y no depende de ninguna librería de UI.
            print(f"Error en la consulta: {e}")
            return None
        
    @staticmethod
    def cerrar_conexion(conexion):
        """Cierra la conexión a la base de datos"""
        if conexion:
            conexion.close()