# import sqlite3 # Eliminado: Ya no se usa SQLite directamente aquí

class Calculo:
    # NOTA: Se asume que se pasará un objeto api_client a los métodos que lo requieran.
    # Este api_client debería tener un método como get_user_profile() que retorne
    # un diccionario o un objeto con los datos del usuario:
    # {'peso': float, 'altura': int (cm), 'sexo': str, 'edad': int, ...}

    # Rangos de IMC y sus categorías
    # Los rangos permanecen igual

    @staticmethod
    # def calcular_imc(usuario): # Firma original
    def calcular_imc(api_client): # Nueva firma
        try:
            user_data = api_client.get_user_profile() # Método hipotético del api_client
            if not user_data:
                raise ValueError("No se pudieron obtener los datos del usuario desde la API.")

            estatura_cm = user_data.get('altura')
            peso_kg = user_data.get('peso')

            if estatura_cm is None or peso_kg is None:
                raise ValueError("La API no devolvió la altura o el peso del usuario.")

            if not isinstance(estatura_cm, (int, float)) or not isinstance(peso_kg, (int, float)):
                raise ValueError("Altura o peso con formato incorrecto desde la API.")
            
            if estatura_cm <= 0 or peso_kg <= 0:
                raise ValueError("Altura o peso deben ser valores positivos.")

            estatura_m = estatura_cm / 100  # Convertir a metros
            imc = peso_kg / (estatura_m ** 2)
            return imc

        except Exception as e: # Captura errores de API (requests.exceptions.RequestException) o ValueError
            print(f"Error al calcular IMC usando la API: {e}")
            return None

    @staticmethod
    def evaluar_imc(imc):
        """Evalúa el IMC y devuelve una categoría y un nivel de riesgo"""
        # Esta función no cambia ya que su lógica es independiente de la fuente de datos.
        # Esta función no cambia.

    @staticmethod
    # def calcular_TMB(usuario): # Firma original
    def calcular_TMB(api_client): # Nueva firma
        try:
            user_data = api_client.get_user_profile()
            if not user_data:
                raise ValueError("No se pudieron obtener los datos del usuario desde la API.")

            estatura_cm = user_data.get('altura')
            edad_años = user_data.get('edad')
            genero_str = user_data.get('sexo') # La API usa 'Masculino'/'Femenino'
            peso_kg = user_data.get('peso')

            if estatura_cm is None or edad_años is None or genero_str is None or peso_kg is None:
                raise ValueError("Datos incompletos (altura, edad, sexo, o peso) desde la API.")

            # Validaciones de tipo y valor
            for val, name in [(estatura_cm, "Altura"), (edad_años, "Edad"), (peso_kg, "Peso")]:
                if not isinstance(val, (int, float)):
                    raise ValueError(f"{name} con formato incorrecto desde la API.")
                if val <= 0:
                     raise ValueError(f"{name} debe ser un valor positivo.")
            
            if not isinstance(genero_str, str):
                 raise ValueError("Género con formato incorrecto desde la API.")


            # La API usa 'Masculino'/'Femenino', la fórmula espera 'masculino'/'femenino'
            genero_normalizado = genero_str.lower()

            if genero_normalizado in ["hombre", "masculino"]:
                tmb = 66.47 + (13.75 * peso_kg) + (5 * estatura_cm) - (6.76 * edad_años)
            elif genero_normalizado in ["mujer", "femenino"]:
                tmb = 655.1 + (9.56 * peso_kg) + (1.85 * estatura_cm) - (4.68 * edad_años)
            else:
                # Tratar de mapear si es posible, o lanzar error si no es reconocido
                if "masculino" in genero_normalizado: # Intento flexible
                     tmb = 66.47 + (13.75 * peso_kg) + (5 * estatura_cm) - (6.76 * edad_años)
                elif "femenino" in genero_normalizado: # Intento flexible
                     tmb = 655.1 + (9.56 * peso_kg) + (1.85 * estatura_cm) - (4.68 * edad_años)
                else:
                    raise ValueError(f"Género no válido o no reconocido desde la API: '{genero_str}'")
            
            return tmb

        except Exception as e:
            print(f"Error al calcular TMB usando la API: {e}")
            return None
    
    @staticmethod
    def evaluar_TMB(tmb, genero):
        """Evalúa la TMB según el género y devuelve una categoría y un nivel de riesgo"""
        # Esta función no cambia, pero 'genero' debe ser consistente con las claves de RANGOS_TMB.
        # La API devuelve 'Masculino'/'Femenino'. Normalizar antes de llamar a evaluar_TMB.
        # Esta función no cambia.
    
    @staticmethod
    # def get_latest_weight(usuario): # Firma original
    def get_latest_weight(api_client): # Nueva firma
        try:
            user_data = api_client.get_user_profile()
            if not user_data:
                raise ValueError("No se pudieron obtener los datos del usuario desde la API.")
            
            peso_kg = user_data.get('peso')
            if peso_kg is None:
                raise ValueError("La API no devolvió el peso del usuario.")
            if not isinstance(peso_kg, (int, float)) or peso_kg <=0:
                raise ValueError("Peso con formato incorrecto o no positivo desde la API.")

            return peso_kg
        except Exception as e:
            print(f"Error al obtener el peso más reciente usando la API: {e}")
            return None
    
    @staticmethod
    # def get_user_gender(usuario): # Firma original
    def get_user_gender(api_client): # Nueva firma
        """Obtiene el género del usuario desde la API."""
        try:
            user_data = api_client.get_user_profile()
            if not user_data:
                raise ValueError("No se pudieron obtener los datos del usuario desde la API.")

            genero_str = user_data.get('sexo') # La API usa 'Masculino'/'Femenino'
            if genero_str is None:
                raise ValueError("La API no devolvió el sexo del usuario.")
            if not isinstance(genero_str, str):
                raise ValueError("Sexo con formato incorrecto desde la API.")

            return genero_str # Retorna 'Masculino' o 'Femenino' como lo da la API
        except Exception as e:
            print(f"Error al obtener el género del usuario usando la API: {e}")
            return "masculino"  # Valor por defecto en caso de error, o se podría lanzar el error.
    
    @staticmethod
    # def calcular_agua_recomendada(usuario): # Firma original
    def calcular_agua_recomendada(api_client): # Nueva firma
        """Calcula la cantidad de agua recomendada en vasos según el peso (obtenido de la API)."""
        try:
            peso = Calculo.get_latest_weight(api_client) # Ya usa la API
            if peso is None:
                return 8  # Valor por defecto si no hay peso registrado
            
            # Cálculo base: 30-35 ml por kg de peso corporal
            # Convertido a vasos de 250 ml
            vasos_base = round((peso * 35) / 250)
            
            # Limitar a un mínimo de 6 y máximo de 12 vasos
            return max(6, min(12, vasos_base))
            
        except Exception as e:
            print(f"Error al calcular agua recomendada: {e}")
            return 8  # Valor por defecto en caso de error