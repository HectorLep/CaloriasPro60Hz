from google import genai
from google.genai import types
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal
from .calculos import Calculo
from datetime import datetime
import sqlite3
import json
import re
import os


class GeminiAssistant(QObject):
    # Señales para comunicación asíncrona con la UI
    connection_status_changed = pyqtSignal(bool, str)  # connected, message
    response_ready = pyqtSignal(str, object)  # response, food_info
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        # API key - IMPORTANTE: Reemplaza con tu API key real de Gemini
        self.api_key = "AIzaSyAtATTf0vfI03BfcHq-8OGWTFd2DgVAGSw"  # ⚠️ CAMBIAR POR TU API KEY
        self.client = None
        self.chat_history = []
        self.last_food_suggestion = None  # Para almacenar la última sugerencia de comida
        self.setup_client()
        
        # Palabras clave relacionadas con la aplicación
        self.keywords_nutricion = [
            'calorias', 'caloria', 'proteina', 'carbohidratos', 'grasas',
            'imc', 'tmb', 'peso', 'dieta', 'comida', 'alimento', 'nutricion',
            'agua', 'hidratacion', 'metabolismo', 'bajar de peso', 'subir de peso',
            'ejercicio', 'actividad fisica', 'salud', 'vitaminas', 'minerales',
            'fibra', 'azucar', 'sodio', 'desayuno', 'almuerzo', 'cena',
            'snack', 'merienda', 'porciones', 'contador', 'app', 'aplicacion'
        ]
        
    def setup_client(self):
        """Configura el cliente de Gemini"""
        try:
            if not self.api_key or self.api_key == "TU_API_KEY_AQUI":
                print("⚠️ ADVERTENCIA: API key no configurada")
                self.client = None
                self.connection_status_changed.emit(False, "API key no configurada")
                return
                
            # Crear cliente con la nueva API
            self.client = genai.Client(api_key=self.api_key)
            print("✅ Cliente Gemini configurado correctamente")
            self.connection_status_changed.emit(True, "Conectado correctamente")
            
        except Exception as e:
            print(f"❌ Error configurando cliente Gemini: {e}")
            self.client = None
            self.connection_status_changed.emit(False, str(e))
    
    def is_question_relevant(self, message):
        """Verifica si la pregunta está relacionada con nutrición/contador de calorías"""
        message_lower = message.lower()
        
        # Verificar si contiene palabras clave relevantes
        for keyword in self.keywords_nutricion:
            if keyword in message_lower:
                return True
        
        # Patrones adicionales que podrían ser relevantes
        patterns = [
            r'\b(cuant[ao]s?\s+calor[ií]as?)\b',
            r'\b(qu[eé]\s+comer)\b',
            r'\b(alimento\s+saludable)\b',
            r'\b(perder\s+peso)\b',
            r'\b(ganar\s+peso)\b',
            r'\b(men[uú]\s+saludable)\b',
        ]
        
        for pattern in patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def extract_food_info(self, message, response):
        """Extrae información de alimentos y calorías de la respuesta - VERSIÓN MEJORADA"""
        try:
            # Limpiar el texto de la respuesta
            response_clean = response.strip()
            message_clean = message.strip().lower()
            response_lower = response_clean.lower()
            
            print(f"DEBUG - Mensaje: {message_clean}")
            print(f"DEBUG - Respuesta: {response_lower}")
            
            # Buscar alimentos mencionados en el mensaje del usuario
            common_foods = {
                'manzana': 'Manzana', 'banana': 'Banana', 'plátano': 'Plátano', 
                'naranja': 'Naranja', 'pera': 'Pera', 'uva': 'Uva',
                'pollo': 'Pollo', 'carne': 'Carne', 'pescado': 'Pescado', 
                'huevo': 'Huevo', 'arroz': 'Arroz', 'pan': 'Pan',
                'pasta': 'Pasta', 'pizza': 'Pizza', 'hamburguesa': 'Hamburguesa', 
                'ensalada': 'Ensalada', 'yogur': 'Yogur',
                'leche': 'Leche', 'queso': 'Queso', 'tomate': 'Tomate', 
                'lechuga': 'Lechuga', 'zanahoria': 'Zanahoria',
                'brócoli': 'Brócoli', 'espinaca': 'Espinaca', 'papa': 'Papa', 
                'patata': 'Patata', 'aguacate': 'Aguacate',
                'nuez': 'Nuez', 'almendra': 'Almendra', 'avena': 'Avena', 
                'cereal': 'Cereal', 'atún': 'Atún', 'salmón': 'Salmón'
            }
            
            # Encontrar alimento mencionado en el mensaje
            detected_food = None
            for food_key, food_name in common_foods.items():
                if food_key in message_clean:
                    detected_food = food_name
                    break
            
            print(f"DEBUG - Alimento detectado en mensaje: {detected_food}")
            
            # Buscar calorías en la respuesta usando patrones más específicos
            calorie_patterns = [
                r'(\d+)\s*calor[ií]as?',  # "95 calorías"
                r'(\d+)\s*cal\b',         # "95 cal"
                r'aproximadamente\s+(\d+)',  # "aproximadamente 95"
                r'contiene\s+(\d+)',      # "contiene 95"
                r'tiene\s+(\d+)',         # "tiene 95"
                r'aporta\s+(\d+)',        # "aporta 95"
            ]
            
            detected_calories = None
            for pattern in calorie_patterns:
                match = re.search(pattern, response_lower)
                if match:
                    potential_calories = int(match.group(1))
                    # Validar que sea un número razonable de calorías (entre 1 y 2000)
                    if 1 <= potential_calories <= 2000:
                        detected_calories = potential_calories
                        print(f"DEBUG - Calorías detectadas: {detected_calories} con patrón: {pattern}")
                        break
            
            # Solo devolver información si encontramos tanto el alimento como las calorías
            if detected_food and detected_calories:
                food_info = {
                    'food_name': detected_food,
                    'calories': detected_calories,
                    'raw_match': f"{detected_calories} calorías para {detected_food}"
                }
                print(f"DEBUG - Información extraída: {food_info}")
                return food_info
            else:
                print(f"DEBUG - No se encontró información completa. Alimento: {detected_food}, Calorías: {detected_calories}")
                return None
            
        except Exception as e:
            print(f"Error extrayendo información de alimentos: {e}")
            return None
    
    def get_system_instruction(self):
        """Define las instrucciones del sistema para el asistente"""
        user_data = self.get_user_health_data()
        
        return f"""Eres un asistente especializado ÚNICAMENTE en nutrición y contador de calorías.

Información del usuario:
{user_data}

REGLAS ESTRICTAS:
1. SOLO responde preguntas sobre: nutrición, calorías, IMC, TMB, alimentación, hidratación, peso, dietas, ejercicio y salud alimentaria
2. SIEMPRE incluye números específicos de calorías cuando sea relevante
3. Mantén respuestas CORTAS pero COMPLETAS: máximo 2 párrafos de 3 líneas cada uno
4. Si preguntan por calorías de alimentos, da el número total y desglose si es necesario
5. Si la pregunta NO es sobre nutrición/contador de calorías, responde: "Solo puedo ayudarte con temas de nutrición y contador de calorías. ¿Tienes alguna pregunta sobre tu alimentación o salud?"
6. Usa un tono amigable pero conciso
7. Siempre recomienda consultar profesionales para decisiones médicas importantes
8. Enfócate en consejos prácticos para la app de contador de calorías
9. Cuando menciones calorías de un alimento específico, usa el formato: "Una [alimento] contiene aproximadamente [número] calorías"

Formato de respuesta: Máximo 120 palabras, directo al punto, SIEMPRE incluir datos numéricos cuando sea posible."""

    def get_user_health_data(self):
        """Obtiene datos relevantes del usuario para personalizar respuestas"""
        try:
            # Intentar importar el módulo de cálculos
            try:
                from .calculos import Calculo
                
                # Obtener datos básicos - usando métodos seguros
                try:
                    imc = Calculo.calcular_imc(self.usuario)
                except:
                    imc = None
                
                try:
                    tmb = Calculo.calcular_TMB(self.usuario)
                except:
                    tmb = None
                
                try:
                    peso = Calculo.get_latest_weight(self.usuario)
                except:
                    peso = None
                
                try:
                    genero = Calculo.get_user_gender(self.usuario)
                except:
                    genero = None
                
                try:
                    edad = getattr(Calculo, 'get_user_age', lambda x: None)(self.usuario)
                except:
                    edad = None
                
                try:
                    altura = getattr(Calculo, 'get_user_height', lambda x: None)(self.usuario)
                except:
                    altura = None
            
            except ImportError:
                print("No se pudo importar el módulo Calculos")
                imc = tmb = peso = genero = edad = altura = None
            
            # Obtener consumo de agua del día
            vasos_agua = 0
            try:
                db_path = f"./users/{self.usuario}/alimentos.db"
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    fecha_actual = datetime.now().strftime("%d-%m-%Y")
                    cursor.execute("SELECT cant FROM agua WHERE fecha = ?", (fecha_actual,))
                    resultado = cursor.fetchone()
                    vasos_agua = resultado[0] if resultado else 0
                    conn.close()
            except Exception as e:
                print(f"Error obteniendo datos de agua: {e}")
                vasos_agua = 0
            
            data_text = f"""
- Peso: {f"{peso} kg" if peso else 'No registrado'}
- Altura: {f"{altura} cm" if altura else 'No registrada'}
- Edad: {f"{edad} años" if edad else 'No registrada'}
- Género: {genero if genero else 'No especificado'}
- IMC: {f"{imc:.2f}" if imc else 'No calculable'}
- TMB: {f"{int(tmb)} cal/día" if tmb else 'No calculable'}
- Agua hoy: {vasos_agua}/8 vasos
"""
            return data_text
            
        except Exception as e:
            print(f"Error obteniendo datos del usuario: {e}")
            return "- Datos del usuario no disponibles"
    
    def limit_response_length(self, response, max_words=120):
        """Limita la longitud de la respuesta"""
        words = response.split()
        if len(words) > max_words:
            # Tomar solo las primeras max_words palabras
            limited_response = ' '.join(words[:max_words])
            # Buscar el último punto para hacer un corte natural
            last_period = limited_response.rfind('.')
            if last_period > len(limited_response) * 0.7:  # Si el punto está en el último 30%
                limited_response = limited_response[:last_period + 1]
            else:
                limited_response += "..."
            return limited_response
        return response
    
    def send_message(self, message):
        """Envía un mensaje al asistente y devuelve la respuesta - Versión simple sin historial"""
        if not self.client:
            error_msg = "Error: No se pudo conectar con Gemini. Verifica tu conexión a internet y API key."
            self.error_occurred.emit(error_msg)
            return error_msg, None
        
        # Verificar si el mensaje está vacío o es el placeholder
        if not message or message.strip() == "" or "Escribe tu pregunta" in message:
            error_msg = "Por favor, escribe una pregunta sobre nutrición o contador de calorías."
            return error_msg, None
        
        # Verificar si la pregunta es relevante
        if not self.is_question_relevant(message):
            irrelevant_msg = "Solo puedo ayudarte con temas de nutrición y contador de calorías. ¿Tienes alguna pregunta sobre tu alimentación o salud?"
            return irrelevant_msg, None
        
        try:
            # Generar respuesta usando la nueva API con system instruction
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=self.get_system_instruction()
                ),
                contents=message
            )
            
            # Limitar la longitud de la respuesta
            limited_response = self.limit_response_length(response.text, max_words=120)
            
            # Extraer información de alimentos
            food_info = self.extract_food_info(message, limited_response)
            self.last_food_suggestion = food_info
            
            # Emitir señal de respuesta lista
            self.response_ready.emit(limited_response, food_info)
            
            return limited_response, food_info
            
        except Exception as e:
            error_msg = self._handle_api_error(e)
            self.error_occurred.emit(error_msg)
            return error_msg, None
    
    def send_message_with_history(self, message):
        """Envía un mensaje manteniendo el historial de conversación"""
        if not self.client:
            error_msg = "Error: No se pudo conectar con Gemini. Verifica tu conexión a internet y API key."
            self.error_occurred.emit(error_msg)
            return error_msg, None
        
        # Verificar si el mensaje está vacío o es el placeholder
        if not message or message.strip() == "" or "Escribe tu pregunta" in message:
            error_msg = "Por favor, escribe una pregunta sobre nutrición o contador de calorías."
            return error_msg, None
        
        # Verificar si la pregunta es relevante
        if not self.is_question_relevant(message):
            irrelevant_msg = "Solo puedo ayudarte con temas de nutrición y contador de calorías. ¿Tienes alguna pregunta sobre tu alimentación o salud?"
            return irrelevant_msg, None
        
        try:
            # Agregar mensaje del usuario al historial
            self.chat_history.append({"role": "user", "content": message})
            
            # Crear contenido con historial para contexto (solo últimos 4 mensajes para mantener contexto corto)
            contents = []
            
            # Agregar los últimos 4 mensajes del historial para contexto
            for msg in self.chat_history[-4:]:
                contents.append(msg["content"])
            
            # Generar respuesta
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=self.get_system_instruction()
                ),
                contents=contents
            )
            
            # Limitar la longitud de la respuesta
            limited_response = self.limit_response_length(response.text, max_words=120)
            
            # Agregar respuesta al historial
            self.chat_history.append({"role": "assistant", "content": limited_response})
            
            # Extraer información de alimentos
            food_info = self.extract_food_info(message, limited_response)
            self.last_food_suggestion = food_info
            
            # Emitir señal de respuesta lista
            self.response_ready.emit(limited_response, food_info)
            
            return limited_response, food_info
            
        except Exception as e:
            error_msg = self._handle_api_error(e)
            self.error_occurred.emit(error_msg)
            return error_msg, None
    
    def _handle_api_error(self, error):
        """Maneja errores de la API de forma centralizada"""
        error_msg = str(error).lower()
        if "api_key" in error_msg or "authentication" in error_msg:
            return "Error de autenticación: Problema con la API key de Gemini."
        elif "quota" in error_msg or "limit" in error_msg:
            return "Límite de API alcanzado. Intenta más tarde."
        else:
            return f"Error al comunicarse con Gemini: {str(error)}"
    
    def add_food_to_database(self, food_name, calories, meal_type="Snack"):
        """Añade un alimento a la base de datos del usuario"""
        try:
            # Verificar que la carpeta del usuario existe
            user_dir = f"./users/{self.usuario}"
            if not os.path.exists(user_dir):
                os.makedirs(user_dir, exist_ok=True)
            
            db_path = f"{user_dir}/alimentos.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Crear tabla si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alimento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    calorias_porcion REAL NOT NULL,
                    fecha TEXT,
                    hora TEXT,
                    tipo_comida TEXT
                )
            """)
            
            fecha_actual = datetime.now().strftime("%d-%m-%Y")
            hora_actual = datetime.now().strftime("%H:%M")
            
            # Insertar el alimento en la base de datos
            cursor.execute("""
                INSERT INTO alimento (nombre, calorias_porcion, fecha, hora, tipo_comida)
                VALUES (?, ?, ?, ?, ?)
            """, (food_name, calories, fecha_actual, hora_actual, meal_type))
            
            conn.commit()
            conn.close()
            
            success_msg = f"✅ {food_name} ({calories} cal) añadido a {meal_type}"
            print(success_msg)
            return True, success_msg
            
        except Exception as e:
            error_msg = f"Error al añadir {food_name}: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def get_meal_types(self):
        """Retorna los tipos de comida disponibles"""
        return ["Desayuno", "Almuerzo", "Cena", "Snack"]
    
    def clear_history(self):
        """Limpia el historial de conversación"""
        self.chat_history = []
        self.last_food_suggestion = None
        print("📝 Historial de chat limpiado")
    
    def is_configured(self):
        """Verifica si el asistente está configurado correctamente"""
        return bool(self.client and self.api_key and self.api_key != "TU_API_KEY_AQUI")
    
    def test_connection(self):
        """Prueba la conexión con Gemini"""
        if not self.client:
            return False, "Cliente no inicializado"
            
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents="Responde solo: 'Conexión exitosa'"
            )
            return True, response.text.strip()
        except Exception as e:
            return False, self._handle_api_error(e)
    
    def get_nutrition_suggestions(self):
        """Obtiene sugerencias rápidas de nutrición basadas en los datos del usuario"""
        try:
            suggestions_prompt = "Dame 3 consejos cortos de nutrición basados en mis datos actuales. Máximo 50 palabras total."
            response, _ = self.send_message(suggestions_prompt)
            return response
        except Exception as e:
            return "Error obteniendo sugerencias de nutrición."
    
    def set_api_key(self, api_key):
        """Permite configurar la API key después de la inicialización"""
        self.api_key = api_key
        self.setup_client()
    
    def get_daily_calories_consumed(self):
        """Obtiene las calorías consumidas hoy por el usuario"""
        try:
            db_path = f"./users/{self.usuario}/alimentos.db"
            if not os.path.exists(db_path):
                return 0
                
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            fecha_actual = datetime.now().strftime("%d-%m-%Y")
            
            cursor.execute("""
                SELECT SUM(calorias_porcion) FROM alimento 
                WHERE fecha = ?
            """, (fecha_actual,))
            
            resultado = cursor.fetchone()
            conn.close()
            
            return resultado[0] if resultado[0] else 0
            
        except Exception as e:
            print(f"Error obteniendo calorías del día: {e}")
            return 0