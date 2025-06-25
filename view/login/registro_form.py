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
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Frame contenedor
        self.frame = QFrame()
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: {gris};
                border: 2px solid {azul_medio_oscuro};
                border-radius: 20px;
                padding: 15px;
            }}
        """)
        self.frame.setFixedSize(500, 600)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setSpacing(10)
        
        # Título
        titulo = QLabel("Registrarse")
        titulo.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        titulo.setStyleSheet(f"color: {azul_medio_oscuro};")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(titulo)
        
        # Área de scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {gris};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {azul_medio_oscuro};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {verde_boton};
                border-radius: 6px;
            }}
        """)
        
        # Widget contenedor del scroll
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        
        # Estilos para labels y entries
        label_style = f"""
            QLabel {{
                background-color: {azul_medio_oscuro};
                color: white;
                font: 13px Arial;
                border-radius: 18px;
                padding: 8px;
                min-width: 172px;
            }}
        """
        
        entry_style = f"""
            QLineEdit {{
                background-color: {color_entry};
                color: black;
                border-radius: 18px;
                padding: 8px;
                min-width: 172px;
                font: 12px Arial;
            }}
        """
        
        combo_style = f"""
            QComboBox {{
                background-color: {gris_label};
                color: {negro_texto};
                border-radius: 15px;
                padding: 8px;
                min-width: 187px;
                font: 12px Arial;
            }}
            QComboBox::drop-down {{
                background-color: {verde_boton};
                border-radius: 8px;
            }}
        """
        
        # Campos del formulario
        self.widgets['nombre_label'] = QLabel("Nombre")
        self.widgets['nombre_label'].setStyleSheet(label_style)
        self.widgets['nombre_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addWidget(self.widgets['nombre_label'])
        
        self.widgets['nombre_entry'] = QLineEdit()
        self.widgets['nombre_entry'].setPlaceholderText("Introduce tu nombre")
        self.widgets['nombre_entry'].setStyleSheet(entry_style)
        scroll_layout.addWidget(self.widgets['nombre_entry'])
        
        self.widgets['contra_label'] = QLabel("Contraseña")
        self.widgets['contra_label'].setStyleSheet(label_style)
        self.widgets['contra_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addWidget(self.widgets['contra_label'])
        
        self.widgets['contra_entry'] = QLineEdit()
        self.widgets['contra_entry'].setEchoMode(QLineEdit.EchoMode.Password)
        self.widgets['contra_entry'].setStyleSheet(entry_style)
        scroll_layout.addWidget(self.widgets['contra_entry'])
        
        self.widgets['gen_label'] = QLabel("Sexo")
        self.widgets['gen_label'].setStyleSheet(label_style)
        self.widgets['gen_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addWidget(self.widgets['gen_label'])
        
        self.widgets['gen_combobox'] = QComboBox()
        self.widgets['gen_combobox'].addItems(["Masculino", "Femenino"])
        self.widgets['gen_combobox'].setStyleSheet(combo_style)
        scroll_layout.addWidget(self.widgets['gen_combobox'])
        
        self.widgets['peso_label'] = QLabel("Peso (kg)")
        self.widgets['peso_label'].setStyleSheet(label_style)
        self.widgets['peso_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addWidget(self.widgets['peso_label'])
        
        self.widgets['peso_entry'] = QLineEdit()
        self.widgets['peso_entry'].setPlaceholderText("Introduce tu peso")
        self.widgets['peso_entry'].setStyleSheet(entry_style)
        scroll_layout.addWidget(self.widgets['peso_entry'])
        
        self.widgets['altura_label'] = QLabel("Altura (cm)")
        self.widgets['altura_label'].setStyleSheet(label_style)
        self.widgets['altura_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addWidget(self.widgets['altura_label'])
        
        self.widgets['altura_entry'] = QLineEdit()
        self.widgets['altura_entry'].setPlaceholderText("Introduce tu altura")
        self.widgets['altura_entry'].setStyleSheet(entry_style)
        scroll_layout.addWidget(self.widgets['altura_entry'])
        
        self.widgets['meta_label'] = QLabel("Meta de calorías diaria")
        self.widgets['meta_label'].setStyleSheet(label_style)
        self.widgets['meta_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addWidget(self.widgets['meta_label'])
        
        self.widgets['meta_entry'] = QLineEdit()
        self.widgets['meta_entry'].setPlaceholderText("Introduce tu meta de calorías")
        self.widgets['meta_entry'].setStyleSheet(entry_style)
        scroll_layout.addWidget(self.widgets['meta_entry'])
        
        self.widgets['lvl_actividad_label'] = QLabel("Nivel de Actividad")
        self.widgets['lvl_actividad_label'].setStyleSheet(label_style)
        self.widgets['lvl_actividad_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addWidget(self.widgets['lvl_actividad_label'])
        
        self.widgets['lvl_actividad_combobox'] = QComboBox()
        self.widgets['lvl_actividad_combobox'].addItems(["Sedentario", "Ligero", "Moderado", "Intenso"])
        self.widgets['lvl_actividad_combobox'].setStyleSheet(combo_style)
        scroll_layout.addWidget(self.widgets['lvl_actividad_combobox'])
        
        self.widgets['edad_label'] = QLabel("Fecha de Nacimiento")
        self.widgets['edad_label'].setStyleSheet(label_style)
        self.widgets['edad_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addWidget(self.widgets['edad_label'])
        
        # DateEdit para fecha de nacimiento
        self.widgets['fecha_nacimiento_entry'] = QDateEdit()
        self.widgets['fecha_nacimiento_entry'].setCalendarPopup(True)
        self.widgets['fecha_nacimiento_entry'].setDate(QDate.currentDate().addYears(-25))
        min_date = QDate.currentDate().addYears(-120)
        max_date = QDate.currentDate().addYears(-13)
        self.widgets['fecha_nacimiento_entry'].setDateRange(min_date, max_date)
        self.widgets['fecha_nacimiento_entry'].setStyleSheet(f"""
            QDateEdit {{
                background-color: {color_entry};
                color: black;
                border-radius: 15px;
                padding: 8px;
                min-width: 187px;
                font: 12px Arial;
            }}
        """)
        scroll_layout.addWidget(self.widgets['fecha_nacimiento_entry'])
        
        # Botones
        button_style = f"""
            QPushButton {{
                border-radius: 18px;
                font: bold 13px Arial;
                padding: 8px;
                min-width: 187px;
            }}
        """
        
        self.widgets['guardar_button'] = QPushButton("Guardar")
        self.widgets['guardar_button'].setStyleSheet(button_style + f"""
            QPushButton {{
                background-color: {verde_boton};
                color: {azul_medio_oscuro};
            }}
            QPushButton:hover {{
                background-color: {verde_oscuro};
            }}
        """)
        self.widgets['guardar_button'].clicked.connect(self._guardar)
        scroll_layout.addWidget(self.widgets['guardar_button'])
        
        self.widgets['btn_volver'] = QPushButton('Volver Atrás')
        self.widgets['btn_volver'].setStyleSheet(button_style + f"""
            QPushButton {{
                background-color: {riesgo_medio};
                color: {azul_medio_oscuro};
            }}
            QPushButton:hover {{
                background-color: {riesgo_alto};
            }}
        """)
        self.widgets['btn_volver'].clicked.connect(self._volver_atras)
        scroll_layout.addWidget(self.widgets['btn_volver'])
        
        scroll_area.setWidget(scroll_widget)
        frame_layout.addWidget(scroll_area)
        
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