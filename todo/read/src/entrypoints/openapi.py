"""OpenAPI documentation generation for todo read service."""

from typing import Dict, Any


def get_openapi_spec() -> Dict[str, Any]:
    """Generate OpenAPI 3.0 specification for todo read service.
    
    Returns:
        OpenAPI specification dictionary
    """
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Todo Read Service API",
            "description": "API for listing todos with pagination, filtering, and sorting",
            "version": "1.0.0",
            "contact": {
                "name": "Todo Read Service",
                "email": "support@todoapp.com"
            }
        },
        "servers": [
            {
                "url": "https://api.todoapp.com/v1",
                "description": "Production server"
            },
            {
                "url": "https://staging-api.todoapp.com/v1", 
                "description": "Staging server"
            }
        ],
        "paths": {
            "/todos": {
                "get": {
                    "summary": "List todos",
                    "description": (
                        "Retrieve a paginated, filtered, and sorted list of todos.\n\n"
                        "Features:\n"
                        "- Pagination via `page` and `limit` parameters\n"
                        "- Status filtering via `status` parameter  \n"
                        "- Sorting by creation date or due date via `sort` and `order` parameters\n\n"
                        "Default behavior:\n"
                        "- Page 1 with 20 items per page\n"
                        "- Sorted by creation date descending (newest first)\n"
                        "- All statuses included"
                    ),
                    "operationId": "listTodos",
                    "tags": ["todos"],
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "description": "Page number (1-based)",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "minimum": 1,
                                "default": 1
                            },
                            "example": 1
                        },
                        {
                            "name": "limit",
                            "in": "query", 
                            "description": "Number of items per page (maximum 100)",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 100,
                                "default": 20
                            },
                            "example": 20
                        },
                        {
                            "name": "status",
                            "in": "query",
                            "description": "Filter todos by completion status",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["pending", "completed"]
                            },
                            "example": "pending"
                        },
                        {
                            "name": "sort",
                            "in": "query",
                            "description": "Field to sort by",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["created_at", "due_date"],
                                "default": "created_at"
                            },
                            "example": "created_at"
                        },
                        {
                            "name": "order",
                            "in": "query",
                            "description": "Sort order",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["asc", "desc"],
                                "default": "desc"
                            },
                            "example": "desc"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Successfully retrieved todos",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ListTodosResponse"
                                    },
                                    "examples": {
                                        "success_with_data": {
                                            "summary": "Success with todos",
                                            "value": {
                                                "data": [
                                                    {
                                                        "id": "123e4567-e89b-12d3-a456-426614174000",
                                                        "title": "Complete project documentation",
                                                        "description": "Write API documentation",
                                                        "status": "pending",
                                                        "created_at": "2026-01-20T10:00:00Z",
                                                        "updated_at": "2026-01-20T10:00:00Z",
                                                        "due_date": "2026-01-25"
                                                    }
                                                ],
                                                "pagination": {
                                                    "page": 1,
                                                    "limit": 20,
                                                    "total": 45,
                                                    "totalPages": 3
                                                }
                                            }
                                        },
                                        "success_empty": {
                                            "summary": "Success with empty results",
                                            "value": {
                                                "data": [],
                                                "pagination": {
                                                    "page": 5,
                                                    "limit": 20, 
                                                    "total": 45,
                                                    "totalPages": 3
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Bad request - invalid query parameters",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    },
                                    "examples": {
                                        "invalid_page": {
                                            "summary": "Invalid page number",
                                            "value": {
                                                "error": {
                                                    "code": "INVALID_PARAMETER",
                                                    "message": "Invalid parameter: page must be >= 1",
                                                    "field": "page"
                                                }
                                            }
                                        },
                                        "invalid_status": {
                                            "summary": "Invalid status value",
                                            "value": {
                                                "error": {
                                                    "code": "INVALID_PARAMETER",
                                                    "message": "Invalid parameter: status must be one of [pending, completed]",
                                                    "field": "status"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "Internal server error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ErrorResponse"
                                    },
                                    "example": {
                                        "error": {
                                            "code": "INTERNAL_ERROR",
                                            "message": "An unexpected error occurred"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "Todo": {
                    "type": "object",
                    "description": "A todo item",
                    "required": ["id", "title", "status", "created_at", "updated_at"],
                    "properties": {
                        "id": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for the todo",
                            "example": "123e4567-e89b-12d3-a456-426614174000"
                        },
                        "title": {
                            "type": "string",
                            "maxLength": 255,
                            "description": "Todo title",
                            "example": "Complete project documentation"
                        },
                        "description": {
                            "type": "string",
                            "nullable": True,
                            "description": "Optional todo description",
                            "example": "Write API documentation"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "completed"],
                            "description": "Completion status",
                            "example": "pending"
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Creation timestamp (ISO 8601)",
                            "example": "2026-01-20T10:00:00Z"
                        },
                        "updated_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Last update timestamp (ISO 8601)",
                            "example": "2026-01-20T10:00:00Z"
                        },
                        "due_date": {
                            "type": "string",
                            "format": "date",
                            "nullable": True,
                            "description": "Optional due date (ISO 8601 date)",
                            "example": "2026-01-25"
                        }
                    }
                },
                "PaginationMetadata": {
                    "type": "object",
                    "description": "Pagination metadata",
                    "required": ["page", "limit", "total", "totalPages"],
                    "properties": {
                        "page": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Current page number (1-based)",
                            "example": 1
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Number of items per page",
                            "example": 20
                        },
                        "total": {
                            "type": "integer",
                            "minimum": 0,
                            "description": "Total count of items matching filters",
                            "example": 45
                        },
                        "totalPages": {
                            "type": "integer",
                            "minimum": 0,
                            "description": "Total number of pages",
                            "example": 3
                        }
                    }
                },
                "ListTodosResponse": {
                    "type": "object",
                    "description": "Response for list todos endpoint",
                    "required": ["data", "pagination"],
                    "properties": {
                        "data": {
                            "type": "array",
                            "description": "Array of todo items (may be empty)",
                            "items": {
                                "$ref": "#/components/schemas/Todo"
                            }
                        },
                        "pagination": {
                            "$ref": "#/components/schemas/PaginationMetadata"
                        }
                    }
                },
                "ErrorResponse": {
                    "type": "object",
                    "description": "Standard error response format",
                    "required": ["error"],
                    "properties": {
                        "error": {
                            "type": "object",
                            "required": ["code", "message"],
                            "properties": {
                                "code": {
                                    "type": "string",
                                    "description": "Error code",
                                    "enum": ["INVALID_PARAMETER", "DATABASE_ERROR", "INTERNAL_ERROR"],
                                    "example": "INVALID_PARAMETER"
                                },
                                "message": {
                                    "type": "string",
                                    "description": "Human-readable error message",
                                    "example": "Invalid parameter: page must be >= 1"
                                },
                                "field": {
                                    "type": "string",
                                    "description": "Field name that caused the error (optional)",
                                    "example": "page"
                                }
                            }
                        }
                    }
                }
            }
        },
        "tags": [
            {
                "name": "todos",
                "description": "Todo operations"
            }
        ]
    }


def generate_openapi_yaml() -> str:
    """Generate OpenAPI specification in YAML format.
    
    Returns:
        YAML string representation of the OpenAPI spec
    """
    import yaml
    spec = get_openapi_spec()
    return yaml.dump(spec, default_flow_style=False, sort_keys=False)


def generate_openapi_json() -> str:
    """Generate OpenAPI specification in JSON format.
    
    Returns:
        JSON string representation of the OpenAPI spec
    """
    import json
    spec = get_openapi_spec()
    return json.dumps(spec, indent=2)