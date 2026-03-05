"""
Error Handling and Logging Module for Smart Irrigation System.

This module provides comprehensive error handling, structured logging,
and circuit breaker patterns for external services.

Requirements: 16.1, 16.2, 16.3, 16.4, 16.5
"""

import logging
import json
import sys
from datetime import datetime
from typing import Optional, Callable, Any
from functools import wraps
import time

# ============================================
# Structured Logging Configuration
# ============================================

class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Requirements: 16.4
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_data['endpoint'] = record.endpoint
        if hasattr(record, 'response_time'):
            log_data['response_time'] = record.response_time
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        if hasattr(record, 'component'):
            log_data['component'] = record.component
        
        return json.dumps(log_data)


def setup_logging(log_level: str = 'INFO') -> logging.Logger:
    """
    Set up structured logging with JSON formatter.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    
    Requirements: 16.4
    """
    logger = logging.getLogger('irrigation_system')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler for persistent logs
    file_handler = logging.FileHandler('Code/backend/data/application.log')
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logging()


# ============================================
# Request Logging
# ============================================

def log_api_request(request_id: str, endpoint: str, response_time: float, 
                    status_code: int, error: Optional[str] = None):
    """
    Log API request with structured data.
    
    Args:
        request_id: Unique request identifier
        endpoint: API endpoint path
        response_time: Response time in milliseconds
        status_code: HTTP status code
        error: Error message if request failed
    
    Requirements: 16.4
    """
    log_data = {
        'request_id': request_id,
        'endpoint': endpoint,
        'response_time': response_time,
        'status_code': status_code
    }
    
    if error:
        logger.error(f"API request failed: {error}", extra=log_data)
    else:
        logger.info(f"API request completed", extra=log_data)


# ============================================
# Error Logging
# ============================================

def log_error(component: str, error_message: str, exception: Optional[Exception] = None):
    """
    Log error with component information and stack trace.
    
    Args:
        component: Component name where error occurred
        error_message: Description of the error
        exception: Exception object if available
    
    Requirements: 16.1
    """
    log_data = {
        'component': component,
        'error_message': error_message
    }
    
    if exception:
        logger.error(
            f"Error in {component}: {error_message}",
            extra=log_data,
            exc_info=exception
        )
    else:
        logger.error(f"Error in {component}: {error_message}", extra=log_data)


def log_critical_error(component: str, error_message: str, exception: Optional[Exception] = None):
    """
    Log critical error that requires immediate attention.
    
    In production, this would trigger SNS/CloudWatch alerts.
    
    Args:
        component: Component name where error occurred
        error_message: Description of the critical error
        exception: Exception object if available
    
    Requirements: 16.5
    """
    log_data = {
        'component': component,
        'error_message': error_message,
        'severity': 'CRITICAL'
    }
    
    logger.critical(
        f"CRITICAL ERROR in {component}: {error_message}",
        extra=log_data,
        exc_info=exception
    )
    
    # PRODUCTION: Send alert via SNS (commented)
    # send_critical_alert_sns(component, error_message)


# ============================================
# Circuit Breaker Pattern
# ============================================

class CircuitBreaker:
    """
    Circuit breaker pattern for external service calls.
    
    Prevents cascading failures by temporarily blocking calls to
    failing services.
    
    Requirements: 16.3
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
        
        Returns:
            Function result
        
        Raises:
            Exception: If circuit is open or function fails
        """
        # Check circuit state
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise Exception(f"Circuit breaker is OPEN. Service unavailable.")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Handle successful call."""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            log_critical_error(
                'CircuitBreaker',
                f'Circuit opened after {self.failure_count} failures'
            )
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        return (time.time() - self.last_failure_time) >= self.timeout


# Global circuit breakers for external services
twilio_circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=300)  # 5 minutes
bedrock_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)  # 1 minute


# ============================================
# Error Handler Decorators
# ============================================

def handle_model_inference_errors(component: str):
    """
    Decorator to handle model inference errors.
    
    Returns 500 status code with generic error message.
    
    Requirements: 16.2
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_error(component, f"Model inference failed: {str(e)}", e)
                raise RuntimeError("Model inference failed. Please try again later.")
        
        return wrapper
    
    return decorator


def handle_external_service_errors(component: str, circuit_breaker: Optional[CircuitBreaker] = None):
    """
    Decorator to handle external service errors with circuit breaker.
    
    Requirements: 16.3
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if circuit_breaker:
                    return circuit_breaker.call(func, *args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                log_error(component, f"External service call failed: {str(e)}", e)
                raise
        
        return wrapper
    
    return decorator


# ============================================
# PRODUCTION: SNS Alert Integration (COMMENTED)
# ============================================

# import boto3
# 
# sns_client = None
# 
# def init_sns_client():
#     """Initialize SNS client for critical alerts."""
#     global sns_client
#     sns_client = boto3.client('sns', region_name=os.getenv('AWS_REGION', 'us-east-1'))
# 
# 
# def send_critical_alert_sns(component: str, error_message: str):
#     """
#     Send critical error alert via SNS.
#     
#     Args:
#         component: Component where error occurred
#         error_message: Error description
#     
#     Requirements: 16.5
#     """
#     global sns_client
#     
#     if sns_client is None:
#         init_sns_client()
#     
#     topic_arn = os.getenv('SNS_ALERT_TOPIC_ARN')
#     
#     try:
#         sns_client.publish(
#             TopicArn=topic_arn,
#             Subject=f'CRITICAL: Error in {component}',
#             Message=f"""
#             Critical error detected in Smart Irrigation System
#             
#             Component: {component}
#             Error: {error_message}
#             Timestamp: {datetime.utcnow().isoformat()}
#             
#             Immediate action required.
#             """
#         )
#     except Exception as e:
#         logger.error(f"Failed to send SNS alert: {str(e)}")


# ============================================
# PRODUCTION: CloudWatch Integration (COMMENTED)
# ============================================

# import boto3
# 
# cloudwatch_client = None
# 
# def init_cloudwatch_client():
#     """Initialize CloudWatch client for logging."""
#     global cloudwatch_client
#     cloudwatch_client = boto3.client('logs', region_name=os.getenv('AWS_REGION', 'us-east-1'))
# 
# 
# def send_logs_to_cloudwatch(log_group: str, log_stream: str, log_events: list):
#     """
#     Send logs to CloudWatch Logs.
#     
#     Args:
#         log_group: CloudWatch log group name
#         log_stream: CloudWatch log stream name
#         log_events: List of log event dictionaries
#     
#     Requirements: 16.4
#     """
#     global cloudwatch_client
#     
#     if cloudwatch_client is None:
#         init_cloudwatch_client()
#     
#     try:
#         cloudwatch_client.put_log_events(
#             logGroupName=log_group,
#             logStreamName=log_stream,
#             logEvents=log_events
#         )
#     except Exception as e:
#         logger.error(f"Failed to send logs to CloudWatch: {str(e)}")
