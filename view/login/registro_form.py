import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
                             QComboBox, QFrame, QScrollArea, QDateEdit, QMessageBox)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from model.login.user_validator import UserValidator
from model.login.auth_service import IAuthService
from model.login.user_database import UserDatabase
from model.util.colores import *
from .form import *

class RegistroForm(IForm, QWidget):

    volver_clicked = pyqtSignal()

    def __init__(self, ventana_principal, auth_service: IAuthService, on_success, on_back):
        super().__init__()
        self.ventana_principal = ventana_principal
        self.auth_service = auth_service
        self.on_success = on_success
        self.on_back = on_back
        self.widgets = {}
        self.user_database = UserDatabase()
        self.validator = UserValidator()
        self.init_ui()
        
    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Frame contenedor, usando tu color `gris`
        self.frame = QFrame()
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: {gris};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        self.frame.setFixedSize(450, 620)

        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setSpacing(15)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título
        titulo = QLabel("Crear una Cuenta")
        titulo.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        # Usando un color de texto blanco para que resalte sobre el fondo `gris`
        titulo.setStyleSheet(f"color: {color_texto_blanco}; margin-bottom: 5px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(titulo)

        # Área de scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {azul_medio_oscuro}; /* Tu color oscuro para el fondo del scroll */
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {verde_boton}; /* Tu color verde para la manija del scroll */
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
                border: none;
            }}
        """)

        # Widget contenedor del scroll
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(5, 0, 5, 0)

        # Estilos basados en tu paleta
        label_style = f"""
            QLabel {{
                background-color: {azul_medio_oscuro}; /* Tu color oscuro para el fondo de las etiquetas */
                color: {color_texto_blanco}; /* Texto blanco para contraste */
                font: bold 13px Arial;
                border-radius: 15px;
                padding: 8px;
                min-height: 20px;
            }}
        """

        input_style = f"""
            QLineEdit, QComboBox, QDateEdit {{
                background-color: {color_entry}; /* Tu color para los campos de entrada */
                color: {negro_texto}; /* Tu color de texto para las entradas */
                border-radius: 15px;
                padding: 8px 12px;
                font: 13px Arial;
                min-height: 20px;
            }}
            QComboBox::drop-down {{
                background-color: {celeste_pero_oscuro}; /* Tu color para el desplegable */
                border-top-right-radius: 15px;
                border-bottom-right-radius: 15px;
                width: 25px;
            }}
        """

        # --- Campos del formulario (sin cambios en la lógica, solo en el estilo) ---
        campos = {
            "Nombre": ("nombre_entry", QLineEdit(), "Introduce tu nombre"),
            "Contraseña": ("contra_entry", QLineEdit(), "Crea una contraseña segura"),
            "Sexo": ("gen_combobox", QComboBox(), None),
            "Peso (kg)": ("peso_entry", QLineEdit(), "Tu peso actual en kilogramos"),
            "Altura (cm)": ("altura_entry", QLineEdit(), "Tu altura en centímetros"),
            "Meta de calorías diaria": ("meta_entry", QLineEdit(), "Ej: 2000 kcal"),
            "Nivel de Actividad": ("lvl_actividad_combobox", QComboBox(), None),
            "Fecha de Nacimiento": ("fecha_nacimiento_entry", QDateEdit(), None)
        }

        for label_text, (widget_name, widget_instance, placeholder) in campos.items():
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            scroll_layout.addWidget(label)

            self.widgets[widget_name] = widget_instance
            widget_instance.setStyleSheet(input_style)

            if isinstance(widget_instance, QLineEdit):
                widget_instance.setPlaceholderText(placeholder)
            if widget_name == "contra_entry":
                widget_instance.setEchoMode(QLineEdit.EchoMode.Password)
            if widget_name == "gen_combobox":
                widget_instance.addItems(["Masculino", "Femenino"])
            if widget_name == "lvl_actividad_combobox":
                widget_instance.addItems(["Sedentario", "Ligero", "Moderado", "Intenso"])
            if isinstance(widget_instance, QDateEdit):
                    widget_instance.setCalendarPopup(True)
                    widget_instance.setDate(QDate.currentDate().addYears(-25))
                    min_date = QDate.currentDate().addYears(-120)
                    max_date = QDate.currentDate().addYears(-13)
                    widget_instance.setDateRange(min_date, max_date)
                    widget_instance.setDisplayFormat("dd/MM/yyyy")

            scroll_layout.addWidget(widget_instance)

        scroll_area.setWidget(scroll_widget)
        frame_layout.addWidget(scroll_area)

        # Botones usando tus variables `verde_boton`, `riesgo_medio` etc.
        self.widgets['guardar_button'] = QPushButton("Crear Cuenta")
        self.widgets['guardar_button'].setStyleSheet(f"""
            QPushButton {{
                background-color: {verde_boton};
                color: {color_texto_blanco};
                border: none;
                border-radius: 15px;
                font: bold 14px Arial;
                padding: 12px;
            }}
            QPushButton:hover {{ background-color: {verde_oscuro}; }}
        """)
        self.widgets['guardar_button'].clicked.connect(self._guardar)
        frame_layout.addWidget(self.widgets['guardar_button'])

        self.widgets['btn_volver'] = QPushButton('Volver Atrás')
        self.widgets['btn_volver'].setStyleSheet(f"""
            QPushButton {{
                background-color: {riesgo_medio};
                color: {color_texto_blanco};
                border: none;
                border-radius: 15px;
                font: bold 14px Arial;
                padding: 12px;
            }}
            QPushButton:hover {{ background-color: {riesgo_alto}; }}
        """)
        self.widgets['btn_volver'].clicked.connect(self._volver_atras)
        frame_layout.addWidget(self.widgets['btn_volver'])

        main_layout.addWidget(self.frame)
            
    def mostrar(self):
        self.show()
    
    def ocultar(self):
        self.hide()
    
    def _volver_atras(self):
        self.volver_clicked.emit()

    def _verificar_usuario_existente(self, nombre):
        """Verifica si el usuario ya existe usando el auth_service"""
        try:
            usuarios_existentes = self.auth_service.obtener_usuarios()
            return nombre in usuarios_existentes
        except Exception as e:
            print(f"Error al verificar usuario existente: {e}")
            return True # Asumir que existe para prevenir errores

    def _guardar(self):
        # Validar nombre
        nombre = self.widgets['nombre_entry'].text()
        valid_nombre, msg_nombre = UserValidator.validar_nombre(nombre)
        if not valid_nombre:
            QMessageBox.warning(self, "Advertencia", msg_nombre)
            return
        
        # Verificar si el usuario ya existe usando auth_service
        if self._verificar_usuario_existente(nombre):
            QMessageBox.warning(self, "Advertencia", "Este nombre de usuario no está disponible.")
            return
        
        # Validar contraseña
        contra = self.widgets['contra_entry'].text()
        valid_contra, msg_contra = UserValidator.validar_contraseña(contra, nombre)
        if not valid_contra:
            QMessageBox.warning(self, "Advertencia", msg_contra)
            return
        
        # Validar fecha de nacimiento
        fecha_qdate = self.widgets['fecha_nacimiento_entry'].date()
        fecha_str = fecha_qdate.toString("dd-MM-yyyy")
        valid_fecha, resultado_fecha = UserValidator.validar_fecha_nacimiento(fecha_str)
        if not valid_fecha:
            QMessageBox.warning(self, "Advertencia", resultado_fecha)
            return
        edad = resultado_fecha
        
        # Validar peso
        valid_peso, resultado_peso = UserValidator.validar_numero(self.widgets['peso_entry'].text(), "peso")
        if not valid_peso:
            QMessageBox.warning(self, "Advertencia", resultado_peso)
            return
        peso = resultado_peso
        
        # Validar altura
        valid_altura, resultado_altura = UserValidator.validar_numero(self.widgets['altura_entry'].text(), "altura")
        if not valid_altura:
            QMessageBox.warning(self, "Advertencia", resultado_altura)
            return
        estatura = resultado_altura
        
        # Validar IMC
        try:
            imc = peso / ((estatura / 100) ** 2)
            if imc < 10 or imc > 60:
                reply = QMessageBox.question(
                    self, 
                    "IMC inusual",
                    f"El IMC calculado es {imc:.2f}, lo cual parece poco realista.\n¿Estás seguro de que los datos son correctos?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
        except ZeroDivisionError:
             QMessageBox.warning(self, "Advertencia", "La altura no puede ser cero.")
             return

        # Validar meta de calorías
        valid_meta, resultado_meta = UserValidator.validar_numero(self.widgets['meta_entry'].text(), "meta de calorías")
        if not valid_meta:
            QMessageBox.warning(self, "Advertencia", resultado_meta)
            return
        meta_cal = resultado_meta
        
        # Obtener otros datos
        nivel_actividad = self.widgets['lvl_actividad_combobox'].currentText()
        genero = self.widgets['gen_combobox'].currentText()
        
        conn = None # Inicializar conn para el bloque finally
        try:
            # Crear base de datos para el usuario
            self.user_database.crear_db_usuario(nombre)
            
            # Registrar usuario en el sistema de autenticación
            datos_usuario = {'nombre': nombre, 'contra': contra}
            if not self.auth_service.registrar_usuario(datos_usuario):
                QMessageBox.warning(self, "Advertencia", "No se pudo registrar el usuario en el servicio de autenticación.")
                return
            
            # Guardar datos adicionales en la base de datos del usuario
            directorio = f'./users/{nombre}'
            conn = sqlite3.connect(f"{directorio}/alimentos.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO datos (nombre, estatura, nivel_actividad, genero, meta_cal, edad)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nombre, estatura, nivel_actividad, genero, meta_cal, edad))
            
            # Guardar peso inicial
            if peso:
                cursor.execute("""
                    INSERT INTO peso (fecha, peso)
                    VALUES (?, ?)
                """, (datetime.now().strftime('%d-%m-%Y'), peso))
            
            # Insertar configuración de mensajes por defecto
            cursor.execute("""
                INSERT INTO mensajes (registrar_alimento, agregar_alimento, graficos, configuracion, salud, admin_alimentos, historial)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (1, 1, 1, 1, 1, 1, 1))
            
            conn.commit()
            
            # Guardar usuario actual para iniciar sesión automáticamente
            self.auth_service.guardar_usuario_actual(nombre)
            
            QMessageBox.information(self, "Éxito", "Se ha registrado correctamente.")
            self.ocultar()
            self.on_success()
            
        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Error al registrarse: {str(e)}")
        finally:
            if conn:
                conn.close()