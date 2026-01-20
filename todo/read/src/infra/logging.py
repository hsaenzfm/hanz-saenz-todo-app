"""Logging infrastructure for todo read service."""

import os
from aws_lambda_powertools import Logger
from .config import get_lambda_config


def setup_logger(service_name: str = "todo-read") -> Logger:
    """Setup structured logging with AWS Lambda Powertools.
    
    Args:
        service_name: Service name for logging context
        
    Returns:
        Configured Logger instance
    """
    config = get_lambda_config()
    
    # Set environment variables for Lambda Powertools
    os.environ.setdefault("POWERTOOLS_SERVICE_NAME", config.powertools_service_name)
    os.environ.setdefault("POWERTOOLS_LOG_LEVEL", config.log_level)
    os.environ.setdefault("POWERTOOLS_LOGGER_SAMPLE_RATE", str(config.powertools_logger_sample_rate))
    os.environ.setdefault("POWERTOOLS_LOGGER_LOG_EVENT", str(config.powertools_logger_log_event).lower())
    
    logger = Logger(
        service=service_name,
        level=config.log_level,
        sample_rate=config.powertools_logger_sample_rate,
        log_uncaught_exceptions=True,
    )
    
    return logger


# Global logger instance
logger = setup_logger()


def log_query_performance(
    query_name: str, 
    duration_ms: float, 
    record_count: int,
    filters: dict = None
) -> None:
    """Log query performance metrics.
    
    Args:
        query_name: Name of the query being executed
        duration_ms: Query execution duration in milliseconds  
        record_count: Number of records returned
        filters: Query filters applied (optional)
    """
    logger.info(
        f"Query performance: {query_name}",
        extra={
            "query_name": query_name,
            "duration_ms": duration_ms,
            "record_count": record_count,
            "filters": filters or {},
        }
    )


def log_database_error(error: Exception, query: str = None, parameters: list = None) -> None:
    """Log database errors with context.
    
    Args:
        error: The database exception
        query: SQL query that failed (optional)
        parameters: Query parameters (optional)
    """
    logger.error(
        "Database error occurred",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "query": query,
            "parameters": parameters,
        }
    )


def log_validation_error(field: str, value: any, reason: str) -> None:
    """Log validation errors with field context.
    
    Args:
        field: Field name that failed validation
        value: Invalid value provided
        reason: Reason for validation failure
    """
    logger.warning(
        "Validation error",
        extra={
            "field": field,
            "value": str(value),
            "reason": reason,
        }
    )