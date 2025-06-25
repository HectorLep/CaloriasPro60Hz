import sqlite3
import os
from datetime import datetime, timedelta

class ChartDataManager:
    """
    Se encarga de obtener y procesar los datos para los gráficos
    de la base de datos específica de un usuario.
    """
    def __init__(self, username: str):
        if not username:
            raise ValueError("El nombre de usuario no puede estar vacío.")
        
        self.username = username
        self.db_path = os.path.join("users", self.username, "alimentos.db")
        
        # --- PRINT DE DIAGNÓSTICO 1 ---
        print(f"✔️ [ChartDataManager inicializado] Usuario: '{self.username}'")
        print(f"    Ruta de la BD que se usará: '{self.db_path}'")
        # --------------------------------

    def _get_start_date(self, period: str) -> str:
        """Calcula la fecha de inicio en formato YYYY-MM-DD."""
        today = datetime.now()
        if period == "Última semana":
            start_date = today - timedelta(days=7)
        elif period == "Último mes":
            start_date = today - timedelta(days=30)
        elif period == "Últimos 3 meses":
            start_date = today - timedelta(days=90)
        elif period == "Último año":
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=7)
        
        return start_date.strftime("%Y-%m-%d")

    def _execute_query(self, query: str, params: tuple):
        """Ejecuta una consulta y devuelve todos los resultados."""
        if not os.path.exists(self.db_path):
            # --- PRINT DE DIAGNÓSTICO 2 (Error) ---
            print(f"❌ ¡ERROR! No se encontró la base de datos en la ruta: {self.db_path}")
            # --------------------------------------
            return []
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()
                # --- PRINT DE DIAGNÓSTICO 3 ---
                print(f"   Resultados crudos de la BD: {results}")
                # --------------------------------
                return results
        except sqlite3.Error as e:
            print(f"❌ ¡ERROR de Base de Datos! en '{self.db_path}': {e}")
            return []

    def _get_query_results(self, table_name, value_column, period):
        """Función genérica para construir y ejecutar la consulta corregida."""
        start_date = self._get_start_date(period)

        # --- CORRECCIÓN CLAVE EN LA CONSULTA ---
        # Reconstruimos la fecha 'DD-MM-YYYY' a 'YYYY-MM-DD' usando SUBSTR
        # para que SQLite pueda compararla correctamente.
        reformatted_date = "SUBSTR(fecha, 7, 4) || '-' || SUBSTR(fecha, 4, 2) || '-' || SUBSTR(fecha, 1, 2)"
        
        query = f"""
            SELECT {reformatted_date}, SUM({value_column}) 
            FROM {table_name}
            WHERE {reformatted_date} >= ?
            GROUP BY {reformatted_date}
            ORDER BY {reformatted_date} ASC
        """
        
        # --- PRINT DE DIAGNÓSTICO 4 ---
        print(f"   Ejecutando consulta para '{table_name}' con fecha de inicio: {start_date}")
        # --------------------------------
        
        results = self._execute_query(query, (start_date,))
        
        if not results:
            return [], []

        # El formato de fecha de la consulta ya es YYYY-MM-DD, por lo que el parseo es directo
        labels = [datetime.strptime(row[0], "%Y-%m-%d").strftime("%d/%m") for row in results]
        data = [row[1] for row in results]
        
        return labels, data

    def get_calories_data(self, period: str) -> tuple[list, list]:
        return self._get_query_results("consumo_diario", "total_cal", period)

    def get_water_data(self, period: str) -> tuple[list, list]:
        return self._get_query_results("agua", "cant", period)

    def get_weight_data(self, period: str) -> tuple[list, list]:
        # Para el peso, usamos AVG en lugar de SUM
        start_date = self._get_start_date(period)
        reformatted_date = "SUBSTR(fecha, 7, 4) || '-' || SUBSTR(fecha, 4, 2) || '-' || SUBSTR(fecha, 1, 2)"
        query = f"""
            SELECT {reformatted_date}, AVG(peso) 
            FROM peso
            WHERE {reformatted_date} >= ?
            GROUP BY {reformatted_date}
            ORDER BY {reformatted_date} ASC
        """
        print(f"   Ejecutando consulta para 'peso' con fecha de inicio: {start_date}")
        results = self._execute_query(query, (start_date,))
        if not results:
            return [], []
        labels = [datetime.strptime(row[0], "%Y-%m-%d").strftime("%d/%m") for row in results]
        data = [row[1] for row in results]
        return labels, data