"""
Module 1: Text Input Handler
Accepts, validates, and normalizes user text input for TTS processing.

Responsibilities:
- Accept raw text from users
- Validate input (not empty, within limits)
- Clean and normalize text (whitespace, encoding, special chars)
- Prepare text for language detection and TTS

Design Principles:
- Fail fast with clear error messages
- Preserve language-specific characters (Urdu, English)
- No language assumptions
- Safe handling of edge cases
"""

from typing import Optional
from dataclasses import dataclass
import re
import ftfy
from loguru import logger


@dataclass
class TextInputResult:
    """
    Result of text input processing.
    
    Attributes:
        success: Whether processing succeeded
        text: Cleaned and normalized text
        original_text: Original input text
        char_count: Character count of cleaned text
        word_count: Approximate word count
        error: Error message if processing failed
    """
    success: bool
    text: str
    original_text: str
    char_count: int
    word_count: int
    error: Optional[str] = None


class TextInputHandler:
    """
    Handles text input validation and normalization.
    
    This is a stateless service class - no instance variables.
    All methods can be called independently.
    """
    
    # Configuration constants
    MIN_TEXT_LENGTH = 1
    MAX_TEXT_LENGTH = 10000  # ~10KB of text
    
    def __init__(self):
        """Initialize the text input handler."""
        logger.info("TextInputHandler initialized")
    
    
    def process(self, text: str) -> TextInputResult:
        """
        Main processing pipeline for text input.
        
        Pipeline:
        1. Validate input (not None, not empty)
        2. Fix encoding issues
        3. Normalize whitespace
        4. Clean special characters (preserve language chars)
        5. Validate length constraints
        6. Return result
        
        Args:
            text: Raw user input text
            
        Returns:
            TextInputResult with success status and processed text
            
        Example:
            >>> handler = TextInputHandler()
            >>> result = handler.process("  Hello   World!  ")
            >>> print(result.text)
            "Hello World!"
        """
        original_text = text
        
        try:
            # Step 1: Initial validation
            validation_error = self._validate_input(text)
            if validation_error:
                return self._create_error_result(original_text, validation_error)
            
            # Step 2: Fix encoding issues (mojibake, etc.)
            text = self._fix_encoding(text)
            
            # Step 3: Normalize whitespace
            text = self._normalize_whitespace(text)
            
            # Step 4: Clean special characters (but preserve language chars)
            text = self._clean_text(text)
            
            # Step 5: Final validation
            final_validation_error = self._validate_processed_text(text)
            if final_validation_error:
                return self._create_error_result(original_text, final_validation_error)
            
            # Step 6: Create success result
            return TextInputResult(
                success=True,
                text=text,
                original_text=original_text,
                char_count=len(text),
                word_count=self._count_words(text),
                error=None
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in text processing: {str(e)}")
            return self._create_error_result(
                original_text, 
                f"Processing error: {str(e)}"
            )
    
    
    def _validate_input(self, text: str) -> Optional[str]:
        """
        Validate raw input text.
        
        Args:
            text: Raw input
            
        Returns:
            Error message if invalid, None if valid
        """
        if text is None:
            return "Text cannot be None"
        
        if not isinstance(text, str):
            return f"Text must be a string, got {type(text).__name__}"
        
        if len(text.strip()) == 0:
            return "Text cannot be empty or whitespace only"
        
        if len(text) > self.MAX_TEXT_LENGTH:
            return f"Text too long ({len(text)} chars). Maximum is {self.MAX_TEXT_LENGTH} characters"
        
        return None
    
    
    def _validate_processed_text(self, text: str) -> Optional[str]:
        """
        Validate processed text after cleaning.
        
        Args:
            text: Processed text
            
        Returns:
            Error message if invalid, None if valid
        """
        if len(text) < self.MIN_TEXT_LENGTH:
            return "Text too short after cleaning (minimum 1 character)"
        
        return None
    
    
    def _fix_encoding(self, text: str) -> str:
        """
        Fix encoding issues using ftfy library.
        
        Handles:
        - Mojibake (garbled text from encoding mismatches)
        - HTML entities
        - Unicode normalization
        
        Args:
            text: Input text
            
        Returns:
            Text with fixed encoding
            
        Example:
            >>> self._fix_encoding("Itâ€™s a test")
            "It's a test"
        """
        try:
            # ftfy fixes common encoding issues
            fixed_text = ftfy.fix_text(text)
            
            if fixed_text != text:
                logger.debug(f"Fixed encoding issues in text")
            
            return fixed_text
        
        except Exception as e:
            logger.warning(f"Could not fix encoding: {str(e)}, using original")
            return text
    
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace characters.
        
        - Replace multiple spaces with single space
        - Replace tabs/newlines with spaces
        - Strip leading/trailing whitespace
        - Preserve single spaces between words
        
        Args:
            text: Input text
            
        Returns:
            Text with normalized whitespace
            
        Example:
            >>> self._normalize_whitespace("Hello    World\\n\\t!")
            "Hello World !"
        """
        # Replace newlines and tabs with spaces
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    
    def _clean_text(self, text: str) -> str:
        """
        Clean special characters while preserving language-specific chars.
        
        Preserves:
        - English letters (A-Z, a-z)
        - Urdu characters (Unicode range: 0600-06FF, 0750-077F, FB50-FDFF, FE70-FEFF)
        - Numbers (0-9)
        - Common punctuation (. , ! ? ' " - : ; )
        - Spaces
        
        Removes:
        - Control characters
        - Unusual symbols
        - Excessive special characters
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Define allowed character pattern
        # This regex preserves:
        # - Latin letters and numbers
        # - Urdu/Arabic script
        # - Common punctuation
        # - Spaces
        pattern = r'[^\w\s\.\,\!\?\'\"\-\:\;\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]'
        
        # Remove characters not matching pattern
        cleaned = re.sub(pattern, '', text)
        
        # Remove any resulting double spaces
        cleaned = re.sub(r' +', ' ', cleaned)
        
        return cleaned.strip()
    
    
    def _count_words(self, text: str) -> int:
        """
        Count approximate number of words.
        
        Note: This is approximate because Urdu doesn't use spaces
        the same way as English. We count space-separated tokens.
        
        Args:
            text: Input text
            
        Returns:
            Approximate word count
        """
        # Split on whitespace and count non-empty tokens
        words = [word for word in text.split() if word.strip()]
        return len(words)
    
    
    def _create_error_result(self, original_text: str, error: str) -> TextInputResult:
        """
        Create an error result object.
        
        Args:
            original_text: Original input text
            error: Error message
            
        Returns:
            TextInputResult with error
        """
        logger.warning(f"Text input validation failed: {error}")
        
        return TextInputResult(
            success=False,
            text="",
            original_text=original_text,
            char_count=0,
            word_count=0,
            error=error
        )
    
    
    def validate_only(self, text: str) -> tuple[bool, Optional[str]]:
        """
        Quick validation without processing.
        
        Args:
            text: Text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Example:
            >>> handler = TextInputHandler()
            >>> is_valid, error = handler.validate_only("Hello")
            >>> print(is_valid)
            True
        """
        error = self._validate_input(text)
        return (error is None, error)


# Convenience function for quick usage
def process_text(text: str) -> TextInputResult:
    """
    Convenience function for one-off text processing.
    
    Args:
        text: Text to process
        
    Returns:
        TextInputResult
        
    Example:
        >>> from modules.text_input import process_text
        >>> result = process_text("Hello World")
        >>> print(result.text)
    """
    handler = TextInputHandler()
    return handler.process(text)


if __name__ == "__main__":
    # Self-test
    print("="*60)
    print("MODULE 1: Text Input Handler - Self Test")
    print("="*60)
    
    handler = TextInputHandler()
    
    # Test cases
    test_cases = [
        "Hello World!",
        "  Multiple    spaces   ",
        "Urdu text: السلام علیکم",
        "Mixed: Hello دنیا",
        "",  # Should fail
        "A" * 15000,  # Should fail (too long)
        "Special chars: @#$%^&*()",
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test[:50]}...")
        result = handler.process(test)
        
        if result.success:
            print(f"  ✅ Success")
            print(f"  📝 Cleaned: {result.text[:50]}")
            print(f"  📊 Stats: {result.char_count} chars, {result.word_count} words")
        else:
            print(f"  ❌ Failed: {result.error}")
    
    print("\n" + "="*60)
    print("✅ Self-test complete!")