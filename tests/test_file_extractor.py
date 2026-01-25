"""
Unit tests for File Extractor (Module 2)
"""

import pytest
from pathlib import Path
from modules.file_extractor import FileExtractor, extract_text


class TestFileExtractor:
    """Test suite for FileExtractor"""
    
    @pytest.fixture
    def extractor(self):
        return FileExtractor()
    
    
    def test_unsupported_file_type(self, extractor):
        """Test that unsupported files fail gracefully"""
        result = extractor.extract("test.txt")
        
        assert result.success is False
        assert "not found" in result.error.lower() or "unsupported" in result.error.lower()
    
    
    def test_nonexistent_file(self, extractor):
        """Test that missing files are handled"""
        result = extractor.extract("nonexistent.pdf")
        
        assert result.success is False
        assert "not found" in result.error.lower()
    
    
    def test_supported_extensions(self, extractor):
        """Test supported file extensions"""
        assert '.pdf' in extractor.SUPPORTED_EXTENSIONS
        assert '.docx' in extractor.SUPPORTED_EXTENSIONS
    
    
    def test_convenience_function(self):
        """Test extract_text convenience function"""
        result = extract_text("nonexistent.pdf")
        
        assert result.success is False
        assert isinstance(result.error, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])