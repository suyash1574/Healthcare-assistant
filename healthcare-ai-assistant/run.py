"""
run.py — Single entry point for Healthcare AI Assistant
Usage:  python run.py
"""
import os
import sys


def check_env():
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(env_path)
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY not set in .env file")
        sys.exit(1)
    print("Environment loaded OK")


def install_deps():
    req = os.path.join(os.path.dirname(__file__), "requirements.txt")
    print("Installing / verifying dependencies...")
    os.system(f'"{sys.executable}" -m pip install -r "{req}" -q 2>nul')
    print("Dependencies ready")


def main():
    print("=" * 45)
    print("  Healthcare AI Assistant")
    print("=" * 45)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    install_deps()
    check_env()

    import uvicorn
    print("\nStarting server -> http://localhost:8000")
    print("Press Ctrl+C to stop\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="warning"
    )


if __name__ == "__main__":
    main()
