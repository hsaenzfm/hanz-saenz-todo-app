"""AWS Lambda API entrypoint for todo read service."""

import json
from typing import Any, Dict
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.exceptions import (
    BadRequestError,
    InternalServerError,
    UnauthorizedError,
)
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit

from ..app.queries import list_todos_query_sync
from ..domain.models import ListTodosQueryParams
from ..domain.exceptions import ValidationError, DatabaseError, create_error_response

# Initialize AWS Lambda Powertools
logger = Logger(service="todo-read")
tracer = Tracer(service="todo-read")
metrics = Metrics(namespace="TodoApp", service="todo-read")

# API Gateway resolver
app = APIGatewayRestResolver()


@app.get("/todos")
@tracer.capture_method
def list_todos() -> Dict[str, Any]:
    """List todos with pagination, filtering, and sorting.
    
    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 20, max: 100)
        status (str): Filter by status ['pending', 'completed'] (optional)
        sort (str): Sort field ['created_at', 'due_date'] (default: 'created_at')
        order (str): Sort order ['asc', 'desc'] (default: 'desc')
    
    Returns:
        JSON response with todos and pagination metadata
        
    Raises:
        BadRequestError: For invalid query parameters
        InternalServerError: For unexpected errors
    """
    try:
        # Extract and validate query parameters
        params = _extract_query_params()
        
        # Add metrics
        metrics.add_metric(name="ListTodosRequest", unit=MetricUnit.Count, value=1)
        metrics.add_metadata(key="page", value=params.page)
        metrics.add_metadata(key="limit", value=params.limit)
        if params.status:
            metrics.add_metadata(key="status_filter", value=params.status)
        
        # Execute query
        logger.info(
            "Processing list todos request",
            extra={
                "page": params.page,
                "limit": params.limit, 
                "status": params.status,
                "sort": params.sort,
                "order": params.order,
            }
        )
        
        response = list_todos_query_sync(params)
        
        # Add success metrics
        metrics.add_metric(name="ListTodosSuccess", unit=MetricUnit.Count, value=1)
        metrics.add_metric(name="TodosReturned", unit=MetricUnit.Count, value=len(response.data))
        
        logger.info(
            "List todos request completed",
            extra={
                "total_count": response.pagination.total,
                "returned_count": len(response.data),
            }
        )
        
        # Convert response to dict for JSON serialization
        return {
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
            },
        }
        
    except ValidationError as e:
        logger.warning("Validation error in list todos", extra={"error": str(e)})
        metrics.add_metric(name="ListTodosValidationError", unit=MetricUnit.Count, value=1)
        raise BadRequestError(str(e))
        
    except DatabaseError as e:
        logger.error("Database error in list todos", extra={"error": str(e)})
        metrics.add_metric(name="ListTodosDatabaseError", unit=MetricUnit.Count, value=1)
        raise InternalServerError("Database error occurred")
        
    except Exception as e:
        logger.error("Unexpected error in list todos", extra={"error": str(e)})
        metrics.add_metric(name="ListTodosUnexpectedError", unit=MetricUnit.Count, value=1)
        raise InternalServerError("An unexpected error occurred")


def _extract_query_params() -> ListTodosQueryParams:
    """Extract and validate query parameters from API Gateway event.
    
    Returns:
        ListTodosQueryParams with validated parameters
        
    Raises:
        ValidationError: If parameters are invalid
    """
    # Get query string parameters
    params = app.current_event.query_string_parameters or {}
    
    try:
        # Extract parameters with defaults
        page = int(params.get("page", "1"))
        limit = int(params.get("limit", "20"))
        status = params.get("status")
        sort = params.get("sort", "created_at")
        order = params.get("order", "desc")
        
        # Create and validate parameters
        query_params = ListTodosQueryParams(
            page=page,
            limit=limit,
            status=status,
            sort=sort,
            order=order,
        )
        
        # Validate
        errors = query_params.validate()
        if errors:
            # Return first validation error with field information
            raise ValidationError(f"Invalid parameter: {errors[0]}")
        
        return query_params
        
    except ValueError as e:
        # Handle integer conversion errors
        if "page" in str(e):
            raise ValidationError("Invalid parameter: page must be a valid integer", field="page")
        elif "limit" in str(e):
            raise ValidationError("Invalid parameter: limit must be a valid integer", field="limit")
        else:
            raise ValidationError(f"Invalid parameter format: {str(e)}")


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST, log_event=True)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler for todo read service.
    
    Args:
        event: AWS Lambda event from API Gateway
        context: AWS Lambda context
        
    Returns:
        API Gateway response
    """
    return app.resolve(event, context)