"""
Notification Service for Smart Irrigation System.

This module provides functions for sending alerts to farmers.
Prototype logs alerts to file.
Production code for Twilio WhatsApp/SMS integration is commented.

Requirements: 3.5
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from translation_tts import translate_text

# ============================================
# PRODUCTION: Twilio Imports (COMMENTED)
# ============================================

# from twilio.rest import Client
# 
# twilio_client = None


# ============================================
# PROTOTYPE: Local Alert Logging Configuration
# ============================================

ALERT_LOG_PATH = 'Code/backend/data/alerts.log'

# Rate limiting: Track last alert time per farmer
_last_alert_time: Dict[str, datetime] = {}
RATE_LIMIT_HOURS = 1  # Maximum 1 alert per farmer per hour


def send_alert(farmer_phone: str, message: str, language: str = 'en') -> bool:
    """
    Send alert notification to farmer (Prototype: logs to file).
    
    Production: Would send via Twilio WhatsApp/SMS
    
    This function:
    1. Checks rate limiting (1 alert per farmer per hour)
    2. Translates message to farmer's preferred language
    3. Logs alert to file (prototype) or sends via Twilio (production)
    
    Args:
        farmer_phone: Farmer's phone number (E.164 format)
        message: Alert message text
        language: ISO language code for translation
    
    Returns:
        True if alert sent successfully, False otherwise
    
    Requirements: 3.5
    """
    # Check rate limiting
    if not check_rate_limit(farmer_phone):
        print(f"Rate limit exceeded for {farmer_phone}. Skipping alert.")
        return False
    
    # Translate message to farmer's language
    try:
        translated_message = translate_text(message, language)
    except Exception as e:
        print(f"Translation failed: {str(e)}. Using original message.")
        translated_message = message
    
    # PROTOTYPE: Log alert to file
    success = log_alert_to_file(farmer_phone, translated_message, language)
    
    # PRODUCTION: Send via Twilio (commented)
    # success = send_alert_twilio(farmer_phone, translated_message)
    
    if success:
        # Update last alert time for rate limiting
        _last_alert_time[farmer_phone] = datetime.now()
    
    return success


def check_rate_limit(farmer_phone: str) -> bool:
    """
    Check if alert can be sent based on rate limiting rules.
    
    Rate limit: Maximum 1 alert per farmer per hour
    
    Args:
        farmer_phone: Farmer's phone number
    
    Returns:
        True if alert can be sent, False if rate limit exceeded
    
    Requirements: 3.5
    """
    if farmer_phone not in _last_alert_time:
        return True
    
    last_alert = _last_alert_time[farmer_phone]
    time_since_last = datetime.now() - last_alert
    
    # Check if enough time has passed (1 hour)
    return time_since_last >= timedelta(hours=RATE_LIMIT_HOURS)


def log_alert_to_file(farmer_phone: str, message: str, language: str) -> bool:
    """
    Log alert to local file (Prototype).
    
    Args:
        farmer_phone: Farmer's phone number
        message: Alert message
        language: Language code
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(ALERT_LOG_PATH), exist_ok=True)
        
        # Log alert with timestamp
        with open(ALERT_LOG_PATH, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().isoformat()
            f.write(f"{timestamp} | {farmer_phone} | {language} | {message}\n")
        
        print(f"ALERT logged for {farmer_phone}: {message}")
        return True
    
    except Exception as e:
        print(f"Failed to log alert: {str(e)}")
        return False


# ============================================
# PRODUCTION: Twilio Integration (COMMENTED)
# ============================================

# def init_twilio_client():
#     """Initialize Twilio client for sending WhatsApp/SMS messages."""
#     global twilio_client
#     
#     account_sid = os.getenv('TWILIO_ACCOUNT_SID')
#     auth_token = os.getenv('TWILIO_AUTH_TOKEN')
#     
#     if not account_sid or not auth_token:
#         raise ValueError("Twilio credentials not configured")
#     
#     twilio_client = Client(account_sid, auth_token)
# 
# 
# def send_alert_twilio(farmer_phone: str, message: str) -> bool:
#     """
#     Send alert via Twilio WhatsApp or SMS.
#     
#     Tries WhatsApp first, falls back to SMS if WhatsApp fails.
#     
#     Args:
#         farmer_phone: Farmer's phone number in E.164 format (e.g., +1234567890)
#         message: Alert message text
#     
#     Returns:
#         True if sent successfully, False otherwise
#     
#     Requirements: 3.5
#     """
#     global twilio_client
#     
#     if twilio_client is None:
#         init_twilio_client()
#     
#     twilio_from = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
#     
#     try:
#         # Try sending via WhatsApp first
#         message_obj = twilio_client.messages.create(
#             from_=twilio_from,
#             to=f'whatsapp:{farmer_phone}',
#             body=message
#         )
#         
#         print(f"WhatsApp alert sent to {farmer_phone}. SID: {message_obj.sid}")
#         return True
#     
#     except Exception as whatsapp_error:
#         print(f"WhatsApp failed: {str(whatsapp_error)}. Trying SMS...")
#         
#         try:
#             # Fallback to SMS
#             message_obj = twilio_client.messages.create(
#                 from_=twilio_from.replace('whatsapp:', ''),
#                 to=farmer_phone,
#                 body=message
#             )
#             
#             print(f"SMS alert sent to {farmer_phone}. SID: {message_obj.sid}")
#             return True
#         
#         except Exception as sms_error:
#             print(f"SMS also failed: {str(sms_error)}")
#             return False
# 
# 
# def send_batch_alerts(alerts: list[tuple[str, str, str]]) -> Dict[str, bool]:
#     """
#     Send multiple alerts in batch (for multiple simultaneous conditions).
#     
#     Args:
#         alerts: List of tuples (farmer_phone, message, language)
#     
#     Returns:
#         Dictionary mapping farmer_phone to success status
#     
#     Requirements: 3.5
#     """
#     results = {}
#     
#     for farmer_phone, message, language in alerts:
#         success = send_alert(farmer_phone, message, language)
#         results[farmer_phone] = success
#     
#     return results


def get_alert_history(farmer_phone: Optional[str] = None, 
                     limit: int = 100) -> list[Dict[str, str]]:
    """
    Get alert history from log file (Prototype).
    
    Args:
        farmer_phone: Filter by specific farmer (optional)
        limit: Maximum number of alerts to return
    
    Returns:
        List of alert dictionaries
    """
    try:
        if not os.path.exists(ALERT_LOG_PATH):
            return []
        
        alerts = []
        
        with open(ALERT_LOG_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse log lines (most recent first)
        for line in reversed(lines[-limit:]):
            parts = line.strip().split(' | ')
            if len(parts) >= 4:
                timestamp, phone, language, message = parts[0], parts[1], parts[2], ' | '.join(parts[3:])
                
                # Filter by farmer_phone if specified
                if farmer_phone is None or phone == farmer_phone:
                    alerts.append({
                        'timestamp': timestamp,
                        'farmer_phone': phone,
                        'language': language,
                        'message': message
                    })
        
        return alerts
    
    except Exception as e:
        print(f"Failed to read alert history: {str(e)}")
        return []


def clear_rate_limits():
    """
    Clear all rate limit tracking (for testing purposes).
    """
    global _last_alert_time
    _last_alert_time.clear()
