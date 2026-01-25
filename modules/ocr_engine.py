"""
Module 3: Image OCR Engine
Extract text from images using Tesseract OCR.

Supports:
- English text recognition
- Urdu text recognition
- Image preprocessing for better accuracy
"""

from typing import Optional, List
from dataclasses import dataclass
from pathlib import Path
import io

# OCR library
import pytesseract

# Image processing
from PIL import Image
import cv2
import numpy as np

from loguru import logger


# Configure Tesseract path (Windows only)
# Uncomment and adjust if Tesseract not in PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


@dataclass
class OCRResult:
    """Result of OCR text extraction"""
    success: bool
    text: str
    image_path: str
    language: str
    confidence: float
    char_count: int
    error: Optional[str] = None


class OCREngine:
    """Extract text from images using Tesseract OCR"""
    
    # Supported image formats
    SUPPORTED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
    
    # Language codes for Tesseract
    LANG_MAP = {
        'en': 'eng',      # English
        'ur': 'urd',      # Urdu
        'mixed': 'eng+urd'  # Both
    }
    
    MAX_IMAGE_SIZE_MB = 10
    
    def __init__(self, preprocess: bool = True):
        """
        Initialize OCR Engine
        
        Args:
            preprocess: Apply image preprocessing for better accuracy
        """
        self.preprocess = preprocess
        logger.info(f"OCREngine initialized (preprocess={preprocess})")
        
        # Verify Tesseract is installed
        self._verify_tesseract()
    
    
    def _verify_tesseract(self):
        """Check if Tesseract is installed"""
        try:
            pytesseract.get_tesseract_version()
            logger.info("✅ Tesseract OCR found")
        except Exception as e:
            logger.error("❌ Tesseract not found. Please install it.")
            logger.error("Windows: https://github.com/UB-Mannheim/tesseract/wiki")
            logger.error("Linux: sudo apt-get install tesseract-ocr")
            logger.error("Mac: brew install tesseract")
    
    
    def extract(self, image_path: str, language: str = 'mixed') -> OCRResult:
        """
        Extract text from image
        
        Args:
            image_path: Path to image file
            language: 'en', 'ur', or 'mixed'
            
        Returns:
            OCRResult with extracted text
        """
        try:
            path = Path(image_path)
            
            # Validate image
            error = self._validate_image(path)
            if error:
                return self._create_error_result(str(path), language, error)
            
            # Load image
            image = Image.open(path)
            
            # Preprocess if enabled
            if self.preprocess:
                image = self._preprocess_image(image)
            
            # Extract text
            lang_code = self.LANG_MAP.get(language, 'eng+urd')
            
            # Get text and confidence
            text = pytesseract.image_to_string(image, lang=lang_code)
            
            # Get confidence score
            data = pytesseract.image_to_data(image, lang=lang_code, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            if not text.strip():
                return self._create_error_result(
                    str(path), 
                    language, 
                    "No text detected in image"
                )
            
            return OCRResult(
                success=True,
                text=text.strip(),
                image_path=str(path),
                language=language,
                confidence=avg_confidence,
                char_count=len(text.strip()),
                error=None
            )
        
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return self._create_error_result(str(image_path), language, f"OCR error: {str(e)}")
    
    
    def extract_from_bytes(self, image_bytes: bytes, filename: str, language: str = 'mixed') -> OCRResult:
        """
        Extract text from image bytes (for web uploads)
        
        Args:
            image_bytes: Image data as bytes
            filename: Original filename
            language: 'en', 'ur', or 'mixed'
            
        Returns:
            OCRResult
        """
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_bytes))
            
            # Preprocess if enabled
            if self.preprocess:
                image = self._preprocess_image(image)
            
            # Extract text
            lang_code = self.LANG_MAP.get(language, 'eng+urd')
            # text = pytesseract.image_to_string(image, lang=lang_code)
            text = pytesseract.image_to_string(image, lang=tesseract_lang, config='--psm 6')
            
            # Get confidence
            data = pytesseract.image_to_data(image, lang=lang_code, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            if not text.strip():
                return self._create_error_result(filename, language, "No text detected")
            
            return OCRResult(
                success=True,
                text=text.strip(),
                image_path=filename,
                language=language,
                confidence=avg_confidence,
                char_count=len(text.strip()),
                error=None
            )
        
        except Exception as e:
            return self._create_error_result(filename, language, f"OCR error: {str(e)}")
    
    
    def _validate_image(self, path: Path) -> Optional[str]:
        """Validate image file"""
        
        if not path.exists():
            return f"Image not found: {path}"
        
        if not path.is_file():
            return f"Not a file: {path}"
        
        extension = path.suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            return f"Unsupported image type: {extension}"
        
        # Check file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > self.MAX_IMAGE_SIZE_MB:
            return f"Image too large: {size_mb:.2f}MB (max: {self.MAX_IMAGE_SIZE_MB}MB)"
        
        return None
    
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy
        
        Steps:
        1. Convert to grayscale
        2. Apply thresholding (binarization)
        3. Denoise
        4. Increase contrast
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert PIL to OpenCV format
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                gray, 
                255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 
                11, 
                2
            )
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
            
            # Convert back to PIL
            processed = Image.fromarray(denoised)
            
            logger.debug("Image preprocessed successfully")
            return processed
        
        except Exception as e:
            logger.warning(f"Preprocessing failed, using original: {str(e)}")
            return image
    
    
    def _create_error_result(self, image_path: str, language: str, error: str) -> OCRResult:
        """Create error result"""
        logger.warning(f"OCR failed for {image_path}: {error}")
        
        return OCRResult(
            success=False,
            text="",
            image_path=image_path,
            language=language,
            confidence=0.0,
            char_count=0,
            error=error
        )
    
    
    def get_available_languages(self) -> List[str]:
        """
        Get list of installed Tesseract languages
        
        Returns:
            List of language codes
        """
        try:
            langs = pytesseract.get_languages()
            logger.info(f"Available OCR languages: {langs}")
            return langs
        except Exception as e:
            logger.error(f"Could not get languages: {str(e)}")
            return []


# Convenience function
def extract_text_from_image(image_path: str, language: str = 'mixed') -> OCRResult:
    """
    Quick OCR extraction
    
    Example:
        >>> from modules.ocr_engine import extract_text_from_image
        >>> result = extract_text_from_image("screenshot.png")
        >>> print(result.text)
    """
    engine = OCREngine()
    return engine.extract(image_path, language)


if __name__ == "__main__":
    print("="*60)
    print("MODULE 3: OCR Engine - Self Test")
    print("="*60)
    
    engine = OCREngine()
    
    # Check available languages
    print("\n📚 Checking installed languages...")
    langs = engine.get_available_languages()
    
    if langs:
        print(f"✅ Found {len(langs)} language(s): {', '.join(langs)}")
        
        if 'eng' in langs:
            print("   ✅ English supported")
        else:
            print("   ⚠️  English not found")
        
        if 'urd' in langs:
            print("   ✅ Urdu supported")
        else:
            print("   ⚠️  Urdu not found - install: tesseract-ocr-urd")
    else:
        print("❌ No languages found - is Tesseract installed?")
    
    print("\n⚠️  To test OCR:")
    print("   1. Create 'sample_images' folder")
    print("   2. Add test images with text")
    print("   3. Run: python demo_ocr_engine.py")