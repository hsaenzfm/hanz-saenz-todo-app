"""Servidor mock con Flask para desarrollo y pruebas interactivas."""

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    print("❌ Flask no está instalado. Instálalo con: pip install flask flask-cors")
    exit(1)

from todo.read.src.domain.models import TodoItem, PaginationMetadata
import math

app = Flask(__name__)
CORS(app)  # Permitir CORS para desarrollo

# Datos mock para desarrollo
MOCK_TODOS = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "Completar documentación del proyecto",
        "description": "Escribir documentación completa de la API y guías de usuario",
        "status": "pending",
        "created_at": "2026-01-20T14:30:00Z",
        "updated_at": "2026-01-20T14:30:00Z",
        "due_date": "2026-01-25"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440002", 
        "title": "Revisar pull request #123",
        "description": "Code review para las nuevas funcionalidades",
        "status": "completed",
        "created_at": "2026-01-20T10:15:00Z",
        "updated_at": "2026-01-20T15:45:00Z",
        "due_date": "2026-01-21"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "title": "Configurar pipeline CI/CD",
        "description": "Setup de integración continua con GitHub Actions",
        "status": "pending",
        "created_at": "2026-01-19T16:20:00Z",
        "updated_at": "2026-01-19T16:20:00Z",
        "due_date": None
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440004",
        "title": "Optimizar queries de base de datos",
        "description": "Mejorar rendimiento de consultas PostgreSQL",
        "status": "pending",
        "created_at": "2026-01-19T09:10:00Z",
        "updated_at": "2026-01-19T09:10:00Z",
        "due_date": "2026-01-23"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440005",
        "title": "Escribir tests de integración",
        "description": "Crear suite completa de tests end-to-end",
        "status": "completed",
        "created_at": "2026-01-18T13:45:00Z",
        "updated_at": "2026-01-19T11:30:00Z",
        "due_date": "2026-01-20"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440006",
        "title": "Implementar autenticación OAuth",
        "description": "Integrar autenticación con Google y GitHub",
        "status": "pending",
        "created_at": "2026-01-18T08:30:00Z",
        "updated_at": "2026-01-18T08:30:00Z",
        "due_date": "2026-01-30"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440007",
        "title": "Configurar monitoreo con Grafana",
        "description": "Setup de dashboards y alertas",
        "status": "completed",
        "created_at": "2026-01-17T14:15:00Z",
        "updated_at": "2026-01-18T10:20:00Z",
        "due_date": "2026-01-19"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440008",
        "title": "Migrar a microservicios",
        "description": "Refactor monolito a arquitectura de microservicios",
        "status": "pending",
        "created_at": "2026-01-16T11:00:00Z",
        "updated_at": "2026-01-16T11:00:00Z",
        "due_date": None
    }
]

def validate_params(request):
    """Valida los parámetros de la request."""
    errors = []
    
    # Validar page
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            errors.append("page must be >= 1")
    except ValueError:
        errors.append("page must be a valid integer")
        page = 1
    
    # Validar limit
    try:
        limit = int(request.args.get('limit', 20))
        if limit < 1:
            errors.append("limit must be >= 1")
        elif limit > 100:
            errors.append("limit must be <= 100")
    except ValueError:
        errors.append("limit must be a valid integer")
        limit = 20
    
    # Validar status
    status = request.args.get('status')
    if status is not None and status not in ['pending', 'completed']:
        errors.append("status must be one of [pending, completed]")
        status = None
    
    # Validar sort
    sort = request.args.get('sort', 'created_at')
    if sort not in ['created_at', 'due_date']:
        errors.append("sort must be one of [created_at, due_date]")
        sort = 'created_at'
    
    # Validar order
    order = request.args.get('order', 'desc')
    if order not in ['asc', 'desc']:
        errors.append("order must be one of [asc, desc]")
        order = 'desc'
    
    return {
        'page': page,
        'limit': limit,
        'status': status,
        'sort': sort,
        'order': order,
        'errors': errors
    }

def filter_and_sort_todos(todos, status, sort, order):
    """Filtra y ordena los todos según los parámetros."""
    # Filtrar por status
    if status:
        todos = [t for t in todos if t['status'] == status]
    
    # Ordenar
    if sort == 'due_date':
        # Para due_date, manejar NULLs apropiadamente
        if order == 'asc':
            todos.sort(key=lambda x: (x['due_date'] is None, x['due_date'] or ''))
        else:
            todos.sort(key=lambda x: (x['due_date'] is None, x['due_date'] or ''), reverse=True)
    else:  # created_at
        todos.sort(key=lambda x: x['created_at'], reverse=(order == 'desc'))
    
    return todos

@app.route('/', methods=['GET'])
def home():
    """Página de inicio con información de la API."""
    return jsonify({
        "message": "Todo Read Service API - Mock Server",
        "version": "1.0.0",
        "endpoints": {
            "GET /todos": "List todos with pagination, filtering, and sorting",
            "GET /health": "Health check endpoint"
        },
        "examples": {
            "basic": "/todos",
            "with_pagination": "/todos?page=1&limit=5",
            "with_filtering": "/todos?status=pending",
            "with_sorting": "/todos?sort=due_date&order=asc",
            "combined": "/todos?page=1&limit=3&status=pending&sort=created_at&order=desc"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "todo-read-mock",
        "total_todos": len(MOCK_TODOS)
    })

@app.route('/todos', methods=['GET'])
def list_todos():
    """Endpoint principal para listar todos."""
    # Validar parámetros
    params = validate_params(request)
    
    if params['errors']:
        return jsonify({
            "error": {
                "code": "INVALID_PARAMETER",
                "message": f"Invalid parameter: {params['errors'][0]}"
            }
        }), 400
    
    # Filtrar y ordenar todos
    filtered_todos = filter_and_sort_todos(
        MOCK_TODOS.copy(), 
        params['status'], 
        params['sort'], 
        params['order']
    )
    
    # Aplicar paginación
    total = len(filtered_todos)
    start_idx = (params['page'] - 1) * params['limit']
    end_idx = start_idx + params['limit']
    page_todos = filtered_todos[start_idx:end_idx]
    
    # Calcular metadatos de paginación
    total_pages = math.ceil(total / params['limit']) if total > 0 else 0
    
    # Crear respuesta
    response = {
        "data": page_todos,
        "pagination": {
            "page": params['page'],
            "limit": params['limit'],
            "total": total,
            "totalPages": total_pages
        }
    }
    
    return jsonify(response)

@app.route('/todos/stats', methods=['GET'])
def todos_stats():
    """Endpoint adicional para estadísticas de todos."""
    pending_count = len([t for t in MOCK_TODOS if t['status'] == 'pending'])
    completed_count = len([t for t in MOCK_TODOS if t['status'] == 'completed'])
    with_due_date = len([t for t in MOCK_TODOS if t['due_date'] is not None])
    
    return jsonify({
        "total": len(MOCK_TODOS),
        "pending": pending_count,
        "completed": completed_count,
        "with_due_date": with_due_date,
        "without_due_date": len(MOCK_TODOS) - with_due_date
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": {
            "code": "NOT_FOUND",
            "message": "Endpoint not found. Try GET /todos"
        }
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred"
        }
    }), 500

def print_startup_info():
    """Imprime información de inicio del servidor."""
    print("🚀 Todo Read Service - Mock Server")
    print("=" * 50)
    print(f"📍 URL: http://localhost:5000")
    print(f"📊 Datos mock: {len(MOCK_TODOS)} todos")
    print(f"   - Pending: {len([t for t in MOCK_TODOS if t['status'] == 'pending'])}")
    print(f"   - Completed: {len([t for t in MOCK_TODOS if t['status'] == 'completed'])}")
    print("\n🌐 Endpoints disponibles:")
    print("   GET /              - Información de la API")
    print("   GET /health        - Health check")
    print("   GET /todos         - Listar todos (endpoint principal)")
    print("   GET /todos/stats   - Estadísticas de todos")
    print("\n📝 Ejemplos de uso:")
    print("   curl http://localhost:5000/todos")
    print("   curl http://localhost:5000/todos?page=1&limit=3")
    print("   curl http://localhost:5000/todos?status=pending")
    print("   curl http://localhost:5000/todos?sort=due_date&order=asc")
    print("   curl 'http://localhost:5000/todos?page=1&limit=2&status=pending&sort=created_at&order=desc'")
    print("\n🌍 También funciona en el navegador:")
    print("   http://localhost:5000/todos?status=pending&limit=3")
    print("=" * 50)

if __name__ == '__main__':
    print_startup_info()
    app.run(debug=True, host='0.0.0.0', port=5000)