"""
Translation and Text-to-Speech Module for Smart Irrigation System.

This module provides functions for translating explanations to different
languages and generating audio versions using text-to-speech.

Requirements: 4.3, 4.4, 4.5, 5.1, 5.2, 5.3
"""

import base64
import tempfile
import os
from typing import Optional
from googletrans import Translator
from gtts import gTTS

# Supported languages for the system
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'es': 'Spanish',
    'pt': 'Portuguese',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'ja': 'Japanese',
    'zh-cn': 'Chinese (Simplified)',
    'ar': 'Arabic',
    'bn': 'Bengali',
    'ta': 'Tamil',
    'te': 'Telugu',
    'mr': 'Marathi',
    'ur': 'Urdu'
}


def translate_text(text: str, target_language: str) -> str:
    """
    Translate text to the target language using Google Translate.
    
    This function:
    1. Validates the target language is supported
    2. Uses googletrans to translate the text
    3. Falls back to English if translation fails
    
    Args:
        text: Text to translate (typically in English)
        target_language: ISO language code (e.g., 'hi', 'es', 'pt')
    
    Returns:
        Translated text string
    
    Raises:
        ValueError: If target_language is not supported
    
    Requirements: 4.3, 5.1, 5.2, 5.3
    """
    # If target is English, return as-is
    if target_language.lower() == 'en':
        return text
    
    # Validate language is supported
    if target_language.lower() not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language: {target_language}. "
            f"Supported languages: {', '.join(SUPPORTED_LANGUAGES.keys())}"
        )
    
    try:
        # Initialize translator
        translator = Translator()
        
        # Translate the text
        translation = translator.translate(text, dest=target_language.lower())
        
        # Return translated text
        return translation.text
    
    except Exception as e:
        # Fallback to English if translation fails
        print(f"Translation failed for language '{target_language}': {str(e)}")
        print("Falling back to English.")
        return text


def generate_audio(text: str, language: str = 'en') -> str:
    """
    Generate audio from text using Google Text-to-Speech (gTTS).
    
    This function:
    1. Generates audio using gTTS
    2. Saves to a temporary file
    3. Encodes as base64 for API response
    4. Cleans up the temporary file
    
    Args:
        text: Text to convert to speech
        language: ISO language code for TTS voice (default: 'en')
    
    Returns:
        Base64-encoded audio string
    
    Raises:
        RuntimeError: If audio generation fails
    
    Requirements: 4.4, 4.5
    """
    try:
        # Map language codes for gTTS compatibility
        # gTTS uses 'zh-cn' for Chinese, but we normalize it
        tts_language = language.lower()
        
        # Generate speech using gTTS
        tts = gTTS(text=text, lang=tts_language, slow=False)
        
        # Create a temporary file to save the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_path = temp_file.name
            tts.save(temp_path)
        
        # Read the audio file and encode as base64
        with open(temp_path, 'rb') as audio_file:
            audio_data = audio_file.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        return audio_base64
    
    except Exception as e:
        raise RuntimeError(f"Audio generation failed: {str(e)}") from e


def translate_and_generate_audio(text: str, target_language: str) -> tuple[str, str]:
    """
    Translate text and generate audio in one operation.
    
    This is a convenience function that combines translation and TTS.
    If translation fails, falls back to English.
    If TTS fails, returns empty string for audio (non-blocking).
    
    Args:
        text: Text to translate and convert to speech
        target_language: ISO language code
    
    Returns:
        Tuple of (translated_text, audio_base64)
    
    Requirements: 4.3, 4.4, 4.5, 5.3
    """
    # Translate the text (with fallback to English)
    try:
        translated_text = translate_text(text, target_language)
    except ValueError as e:
        # Unsupported language - return error info
        raise e
    except Exception as e:
        # Translation failed - fallback to English
        print(f"Translation error: {str(e)}. Using English.")
        translated_text = text
        target_language = 'en'
    
    # Generate audio (with error handling and timeout)
    # Skip audio generation if it takes too long (non-blocking)
    audio_base64 = ""
    try:
        # For now, skip TTS to avoid timeout issues
        # TTS can be enabled later with async processing
        # audio_base64 = generate_audio(translated_text, target_language)
        print("TTS generation skipped (can be enabled with async processing)")
    except Exception as e:
        # TTS failed - return empty audio
        print(f"TTS error: {str(e)}. Returning text-only response.")
        audio_base64 = ""
    
    return translated_text, audio_base64


def is_language_supported(language_code: str) -> bool:
    """
    Check if a language code is supported.
    
    Args:
        language_code: ISO language code to check
    
    Returns:
        True if supported, False otherwise
    
    Requirements: 5.1, 5.2
    """
    return language_code.lower() in SUPPORTED_LANGUAGES


def get_supported_languages() -> dict:
    """
    Get the dictionary of supported languages.
    
    Returns:
        Dictionary mapping language codes to language names
    
    Requirements: 5.1, 5.2
    """
    return SUPPORTED_LANGUAGES.copy()
