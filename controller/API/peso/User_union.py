# ejemplo_integracion.py
# Ejemplo de cómo usar ambas APIs en conjunto

import requests
import json
from datetime import date, datetime

# URLs de las APIs
USER_API_URL = "http://127.0.0.1:8000"
PESO_API_URL = "http://127.0.0.1:8001"

class ClienteAPIs:
    def __init__(self):
        self.token = None
        self.user_data = None
    
    def registrar_usuario(self, datos_usuario):
        """Registra un nuevo usuario en la API de usuarios"""
        response = requests.post(f"{USER_API_URL}/register/", json=datos_usuario)
        if response.status_code == 201:
            print("✅ Usuario registrado exitosamente")
            return response.json()
        else:
            print(f"❌ Error al registrar usuario: {response.text}")
            return None
    
    def login(self, username, password):
        """Inicia sesión y obtiene el token"""
        data = {
            "username": username,
            "password": password
        }
        response = requests.post(f"{USER_API_URL}/login/", data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            print("✅ Login exitoso")
            
            # Obtener información del usuario
            self.obtener_info_usuario()
            return True
        else:
            print(f"❌ Error en login: {response.text}")
            return False
    
    def obtener_info_usuario(self):
        """Obtiene la información del usuario actual"""
        if not self.token:
            print("❌ No hay token de autenticación")
            return None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{USER_API_URL}/users/me/", headers=headers)
        
        if response.status_code == 200:
            self.user_data = response.json()
            print(f"✅ Información del usuario obtenida: {self.user_data['nombre_usuario']}")
            return self.user_data
        else:
            print(f"❌ Error al obtener información del usuario: {response.text}")
            return None
    
    def registrar_peso(self, fecha, peso):
        """Registra un nuevo peso en la API de peso"""
        if not self.token:
            print("❌ No hay token de autenticación")
            return None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {
            "fecha": fecha.isoformat(),
            "peso": peso
        }
        
        response = requests.post(f"{PESO_API_URL}/peso/", json=data, headers=headers)
        
        if response.status_code == 201:
            registro = response.json()
            print(f"✅ Peso registrado: {peso} kg el {fecha.strftime('%d-%m-%Y')}")
            return registro
        else:
            print(f"❌ Error al registrar peso: {response.text}")
            return None
    
    def obtener_registros_peso(self):
        """Obtiene todos los registros de peso del usuario"""
        if not self.token:
            print("❌ No hay token de autenticación")
            return None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{PESO_API_URL}/peso/", headers=headers)
        
        if response.status_code == 200:
            registros = response.json()
            print(f"✅ Se obtuvieron {len(registros)} registros de peso")
            return registros
        else:
            print(f"❌ Error al obtener registros de peso: {response.text}")
            return None
    
    def obtener_estadisticas_peso(self):
        """Obtiene las estadísticas de peso del usuario"""
        if not self.token:
            print("❌ No hay token de autenticación")
            return None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{PESO_API_URL}/peso/estadisticas/", headers=headers)
        
        if response.status_code == 200:
            estadisticas = response.json()
            print("✅ Estadísticas de peso obtenidas:")
            print(f"   • Peso actual: {estadisticas['peso_actual']} kg")
            print(f"   • Peso inicial: {estadisticas['peso_inicial']} kg")
            print(f"   • Diferencia: {estadisticas['diferencia_peso']:+.1f} kg")
            print(f"   • Promedio: {estadisticas['peso_promedio']:.1f} kg")
            print(f"   • Total registros: {estadisticas['total_registros']}")
            return estadisticas
        else:
            print(f"❌ Error al obtener estadísticas: {response.text}")
            return None
    
    def actualizar_peso(self, registro_id, nuevo_peso=None, nueva_fecha=None):
        """Actualiza un registro de peso existente"""
        if not self.token:
            print("❌ No hay token de autenticación")
            return None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {}
        
        if nuevo_peso is not None:
            data["peso"] = nuevo_peso
        if nueva_fecha is not None:
            data["fecha"] = nueva_fecha.isoformat()
        
        response = requests.put(f"{PESO_API_URL}/peso/{registro_id}", json=data, headers=headers)
        
        if response.status_code == 200:
            registro = response.json()
            print(f"✅ Registro actualizado: {registro['peso']} kg el {registro['fecha']}")
            return registro
        else:
            print(f"❌ Error al actualizar registro: {response.text}")
            return None


def ejemplo_uso_completo():
    """Ejemplo completo de uso de ambas APIs"""
    
    cliente = ClienteAPIs()
    
    # 1. Registrar un nuevo usuario
    print("=== REGISTRO DE USUARIO ===")
    datos_usuario = {
        "nombre_usuario": "juan_test",
        "password": "password123",
        "sexo": "Masculino",
        "peso": 75.5,
        "altura": 175,
        "meta_calorias": 2000,
        "nivel_actividad": "Moderado",
        "fecha_nacimiento": "1990-05-15",
        "edad": 33
    }
    
    usuario = cliente.registrar_usuario(datos_usuario)
    if not usuario:
        print("❌ No se pudo registrar el usuario, intentando login...")
    
    # 2. Hacer login
    print("\n=== LOGIN ===")
    if not cliente.login("juan_test", "password123"):
        print("❌ No se pudo hacer login, terminando ejemplo")
        return
    
    # 3. Registrar varios pesos
    print("\n=== REGISTRO DE PESOS ===")
    pesos_ejemplo = [
        (date(2024, 1, 1), 75.5),
        (date(2024, 1, 15), 75.2),
        (date(2024, 2, 1), 74.8),
        (date(2024, 2, 15), 74.5),
        (date(2024, 3, 1), 74.0),
    ]
    
    for fecha, peso in pesos_ejemplo:
        cliente.registrar_peso(fecha, peso)
    
    # 4. Obtener todos los registros
    print("\n=== OBTENER REGISTROS ===")
    registros = cliente.obtener_registros_peso()
    
    if registros:
        print("Registros de peso:")
        for registro in registros:
            fecha_formato = datetime.fromisoformat(registro['fecha']).strftime('%d-%m-%Y')
            print(f"   • {fecha_formato}: {registro['peso']} kg")
    
    # 5. Obtener estadísticas
    print("\n=== ESTADÍSTICAS ===")
    cliente.obtener_estadisticas_peso()
    
    # 6. Actualizar un registro (si existe)
    if registros and len(registros) > 0:
        print("\n=== ACTUALIZAR REGISTRO ===")
        primer_registro = registros[0]
        cliente.actualizar_peso(primer_registro['id'], nuevo_peso=74.2)
    
    print("\n=== EJEMPLO COMPLETADO ===")


if __name__ == "__main__":
    print("🚀 Iniciando ejemplo de integración de APIs")
    print("📋 Asegúrate de que ambas APIs estén ejecutándose:")
    print("   • API Usuarios: http://127.0.0.1:8000")
    print("   • API Peso: http://127.0.0.1:8001")
    print()
    
    try:
        ejemplo_uso_completo()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar a las APIs")
        print("   Verifica que ambas APIs estén ejecutándose")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")