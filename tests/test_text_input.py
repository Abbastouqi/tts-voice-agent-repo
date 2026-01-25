"""
Unit tests for Text Input Handler (Module 1)
"""

import pytest
from modules.text_input import TextInputHandler, process_text


class TestTextInputHandler:
    """Test suite for TextInputHandler class"""
    
    @pytest.fixture
    def handler(self):
        """Create handler instance for tests"""
        return TextInputHandler()
    
    
    # ===== VALIDATION TESTS =====
    
    def test_valid_english_text(self, handler):
        """Test processing valid English text"""
        result = handler.process("Hello World!")
        
        assert result.success is True
        assert result.text == "Hello World!"
        assert result.error is None
        assert result.char_count > 0
        assert result.word_count == 2
    
    
    def test_valid_urdu_text(self, handler):
        """Test processing valid Urdu text"""
        result = handler.process("السلام علیکم")
        
        assert result.success is True
        assert "السلام" in result.text
        assert result.error is None
    
    
    def test_mixed_language_text(self, handler):
        """Test processing mixed English and Urdu"""
        result = handler.process("Hello دنیا World")
        
        assert result.success is True
        assert "Hello" in result.text
        assert "دنیا" in result.text
        assert result.word_count == 3
    
    
    def test_empty_text_fails(self, handler):
        """Test that empty text fails validation"""
        result = handler.process("")
        
        assert result.success is False
        assert result.error is not None
        assert "empty" in result.error.lower()
    
    
    def test_whitespace_only_fails(self, handler):
        """Test that whitespace-only text fails"""
        result = handler.process("   \n\t  ")
        
        assert result.success is False
        assert result.error is not None
    
    
    def test_none_input_fails(self, handler):
        """Test that None input fails"""
        result = handler.process(None)
        
        assert result.success is False
        assert "None" in result.error
    
    
    def test_too_long_text_fails(self, handler):
        """Test that text exceeding max length fails"""
        long_text = "A" * 15000  # Exceeds MAX_TEXT_LENGTH
        result = handler.process(long_text)
        
        assert result.success is False
        assert "too long" in result.error.lower()
    
    
    # ===== NORMALIZATION TESTS =====
    
    def test_whitespace_normalization(self, handler):
        """Test that multiple spaces are normalized"""
        result = handler.process("Hello    World")
        
        assert result.success is True
        assert result.text == "Hello World"
    
    
    def test_newline_normalization(self, handler):
        """Test that newlines are converted to spaces"""
        result = handler.process("Hello\nWorld")
        
        assert result.success is True
        assert "Hello World" == result.text
    
    
    def test_tab_normalization(self, handler):
        """Test that tabs are converted to spaces"""
        result = handler.process("Hello\tWorld")
        
        assert result.success is True
        assert "Hello World" == result.text
    
    
    def test_leading_trailing_whitespace_removed(self, handler):
        """Test that leading/trailing whitespace is stripped"""
        result = handler.process("  Hello World  ")
        
        assert result.success is True
        assert result.text == "Hello World"
    
    
    # ===== CHARACTER CLEANING TESTS =====
    
    def test_basic_punctuation_preserved(self, handler):
        """Test that basic punctuation is preserved"""
        result = handler.process("Hello, World! How are you?")
        
        assert result.success is True
        assert "," in result.text
        assert "!" in result.text
        assert "?" in result.text
    
    
    def test_special_chars_removed(self, handler):
        """Test that unusual special characters are removed"""
        result = handler.process("Hello@#$%World")
        
        assert result.success is True
        # Special chars should be removed, but text remains
        assert "Hello" in result.text
        assert "World" in result.text
    
    
    # ===== WORD COUNTING TESTS =====
    
    def test_word_count_english(self, handler):
        """Test word counting for English text"""
        result = handler.process("One two three four")
        
        assert result.word_count == 4
    
    
    def test_word_count_with_punctuation(self, handler):
        """Test word counting ignores punctuation"""
        result = handler.process("Hello, World!")
        
        assert result.word_count == 2
    
    
    # ===== ENCODING TESTS =====
    
    def test_encoding_fix(self, handler):
        """Test that encoding issues are fixed"""
        # This might not show visible difference in all cases,
        # but ensures ftfy doesn't crash
        result = handler.process("It's a test")
        
        assert result.success is True
        assert "test" in result.text
    
    
    # ===== CONVENIENCE FUNCTION TESTS =====
    
    def test_process_text_function(self):
        """Test the convenience function works"""
        result = process_text("Hello World")
        
        assert result.success is True
        assert result.text == "Hello World"
    
    
    # ===== VALIDATE ONLY TESTS =====
    
    def test_validate_only_valid_text(self, handler):
        """Test validate_only for valid text"""
        is_valid, error = handler.validate_only("Hello World")
        
        assert is_valid is True
        assert error is None
    
    
    def test_validate_only_invalid_text(self, handler):
        """Test validate_only for invalid text"""
        is_valid, error = handler.validate_only("")
        
        assert is_valid is False
        assert error is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])