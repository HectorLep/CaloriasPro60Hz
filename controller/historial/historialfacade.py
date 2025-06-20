from model.util.base import DBManager
from typing import List, Tuple
from datetime import datetime

class HistorialFacade: 
    def __init__(self, usuario: str):
        self.usuario = usuario
        self._connection = None
    
    def _get_connection(self):
        """Obtener conexión a la base de datos"""
        if not self._connection:
            self._connection = DBManager.conectar_usuario(self.usuario)
        return self._connection
    
    def _close_connection(self):
        """Cerrar conexión a la base de datos"""
        if self._connection:
            DBManager.cerrar_conexion(self._connection)
            self._connection = None
    
    def obtener_todos_los_registros(self) -> List[Tuple]:
        """Obtener todos los registros del historial"""
        conn = self._get_connection()
        
        query = """
            SELECT c.nombre,
                CASE 
                    WHEN a.calorias_porcion IS NOT NULL THEN 'Porción'
                    ELSE '100gr'
                END AS tipo_caloria,
                c.cantidad,
                c.total_cal,
                c.fecha,
                c.hora,
                CASE 
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 6 AND 10 THEN 'Desayuno'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 11 AND 11 THEN 'Media mañana'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 12 AND 15 THEN 'Almuerzo'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 16 AND 17 THEN 'Merienda'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 18 AND 22 THEN 'Cena'
                    ELSE 'Otro'
                END AS momento_dia
            FROM consumo_diario c
            JOIN alimento a ON c.nombre = a.nombre
            ORDER BY date(substr(c.fecha, 7, 4) || '-' || substr(c.fecha, 4, 2) || '-' || substr(c.fecha, 1, 2)) DESC,
                     time(c.hora) DESC
        """
        
        registros = DBManager.ejecutar_query(conn, query, fetch_all=True)
        
        registros_formateados = []
        if registros:
            for registro in registros:
                cantidad = f"{registro[2]} Gr" if registro[1] == '100gr' else str(registro[2])
                registros_formateados.append((
                    registro[0],  # nombre
                    registro[1],  # tipo_caloria
                    cantidad,     # cantidad formateada
                    registro[3],  # total_cal
                    registro[4],  # fecha
                    registro[5],  # hora
                    registro[6]   # momento_dia
                ))
        
        return registros_formateados
    
    def obtener_registros_por_fecha(self, fecha: str) -> List[Tuple]:
        """Obtener registros para una fecha específica"""
        conn = self._get_connection()
        
        query = """
            SELECT 
                a.nombre,
                CASE 
                    WHEN a.calorias_porcion IS NOT NULL THEN 'Porción'
                    ELSE '100gr'
                END AS tipo_caloria,
                c.cantidad,
                c.total_cal,
                c.fecha,
                c.hora,
                CASE 
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 6 AND 10 THEN 'Desayuno'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 11 AND 11 THEN 'Media mañana'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 12 AND 15 THEN 'Almuerzo'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 16 AND 17 THEN 'Merienda'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 18 AND 22 THEN 'Cena'
                    ELSE 'Otro'
                END AS momento_dia
            FROM consumo_diario c
            JOIN alimento a ON c.nombre = a.nombre
            WHERE strftime('%Y-%m-%d', substr(c.fecha, 7, 4) || '-' || substr(c.fecha, 4, 2) || '-' || substr(c.fecha, 1, 2)) = ?
            ORDER BY time(c.hora) DESC
        """
        
        registros = DBManager.ejecutar_query(conn, query, params=(fecha,), fetch_all=True)
        
        registros_formateados = []
        if registros:
            for registro in registros:
                cantidad = f"{registro[2]} Gr" if registro[1] == '100gr' else str(registro[2])
                registros_formateados.append((
                    registro[0],  # nombre
                    registro[1],  # tipo_caloria
                    cantidad,     # cantidad formateada
                    registro[3],  # total_cal
                    registro[4],  # fecha
                    registro[5],  # hora
                    registro[6]   # momento_dia
                ))
        
        return registros_formateados
    
    def obtener_registros_por_rango_fecha(self, fecha_inicio: str, fecha_fin: str) -> List[Tuple]:
        """Obtener registros para un rango de fechas"""
        conn = self._get_connection()
        
        query = """
            SELECT 
                a.nombre,
                CASE 
                    WHEN a.calorias_porcion IS NOT NULL THEN 'Porción'
                    ELSE '100gr'
                END AS tipo_caloria,
                c.cantidad,
                c.total_cal,
                c.fecha,
                c.hora,
                CASE 
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 6 AND 10 THEN 'Desayuno'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 11 AND 11 THEN 'Media mañana'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 12 AND 15 THEN 'Almuerzo'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 16 AND 17 THEN 'Merienda'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 18 AND 22 THEN 'Cena'
                    ELSE 'Otro'
                END AS momento_dia
            FROM consumo_diario c
            JOIN alimento a ON c.nombre = a.nombre
            WHERE strftime('%Y-%m-%d', substr(c.fecha, 7, 4) || '-' || substr(c.fecha, 4, 2) || '-' || substr(c.fecha, 1, 2)) 
                  BETWEEN ? AND ?
            ORDER BY date(substr(c.fecha, 7, 4) || '-' || substr(c.fecha, 4, 2) || '-' || substr(c.fecha, 1, 2)) DESC,
                     time(c.hora) DESC
        """
        
        registros = DBManager.ejecutar_query(conn, query, params=(fecha_inicio, fecha_fin), fetch_all=True)
        
        registros_formateados = []
        if registros:
            for registro in registros:
                cantidad = f"{registro[2]} Gr" if registro[1] == '100gr' else str(registro[2])
                registros_formateados.append((
                    registro[0],  # nombre
                    registro[1],  # tipo_caloria
                    cantidad,     # cantidad formateada
                    registro[3],  # total_cal
                    registro[4],  # fecha
                    registro[5],  # hora
                    registro[6]   # momento_dia
                ))
        
        return registros_formateados
    
    def obtener_registros_por_nombre_alimento(self, nombre_alimento: str) -> List[Tuple]:
        """Buscar registros por nombre de alimento"""
        conn = self._get_connection()
        
        query = """
            SELECT 
                a.nombre,
                CASE 
                    WHEN a.calorias_porcion IS NOT NULL THEN 'Porción'
                    ELSE '100gr'
                END AS tipo_caloria,
                c.cantidad,
                c.total_cal,
                c.fecha,
                c.hora,
                CASE 
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 6 AND 10 THEN 'Desayuno'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 11 AND 11 THEN 'Media mañana'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 12 AND 15 THEN 'Almuerzo'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 16 AND 17 THEN 'Merienda'
                    WHEN CAST(substr(c.hora, 1, 2) AS INTEGER) BETWEEN 18 AND 22 THEN 'Cena'
                    ELSE 'Otro'
                END AS momento_dia
            FROM consumo_diario c
            JOIN alimento a ON c.nombre = a.nombre
            WHERE LOWER(a.nombre) LIKE LOWER(?)
            ORDER BY date(substr(c.fecha, 7, 4) || '-' || substr(c.fecha, 4, 2) || '-' || substr(c.fecha, 1, 2)) DESC,
                     time(c.hora) DESC
        """
        
        registros = DBManager.ejecutar_query(conn, query, params=(f'%{nombre_alimento}%',), fetch_all=True)
        
        registros_formateados = []
        if registros:
            for registro in registros:
                cantidad = f"{registro[2]} Gr" if registro[1] == '100gr' else str(registro[2])
                registros_formateados.append((
                    registro[0],  # nombre
                    registro[1],  # tipo_caloria
                    cantidad,     # cantidad formateada
                    registro[3],  # total_cal
                    registro[4],  # fecha
                    registro[5],  # hora
                    registro[6]   # momento_dia
                ))
        
        return registros_formateados
    
    def obtener_registros_por_momento_dia(self, momento_dia: str) -> List[Tuple]:
        """Filtrar registros por momento del día"""
        registros_completos = self.obtener_todos_los_registros()
        
        if momento_dia == "Todos":
            return registros_completos
        
        registros_filtrados = []
        for registro in registros_completos:
            if len(registro) > 6 and registro[6] == momento_dia:
                registros_filtrados.append(registro)
        
        return registros_filtrados
    
    def obtener_estadisticas_fecha(self, fecha: str) -> dict:
        """Obtener estadísticas para una fecha específica"""
        registros = self.obtener_registros_por_fecha(fecha)
        
        total_calorias = sum(float(registro[3]) for registro in registros)
        total_alimentos = len(registros)
        
        return {
            'total_calorias': total_calorias,
            'total_alimentos': total_alimentos,
            'promedio_calorias': total_calorias / total_alimentos if total_alimentos > 0 else 0
        }
    
    def obtener_estadisticas_rango_fechas(self, fecha_inicio: str, fecha_fin: str) -> dict:
        """Obtener estadísticas para un rango de fechas"""
        registros = self.obtener_registros_por_rango_fecha(fecha_inicio, fecha_fin)
        
        if not registros:
            return {
                'total_calorias': 0,
                'total_alimentos': 0,
                'promedio_diario': 0,
                'dias_con_registros': 0
            }
        
        total_calorias = sum(float(registro[3]) for registro in registros)
        total_alimentos = len(registros)
        
        # Calcular días únicos
        fechas_unicas = set(registro[4] for registro in registros)
        dias_con_registros = len(fechas_unicas)
        
        # Calcular días totales en el rango
        fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
        dias_totales = (fecha_fin_dt - fecha_inicio_dt).days + 1
        
        return {
            'total_calorias': total_calorias,
            'total_alimentos': total_alimentos,
            'promedio_diario': total_calorias / dias_con_registros if dias_con_registros > 0 else 0,
            'dias_con_registros': dias_con_registros,
            'dias_totales': dias_totales
        }
    
    def obtener_alimentos_mas_consumidos(self, limite: int = 10) -> List[Tuple]:
        """Obtener los alimentos más consumidos"""
        conn = self._get_connection()
        
        query = """
            SELECT c.nombre, COUNT(*) as frecuencia, SUM(c.total_cal) as total_calorias
            FROM consumo_diario c
            GROUP BY c.nombre
            ORDER BY frecuencia DESC, total_calorias DESC
            LIMIT ?
        """
        
        return DBManager.ejecutar_query(conn, query, params=(limite,), fetch_all=True)
    
    def obtener_consumo_por_momento_dia(self) -> List[Tuple]:
        """Obtener estadísticas de consumo por momento del día"""
        registros = self.obtener_todos_los_registros()
        
        estadisticas_momento = {}
        for registro in registros:
            if len(registro) > 6:
                momento = registro[6]
                calorias = float(registro[3])
                
                if momento not in estadisticas_momento:
                    estadisticas_momento[momento] = {'count': 0, 'total_calorias': 0}
                
                estadisticas_momento[momento]['count'] += 1
                estadisticas_momento[momento]['total_calorias'] += calorias
        
        # Convertir a lista de tuplas
        resultado = []
        for momento, stats in estadisticas_momento.items():
            promedio = stats['total_calorias'] / stats['count'] if stats['count'] > 0 else 0
            resultado.append((momento, stats['count'], stats['total_calorias'], promedio))
        
        # Ordenar por total de calorías descendente
        resultado.sort(key=lambda x: x[2], reverse=True)
        
        return resultado
    
    def cleanup(self):
        """Limpiar recursos y cerrar conexiones"""
        self._close_connection()