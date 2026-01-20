"""Database and AWS Lambda configuration for todo read service."""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """PostgreSQL database configuration."""
    
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "require"
    connect_timeout: int = 30
    
    @property
    def connection_string(self) -> str:
        """Get PostgreSQL connection string."""
        return (
            f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/"
            f"{self.database}?sslmode={self.ssl_mode}&connect_timeout={self.connect_timeout}"
        )


def get_database_config() -> DatabaseConfig:
    """Get database configuration from environment variables.
    
    Environment Variables:
        DB_HOST: PostgreSQL host
        DB_PORT: PostgreSQL port (default: 5432)
        DB_NAME: Database name
        DB_USER: Database username
        DB_PASSWORD: Database password
        DB_SSL_MODE: SSL mode (default: require)
        DB_CONNECT_TIMEOUT: Connection timeout in seconds (default: 30)
    
    Returns:
        DatabaseConfig: Configuration object
        
    Raises:
        ValueError: If required environment variables are missing
    """
    host = os.environ.get("DB_HOST")
    if not host:
        raise ValueError("DB_HOST environment variable is required")
        
    database = os.environ.get("DB_NAME")
    if not database:
        raise ValueError("DB_NAME environment variable is required")
        
    username = os.environ.get("DB_USER")
    if not username:
        raise ValueError("DB_USER environment variable is required")
        
    password = os.environ.get("DB_PASSWORD")
    if not password:
        raise ValueError("DB_PASSWORD environment variable is required")
    
    port = int(os.environ.get("DB_PORT", "5432"))
    ssl_mode = os.environ.get("DB_SSL_MODE", "require")
    connect_timeout = int(os.environ.get("DB_CONNECT_TIMEOUT", "30"))
    
    return DatabaseConfig(
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
        ssl_mode=ssl_mode,
        connect_timeout=connect_timeout,
    )


@dataclass
class LambdaConfig:
    """AWS Lambda Powertools configuration."""
    
    service_name: str = "todo-read"
    log_level: str = "INFO"
    powertools_service_name: str = "todo-read"
    powertools_metrics_namespace: str = "TodoApp"
    powertools_logger_log_event: bool = False
    powertools_logger_sample_rate: float = 0.01
    powertools_trace_capture_response: bool = True
    powertools_trace_capture_error: bool = True


def get_lambda_config() -> LambdaConfig:
    """Get Lambda Powertools configuration from environment variables.
    
    Environment Variables:
        POWERTOOLS_SERVICE_NAME: Service name for tracing/logging (default: todo-read)
        POWERTOOLS_LOG_LEVEL: Log level (default: INFO)
        POWERTOOLS_METRICS_NAMESPACE: Metrics namespace (default: TodoApp)
        POWERTOOLS_LOGGER_LOG_EVENT: Log event details (default: false)
        POWERTOOLS_LOGGER_SAMPLE_RATE: Log sampling rate (default: 0.01)
        POWERTOOLS_TRACE_CAPTURE_RESPONSE: Capture response in traces (default: true)
        POWERTOOLS_TRACE_CAPTURE_ERROR: Capture errors in traces (default: true)
    
    Returns:
        LambdaConfig: Configuration object
    """
    return LambdaConfig(
        service_name=os.environ.get("POWERTOOLS_SERVICE_NAME", "todo-read"),
        log_level=os.environ.get("POWERTOOLS_LOG_LEVEL", "INFO"),
        powertools_service_name=os.environ.get("POWERTOOLS_SERVICE_NAME", "todo-read"),
        powertools_metrics_namespace=os.environ.get("POWERTOOLS_METRICS_NAMESPACE", "TodoApp"),
        powertools_logger_log_event=os.environ.get("POWERTOOLS_LOGGER_LOG_EVENT", "false").lower() == "true",
        powertools_logger_sample_rate=float(os.environ.get("POWERTOOLS_LOGGER_SAMPLE_RATE", "0.01")),
        powertools_trace_capture_response=os.environ.get("POWERTOOLS_TRACE_CAPTURE_RESPONSE", "true").lower() == "true",
        powertools_trace_capture_error=os.environ.get("POWERTOOLS_TRACE_CAPTURE_ERROR", "true").lower() == "true",
    )