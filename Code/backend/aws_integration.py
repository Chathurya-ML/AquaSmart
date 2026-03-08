"""
AWS Integration Layer with Fallback Support.

This module provides a unified interface for AWS services with automatic
fallback to local storage if AWS services are unavailable.

Supports:
- AWS Timestream (fallback: local CSV)
- AWS RDS PostgreSQL (fallback: local SQLite)
- AWS S3 (fallback: local Parquet files)
- Amazon Bedrock LLM (fallback: local DistilGPT-2)
- AWS SNS (fallback: local logging)

Requirements: 7.1, 7.2, 8.1, 8.2, 15.1, 15.2
"""

import os
import json
import time
import boto3
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

# ============================================
# Configuration
# ============================================

AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
USE_AWS = os.getenv('USE_AWS', 'true').lower() == 'true'
FALLBACK_ENABLED = os.getenv('FALLBACK_ENABLED', 'true').lower() == 'true'

# AWS Service Configuration
TIMESTREAM_DATABASE = os.getenv('TIMESTREAM_DATABASE', 'irrigation_db')
TIMESTREAM_TABLE = os.getenv('TIMESTREAM_TABLE', 'sensor_readings')
RDS_HOST = os.getenv('RDS_HOST')
RDS_PORT = int(os.getenv('RDS_PORT', 5432))
RDS_DATABASE = os.getenv('RDS_DATABASE', 'irrigation_db')
RDS_USER = os.getenv('RDS_USER')
RDS_PASSWORD = os.getenv('RDS_PASSWORD')
S3_BUCKET = os.getenv('S3_BUCKET', 'irrigation-model-results')
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

# ============================================
# AWS Clients (Lazy Initialization)
# ============================================

_aws_clients = {
    'timestream_write': None,
    'timestream_query': None,
    's3': None,
    'sns': None,
    'bedrock': None,
    'rds': None
}

_aws_available = {
    'timestream': False,
    'rds': False,
    's3': False,
    'sns': False,
    'bedrock': False
}


def _init_aws_client(service_name: str):
    """Initialize AWS client with error handling."""
    try:
        if service_name == 'timestream_write':
            _aws_clients['timestream_write'] = boto3.client(
                'timestream-write',
                region_name=AWS_REGION
            )
            _aws_available['timestream'] = True
        elif service_name == 'timestream_query':
            _aws_clients['timestream_query'] = boto3.client(
                'timestream-query',
                region_name=AWS_REGION
            )
        elif service_name == 's3':
            _aws_clients['s3'] = boto3.client(
                's3',
                region_name=AWS_REGION
            )
            _aws_available['s3'] = True
        elif service_name == 'sns':
            _aws_clients['sns'] = boto3.client(
                'sns',
                region_name=AWS_REGION
            )
            _aws_available['sns'] = True
        elif service_name == 'bedrock':
            _aws_clients['bedrock'] = boto3.client(
                'bedrock-runtime',
                region_name=AWS_REGION
            )
            _aws_available['bedrock'] = True
        elif service_name == 'rds':
            import psycopg2
            _aws_clients['rds'] = psycopg2.connect(
                host=RDS_HOST,
                port=RDS_PORT,
                database=RDS_DATABASE,
                user=RDS_USER,
                password=RDS_PASSWORD
            )
            _aws_available['rds'] = True
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"AWS credentials not configured: {str(e)}")
        print("Falling back to local storage...")
    except Exception as e:
        print(f"Failed to initialize {service_name}: {str(e)}")
        print("Falling back to local storage...")


def get_aws_client(service_name: str):
    """Get or initialize AWS client."""
    if not USE_AWS:
        return None
    
    if _aws_clients[service_name] is None:
        _init_aws_client(service_name)
    
    return _aws_clients[service_name]


# ============================================
# Timestream Integration
# ============================================

def write_sensor_data(sensor_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Write sensor data to Timestream with fallback to local CSV.
    
    Args:
        sensor_data: Dictionary with sensor readings
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if USE_AWS and _aws_available['timestream']:
        try:
            client = get_aws_client('timestream_write')
            if client is None:
                raise Exception("Timestream client not available")
            
            records = [{
                'Time': str(int(time.time() * 1000)),
                'Dimensions': [
                    {'Name': 'sensor_id', 'Value': sensor_data.get('sensor_id', 'default')},
                    {'Name': 'farm_id', 'Value': sensor_data.get('farm_id', 'default')}
                ],
                'MeasureName': 'sensor_metrics',
                'MeasureValueType': 'MULTI',
                'MeasureValues': [
                    {'Name': 'temperature', 'Value': str(sensor_data['temperature']), 'Type': 'DOUBLE'},
                    {'Name': 'humidity', 'Value': str(sensor_data['humidity']), 'Type': 'DOUBLE'},
                    {'Name': 'soil_moisture', 'Value': str(sensor_data['soil_moisture']), 'Type': 'DOUBLE'},
                ]
            }]
            
            client.write_records(
                DatabaseName=TIMESTREAM_DATABASE,
                TableName=TIMESTREAM_TABLE,
                Records=records
            )
            
            return True, "Data written to AWS Timestream"
        
        except Exception as e:
            print(f"Timestream write failed: {str(e)}")
            if not FALLBACK_ENABLED:
                return False, f"Timestream error: {str(e)}"
    
    # Fallback to local storage
    try:
        import pandas as pd
        from pathlib import Path
        
        csv_path = 'Code/backend/data/sensor_readings.csv'
        Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame([sensor_data])
        if os.path.exists(csv_path):
            df.to_csv(csv_path, mode='a', header=False, index=False)
        else:
            df.to_csv(csv_path, index=False)
        
        return True, "Data written to local CSV (fallback)"
    
    except Exception as e:
        return False, f"Both Timestream and local storage failed: {str(e)}"


# ============================================
# RDS Integration
# ============================================

def store_decision_aws(decision_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Store irrigation decision to RDS with fallback to SQLite.
    
    Args:
        decision_data: Dictionary with decision information
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if USE_AWS and RDS_HOST and _aws_available['rds']:
        try:
            client = get_aws_client('rds')
            if client is None:
                raise Exception("RDS connection not available")
            
            cursor = client.cursor()
            cursor.execute("""
                INSERT INTO irrigation_decisions 
                (decision_id, farmer_id, timestamp, current_moisture, 
                 forecasted_moisture, irrigation_amount, alerts, explanation)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                decision_data.get('decision_id'),
                decision_data.get('farmer_id'),
                decision_data.get('timestamp'),
                decision_data.get('current_moisture'),
                decision_data.get('forecasted_moisture'),
                decision_data.get('irrigation_amount'),
                json.dumps(decision_data.get('alerts', [])),
                decision_data.get('explanation')
            ))
            
            client.commit()
            return True, "Decision stored in AWS RDS"
        
        except Exception as e:
            print(f"RDS storage failed: {str(e)}")
            if not FALLBACK_ENABLED:
                return False, f"RDS error: {str(e)}"
    
    # Fallback to local SQLite
    try:
        import sqlite3
        
        db_path = 'Code/backend/data/irrigation_decisions.db'
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS irrigation_decisions (
                decision_id TEXT PRIMARY KEY,
                farmer_id TEXT,
                timestamp TEXT,
                current_moisture REAL,
                forecasted_moisture REAL,
                irrigation_amount REAL,
                alerts TEXT,
                explanation TEXT
            )
        """)
        
        cursor.execute("""
            INSERT INTO irrigation_decisions 
            (decision_id, farmer_id, timestamp, current_moisture, 
             forecasted_moisture, irrigation_amount, alerts, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision_data.get('decision_id'),
            decision_data.get('farmer_id'),
            decision_data.get('timestamp'),
            decision_data.get('current_moisture'),
            decision_data.get('forecasted_moisture'),
            decision_data.get('irrigation_amount'),
            json.dumps(decision_data.get('alerts', [])),
            decision_data.get('explanation')
        ))
        
        conn.commit()
        conn.close()
        
        return True, "Decision stored in local SQLite (fallback)"
    
    except Exception as e:
        return False, f"Both RDS and local storage failed: {str(e)}"


# ============================================
# S3 Integration
# ============================================

def log_model_prediction_aws(model_type: str, prediction_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Log model prediction to S3 with fallback to local Parquet.
    
    Args:
        model_type: Type of model ('lstm' or 'rl')
        prediction_data: Dictionary with prediction information
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if USE_AWS and _aws_available['s3']:
        try:
            import pandas as pd
            import io
            
            client = get_aws_client('s3')
            if client is None:
                raise Exception("S3 client not available")
            
            date = datetime.now()
            prefix = 'lstm-predictions' if model_type == 'lstm' else 'rl-decisions'
            s3_key = f"{prefix}/year={date.year}/month={date.month:02d}/day={date.day:02d}/predictions_{date.strftime('%H%M%S')}.parquet"
            
            df = pd.DataFrame([prediction_data])
            parquet_buffer = io.BytesIO()
            df.to_parquet(parquet_buffer, engine='pyarrow', index=False)
            parquet_buffer.seek(0)
            
            client.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=parquet_buffer.getvalue()
            )
            
            return True, f"Prediction logged to AWS S3: {s3_key}"
        
        except Exception as e:
            print(f"S3 logging failed: {str(e)}")
            if not FALLBACK_ENABLED:
                return False, f"S3 error: {str(e)}"
    
    # Fallback to local Parquet
    try:
        import pandas as pd
        from pathlib import Path
        
        date = datetime.now()
        path = Path('Code/backend/data/model_results') / model_type / \
               f"year={date.year}" / f"month={date.month:02d}" / f"day={date.day:02d}"
        path.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame([prediction_data])
        file_path = path / f"predictions_{date.strftime('%H%M%S')}.parquet"
        df.to_parquet(file_path, engine='pyarrow', index=False)
        
        return True, f"Prediction logged to local Parquet (fallback): {file_path}"
    
    except Exception as e:
        return False, f"Both S3 and local storage failed: {str(e)}"


# ============================================
# SNS Integration
# ============================================

def send_notification_aws(phone_number: str, message: str) -> Tuple[bool, str]:
    """
    Send SMS notification via SNS with fallback to local logging.
    
    Args:
        phone_number: Phone number to send to
        message: Message content
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if USE_AWS and SNS_TOPIC_ARN and _aws_available['sns']:
        try:
            client = get_aws_client('sns')
            if client is None:
                raise Exception("SNS client not available")
            
            response = client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=message,
                Subject='Smart Irrigation Alert'
            )
            
            return True, f"Notification sent via AWS SNS: {response['MessageId']}"
        
        except Exception as e:
            print(f"SNS notification failed: {str(e)}")
            if not FALLBACK_ENABLED:
                return False, f"SNS error: {str(e)}"
    
    # Fallback to local logging
    try:
        log_path = 'Code/backend/data/notifications.log'
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        with open(log_path, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] To: {phone_number}\n")
            f.write(f"Message: {message}\n")
            f.write("-" * 80 + "\n")
        
        return True, "Notification logged locally (fallback)"
    
    except Exception as e:
        return False, f"Both SNS and local logging failed: {str(e)}"


# ============================================
# Bedrock LLM Integration
# ============================================

def generate_explanation_bedrock(prompt: str) -> Tuple[bool, str]:
    """
    Generate explanation using Amazon Bedrock with fallback to local LLM.
    
    Args:
        prompt: Prompt for LLM
    
    Returns:
        Tuple of (success: bool, explanation: str)
    """
    if USE_AWS and _aws_available['bedrock']:
        try:
            client = get_aws_client('bedrock')
            if client is None:
                raise Exception("Bedrock client not available")
            
            response = client.invoke_model(
                modelId=BEDROCK_MODEL_ID,
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-06-01',
                    'max_tokens': 1024,
                    'messages': [
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ]
                })
            )
            
            result = json.loads(response['body'].read())
            explanation = result['content'][0]['text']
            
            return True, explanation
        
        except Exception as e:
            print(f"Bedrock LLM failed: {str(e)}")
            if not FALLBACK_ENABLED:
                return False, f"Bedrock error: {str(e)}"
    
    # Fallback to local LLM
    try:
        from transformers import pipeline
        
        generator = pipeline('text-generation', model='distilgpt2')
        result = generator(prompt, max_length=150, num_return_sequences=1)
        explanation = result[0]['generated_text']
        
        return True, explanation
    
    except Exception as e:
        return False, f"Both Bedrock and local LLM failed: {str(e)}"


# ============================================
# Status Check
# ============================================

def get_aws_status() -> Dict[str, Any]:
    """Get status of AWS services and fallback availability."""
    return {
        'aws_enabled': USE_AWS,
        'fallback_enabled': FALLBACK_ENABLED,
        'services': {
            'timestream': _aws_available['timestream'],
            'rds': _aws_available['rds'],
            's3': _aws_available['s3'],
            'sns': _aws_available['sns'],
            'bedrock': _aws_available['bedrock']
        }
    }


# Initialize AWS clients on module load
# DISABLED: Causes hanging on import. Clients will initialize lazily when first used.
# if USE_AWS:
#     print("Initializing AWS integration layer...")
#     for service in ['timestream_write', 's3', 'sns', 'bedrock']:
#         try:
#             _init_aws_client(service)
#         except:
#             pass
