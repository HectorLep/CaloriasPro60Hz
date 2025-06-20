from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMessageBox, QGridLayout,
                             QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QPixmap
import sqlite3
from datetime import datetime

# Importaciones adaptadas (asumiendo que tienes versiones PyQt6 de estos módulos)
# from View.Agregar_Recordatorio.agregar_recordatorio_pyqt6 import Agregar_Recordatorio
from model.salud.update_peso import Peso
# from Controller.Pulsaciones.Pulsaciones_pyqt6 import Pulsaciones
from model.salud.calculos import Calculo
# from Model.Salud.Progreso_pyqt6 import ProgresoSalud
from model.salud.GerminiChatWindow import GeminiChatWindow
from model.util.usuario_manager import UsuarioManager, BaseWidget
from model.salud.AguaManager import AguaManager,VasoAnimado

# Colores adaptados a PyQt6
class Colores:
    verde_boton = QColor(46, 204, 113)
    verde_oscuro = QColor(39, 174, 96)
    azul_medio_oscuro = QColor(52, 73, 94)
    segundo_label = QColor(149, 165, 166)
    riesgo_alto = QColor(231, 76, 60)
    riesgo_medio = QColor(241, 196, 15)
    riesgo_bajo = QColor(46, 204, 113)

class InfoButton(QPushButton):
    """Botón de información personalizado"""
    def __init__(self, text="?", parent=None):
        super().__init__(text, parent)
        self.setFixedSize(30, 30)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
        """)

class MetricFrame(QFrame):
    """Frame personalizado para mostrar métricas (IMC, TMB)"""
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setFixedSize(250, 80)
        self.setStyleSheet("""
            QFrame {
                background-color: #34495E;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        
        layout = QGridLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Título
        self.title_label = QLabel(f"{title}:")
        self.title_label.setStyleSheet("color: #95A5A6; font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title_label, 0, 0)
        
        # Resultado
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        layout.addWidget(self.result_label, 0, 1)
        
        # Mensaje/Categoría
        self.message_label = QLabel("")
        self.message_label.setStyleSheet("color: white; font-size: 11px;")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label, 1, 0, 1, 2)
        
        # Botón de información
        self.info_button = InfoButton()
        layout.addWidget(self.info_button, 0, 2)

class Salud(QWidget, BaseWidget):
    def __init__(self, parent=None, usuario=None): 
        QWidget.__init__(self, parent)  # Llama al constructor explícito de QWidget
        BaseWidget.__init__(self, parent=parent, usuario=usuario)  # Y luego el de BaseWidget

        if not usuario:
            usuario = UsuarioManager.obtener_usuario_actual()

        if not usuario:
            self.setup_error_ui("No se ha proporcionado un usuario válido.")
            return
        self.usuario = usuario
        self.sub = self  # Para mantener compatibilidad con el código original
        self.alerts_shown = False
        
        # Simulación de datos del usuario (reemplazar con tu lógica de base de datos)
        self.genero = "masculino"
        
        self.init_ui()
        self.setup_styles()
        self.actualizar_datos_usuario()
        self.update_health_metrics(show_alerts=False)
        self.obtener_datos_usuario_bd()
        
        # AGREGAR ESTAS LÍNEAS PARA INICIALIZAR EL AGUA MANAGER
        self.init_agua_manager()
        
        self.mostrar_mensaje_bienvenida()


    def init_agua_manager(self):
        """Inicializa el gestor de agua"""
        try:
            self.agua_manager = AguaManager(self.usuario)
            # Conectar la señal para actualizar estadísticas cuando cambie el consumo de agua
            self.agua_manager.agua_actualizada.connect(self.on_agua_actualizada)
            self.agua_manager.vasitos_mostrados()
        except Exception as e:
            print(f"Error al inicializar AguaManager: {e}")
            self.agua_manager = None

    # 4. AGREGAR ESTE MÉTODO PARA MANEJAR ACTUALIZACIONES DE AGUA
    def on_agua_actualizada(self, vasos_actuales, vasos_recomendados):
        """Callback cuando se actualiza el consumo de agua"""
        print(f"Agua actualizada: {vasos_actuales}/{vasos_recomendados} vasos")
        # Aquí puedes actualizar otros elementos de la UI que dependan del consumo de agua

    def init_ui(self):
            """Inicializa la interfaz de usuario"""
            self.setWindowTitle("Panel de Salud")
            self.setGeometry(100, 100, 900, 600)
            
            # Layout principal
            main_layout = QHBoxLayout(self)
            main_layout.setSpacing(20)
            main_layout.setContentsMargins(20, 20, 20, 20)
            
            # --- COLUMNA IZQUIERDA (BOTONES Y AHORA TAMBIÉN EL VASO) ---
            left_layout = QVBoxLayout()
            left_layout.setSpacing(15)
            
            # Botones
            self.btn_actualizar_peso = QPushButton("Actualizar Peso")
            self.btn_actualizar_peso.setFixedSize(250, 50)
            self.btn_actualizar_peso.clicked.connect(self.actualizar_peso)
            left_layout.addWidget(self.btn_actualizar_peso)
            
            self.btn_medir_pulsaciones = QPushButton("Medir pulsaciones")
            self.btn_medir_pulsaciones.setFixedSize(250, 50)
            self.btn_medir_pulsaciones.clicked.connect(self.pulsaciones)
            left_layout.addWidget(self.btn_medir_pulsaciones)
            
            self.btn_recordatorio = QPushButton("Añadir Recordatorio")
            self.btn_recordatorio.setFixedSize(250, 50)
            self.btn_recordatorio.clicked.connect(self.abrir_ventana_recordatorio)
            left_layout.addWidget(self.btn_recordatorio)
            
            self.btn_asistente_ia = QPushButton("🤖 Asistente IA")
            self.btn_asistente_ia.setFixedSize(250, 50)
            self.btn_asistente_ia.clicked.connect(self.abrir_asistente_ia)
            left_layout.addWidget(self.btn_asistente_ia)
            
            # --- CÓDIGO DEL PANEL DE AGUA (MOVIDO AQUÍ) ---
            agua_title = QLabel("💧 Hidratación Diaria")
            agua_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            agua_title.setStyleSheet("color: #3498DB; font-size: 18px; font-weight: bold; padding: 10px;")
            left_layout.addWidget(agua_title)
            
            self.agua_container = QFrame()
            self.agua_container.setFixedSize(300, 400)
            self.agua_container.setStyleSheet("background-color: #34495E; border-radius: 15px; padding: 10px;")
            left_layout.addWidget(self.agua_container)

            # Espaciador final para empujar todo lo de esta columna hacia arriba
            left_layout.addStretch()
            
            
            # --- COLUMNA DERECHA (MÉTRICAS Y GRÁFICOS) ---
            right_layout = QVBoxLayout()
            right_layout.setSpacing(15)
            right_layout.setContentsMargins(0, 0, 0, 0)
            
            # Botón de ayuda
            help_layout = QHBoxLayout()
            help_layout.addStretch()
            self.boton_ayuda = InfoButton("i")
            self.boton_ayuda.clicked.connect(self.mostrar_advertencia)
            help_layout.addWidget(self.boton_ayuda)
            right_layout.addLayout(help_layout)
            
            # Frames de métricas
            self.frame_imc = MetricFrame("IMC")
            self.frame_imc.info_button.clicked.connect(self.mostrar_info_imc)
            right_layout.addWidget(self.frame_imc)
            
            self.frame_tmb = MetricFrame("TMB")
            self.frame_tmb.info_button.clicked.connect(self.mostrar_info_tmb)
            right_layout.addWidget(self.frame_tmb)
            
            # Frame de progreso
            self.frame_graficos = QFrame()
            self.frame_graficos.setFixedSize(300, 200)
            self.frame_graficos.setStyleSheet("background-color: #34495E; border-radius: 10px;")
            
            graficos_layout = QVBoxLayout(self.frame_graficos)
            self.lbl_graficos = QLabel("Progreso de Salud")
            self.lbl_graficos.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lbl_graficos.setStyleSheet("color: white; font-weight: bold; font-size: 14px; margin: 10px;")
            graficos_layout.addWidget(self.lbl_graficos)
            
            right_layout.addWidget(self.frame_graficos)
            right_layout.addStretch()
            
            
            # --- AGREGAR LAS DOS COLUMNAS VISIBLES AL LAYOUT PRINCIPAL ---
            main_layout.addLayout(left_layout)
            main_layout.addStretch() # Este espaciador empuja todo lo que venga después
            main_layout.addLayout(right_layout)
            
    def init_agua_manager(self):
        """Inicializa el gestor de agua"""
        try:
            # Crear el AguaManager
            self.agua_manager = AguaManager(self.usuario)
            
            # Crear layout para el contenedor de agua
            agua_layout = QVBoxLayout(self.agua_container)
            agua_layout.setContentsMargins(5, 5, 5, 5)
            
            # Agregar el AguaManager al contenedor
            agua_layout.addWidget(self.agua_manager)
            
            # Conectar señales
            self.agua_manager.agua_actualizada.connect(self.on_agua_actualizada)
            
            # Cargar datos iniciales
            self.agua_manager.vasitos_mostrados()
            
            print("AguaManager inicializado correctamente")
            
        except Exception as e:
            print(f"Error al inicializar AguaManager: {e}")
            # Mostrar mensaje de error en el contenedor
            error_layout = QVBoxLayout(self.agua_container)
            error_label = QLabel("Error al cargar\ngestor de agua")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #E74C3C; font-size: 14px;")
            error_layout.addWidget(error_label)
            self.agua_manager = None

    def get_agua_stats(self):
        """Obtiene estadísticas del consumo de agua"""
        if self.agua_manager:
            return self.agua_manager.get_info_agua()
        return {'vasos_actuales': 0, 'vasos_recomendados': 8, 'porcentaje': 0}
        

    def setup_styles(self):
        """Configura los estilos de los botones y elementos"""
        button_style = """
            QPushButton {
                background-color: #2ECC71;
                color: #34495E;
                border: none;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """
        
        self.btn_actualizar_peso.setStyleSheet(button_style)
        self.btn_medir_pulsaciones.setStyleSheet(button_style)
        self.btn_recordatorio.setStyleSheet(button_style)
        
        # Estilo especial para el botón de IA
        ia_style = """
            QPushButton {
                background-color: #7C3AED;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5B21B6;
            }
        """
        self.btn_asistente_ia.setStyleSheet(ia_style)

    def actualizar_datos_usuario(self):
        """Obtiene los datos básicos del usuario de la base de datos"""
        try:
            # Aquí iría tu lógica de base de datos
            # self.genero = Calculo.get_user_gender(self.usuario)
            pass
        except:
            self.genero = "masculino"  # valor por defecto

    def obtener_datos_usuario_bd(self):
        """Obtiene los datos del usuario desde la base de datos"""
        try:
            from model.util.base import DBManager
            conn = DBManager.conectar_principal()
            
            # Adaptar esta query según tu estructura de base de datos de usuarios
            query = "SELECT genero, altura, edad FROM usuarios WHERE usuario = ?"
            resultado = DBManager.ejecutar_query(conn, query, (self.usuario,))
            
            if resultado:
                genero, altura, edad = resultado
                self.genero = genero
                self.altura = altura / 100 if altura > 10 else altura  # Convertir cm a m si es necesario
                self.edad = edad
                return True
            else:
                print(f"No se encontraron datos para el usuario: {self.usuario}")
                return False
                
        except Exception as e:
            print(f"Error al obtener datos del usuario: {e}")
            return False
        finally:
            if conn:
                DBManager.cerrar_conexion(conn)

    def mostrar_mensaje_bienvenida(self):
        """Muestra mensaje de bienvenida"""
        QTimer.singleShot(1000, lambda: self.mostrar_mensaje(
            "Esta es la pestaña de Salud, aquí podrás gestionar tu peso actual, "
            "medir tus pulsaciones, ver tu IMC (índice de masa corporal) al igual "
            "que tu TMB (tasa metabólica basal)", "Salud"))

    def mostrar_mensaje(self, mensaje, titulo):
        """Muestra un mensaje informativo"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()

    def mostrar_advertencia(self):
        """Muestra la advertencia de información de la pestaña"""
        self.mostrar_mensaje(
            "Esta es la pestaña de Salud, aquí podrás gestionar tu peso actual, "
            "medir tus pulsaciones, ver tu IMC (índice de masa corporal) al igual "
            "que tu TMB (tasa metabólica basal)", "Salud")

    def mostrar_info_imc(self):
        """Muestra información detallada sobre el IMC y recomendaciones"""
        imc = self.calcular_imc()
        if imc is not None:
            # categoria, _ = Calculo.evaluar_imc(imc)
            categoria = self.evaluar_imc_simple(imc)
            
            mensajes_recomendacion = {
                "Delgadez severa": "Es importante consultar a un profesional de la salud lo antes posible.",
                "Delgadez moderada": "Considera consultar a un nutricionista para mejorar tu alimentación.",
                "Delgadez leve": "Intenta aumentar el consumo de alimentos nutritivos.",
                "Peso normal": "¡Mantén tus hábitos saludables!",
                "Sobrepeso": "Considera incrementar tu actividad física y revisar tu alimentación.",
                "Obesidad grado I": "Es recomendable consultar con un profesional de la salud.",
                "Obesidad grado II": "Es importante buscar asesoría médica especializada.",
                "Obesidad grado III": "Se recomienda atención médica especializada."
            }
            
            recomendacion = mensajes_recomendacion.get(categoria, 
                "Consulta a un profesional de la salud para una evaluación personalizada.")
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Información sobre IMC")
            msg_box.setText(f"Tu IMC actual es {imc:.2f}, lo que indica: {categoria}\n\n"
                          f"Recomendación:\n{recomendacion}\n\n"
                          "Recuerda que el IMC es solo un indicador.")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
        else:
            self.mostrar_error("No se pudo calcular el IMC. Asegúrate de tener registrados tu peso y estatura.")

    def mostrar_info_tmb(self):
        """Muestra información detallada sobre la TMB y recomendaciones"""
        tmb = self.calcular_TMB()
        if tmb is not None:
            # categoria, _ = Calculo.evaluar_TMB(tmb, self.genero)
            categoria = self.evaluar_tmb_simple(tmb)
            
            mensajes_recomendacion = {
                "TMB baja": "Puede ser recomendable revisar tu alimentación.",
                "TMB normal-baja": "Tu metabolismo está en la parte baja del rango normal.",
                "TMB normal": "Tu metabolismo está en un rango saludable.",
                "TMB normal-alta": "Tu metabolismo es ligeramente elevado.",
                "TMB alta": "Tu metabolismo es más acelerado que el promedio."
            }
            
            recomendacion = mensajes_recomendacion.get(categoria, 
                "Consulta a un profesional de la salud para una evaluación personalizada.")
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Información sobre TMB")
            msg_box.setText(f"Tu Tasa Metabólica Basal es {int(tmb)} calorías/día\n\n"
                          f"Categoría: {categoria}\n\n"
                          f"Recomendación:\n{recomendacion}")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
        else:
            self.mostrar_error("No se pudo calcular la TMB.")

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Error")
        msg_box.setText(mensaje)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.exec()

    # DESPUÉS (código corregido):
    def abrir_asistente_ia(self):
        """Abre la ventana del chat con el asistente de IA"""
        try:
            # Creamos la ventana del chat como un atributo de la clase
            # para que no se cierre inmediatamente (persistencia).
            self.chat_window = GeminiChatWindow(usuario=self.usuario)
            self.chat_window.show()
        except Exception as e:
            self.mostrar_error(f"No se pudo abrir el asistente de IA: {str(e)}")

    def actualizar_peso(self):
        """Abre la ventana para actualizar peso"""
        def update_and_refresh():
            """Callback que se ejecuta después de actualizar el peso"""
            self.update_health_metrics(show_alerts=True)
            print("Métricas de salud actualizadas después de cambio de peso")
        
        try:
            # Crear y mostrar la ventana de actualización de peso
            peso_dialog = Peso(parent=self, usuario=self.usuario, callback=update_and_refresh)
            
            # Conectar la señal peso_actualizado para actualizar métricas
            peso_dialog.peso_actualizado.connect(lambda: self.update_health_metrics(show_alerts=True))
            
            # Ejecutar el diálogo
            result = peso_dialog.exec()
            
            if result == peso_dialog.DialogCode.Accepted:
                print("Peso actualizado exitosamente")
            
        except Exception as e:
            self.mostrar_error(f"Error al abrir ventana de actualización de peso: {str(e)}")
            print(f"Error detallado: {e}")
                        
    def pulsaciones(self):
        """Abre la ventana para medir pulsaciones"""
        try:
            # Pulsaciones(self.sub)
            self.mostrar_mensaje("Función de medición de pulsaciones en desarrollo", "Pulsaciones")
        except Exception as e:
            self.mostrar_error(f"Error al abrir ventana de pulsaciones: {str(e)}")

    def abrir_ventana_recordatorio(self):
        """Abre la ventana para agregar recordatorios"""
        try:
            # Agregar_Recordatorio(self.usuario)
            self.mostrar_mensaje("Función de recordatorios en desarrollo", "Recordatorios")
        except Exception as e:
            self.mostrar_error(f"Error al abrir ventana de recordatorios: {str(e)}")

    def update_health_metrics(self, show_alerts=True):
        """Actualiza las métricas de salud (IMC y TMB)"""
        try:
            imc = self.calcular_imc()
            tmb = self.calcular_TMB()

            # Actualizar IMC
            if imc is not None:
                categoria_imc = self.evaluar_imc_simple(imc)
                self.frame_imc.result_label.setText(f"{imc:.2f}")
                self.frame_imc.message_label.setText(categoria_imc)
                
                # Cambiar color según nivel de riesgo
                if imc < 16.5 or imc > 40:
                    color = "#E74C3C"  # riesgo alto
                    if show_alerts and not self.alerts_shown:
                        self.mostrar_alerta_imc(imc, categoria_imc)
                        self.alerts_shown = True
                elif imc < 18.5 or imc > 30:
                    color = "#F1C40F"  # riesgo medio
                else:
                    color = "#2ECC71"  # riesgo bajo
                
                self.frame_imc.result_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 16px;")
            else:
                self.frame_imc.result_label.setText("Sin datos")
                self.frame_imc.message_label.setText("Actualiza tu peso y estatura")

            # Actualizar TMB
            if tmb is not None:
                categoria_tmb = self.evaluar_tmb_simple(tmb)
                self.frame_tmb.result_label.setText(f"{int(tmb)}")
                self.frame_tmb.message_label.setText(categoria_tmb)
                
                # Cambiar color según nivel de riesgo
                if tmb < 1000:
                    color = "#E74C3C"  # riesgo alto
                    if show_alerts and not self.alerts_shown:
                        self.mostrar_alerta_tmb(tmb)
                        self.alerts_shown = True
                elif tmb < 1200 or tmb > 2500:
                    color = "#F1C40F"  # riesgo medio
                else:
                    color = "#2ECC71"  # riesgo bajo
                
                self.frame_tmb.result_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 16px;")
            else:
                self.frame_tmb.result_label.setText("Sin datos")
                self.frame_tmb.message_label.setText("Actualiza tus datos personales")
                
        except Exception as e:
            print(f"Error al actualizar métricas de salud: {e}")

    def mostrar_alerta_imc(self, imc, categoria):
        """Muestra alerta para IMC de riesgo"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("¡Alerta de salud!")
        msg_box.setText(f"Tu IMC de {imc:.2f} indica {categoria}, lo que puede "
                       "representar un riesgo significativo para tu salud. "
                       "Se recomienda consultar con un profesional médico.")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec()

    def mostrar_alerta_tmb(self, tmb):
        """Muestra alerta para TMB baja"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("¡Alerta de TMB baja!")
        msg_box.setText("Tu Tasa Metabólica Basal es inusualmente baja. "
                       "Esto podría indicar problemas de salud o datos incorrectos.")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec()

    def calcular_imc(self):
        """Calcula el IMC del usuario usando datos reales de la base de datos"""
        try:
            # Obtener peso actual de la base de datos
            conn = None
            try:
                from model.util.base import DBManager
                conn = DBManager.conectar_usuario(self.usuario)
                
                # Obtener el último peso registrado
                query_peso = "SELECT peso FROM peso ORDER BY num DESC LIMIT 1"
                resultado_peso = DBManager.ejecutar_query(conn, query_peso)
                
                if not resultado_peso:
                    print("No hay peso registrado")
                    return None
                
                peso = float(resultado_peso[0])
                
                # Obtener altura del perfil del usuario
                # Aquí necesitarías adaptar según tu estructura de base de datos
                # Por ahora uso un valor por defecto, pero deberías obtenerlo de la BD
                altura = 1.75  # metros - CAMBIAR POR QUERY A TU TABLA DE USUARIOS
                
                # Calcular IMC
                imc = peso / (altura ** 2)
                return imc
                
            finally:
                if conn:
                    DBManager.cerrar_conexion(conn)
                
        except Exception as e:
            print(f"Error al calcular IMC: {e}")
            return None


    def calcular_TMB(self):
        """Calcula la TMB del usuario usando datos reales de la base de datos"""
        try:
            # Obtener datos del usuario de la base de datos
            conn = None
            try:
                from model.util.base import DBManager
                conn = DBManager.conectar_usuario(self.usuario)
                
                # Obtener el último peso registrado
                query_peso = "SELECT peso FROM peso ORDER BY num DESC LIMIT 1"
                resultado_peso = DBManager.ejecutar_query(conn, query_peso)
                
                if not resultado_peso:
                    print("No hay peso registrado")
                    return None
                
                peso = float(resultado_peso[0])
                
                # Obtener otros datos del perfil del usuario
                # Estos valores deberían venir de tu tabla de usuarios/perfil
                altura = 175  # cm - CAMBIAR POR QUERY A TU TABLA DE USUARIOS
                edad = 30     # años - CAMBIAR POR QUERY A TU TABLA DE USUARIOS
                
                # Fórmula Harris-Benedict
                if self.genero.lower() == "masculino":
                    tmb = 88.362 + (13.397 * peso) + (4.799 * altura) - (5.677 * edad)
                else:
                    tmb = 447.593 + (9.247 * peso) + (3.098 * altura) - (4.330 * edad)
                
                return tmb
                
            finally:
                if conn:
                    DBManager.cerrar_conexion(conn)
                
        except Exception as e:
            print(f"Error al calcular TMB: {e}")
            return None


    def evaluar_imc_simple(self, imc):
        """Evaluación simple del IMC"""
        if imc < 16:
            return "Delgadez severa"
        elif imc < 17:
            return "Delgadez moderada"
        elif imc < 18.5:
            return "Delgadez leve"
        elif imc < 25:
            return "Peso normal"
        elif imc < 30:
            return "Sobrepeso"
        elif imc < 35:
            return "Obesidad grado I"
        elif imc < 40:
            return "Obesidad grado II"
        else:
            return "Obesidad grado III"

    def evaluar_tmb_simple(self, tmb):
        """Evaluación simple de la TMB"""
        if tmb < 1000:
            return "TMB muy baja"
        elif tmb < 1200:
            return "TMB baja"
        elif tmb < 1600:
            return "TMB normal-baja"
        elif tmb < 2000:
            return "TMB normal"
        elif tmb < 2500:
            return "TMB normal-alta"
        else:
            return "TMB alta"

# Ejemplo de uso
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Estilo moderno
    
    # Aplicar tema oscuro
    app.setStyleSheet("""
        QWidget {
            background-color: #2C3E50;
            color: white;
        }
        QMessageBox {
            background-color: #34495E;
        }
    """)
    
    window = Salud(usuario="test_user")
    window.show()
    
    sys.exit(app.exec())