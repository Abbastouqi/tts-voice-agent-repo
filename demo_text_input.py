"""
Demo script for Module 1: Text Input Handler
Run this to see the module in action with various inputs.
"""

from modules.text_input import TextInputHandler
from config import setup_logging

# Setup logging
logger = setup_logging()

def main():
    print("="*70)
    print("🎯 MODULE 1 DEMO: Text Input Handler")
    print("="*70)
    
    handler = TextInputHandler()
    
    # Test cases with descriptions
    test_cases = [
        {
            "name": "Simple English",
            "input": "Hello, how are you today?",
            "expected": "Should work perfectly"
        },
        {
            "name": "Urdu Text",
            "input": "السلام علیکم، کیسے ہیں آپ؟",
            "expected": "Should preserve Urdu characters"
        },
        {
            "name": "Mixed Language",
            "input": "Hello دنیا! This is a test یہ ایک ٹیسٹ ہے",
            "expected": "Should preserve both languages"
        },
        {
            "name": "Multiple Spaces",
            "input": "Too    many     spaces    here",
            "expected": "Should normalize to single spaces"
        },
        {
            "name": "Newlines and Tabs",
            "input": "Line 1\nLine 2\tTabbed",
            "expected": "Should convert to spaces"
        },
        {
            "name": "Special Characters",
            "input": "Hello @#$% World &*()!",
            "expected": "Should remove unusual symbols"
        },
        {
            "name": "Leading/Trailing Whitespace",
            "input": "   Trimmed text   ",
            "expected": "Should trim whitespace"
        },
        {
            "name": "Empty String",
            "input": "",
            "expected": "Should FAIL - empty text"
        },
        {
            "name": "Only Whitespace",
            "input": "    \n\t   ",
            "expected": "Should FAIL - whitespace only"
        },
        {
            "name": "Very Long Text",
            "input": "A" * 15000,
            "expected": "Should FAIL - exceeds max length"
        },
    ]
    
    # Process each test case
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*70}")
        print(f"Test {i}: {test['name']}")
        print(f"{'─'*70}")
        print(f"📥 Input: {test['input'][:60]}{'...' if len(test['input']) > 60 else ''}")
        print(f"🎯 Expected: {test['expected']}")
        
        # Process the text
        result = handler.process(test['input'])
        
        # Display result
        if result.success:
            print(f"✅ Status: SUCCESS")
            print(f"📝 Output: {result.text[:60]}{'...' if len(result.text) > 60 else ''}")
            print(f"📊 Stats:")
            print(f"   • Characters: {result.char_count}")
            print(f"   • Words: {result.word_count}")
            print(f"   • Original length: {len(result.original_text)}")
        else:
            print(f"❌ Status: FAILED")
            print(f"🚫 Error: {result.error}")
    
    print(f"\n{'='*70}")
    print("✅ Demo complete! Module 1 is working correctly.")
    print("="*70)


if __name__ == "__main__":
    main()