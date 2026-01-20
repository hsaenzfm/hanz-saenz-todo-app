"""Servidor de desarrollo simple para probar la funcionalidad localmente."""

import asyncio
import json
import os
from todo.read.src.app.queries import list_todos_query_sync
from todo.read.src.domain.models import ListTodosQueryParams
from todo.read.src.domain.exceptions import ValidationError, DatabaseError


def test_basic_functionality():
    """Prueba la funcionalidad básica sin base de datos."""
    print("🧪 Probando funcionalidad básica...")
    
    try:
        # Test 1: Parámetros por defecto
        print("\n📋 Test 1: Listado básico (página 1, 20 elementos)")
        params = ListTodosQueryParams()
        
        # Como no hay base de datos real, esto fallará pero podemos ver la estructura
        response = list_todos_query_sync(params)
        print("✅ Respuesta exitosa:")
        print_response(response)
        
    except DatabaseError as e:
        print(f"⚠️  Error de base de datos (esperado sin DB configurada): {e.message}")
        print("💡 Para probar con datos reales, configura PostgreSQL según el README")
        
    except ValidationError as e:
        print(f"❌ Error de validación: {e.message}")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def test_validation():
    """Prueba la validación de parámetros."""
    print("\n🔍 Probando validación de parámetros...")
    
    test_cases = [
        # (descripción, params, debería_fallar)
        ("Parámetros válidos", {"page": 1, "limit": 20}, False),
        ("Página inválida (0)", {"page": 0, "limit": 20}, True),
        ("Límite muy alto", {"page": 1, "limit": 101}, True),
        ("Status inválido", {"page": 1, "limit": 20, "status": "invalid"}, True),
        ("Sort field inválido", {"page": 1, "limit": 20, "sort": "invalid"}, True),
        ("Order inválido", {"page": 1, "limit": 20, "order": "invalid"}, True),
    ]
    
    for description, param_dict, should_fail in test_cases:
        print(f"\n  🧪 {description}")
        try:
            params = ListTodosQueryParams(**param_dict)
            response = list_todos_query_sync(params)
            
            if should_fail:
                print(f"    ⚠️  Se esperaba un error pero pasó")
            else:
                print(f"    ✅ Validación exitosa")
                
        except ValidationError as e:
            if should_fail:
                print(f"    ✅ Error de validación esperado: {e.message}")
            else:
                print(f"    ❌ Error de validación inesperado: {e.message}")
                
        except DatabaseError as e:
            print(f"    ⚠️  Error de base de datos (normal sin DB): {e.message}")
            
        except Exception as e:
            print(f"    ❌ Error inesperado: {e}")


def print_response(response):
    """Imprime una respuesta formateada."""
    response_dict = {
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
    }
    print(json.dumps(response_dict, indent=2))


def show_environment_status():
    """Muestra el estado del entorno."""
    print("🌍 Estado del entorno:")
    
    env_vars = [
        "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", 
        "POWERTOOLS_SERVICE_NAME", "POWERTOOLS_LOG_LEVEL"
    ]
    
    for var in env_vars:
        value = os.environ.get(var, "❌ No configurado")
        # Ocultar passwords
        if "PASSWORD" in var and value != "❌ No configurado":
            value = "*" * len(value)
        print(f"  {var}: {value}")


def main():
    """Función principal."""
    print("🚀 Servidor de Desarrollo - Todo Read Service")
    print("=" * 50)
    
    show_environment_status()
    test_validation()
    test_basic_functionality()
    
    print("\n" + "=" * 50)
    print("💡 Para probar con datos reales:")
    print("   1. Configura PostgreSQL según el README")
    print("   2. Crea el archivo .env con las variables de entorno")
    print("   3. Ejecuta el schema SQL")
    print("   4. Vuelve a ejecutar este script")
    print("\n💡 Para un servidor web interactivo, ejecuta:")
    print("   python mock_server.py")


if __name__ == "__main__":
    main()