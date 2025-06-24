# Archivo central de mensajes de bienvenida con formato HTML profesional.

MENSAJES = {
    "salud": {
        "titulo": "❤️ Panel de Salud",
        "mensaje_html": """
        <div style='text-align: center; padding: 15px;'>
            <h2 style='color: #2ECC71; margin-bottom: 15px;'>
                Tu Centro de Bienestar Personal
            </h2>
            <p style='font-size: 16px; line-height: 1.5; color: #333;'>
                Aquí puedes monitorear tus métricas de salud más importantes para seguir tu progreso.
            </p>
            <div style='background: #f0fdf4; padding: 15px; border-radius: 10px; margin: 15px 0; border: 1px solid #dcfce7;'>
                <h3 style='color: #16a34a; margin-bottom: 10px;'>Funciones Clave:</h3>
                <ul style='text-align: left; color: #424242; line-height: 1.7;'>
                    <li><b>Gestiona tu peso</b> y observa tu evolución.</li>
                    <li><b>Mide tus pulsaciones</b> en tiempo real.</li>
                    <li>Calcula tu <b>IMC y TMB</b> automáticamente.</li>
                    <li>Controla tu <b>hidratación diaria</b>.</li>
                </ul>
            </div>
            <p style='font-size: 14px; color: #666; font-style: italic;'>
                💡 Usa el Asistente IA para obtener consejos de salud personalizados.
            </p>
        </div>
        """
    },
    "configuracion": {
        "titulo": "⚙️ Configuración de Perfil",
        "mensaje_html": """
        <div style='text-align: center; padding: 15px;'>
            <h2 style='color: #3498DB; margin-bottom: 15px;'>
                Personaliza Tu Experiencia
            </h2>
            <p style='font-size: 16px; line-height: 1.5; color: #333;'>
                Ajusta tus datos y preferencias para que la aplicación se adapte a ti.
            </p>
            <div style='background: #eff6ff; padding: 15px; border-radius: 10px; margin: 15px 0; border: 1px solid #dbeafe;'>
                <h3 style='color: #2563eb; margin-bottom: 10px;'>Opciones Disponibles:</h3>
                <ul style='text-align: left; color: #424242; line-height: 1.7;'>
                    <li>Actualiza tus <b>datos personales</b> (edad, peso, etc.).</li>
                    <li>Establece tus <b>metas calóricas</b> diarias.</li>
                    <li>Define tu <b>nivel de actividad</b> física.</li>
                    <li>Configura <b>recordatorios</b> para no olvidar pesar-te.</li>
                </ul>
            </div>
            <p style='font-size: 14px; color: #666; font-style: italic;'>
                💡 Mantener tus datos actualizados garantiza cálculos más precisos.
            </p>
        </div>
        """
    },
    "agregar_alimento": {
        "titulo": "➕ Agregar Nuevos Alimentos",
        "mensaje_html": """
        <div style='text-align: center; padding: 15px;'>
            <h2 style='color: #E67E22; margin-bottom: 15px;'>
                Expande Tu Base de Datos
            </h2>
            <p style='font-size: 16px; line-height: 1.5; color: #333;'>
                Añade aquí los alimentos que no encuentres en la lista para usarlos en tus registros.
            </p>
            <div style='background: #fff7ed; padding: 15px; border-radius: 10px; margin: 15px 0; border: 1px solid #ffedd5;'>
                <h3 style='color: #c2410c; margin-bottom: 10px;'>¿Cómo funciona?:</h3>
                <ul style='text-align: left; color: #424242; line-height: 1.7;'>
                    <li>Ingresa el <b>nombre del alimento</b>.</li>
                    <li>Elige si las calorías son por <b>100gr</b> o por <b>porción</b>.</li>
                    <li>Introduce la cantidad de <b>calorías</b>.</li>
                </ul>
            </div>
            <p style='font-size: 14px; color: #666; font-style: italic;'>
                💡 Usa el botón 'Buscar Calorías' para consultar valores nutricionales en la web.
            </p>
        </div>
        """
    },
    "registrar_alimento": {
        "titulo": "🍎 Registro de Alimentos",
        "mensaje_html": """
        <div style='text-align: center; padding: 15px;'>
            <h2 style='color: #E74C3C; margin-bottom: 15px;'>
                ¿Qué comiste hoy?
            </h2>
            <p style='font-size: 16px; line-height: 1.5; color: #333;'>
                Registra aquí los alimentos que consumes para llevar un control de tus calorías.
            </p>
            <div style='background: #fef2f2; padding: 15px; border-radius: 10px; margin: 15px 0; border: 1px solid #fee2e2;'>
                <h3 style='color: #b91c1c; margin-bottom: 10px;'>Pasos para registrar:</h3>
                <ul style='text-align: left; color: #424242; line-height: 1.7;'>
                    <li><b>Selecciona un alimento</b> del desplegable o búscalo.</li>
                    <li>Ingresa la <b>cantidad</b> que consumiste.</li>
                    <li>Ajusta la <b>hora</b> del consumo.</li>
                    <li>¡Haz clic en <b>Registrar Alimento</b>!</li>
                </ul>
            </div>
            <p style='font-size: 14px; color: #666; font-style: italic;'>
                💡 Si un alimento no está en la lista, primero debes añadirlo en la pestaña 'Agregar Alimento'.
            </p>
        </div>
        """
    },
    "historial": {
        "titulo": "📊 Historial de Consumo",
        "mensaje_html": """
        <div style='text-align: center; padding: 15px;'>
            <h2 style='color: #4CAF50; margin-bottom: 15px;'>
                Tu Diario Alimentario
            </h2>
            <p style='font-size: 16px; line-height: 1.5; color: #333;'>
                Aquí puedes explorar y analizar todo tu historial alimentario de manera intuitiva y detallada.
            </p>
            <div style='background: #f0fdf4; padding: 15px; border-radius: 10px; margin: 15px 0; border: 1px solid #dcfce7;'>
                <h3 style='color: #16a34a; margin-bottom: 10px;'>Funciones Principales:</h3>
                <ul style='text-align: left; color: #424242; line-height: 1.7;'>
                    <li><b>Búsqueda Avanzada:</b> Encuentra alimentos específicos.</li>
                    <li><b>Filtros de Fecha:</b> Analiza períodos de tiempo.</li>
                    <li><b>Estadísticas en Tiempo Real:</b> Ve tus métricas al instante.</li>
                    <li><b>Exportación CSV:</b> Lleva tus datos donde necesites.</li>
                </ul>
            </div>
            <p style='font-size: 14px; color: #666; font-style: italic;'>
                💡 Usa el botón de ayuda (❓) para obtener más información.
            </p>
        </div>
        """
    }
}