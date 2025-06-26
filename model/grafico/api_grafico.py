import sqlite3
import os
from datetime import date, timedelta, datetime

class APICaloriesDataManager:
    def __init__(self):
        self.db_path = "alimentos_app.db"  

    def _get_start_date(self, period: str) -> str:
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

    def get_calories_data(self, period: str):
        if not os.path.exists(self.db_path):
            print(f"No se encuentra {self.db_path}")
            return [], []

        start_date = self._get_start_date(period)
        end_date = date.today().strftime("%Y-%m-%d")

        query = """
            SELECT 
                fecha, 
                SUM(total_cal) as total_calorias 
            FROM consumo_diario 
            WHERE fecha BETWEEN ? AND ?
            GROUP BY fecha
            ORDER BY fecha ASC
        """

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (start_date, end_date))
            results = cursor.fetchall()

        if not results:
            return [], []

        labels = [datetime.strptime(row[0], "%Y-%m-%d").strftime("%d/%m") for row in results]
        data = [row[1] for row in results]

        return labels, data
