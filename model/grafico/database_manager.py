import sqlite3
import os
from datetime import datetime, date, timedelta

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

    def _get_start_date(self, period: str) -> str:
        """
        Calcula la fecha de inicio basado en el período seleccionado.
        """
        today = date.today()

        if period == "Última semana":
            start_date = today - timedelta(days=7)
        elif period == "Último mes":
            start_date = today - timedelta(days=30)
        elif period == "Últimos 3 meses":
            start_date = today - timedelta(days=90)
        elif period == "Último año":
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=30)

        return start_date.strftime("%Y-%m-%d")

    def _execute_query(self, query: str, params: tuple):
        """Ejecuta una consulta y devuelve todos los resultados."""
        if not os.path.exists(self.db_path):
            print(f"Error: No se encontró la base de datos en la ruta: {self.db_path}")
            return []
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error en la base de datos '{self.db_path}': {e}")
            return []

    def _get_aggregated_data(self, table_name: str, value_column: str, aggregation_func: str, period: str) -> tuple[list, list]:
        """
        Función genérica y robusta para obtener datos agregados, filtrando correctamente por fecha.
        """
        start_date = self._get_start_date(period)
        end_date = date.today().strftime("%Y-%m-%d")

        # Formateamos fecha como DATE real para comparación precisa
        reformatted_date = "DATE(SUBSTR(fecha, 7, 4) || '-' || SUBSTR(fecha, 4, 2) || '-' || SUBSTR(fecha, 1, 2))"

        query = f"""
            SELECT 
                {reformatted_date}, 
                {aggregation_func}({value_column}) 
            FROM {table_name}
            WHERE {reformatted_date} >= ? AND {reformatted_date} <= ?
            GROUP BY {reformatted_date}
            ORDER BY {reformatted_date} ASC
        """

        results = self._execute_query(query, (start_date, end_date))

        if not results:
            return [], []

        labels = [datetime.strptime(row[0], "%Y-%m-%d").strftime("%d/%m") for row in results]
        data = [row[1] for row in results]

        return labels, data

    '''funcion en caso de ya no usar api_grafico.py (es decir ya no usar la base de datos de la api para el total calorias)'''
    #def get_calories_data(self, period: str) -> tuple[list, list]:         
        #return self._get_aggregated_data("consumo_diario", "total_cal", "SUM", period)

    def get_water_data(self, period: str) -> tuple[list, list]:
        return self._get_aggregated_data("agua", "cant", "SUM", period)

    def get_weight_data(self, period: str) -> tuple[list, list]:
        return self._get_aggregated_data("peso", "peso", "AVG", period)
