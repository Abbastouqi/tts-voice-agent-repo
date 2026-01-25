"""
Main Application Entry Point
TTS Voice Agent - Real-Time Multilingual Text-to-Speech System
"""

from config import startup, settings

def main():
    """
    Application entry point.
    Initializes configuration and starts the system.
    """
    
    # Initialize application
    logger = startup()
    
    logger.info("=" * 60)
    logger.success("✅ Module 0: Bootstrap Complete!")
    logger.info("=" * 60)
    
    # Display configuration summary
    print(f"\n📊 Configuration Summary:")
    print(f"   • App Name: {settings.APP_NAME}")
    print(f"   • Version: {settings.APP_VERSION}")
    print(f"   • Debug Mode: {settings.DEBUG_MODE}")
    print(f"   • Supported Languages: {', '.join(settings.SUPPORTED_LANGUAGES)}")
    print(f"   • TTS Mode: {settings.TTS_MODE}")
    print(f"   • Max File Size: {settings.MAX_FILE_SIZE_MB}MB")
    print(f"   • Audio Format: {settings.AUDIO_FORMAT.upper()}")
    
    print(f"\n✅ System initialized successfully!")
    print(f"🎯 Ready for Module 1 development...\n")


if __name__ == "__main__":
    main()