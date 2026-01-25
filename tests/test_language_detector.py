"""
Unit Tests for MODULE 4: Language Detection Engine
===================================================
Tests Unicode-based detection and library fallback

Run with: pytest tests/test_language_detector.py -v
Coverage: pytest tests/test_language_detector.py --cov=modules.language_detector
"""

import pytest
from modules.language_detector import (
    LanguageDetector,
    LanguageDetectionResult,
    detect_language,
    quick_detect
)


class TestLanguageDetectorValidation:
    """Test input validation"""
    
    def test_none_input(self):
        """Should reject None input"""
        detector = LanguageDetector()
        result = detector.detect(None)
        
        assert result.success == False
        assert "cannot be None" in result.error
    
    def test_empty_string(self):
        """Should reject empty string"""
        detector = LanguageDetector()
        result = detector.detect("")
        
        assert result.success == False
        assert "empty" in result.error.lower()
    
    def test_whitespace_only(self):
        """Should reject whitespace-only input"""
        detector = LanguageDetector()
        result = detector.detect("   \n\t  ")
        
        assert result.success == False
        assert "empty" in result.error.lower()
    
    def test_too_short(self):
        """Should reject text shorter than 3 characters"""
        detector = LanguageDetector()
        result = detector.detect("Hi")
        
        assert result.success == False
        assert "too short" in result.error.lower()
    
    def test_non_string_input(self):
        """Should reject non-string input"""
        detector = LanguageDetector()
        result = detector.detect(12345)
        
        assert result.success == False
        assert "must be a string" in result.error


class TestEnglishDetection:
    """Test English language detection"""
    
    def test_simple_english(self):
        """Should detect simple English text"""
        detector = LanguageDetector()
        result = detector.detect("Hello World")
        
        assert result.success == True
        assert result.language == "en"
        assert result.confidence > 50
    
    def test_long_english_text(self):
        """Should detect longer English paragraph"""
        text = "This is a longer piece of English text. It contains multiple sentences and should be easily detected as English language content."
        detector = LanguageDetector()
        result = detector.detect(text)
        
        assert result.success == True
        assert result.language == "en"
        assert result.confidence > 70
    
    def test_english_with_numbers(self):
        """Should detect English with numbers"""
        detector = LanguageDetector()
        result = detector.detect("The year is 2026 and we are testing")
        
        assert result.success == True
        assert result.language == "en"
    
    def test_english_with_punctuation(self):
        """Should detect English with heavy punctuation"""
        detector = LanguageDetector()
        result = detector.detect("Hello! How are you? I'm doing great, thanks.")
        
        assert result.success == True
        assert result.language == "en"


class TestUrduDetection:
    """Test Urdu language detection"""
    
    def test_simple_urdu(self):
        """Should detect simple Urdu text"""
        detector = LanguageDetector()
        result = detector.detect("سلام دنیا")
        
        assert result.success == True
        assert result.language == "ur"
        assert result.confidence > 50
    
    def test_long_urdu_text(self):
        """Should detect longer Urdu paragraph"""
        text = "یہ ایک طویل اردو متن ہے۔ اس میں متعدد جملے ہیں اور اسے آسانی سے اردو زبان کے مواد کے طور پر پہچانا جانا چاہیے۔"
        detector = LanguageDetector()
        result = detector.detect(text)
        
        assert result.success == True
        assert result.language == "ur"
        assert result.confidence > 70
    
    def test_urdu_with_numbers(self):
        """Should detect Urdu with English numbers"""
        detector = LanguageDetector()
        result = detector.detect("سال 2026 ہے اور ہم جانچ رہے ہیں")
        
        assert result.success == True
        assert result.language == "ur"
    
    def test_urdu_common_phrases(self):
        """Should detect common Urdu phrases"""
        phrases = [
            "السلام علیکم",
            "شکریہ",
            "خوش آمدید",
            "اللہ حافظ"
        ]
        
        detector = LanguageDetector()
        for phrase in phrases:
            result = detector.detect(phrase)
            assert result.success == True
            assert result.language == "ur", f"Failed for phrase: {phrase}"


class TestMixedLanguage:
    """Test mixed English-Urdu text"""
    
    def test_mixed_text_english_dominant(self):
        """Mixed text with more English should detect as English"""
        text = "Hello سلام this is mostly English text"
        detector = LanguageDetector()
        result = detector.detect(text)
        
        assert result.success == True
        # Should be English (more English characters)
        assert result.language == "en"
    
    def test_mixed_text_urdu_dominant(self):
        """Mixed text with more Urdu should detect as Urdu"""
        text = "یہ زیادہ تر اردو ہے with some English"
        detector = LanguageDetector()
        result = detector.detect(text)
        
        assert result.success == True
        # Should be Urdu (more Urdu characters)
        assert result.language == "ur"
    
    def test_is_mixed_language(self):
        """Should identify mixed language text"""
        detector = LanguageDetector()
        
        # True mixed (both languages significant)
        mixed_text = "Hello World سلام دنیا"
        assert detector.is_mixed_language(mixed_text) == True
        
        # Not mixed (pure English)
        english_text = "Hello World"
        assert detector.is_mixed_language(english_text) == False
        
        # Not mixed (pure Urdu)
        urdu_text = "سلام دنیا"
        assert detector.is_mixed_language(urdu_text) == False


class TestDetectionMethods:
    """Test different detection methods"""
    
    def test_unicode_method_used(self):
        """Should use Unicode method for clear cases"""
        detector = LanguageDetector()
        result = detector.detect("Hello World")
        
        assert result.method == "unicode"
    
    def test_result_contains_text_sample(self):
        """Result should contain text sample"""
        detector = LanguageDetector()
        result = detector.detect("This is a test text")
        
        assert result.success == True
        assert len(result.text_sample) > 0
        assert "This is a test" in result.text_sample
    
    def test_result_contains_char_count(self):
        """Result should contain character count"""
        text = "Hello World"
        detector = LanguageDetector()
        result = detector.detect(text)
        
        assert result.char_count == len(text)


class TestConvenienceFunctions:
    """Test quick-access functions"""
    
    def test_detect_language_function(self):
        """Quick detect_language() should work"""
        result = detect_language("Hello World")
        
        assert isinstance(result, LanguageDetectionResult)
        assert result.success == True
        assert result.language == "en"
    
    def test_quick_detect_function(self):
        """Ultra-quick quick_detect() should return just code"""
        lang = quick_detect("Hello World")
        
        assert isinstance(lang, str)
        assert lang == "en"
    
    def test_quick_detect_urdu(self):
        """quick_detect() should work for Urdu"""
        lang = quick_detect("سلام دنیا")
        
        assert lang == "ur"
    
    def test_quick_detect_error_handling(self):
        """quick_detect() should default to 'en' on error"""
        lang = quick_detect("")  # Invalid input
        
        assert lang == "en"  # Defaults to English


class TestSupportedLanguages:
    """Test language support queries"""
    
    def test_get_supported_languages(self):
        """Should return list of supported languages"""
        detector = LanguageDetector()
        languages = detector.get_supported_languages()
        
        assert isinstance(languages, list)
        assert "en" in languages
        assert "ur" in languages
        assert len(languages) == 2


class TestEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_only_numbers(self):
        """Should handle text with only numbers"""
        detector = LanguageDetector()
        result = detector.detect("123 456 789")
        
        assert result.success == True
        # Should default to English
        assert result.language == "en"
    
    def test_only_punctuation(self):
        """Should handle text with mostly punctuation"""
        detector = LanguageDetector()
        result = detector.detect("!!! ??? ...")
        
        assert result.success == True
    
    def test_very_long_text(self):
        """Should handle very long text"""
        long_text = "Hello World " * 1000  # 12,000 characters
        detector = LanguageDetector()
        result = detector.detect(long_text)
        
        assert result.success == True
        assert result.language == "en"
        assert result.char_count > 10000
    
    def test_special_characters(self):
        """Should handle special characters gracefully"""
        text = "Hello @#$%^& World"
        detector = LanguageDetector()
        result = detector.detect(text)
        
        assert result.success == True
        assert result.language == "en"
    
    def test_minimum_valid_length(self):
        """Should accept exactly 3 characters"""
        detector = LanguageDetector()
        result = detector.detect("Hi!")
        
        assert result.success == True


class TestConfidenceScores:
    """Test confidence score accuracy"""
    
    def test_high_confidence_english(self):
        """Pure English should have high confidence"""
        text = "This is pure English text without any other language"
        detector = LanguageDetector()
        result = detector.detect(text)
        
        assert result.confidence > 70
    
    def test_high_confidence_urdu(self):
        """Pure Urdu should have high confidence"""
        text = "یہ خالص اردو متن ہے کسی دوسری زبان کے بغیر"
        detector = LanguageDetector()
        result = detector.detect(text)
        
        assert result.confidence > 70
    
    def test_lower_confidence_mixed(self):
        """Mixed text might have lower confidence"""
        text = "Hello سلام World دنیا"
        detector = LanguageDetector()
        result = detector.detect(text)
        
        # Still should succeed
        assert result.success == True
        # Confidence might be lower but still meaningful
        assert result.confidence > 0


# ============================================
# PYTEST CONFIGURATION
# ============================================

def test_module_imports():
    """Verify all necessary imports work"""
    from modules.language_detector import (
        LanguageDetector,
        LanguageDetectionResult,
        detect_language,
        quick_detect
    )
    
    assert LanguageDetector is not None
    assert LanguageDetectionResult is not None
    assert callable(detect_language)
    assert callable(quick_detect)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])