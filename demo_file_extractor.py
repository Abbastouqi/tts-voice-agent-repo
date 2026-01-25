"""
Demo for Module 2: File Text Extraction
"""

from modules.file_extractor import FileExtractor
from config import setup_logging
from pathlib import Path

logger = setup_logging()


def main():
    print("="*70)
    print("🎯 MODULE 2 DEMO: File Text Extraction")
    print("="*70)
    
    extractor = FileExtractor()
    
    # Check for sample files
    sample_dir = Path("sample_files")
    
    if not sample_dir.exists():
        print("\n⚠️  'sample_files' directory not found")
        print("\n📝 To test this module:")
        print("   1. Create folder: mkdir sample_files")
        print("   2. Add test files (PDF or DOCX)")
        print("   3. Run this demo again")
        return
    
    # Find all PDF and DOCX files
    pdf_files = list(sample_dir.glob("*.pdf"))
    docx_files = list(sample_dir.glob("*.docx"))
    
    all_files = pdf_files + docx_files
    
    if not all_files:
        print(f"\n⚠️  No PDF or DOCX files found in {sample_dir}")
        print("\n📝 Add some test files and run again")
        return
    
    print(f"\n📁 Found {len(all_files)} file(s) to process\n")
    
    # Process each file
    for i, file_path in enumerate(all_files, 1):
        print(f"{'─'*70}")
        print(f"File {i}: {file_path.name}")
        print(f"{'─'*70}")
        
        result = extractor.extract(str(file_path))
        
        if result.success:
            print(f"✅ Status: SUCCESS")
            print(f"📄 Type: {result.file_type.upper()}")
            print(f"📊 Pages: {result.page_count}")
            print(f"📝 Characters: {result.char_count:,}")
            print(f"📖 First 200 chars:")
            print(f"   {result.text[:200]}...")
        else:
            print(f"❌ Status: FAILED")
            print(f"🚫 Error: {result.error}")
        
        print()
    
    print("="*70)
    print("✅ Demo complete!")


if __name__ == "__main__":
    main()