# Todo Application - List Todos Feature

Aplicación de gestión de tareas con funcionalidades de listado, paginación, filtrado y ordenamiento.

## 🚀 Inicio Rápido

### Prerrequisitos

- **Python 3.11+** instalado
- **UV** (gestor de paquetes Python) o **pip**
- **PostgreSQL** (para pruebas con base de datos real)

### 1. Instalación de Dependencias

```bash
# Si usas UV (recomendado)
uv sync

# O si usas pip
pip install -e .
pip install -e ".[dev]"
```

### 2. Configuración del Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Variables de entorno para desarrollo local
DB_HOST=localhost
DB_PORT=5432
DB_NAME=todoapp_dev
DB_USER=postgres
DB_PASSWORD=tu_password
DB_SSL_MODE=disable
DB_CONNECT_TIMEOUT=30

# AWS Lambda Powertools (para desarrollo local)
POWERTOOLS_SERVICE_NAME=todo-read
POWERTOOLS_LOG_LEVEL=DEBUG
POWERTOOLS_METRICS_NAMESPACE=TodoApp
POWERTOOLS_LOGGER_LOG_EVENT=false
POWERTOOLS_LOGGER_SAMPLE_RATE=1.0
POWERTOOLS_TRACE_CAPTURE_RESPONSE=true
POWERTOOLS_TRACE_CAPTURE_ERROR=true
```

### 3. Configuración de Base de Datos (Opcional)

Si quieres probar con PostgreSQL real:

```bash
# Crear base de datos
psql -U postgres -c "CREATE DATABASE todoapp_dev;"

# Ejecutar schema
psql -U postgres -d todoapp_dev -f todo/read/src/infra/schema.sql

# Insertar datos de prueba (opcional)
psql -U postgres -d todoapp_dev -c "
INSERT INTO todo_read_projection (id, title, description, status, created_at, updated_at, due_date)
VALUES 
  ('550e8400-e29b-41d4-a716-446655440001', 'Completar documentación', 'Escribir documentación de API', 'pending', '2026-01-20T10:00:00Z', '2026-01-20T10:00:00Z', '2026-01-25'),
  ('550e8400-e29b-41d4-a716-446655440002', 'Revisar código', 'Hacer review del PR', 'completed', '2026-01-19T09:00:00Z', '2026-01-19T15:00:00Z', '2026-01-20'),
  ('550e8400-e29b-41d4-a716-446655440003', 'Configurar CI/CD', 'Setup pipeline', 'pending', '2026-01-18T08:00:00Z', '2026-01-18T08:00:00Z', null);
"
```

## 🧪 Ejecutar Tests

### Tests Unitarios e Integración
```bash
# Ejecutar todos los tests
pytest

# Tests con coverage
pytest --cov=todo --cov-report=html

# Tests específicos
pytest todo/read/tests/integration/test_list_todos.py -v
pytest todo/read/tests/performance/ -v
```

### Tests de Performance
```bash
# Tests de rendimiento (simula 1000+ todos)
pytest todo/read/tests/performance/test_list_performance.py -v -s
```

## 🖥️ Ejecutar Localmente

### Opción 1: Servidor de Desarrollo Directo

Crea un servidor de desarrollo simple:

```python
# dev_server.py
import asyncio
import json
from todo.read.src.app.queries import list_todos_query_sync
from todo.read.src.domain.models import ListTodosQueryParams
from todo.read.src.domain.exceptions import ValidationError, DatabaseError

def test_local():
    """Prueba local del endpoint"""
    try:
        # Ejemplo: listar todos con paginación
        params = ListTodosQueryParams(page=1, limit=5)
        response = list_todos_query_sync(params)
        
        print("✅ Respuesta exitosa:")
        print(json.dumps({
            "data": [
                {
                    "id": todo.id,
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status,
                    "created_at": todo.created_at,
                    "updated_at": todo.updated_at,
                    "due_date": todo.due_date,
                }
                for todo in response.data
            ],
            "pagination": {
                "page": response.pagination.page,
                "limit": response.pagination.limit,
                "total": response.pagination.total,
                "totalPages": response.pagination.totalPages,
            }
        }, indent=2))
        
    except ValidationError as e:
        print(f"❌ Error de validación: {e.message}")
    except DatabaseError as e:
        print(f"❌ Error de base de datos: {e.message}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_local()
```

```bash
# Ejecutar el test local
python dev_server.py
```

### Opción 2: Con AWS SAM (si tienes SAM instalado)

```bash
# Instalar AWS SAM CLI primero
# Windows: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

# Construir el proyecto
sam build --template deploy/lambda-config.yaml

# Ejecutar localmente
sam local start-api --template deploy/lambda-config.yaml --port 3000

# Probar el endpoint
curl "http://localhost:3000/todos?page=1&limit=5&status=pending&sort=created_at&order=desc"
```

### Opción 3: Mock para Desarrollo

Crea un mock simple sin base de datos:

```python
# mock_server.py
from flask import Flask, request, jsonify
from todo.read.src.domain.models import ListTodosQueryParams, TodoItem, PaginationMetadata, ListTodosResponse

app = Flask(__name__)

# Datos mock
MOCK_TODOS = [
    TodoItem("1", "Completar proyecto", "Terminar funcionalidad", "pending", "2026-01-20T10:00:00Z", "2026-01-20T10:00:00Z", "2026-01-25"),
    TodoItem("2", "Revisar código", "Code review", "completed", "2026-01-19T09:00:00Z", "2026-01-19T15:00:00Z", "2026-01-20"),
    TodoItem("3", "Setup CI/CD", "Configurar pipeline", "pending", "2026-01-18T08:00:00Z", "2026-01-18T08:00:00Z", None),
]

@app.route('/todos', methods=['GET'])
def list_todos():
    # Extraer parámetros
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    status = request.args.get('status')
    sort = request.args.get('sort', 'created_at')
    order = request.args.get('order', 'desc')
    
    # Filtrar por status
    filtered_todos = MOCK_TODOS
    if status:
        filtered_todos = [t for t in filtered_todos if t.status == status]
    
    # Simular paginación
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_todos = filtered_todos[start_idx:end_idx]
    
    # Crear respuesta
    response = {
        "data": [
            {
                "id": todo.id,
                "title": todo.title,
                "description": todo.description,
                "status": todo.status,
                "created_at": todo.created_at,
                "updated_at": todo.updated_at,
                "due_date": todo.due_date,
            }
            for todo in page_todos
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(filtered_todos),
            "totalPages": (len(filtered_todos) + limit - 1) // limit,
        }
    }
    
    return jsonify(response)

if __name__ == '__main__':
    print("🚀 Servidor mock corriendo en http://localhost:5000")
    print("📝 Prueba: http://localhost:5000/todos?page=1&limit=2&status=pending")
    app.run(debug=True, host='0.0.0.0', port=5000)
```

```bash
# Instalar Flask si no lo tienes
pip install flask

# Ejecutar servidor mock
python mock_server.py
```

## 🌐 Endpoints Disponibles

### GET /todos

**Parámetros de consulta:**
- `page` (int, opcional): Número de página (default: 1)
- `limit` (int, opcional): Elementos por página (default: 20, max: 100)
- `status` (string, opcional): Filtro por estado ['pending', 'completed']
- `sort` (string, opcional): Campo de ordenamiento ['created_at', 'due_date'] (default: 'created_at')
- `order` (string, opcional): Dirección ['asc', 'desc'] (default: 'desc')

**Ejemplos:**
```bash
# Listar todos los todos (página 1)
curl "http://localhost:5000/todos"

# Filtrar por pending, ordenar por fecha de creación
curl "http://localhost:5000/todos?status=pending&sort=created_at&order=desc"

# Página 2 con límite de 5 elementos
curl "http://localhost:5000/todos?page=2&limit=5"

# Filtrar completed, ordenar por due_date
curl "http://localhost:5000/todos?status=completed&sort=due_date&order=asc"
```

## 🏗️ Estructura del Proyecto

```
todo/read/
├── src/
│   ├── entrypoints/    # Puntos de entrada (Lambda handlers)
│   ├── app/            # Lógica de aplicación (queries)
│   ├── domain/         # Modelos de dominio y validación
│   └── infra/          # Infraestructura (DB, configuración)
└── tests/
    ├── integration/    # Tests de integración
    └── performance/    # Tests de rendimiento
```

## 🐛 Solución de Problemas

### Error "sam command not found"
```bash
# Instalar AWS SAM CLI
# Windows: Descargar desde https://github.com/aws/aws-sam-cli/releases
# macOS: brew install aws-sam-cli
# Linux: pip install aws-sam-cli
```

### Error de conexión a base de datos
- Verifica que PostgreSQL esté ejecutándose
- Confirma las credenciales en `.env`
- Ejecuta primero con el servidor mock

### Tests fallan
```bash
# Verificar dependencias
pip install -e ".[dev]"

# Ejecutar tests con más detalle
pytest -v -s
```

## 📚 Documentación Adicional

- [OpenAPI Spec](todo/read/src/entrypoints/openapi.py) - Especificación completa de la API
- [Configuración AWS](deploy/lambda-config.yaml) - Configuración de deployment
- [Tests](todo/read/tests/) - Suite completa de pruebas