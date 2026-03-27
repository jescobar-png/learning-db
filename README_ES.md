# Administrador de Tareas - Tutorial de Base de Datos

Un proyecto práctico de aprendizaje de bases de datos que demuestra una aplicación Python completa conectada a una base de datos MySQL usando Docker.

📖 **Disponible en otros idiomas**: [English](README.md)

## Descripción General

Este proyecto enseña fundamentos de bases de datos construyendo un sistema simple de gestión de tareas con:
- **Backend de Python** con capa de abstracción de base de datos limpia
- **Interfaz de Streamlit** para gestión interactiva de tareas
- **Base de datos MySQL** ejecutándose en Docker para persistencia de datos
- **Pruebas exhaustivas** para garantizar confiabilidad

### Conceptos Clave de Aprendizaje

- Conexión a base de datos y gestión de configuración
- Operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
- Consultas parametrizadas para prevención de inyección SQL
- Manejo de errores y mensajes de error amigables
- Anotaciones de tipo y documentación de código
- Pruebas de operaciones de base de datos
- Docker para bases de datos containerizadas

---

## Arquitectura del Proyecto

```
proyecto/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación Streamlit
│   └── db.py                # Capa de acceso a base de datos
├── tests/
│   ├── __init__.py
│   ├── test_db.py           # Pruebas unitarias de base de datos
│   └── test_main.py         # Pruebas de aplicación
├── docker-compose.yml       # Configuración del contenedor MySQL
├── requirements.txt         # Dependencias de Python
├── .env                     # Variables de entorno (local)
├── .env.example            # Plantilla de entorno (para git)
├── .gitignore              # Exclusiones de Git
└── README_ES.md            # Este archivo
```

### Patrón de Tres Agentes

1. **Agente de Aplicación** (`app/main.py`): Maneja la interacción del usuario y visualización
2. **Agente de Base de Datos** (`app/db.py`): Gestiona todas las operaciones de base de datos
3. **Agente de Infraestructura** (`docker-compose.yml`): Gestiona el contenedor MySQL

---

## Requisitos Previos

- Docker y Docker Compose
- Python 3.8+
- pip (gestor de paquetes de Python)

---

## Inicio Rápido

### 1. Clonar y Configurar

```bash
# Clonar el repositorio
git clone <URL-del-repositorio>

# Navegar al directorio del proyecto
cd db-tutorial

# Crear entorno virtual (opcional pero recomendado)
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Entorno

El proyecto incluye un archivo `.env` con valores predeterminados:

```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=testdb
MYSQL_USER=testuser
MYSQL_PASSWORD=testpass
```

Para personalizar, edita `.env` con tus valores deseados.

### 3. Iniciar el Contenedor MySQL

```bash
# Iniciar el contenedor MySQL
docker-compose up -d

# Verificar que está ejecutándose
docker ps
```

### 4. Ejecutar la Aplicación

```bash
# Iniciar la aplicación Streamlit
streamlit run app/main.py

# La aplicación se abrirá en http://localhost:8501
```

---

## Uso

### Crear una Tarea

1. Ingresa el título de la tarea (requerido)
2. Añade descripción opcional
3. Selecciona prioridad (baja, media, alta)
4. Haz clic en "Añadir Tarea"

### Gestionar Tareas

- **Actualizar Estado**: Cambia el estado de la tarea desde el menú desplegable
- **Eliminar**: Elimina la tarea con el botón de eliminar
- **Filtrar**: Usa la barra lateral para filtrar por estado y prioridad

### Ver Estadísticas

Ve el resumen de tareas en la barra lateral:
- Conteo total de tareas
- Conteo de tareas pendientes
- Conteo de tareas completadas

---

## Referencia de API

### Módulo de Base de Datos (`app/db.py`)

#### Conexión

```python
from app.db import connect_db, init_db

# Inicializar base de datos (crea tablas si es necesario)
init_db()

# Obtener conexión
connection = connect_db()
```

#### Operaciones de Tareas

```python
from app.db import (
    create_task,
    get_all_tasks,
    get_task_by_id,
    get_tasks_by_status,
    update_task,
    update_task_status,
    delete_task,
    get_task_statistics,
)

# Crear tarea
success, task_id, message = create_task(
    title="Mi Tarea",
    description="Detalles de la tarea",
    priority="high"
)

# Obtener todas las tareas
success, tasks, message = get_all_tasks()

# Obtener tarea individual
success, task, message = get_task_by_id(task_id=1)

# Filtrar por estado
success, tasks, message = get_tasks_by_status("pending")

# Actualizar tarea
success, message = update_task(
    task_id=1,
    title="Título Actualizado",
    priority="medium"
)

# Actualizar solo el estado
success, message = update_task_status(task_id=1, status="completed")

# Eliminar tarea
success, message = delete_task(task_id=1)

# Obtener estadísticas
success, stats, message = get_task_statistics()
```

Todas las funciones devuelven tuplas con:
- `success`: Booleano indicando resultado de la operación
- `data`: Datos devueltos (o mensaje para operaciones sin datos)
- `message`: Mensaje de estado legible para el usuario

---

## Pruebas

### Ejecutar Todas las Pruebas

```bash
# Instalar dependencias de prueba (incluidas en requirements.txt)
pip install pytest

# Ejecutar todas las pruebas
pytest

# Ejecutar archivo de prueba específico
pytest tests/test_db.py

# Ejecutar prueba específica
pytest tests/test_db.py::TestTaskCreation::test_create_task_success

# Ejecutar con salida detallada
pytest -v
```

### Cobertura de Pruebas

Las pruebas están organizadas por funcionalidad:

- **Pruebas de Conexión**: Conectividad de base de datos
- **Pruebas CRUD**: Operaciones de crear, leer, actualizar, eliminar
- **Pruebas de Filtro**: Filtrado basado en estado
- **Pruebas de Estadísticas**: Agregación de datos
- **Pruebas de Manejo de Errores**: Entradas inválidas y casos límite

---

## Esquema de Base de Datos

### Tabla de Tareas

```sql
CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Columnas:**
- `id`: Identificador único de tarea
- `title`: Título de la tarea (requerido)
- `description`: Descripción detallada de la tarea (opcional)
- `status`: Estado actual de la tarea
- `priority`: Nivel de urgencia de la tarea
- `created_at`: Marca de tiempo de creación
- `updated_at`: Marca de tiempo de última modificación

---

## Calidad del Código

### Estándares

Siguiendo mejores prácticas:
- **Anotaciones de Tipo**: Todas las funciones anotadas con tipos
- **Manejo de Errores**: Bloques try-catch con mensajes amigables
- **Documentación**: Docstrings para todas las funciones
- **Seguridad SQL**: Consultas parametrizadas previenen inyección SQL
- **Nomenclatura**: snake_case para funciones/variables, PascalCase para clases

### Formato

El código sigue estos estándares:
- **Longitud de Línea**: 88 caracteres (estándar de Black)
- **Indentación**: 4 espacios
- **Importaciones**: Organizadas según PEP 8
- **Comas Finales**: Usadas en construcciones de múltiples líneas

### Herramientas

```bash
# Formatear código
black app/ tests/

# Ordenar importaciones
isort app/ tests/

# Verificar estilo de código
flake8 app/ tests/

# Verificación de tipos
mypy app/
```

---

## Solución de Problemas

### Error de Conexión a Base de Datos

**Problema**: "Cannot connect to MySQL server"

**Soluciones**:
1. Verifica que el contenedor Docker está ejecutándose: `docker ps`
2. Comprueba que el archivo `.env` tiene las credenciales correctas de MySQL
3. Espera 10-15 segundos después de iniciar el contenedor para que MySQL se inicialice
4. Verifica que el puerto 3306 no está en uso: `lsof -i :3306`

### Módulo No Encontrado

**Problema**: "ModuleNotFoundError: No module named 'streamlit'"

**Solución**:
```bash
pip install -r requirements.txt
```

### Puerto Ya en Uso

**Problema**: "Error: port 3306 is already allocated"

**Soluciones**:
1. Detén el contenedor existente: `docker-compose down`
2. O usa un puerto diferente en `docker-compose.yml`:
   ```yaml
   ports:
     - "3307:3306"  # Cambia el puerto del host
   ```

### Permiso Denegado en .env

**Problema**: No se pueden leer las variables de entorno

**Solución**:
```bash
chmod 600 .env
```

---

## Flujo de Trabajo de Desarrollo

### Agregar una Nueva Función

1. **Planificar**: Añade función a `app/db.py` para operación de base de datos
2. **Implementar**: Escribe función de base de datos con anotaciones de tipo y manejo de errores
3. **Probar**: Añade pruebas a `tests/test_db.py`
4. **UI**: Añade componente de UI a `app/main.py` si es necesario
5. **Verificar**: Ejecuta todas las pruebas y pruebas manuales
6. **Commit**: Añade a git con mensaje descriptivo

### Ejemplo: Agregar Fecha de Vencimiento de Tarea

```python
# 1. Añadir a db.py
def update_task_due_date(task_id: int, due_date: str) -> Tuple[bool, str]:
    """Actualizar fecha de vencimiento de tarea."""
    # Implementación...

# 2. Añadir a tests/test_db.py
def test_update_task_due_date():
    """Probar configuración de fecha de vencimiento de tarea."""
    # Implementación de prueba...

# 3. Añadir UI a main.py
due_date = st.date_input("Fecha de Vencimiento")
if st.button("Establecer Fecha de Vencimiento"):
    success, msg = update_task_due_date(task_id, str(due_date))
```

---

## Flujo de Trabajo de Git

### Configuración Inicial

```bash
git add .
git commit -m "Configuración inicial del proyecto con base de datos y UI"
```

### Hacer Cambios

```bash
# Realizar cambios en el código...

# Preparar cambios
git add app/ tests/

# Commit con mensaje descriptivo
git commit -m "Agregar filtrado de prioridad de tareas"

# Enviar al remoto (si está configurado)
git push origin main
```

### Ignorar Archivos Sensibles

El archivo `.gitignore` excluye:
- Entornos virtuales (`venv/`, `myenv/`)
- Archivos de entorno (`.env`)
- Cachés de Python (`__pycache__/`)
- Configuración de IDE (`.vscode/`, `.idea/`)

---

## Consejos de Rendimiento

1. **Connection Pooling**: La versión actual crea una nueva conexión por operación. Para producción, usa `mysql-connector-python` con agrupación de conexiones.

2. **Optimización de Consultas**: Añade índices de base de datos para columnas frecuentemente buscadas.

3. **Caché**: Usa el decorador `@st.cache_data` de Streamlit para consultas costosas.

4. **Paginación**: Para listas de tareas grandes, implementa paginación en lugar de cargar todo de una vez.

---

## Recursos

- [Documentación de MySQL](https://dev.mysql.com/doc/)
- [Documentación de Streamlit](https://docs.streamlit.io/)
- [Python mysql-connector-python](https://dev.mysql.com/doc/connector-python/en/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Anotaciones de Tipo en Python](https://docs.python.org/3/library/typing.html)

---

## Licencia

Proyecto educativo - Libre de usar y modificar con propósitos de aprendizaje.

---

## Definición de Hecho

Una función está completa cuando:
- ✅ El código sigue las guías de estilo
- ✅ Anotaciones de tipo en todas las funciones
- ✅ Manejo de errores implementado
- ✅ Pruebas escritas y pasando
- ✅ Pruebas manuales realizadas
- ✅ Operaciones de base de datos verificadas
- ✅ UI muestra datos correctamente
- ✅ Sin errores o advertencias en consola
