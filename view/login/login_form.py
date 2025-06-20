#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formularios de Login convertidos a PyQt6
"""

import sqlite3
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QComboBox, QFrame,
                             QScrollArea, QDateEdit, QMessageBox, QSpacerItem,
                             QSizePolicy)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from model.login.user_validator import UserValidator
from model.login.auth_service import IAuthService 
from model.login.user_database import UserDatabase
from model.util.colores import *

class IForm: 
    def mostrar(self):
        """
        Este método debe ser implementado por las subclases para mostrar el widget.
        """
        raise NotImplementedError

    def ocultar(self):
        """
        Este método debe ser implementado por las subclases para ocultar el widget.
        """
        raise NotImplementedError


class LoginForm(IForm, QWidget):

    iniciar_sesion_clicked = pyqtSignal()
    registrarse_clicked = pyqtSignal()

    def __init__(self, ventana_principal, auth_service: IAuthService, on_success):
        super().__init__()
        self.ventana_principal = ventana_principal
        self.auth_service = auth_service
        self.on_success = on_success
        self.widgets = {}
        self.init_ui()
    
    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        
        # Frame contenedor
        self.frame = QFrame()
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: {gris};
                border: 2px solid {azul_medio_oscuro};
                border-radius: 20px;
                padding: 20px;
            }}
        """)
        self.frame.setFixedSize(400, 300)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.setSpacing(20)
        
        # Título
        titulo = QLabel("Bienvenido")
        titulo.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        titulo.setStyleSheet(f"color: {azul_medio_oscuro};")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(titulo)
        
        # Botones
        btn_style = f"""
            QPushButton {{
                background-color: {verde_boton};
                color: {azul_medio_oscuro};
                border: none;
                border-radius: 20px;
                font: bold 18px Arial;
                padding: 15px;
                min-width: 170px;
                min-height: 50px;
            }}
            QPushButton:hover {{
                background-color: {verde_oscuro};
            }}
        """
        
        self.widgets['btn_iniciar'] = QPushButton('Iniciar Sesión')
        self.widgets['btn_iniciar'].setStyleSheet(btn_style)
        self.widgets['btn_iniciar'].clicked.connect(self._mostrar_iniciar_sesion)
        frame_layout.addWidget(self.widgets['btn_iniciar'])
        
        self.widgets['btn_registrarse'] = QPushButton('Registrarse')
        self.widgets['btn_registrarse'].setStyleSheet(btn_style)
        self.widgets['btn_registrarse'].clicked.connect(self._mostrar_registro)
        frame_layout.addWidget(self.widgets['btn_registrarse'])
        
        main_layout.addWidget(self.frame)
    
    def mostrar(self):
        self.show()
    
    def ocultar(self):
        self.hide()
    
    def _mostrar_iniciar_sesion(self):
        self.iniciar_sesion_clicked.emit()

    
    def _mostrar_registro(self):
        self.registrarse_clicked.emit()



class IniciarSesionForm(IForm, QWidget):

    volver_clicked = pyqtSignal()

    def __init__(self, ventana_principal, auth_service: IAuthService, on_success, on_back):
        super().__init__()
        self.ventana_principal = ventana_principal
        self.auth_service = auth_service
        self.on_success = on_success
        self.on_back = on_back
        self.widgets = {}
        self.init_ui()
    
    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(20)
        
        # Frame contenedor
        self.frame = QFrame()
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: {gris};
                border: 2px solid {azul_medio_oscuro};
                border-radius: 20px;
                padding: 20px;
            }}
        """)
        self.frame.setFixedSize(400, 400)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.setSpacing(15)
        
        # Título
        titulo = QLabel("Iniciar Sesión")
        titulo.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        titulo.setStyleSheet(f"color: {azul_medio_oscuro};")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(titulo)
        
        # Label Usuario
        self.widgets['users_label'] = QLabel("Usuario")
        self.widgets['users_label'].setStyleSheet(f"""
            QLabel {{
                background-color: {azul_medio_oscuro};
                color: white;
                font: 20px Arial;
                border-radius: 20px;
                padding: 10px;
                min-width: 250px;
            }}
        """)
        self.widgets['users_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.widgets['users_label'])
        
        # ComboBox Usuario - Usar auth_service para obtener usuarios
        self.widgets['users_combobox'] = QComboBox()
        self._cargar_usuarios()  # Método separado para cargar usuarios
        self.widgets['users_combobox'].setStyleSheet(f"""
            QComboBox {{
                background-color: {gris_label};
                color: black;
                border-radius: 20px;
                padding: 12px;
                min-width: 280px;
                min-height: 40px;
                font: 16px Arial;
            }}
            QComboBox::drop-down {{
                background-color: {verde_boton};
                border-radius: 10px;
            }}
            QComboBox::drop-down:hover {{
                background-color: {verde_oscuro};
            }}
        """)        
        self.widgets['users_combobox'].currentTextChanged.connect(self._mostrar_campo_contrasena)
        frame_layout.addWidget(self.widgets['users_combobox'])
        
        # Contenedor para campos dinámicos
        self.dynamic_container = QWidget()
        self.dynamic_layout = QVBoxLayout(self.dynamic_container)
        self.dynamic_layout.setSpacing(10)
        frame_layout.addWidget(self.dynamic_container)
        
        # Mostrar campos de contraseña inmediatamente
        self._mostrar_campo_contrasena()
        
        main_layout.addWidget(self.frame)
    
    def _cargar_usuarios(self):
        """Carga los usuarios disponibles usando el auth_service"""
        try:
            usuarios = self.auth_service.obtener_usuarios()
            self.widgets['users_combobox'].clear()
            self.widgets['users_combobox'].addItems(usuarios)
            
            # Si no hay usuarios registrados, mostrar mensaje
            if not usuarios:
                self.widgets['users_combobox'].addItem("No hay usuarios registrados")
                self.widgets['users_combobox'].setEnabled(False)
            else:
                self.widgets['users_combobox'].setEnabled(True)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar usuarios: {str(e)}")
    
    def mostrar(self):
        # Recargar usuarios cada vez que se muestra el formulario
        self._cargar_usuarios()
        self.show()
    
    def ocultar(self):
        self.hide()
        
    def _mostrar_campo_contrasena(self):
        # Verificar si hay usuarios válidos
        if (self.widgets['users_combobox'].count() == 0 or 
            self.widgets['users_combobox'].currentText() == "No hay usuarios registrados"):
            return
            
        # Limpiar widgets dinámicos
        while self.dynamic_layout.count():
            child = self.dynamic_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        # Ajustar el frame para que sea más grande
        self.frame.setFixedSize(400, 550)  # Aumentar altura
        
        # Label Contraseña (moverlo más arriba con mayor separación)
        self.widgets['contra_label'] = QLabel("Contraseña")
        self.widgets['contra_label'].setStyleSheet(f"""
            QLabel {{
                background-color: {azul_medio_oscuro};
                color: white;
                font: bold 18px Arial;
                border-radius: 20px;
                padding: 12px;
                min-width: 280px;
                min-height: 45px;
            }}
        """)
        self.widgets['contra_label'].setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dynamic_layout.addWidget(self.widgets['contra_label'])
        
        # Spacer pequeño
        spacer1 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.dynamic_layout.addItem(spacer1)
        
        # Entry Contraseña (más grande)
        self.widgets['contra_entry'] = QLineEdit()
        self.widgets['contra_entry'].setEchoMode(QLineEdit.EchoMode.Password)
        self.widgets['contra_entry'].setStyleSheet(f"""
            QLineEdit {{
                background-color: {color_entry};
                color: black;
                border-radius: 20px;
                padding: 12px;
                min-width: 280px;
                min-height: 40px;
                font: 16px Arial;
            }}
        """)
        self.widgets['contra_entry'].returnPressed.connect(self._iniciar_sesion)
        self.dynamic_layout.addWidget(self.widgets['contra_entry'])
        
        # Spacer mediano
        spacer2 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.dynamic_layout.addItem(spacer2)
        
        # Botón Iniciar Sesión (más grande)
        self.widgets['btn_iniciar_sesion'] = QPushButton("Iniciar Sesión")
        self.widgets['btn_iniciar_sesion'].setStyleSheet(f"""
            QPushButton {{
                background-color: {verde_boton};
                border: none;
                border-radius: 25px;
                font: bold 16px Arial;
                padding: 15px;
                min-width: 280px;
                min-height: 50px;
            }}
            QPushButton:hover {{
                background-color: {verde_oscuro};
            }}
        """)
        # Fijar el color del texto
        palette_iniciar = self.widgets['btn_iniciar_sesion'].palette()
        palette_iniciar.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
        self.widgets['btn_iniciar_sesion'].setPalette(palette_iniciar)
        
        self.widgets['btn_iniciar_sesion'].clicked.connect(self._iniciar_sesion)
        self.dynamic_layout.addWidget(self.widgets['btn_iniciar_sesion'])
        
        # Spacer pequeño
        spacer3 = QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.dynamic_layout.addItem(spacer3)
        
        # Botón Volver (más grande)
        self.widgets['btn_volver'] = QPushButton('Volver Atrás')
        self.widgets['btn_volver'].setStyleSheet(f"""
            QPushButton {{
                background-color: {riesgo_medio};
                border: none;
                border-radius: 25px;
                font: bold 16px Arial;
                padding: 15px;
                min-width: 280px;
                min-height: 50px;
            }}
            QPushButton:hover {{
                background-color: {riesgo_alto};
            }}
        """)
        # Fijar el color del texto
        palette = self.widgets['btn_volver'].palette()
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("white"))
        self.widgets['btn_volver'].setPalette(palette)

        self.widgets['btn_volver'].clicked.connect(self._volver_atras)
        self.dynamic_layout.addWidget(self.widgets['btn_volver'])
            
    def _volver_atras(self):
        self.volver_clicked.emit()

    def _iniciar_sesion(self):
        usuario = self.widgets['users_combobox'].currentText()
        
        # Verificar que hay un usuario válido seleccionado
        if not usuario or usuario == "No hay usuarios registrados":
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona un usuario válido.")
            return
            
        contrasena = self.widgets['contra_entry'].text()
        
        if not contrasena:
            QMessageBox.warning(self, "Advertencia", "Por favor ingresa tu contraseña.")
            return
        
        try:
            # Usar el auth_service para verificar credenciales
            if self.auth_service.verificar_credenciales(usuario, contrasena):
                # Usar el auth_service para guardar el usuario actual
                if self.auth_service.guardar_usuario_actual(usuario):
                    QMessageBox.information(self, "Éxito", f"Ha iniciado sesión como {usuario}")
                    self.ocultar()
                    self.on_success()
                else:
                    QMessageBox.warning(self, "Error", "No se pudo guardar la sesión actual.")
            else:
                QMessageBox.warning(self, "Advertencia", "Contraseña incorrecta.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al iniciar sesión: {str(e)}")


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