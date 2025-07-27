Proyecto: Chatbot Académico – Recordatorios por WhatsApp
Estado Actual
Sistema funcional que envía recordatorios de exámenes a WhatsApp usando Twilio API.

Base de datos SQLite (data.db) con tablas:

Usuarios (usuarios) – Cada usuario tiene un número de teléfono, una zona horaria y configuración de alertas.

Exámenes (examenes) – Cada examen tiene un curso, fecha y recordatorios asociados.

scheduler.py automatiza el envío de mensajes diarios (mediante el Programador de Tareas de Windows).

Alertas configuradas por defecto para 30, 20, 10 y 5 días antes de cada examen.

Mensajes incluyen frases motivadoras.

Funciona para usuarios en diferentes zonas horarias (ejemplo: Perú y España).

Archivos Clave
models.py – Define tablas Usuario y Examen.

scheduler.py – Lógica para enviar recordatorios (simulación o envío real).

add_data.py – Añade un usuario y examen de prueba.

ver_db.py – Muestra usuarios y exámenes en la base de datos.

run_scheduler.bat – Ejecuta el scheduler manualmente.

Tarea Programada en Windows – Corre run_scheduler.bat cada día a las 8:00 a.m.

Últimos Avances
Soporte multi-zona horaria:

Campo timezone en la tabla usuarios.

Configuración por defecto: "America/Lima".

Pruebas exitosas:

Mensajes enviados correctamente a dos usuarios: Perú y Madrid.

Scheduler probado con simulación (--sim) y envío real (--send).

Tarea Programada Oficial:

Solo existe una tarea activa llamada "Recordatorios Académicos".

Configurada para correr todos los días a las 8:00 a.m.

Siguientes Pasos
Diseñar inscripción de estudiantes:

Registro de teléfono, cursos y fechas de exámenes mediante una interfaz.

Posibilidad de que cada estudiante ajuste su zona horaria.

Pensar en versión App Store/Google Play:

Explorar frameworks como Django REST API + React Native para convertir el sistema en app móvil.

Requisitos para publicar la app en tiendas oficiales (cuentas de desarrollador, políticas de privacidad, etc.).

Automatización global:

El scheduler debe adaptarse automáticamente a la zona horaria de cada usuario.

Pruebas
Simulación:
python scheduler.py --sim 2025-08-10

Envío real:
python scheduler.py --send