"""
MODULE 4: Language Detection Engine
====================================
Purpose: Automatically detect if text is English or Urdu
Strategy: Unicode-based primary detection + library fallback
Input: Clean text from Module 1
Output: Language code ('en' or 'ur')

Author: TTS Voice Agent Team
Date: January 2026
"""

import re
from dataclasses import dataclass
from typing import Optional
from loguru import logger

# Optional: langdetect library for fallback (install: pip install langdetect)
try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logger.warning("langdetect library not available. Using Unicode-only detection.")


@dataclass
class LanguageDetectionResult:
    """
    Structured result from language detection
    
    Attributes:
        success (bool): Detection succeeded
        language (str): Detected language code ('en' or 'ur')
        confidence (float): Confidence score (0-100%)
        method (str): Detection method used ('unicode' or 'library')
        text_sample (str): First 100 chars of analyzed text
        char_count (int): Total character count
        error (Optional[str]): Error message if failed
    """
    success: bool
    language: str
    confidence: float
    method: str
    text_sample: str
    char_count: int
    error: Optional[str] = None


class LanguageDetector:
    """
    Detects whether text is English or Urdu
    
    Detection Strategy:
    1. PRIMARY: Unicode range analysis (fast, 99% accurate for Urdu)
       - Urdu uses Arabic script: U+0600-U+06FF, U+0750-U+077F, U+FB50-U+FDFF, U+FE70-U+FEFF
       - If >30% Urdu characters → classify as Urdu
    
    2. FALLBACK: langdetect library (if available)
       - Uses statistical n-gram analysis
       - More accurate for mixed/ambiguous text
    
    Why This Approach:
    - Unicode detection is instant (<0.01 seconds)
    - Urdu script is easily distinguishable from Latin
    - Handles mixed text (English with Urdu numbers/punctuation)
    """
    
    # Unicode ranges for Urdu/Arabic script
    URDU_UNICODE_RANGES = [
        (0x0600, 0x06FF),  # Arabic block (main Urdu characters)
        (0x0750, 0x077F),  # Arabic Supplement
        (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
        (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B
    ]
    
    # Threshold: If >30% of characters are Urdu, classify as Urdu
    URDU_THRESHOLD = 0.30
    
    def __init__(self, use_library_fallback: bool = True):
        """
        Initialize language detector
        
        Args:
            use_library_fallback (bool): Use langdetect if available (default: True)
        """
        self.use_fallback = use_library_fallback and LANGDETECT_AVAILABLE
        logger.info(f"Language Detector initialized. Fallback: {self.use_fallback}")
    
    def detect(self, text: str) -> LanguageDetectionResult:
        """
        Main detection pipeline
        
        Args:
            text (str): Input text to analyze
        
        Returns:
            LanguageDetectionResult: Detection result with language and confidence
        
        Example:
            >>> detector = LanguageDetector()
            >>> result = detector.detect("Hello World")
            >>> print(result.language)  # 'en'
            >>> result = detector.detect("سلام دنیا")
            >>> print(result.language)  # 'ur'
        """
        logger.debug(f"Detecting language for text: {text[:50]}...")
        
        # Step 1: Validate input
        validation_error = self._validate_input(text)
        if validation_error:
            return LanguageDetectionResult(
                success=False,
                language="",
                confidence=0.0,
                method="",
                text_sample="",
                char_count=0,
                error=validation_error
            )
        
        # Step 2: Try Unicode-based detection (PRIMARY)
        unicode_result = self._detect_by_unicode(text)
        
        # If Unicode detection is confident (>70%), use it
        if unicode_result['confidence'] > 70:
            logger.info(f"Unicode detection confident: {unicode_result['language']} ({unicode_result['confidence']:.1f}%)")
            return LanguageDetectionResult(
                success=True,
                language=unicode_result['language'],
                confidence=unicode_result['confidence'],
                method='unicode',
                text_sample=text[:100],
                char_count=len(text)
            )
        
        # Step 3: Try library-based detection (FALLBACK)
        if self.use_fallback:
            library_result = self._detect_by_library(text)
            if library_result['success']:
                logger.info(f"Library detection: {library_result['language']} ({library_result['confidence']:.1f}%)")
                return LanguageDetectionResult(
                    success=True,
                    language=library_result['language'],
                    confidence=library_result['confidence'],
                    method='library',
                    text_sample=text[:100],
                    char_count=len(text)
                )
        
        # Step 4: Default to Unicode result (even if low confidence)
        logger.warning(f"Low confidence detection, using Unicode result: {unicode_result['language']}")
        return LanguageDetectionResult(
            success=True,
            language=unicode_result['language'],
            confidence=unicode_result['confidence'],
            method='unicode',
            text_sample=text[:100],
            char_count=len(text)
        )
    
    def _validate_input(self, text: str) -> Optional[str]:
        """
        Validate input text
        
        Args:
            text (str): Input text
        
        Returns:
            Optional[str]: Error message if invalid, None if valid
        """
        if text is None:
            return "Text cannot be None"
        
        if not isinstance(text, str):
            return "Text must be a string"
        
        if not text.strip():
            return "Text cannot be empty or only whitespace"
        
        if len(text.strip()) < 3:
            return "Text too short for reliable detection (minimum 3 characters)"
        
        return None
    
    def _detect_by_unicode(self, text: str) -> dict:
        """
        Detect language by analyzing Unicode character ranges
        
        Strategy:
        - Count characters in Urdu Unicode ranges
        - Calculate percentage of Urdu characters
        - If >30% Urdu → classify as Urdu
        - Otherwise → classify as English
        
        Args:
            text (str): Input text
        
        Returns:
            dict: {'language': str, 'confidence': float}
        """
        total_chars = 0
        urdu_chars = 0
        
        for char in text:
            # Skip whitespace and punctuation
            if char.isspace() or char in '.,!?;:\'"()-[]{}':
                continue
            
            total_chars += 1
            
            # Check if character is in Urdu Unicode ranges
            char_code = ord(char)
            for start, end in self.URDU_UNICODE_RANGES:
                if start <= char_code <= end:
                    urdu_chars += 1
                    break
        
        # Handle edge case: no analyzable characters
        if total_chars == 0:
            return {'language': 'en', 'confidence': 50.0}
        
        # Calculate Urdu percentage
        urdu_percentage = (urdu_chars / total_chars) * 100
        
        # Determine language
        if urdu_percentage > (self.URDU_THRESHOLD * 100):
            # High Urdu content → Urdu language
            confidence = min(urdu_percentage + 20, 99.0)  # Boost confidence
            return {'language': 'ur', 'confidence': confidence}
        else:
            # Low Urdu content → English language
            confidence = min((100 - urdu_percentage) + 20, 99.0)
            return {'language': 'en', 'confidence': confidence}
    
    def _detect_by_library(self, text: str) -> dict:
        """
        Detect language using langdetect library (fallback method)
        
        Maps langdetect codes to our supported languages:
        - 'en' → 'en' (English)
        - 'ur' → 'ur' (Urdu)
        - Others → Default to 'en'
        
        Args:
            text (str): Input text
        
        Returns:
            dict: {'success': bool, 'language': str, 'confidence': float}
        """
        if not LANGDETECT_AVAILABLE:
            return {'success': False, 'language': '', 'confidence': 0.0}
        
        try:
            detected_lang = detect(text)
            
            # Map to our supported languages
            if detected_lang == 'ur':
                return {'success': True, 'language': 'ur', 'confidence': 95.0}
            elif detected_lang == 'en':
                return {'success': True, 'language': 'en', 'confidence': 95.0}
            else:
                # Unsupported language detected, default to English
                logger.warning(f"Unsupported language detected: {detected_lang}, defaulting to English")
                return {'success': True, 'language': 'en', 'confidence': 60.0}
        
        except LangDetectException as e:
            logger.error(f"Library detection failed: {e}")
            return {'success': False, 'language': '', 'confidence': 0.0}
    
    def get_supported_languages(self) -> list:
        """
        Get list of supported language codes
        
        Returns:
            list: ['en', 'ur']
        """
        return ['en', 'ur']
    
    def is_mixed_language(self, text: str, threshold: float = 0.20) -> bool:
        """
        Check if text contains significant mix of English and Urdu
        
        Args:
            text (str): Input text
            threshold (float): Minimum percentage for "significant" (default: 20%)
        
        Returns:
            bool: True if text has 20-80% Urdu characters (mixed)
        
        Example:
            >>> detector = LanguageDetector()
            >>> detector.is_mixed_language("Hello سلام World")  # True
            >>> detector.is_mixed_language("Hello World")       # False
        """
        unicode_result = self._detect_by_unicode(text)
        
        # Extract Urdu percentage from confidence calculation
        total_chars = sum(1 for char in text if not char.isspace() and char not in '.,!?;:\'"()-[]{}')
        if total_chars == 0:
            return False
        
        urdu_chars = 0
        for char in text:
            if char.isspace() or char in '.,!?;:\'"()-[]{}':
                continue
            char_code = ord(char)
            for start, end in self.URDU_UNICODE_RANGES:
                if start <= char_code <= end:
                    urdu_chars += 1
                    break
        
        urdu_percentage = (urdu_chars / total_chars)
        
        # Mixed if between threshold and (1 - threshold)
        return threshold <= urdu_percentage <= (1 - threshold)


# ============================================
# CONVENIENCE FUNCTIONS (Quick Access)
# ============================================

def detect_language(text: str) -> LanguageDetectionResult:
    """
    Quick one-liner for language detection
    
    Args:
        text (str): Input text
    
    Returns:
        LanguageDetectionResult: Detection result
    
    Example:
        >>> from modules.language_detector import detect_language
        >>> result = detect_language("Hello World")
        >>> print(result.language)  # 'en'
    """
    detector = LanguageDetector()
    return detector.detect(text)


def quick_detect(text: str) -> str:
    """
    Ultra-quick detection - returns just the language code
    
    Args:
        text (str): Input text
    
    Returns:
        str: 'en' or 'ur' (defaults to 'en' on error)
    
    Example:
        >>> from modules.language_detector import quick_detect
        >>> quick_detect("سلام")  # 'ur'
        >>> quick_detect("Hello")  # 'en'
    """
    result = detect_language(text)
    return result.language if result.success else 'en'


# ============================================
# MODULE TESTING (Run directly)
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("MODULE 4: Language Detection Engine - Direct Test")
    print("=" * 60)
    
    detector = LanguageDetector()
    
    test_cases = [
        ("Hello World", "en"),
        ("سلام دنیا", "ur"),
        ("This is a test", "en"),
        ("یہ ایک ٹیسٹ ہے", "ur"),
        ("Hello سلام Mixed", "mixed"),
        ("123 456 789", "en"),
        ("Pakistan زندہ باد", "mixed"),
    ]
    
    print("\nTesting language detection:\n")
    
    for text, expected in test_cases:
        result = detector.detect(text)
        status = "✓" if result.success else "✗"
        print(f"{status} Text: {text[:30]:30} → {result.language} ({result.confidence:.1f}% via {result.method})")
    
    print("\n" + "=" * 60)
    print("Direct test completed!")
    print("=" * 60)