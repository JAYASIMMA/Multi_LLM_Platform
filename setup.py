#!/usr/bin/env python
"""
Automatic Setup Script for Multi-LLM Platform
This script will set up everything automatically.
"""

import subprocess
import sys
import os

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False

def check_python():
    """Check Python version"""
    print_header("Checking Python Installation")
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        print("Please install Python 3.8+ from https://www.python.org")
        return False
    
    print("✅ Python version is compatible")
    return True

def create_directories():
    """Create necessary directories"""
    print_header("Creating Directory Structure")
    
    directories = [
        'uploads',
        'static',
        'static/images',
        'static/images/icons',
        'templates'
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created: {directory}")
        except Exception as e:
            print(f"❌ Failed to create {directory}: {e}")
            return False
    
    return True

def install_packages():
    """Install required Python packages"""
    print_header("Installing Python Packages")
    
    packages = [
        'Flask==3.0.0',
        'Werkzeug==3.0.1',
        'ollama',
        'Pillow',
        'python-dotenv'
    ]
    
    # Upgrade pip first
    if not run_command(
        f'"{sys.executable}" -m pip install --upgrade pip',
        "Upgrading pip"
    ):
        print("⚠️  Warning: Could not upgrade pip, continuing anyway...")
    
    # Install each package
    all_success = True
    for package in packages:
        if not run_command(
            f'"{sys.executable}" -m pip install {package}',
            f"Installing {package}"
        ):
            all_success = False
    
    return all_success

def verify_installation():
    """Verify all packages are installed correctly"""
    print_header("Verifying Installation")
    
    required_modules = {
        'flask': 'Flask',
        'werkzeug': 'Werkzeug',
        'ollama': 'Ollama',
        'PIL': 'Pillow',
        'dotenv': 'python-dotenv'
    }
    
    all_installed = True
    for module_name, package_name in required_modules.items():
        try:
            __import__(module_name)
            print(f"✅ {package_name} - Installed")
        except ImportError:
            print(f"❌ {package_name} - NOT INSTALLED")
            all_installed = False
    
    return all_installed

def initialize_database():
    """Initialize the database"""
    print_header("Initializing Database")
    
    try:
        from app import init_db
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"⚠️  Could not initialize database: {e}")
        print("You'll need to run this manually later.")
        return True  # Don't fail setup for this

def check_ollama():
    """Check if Ollama is installed"""
    print_header("Checking Ollama Installation")
    
    try:
        result = subprocess.run(
            'ollama --version',
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama command failed")
            return False
    except Exception as e:
        print("❌ Ollama is not installed or not in PATH")
        print("\n📥 Please install Ollama:")
        print("   Windows: https://ollama.ai/download")
        print("   Mac/Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    print_header("Creating Configuration File")
    
    if os.path.exists('.env'):
        print("⚠️  .env file already exists, skipping...")
        return True
    
    try:
        import secrets
        secret_key = secrets.token_hex(32)
        
        env_content = f"""# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV=development
FLASK_DEBUG=True

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216

# Database Configuration
DATABASE_NAME=multi_llm.db

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env file with secure secret key")
        return True
    except Exception as e:
        print(f"⚠️  Could not create .env file: {e}")
        return True  # Don't fail setup for this

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("  🎉 SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 NEXT STEPS:\n")
    
    print("1. Install Ollama (if not already installed):")
    print("   Windows: Download from https://ollama.ai/download")
    print("   Mac/Linux: curl -fsSL https://ollama.ai/install.sh | sh\n")
    
    print("2. Pull the AI models:")
    print("   ollama pull Jayasimma/bharatbuddy")
    print("   ollama pull Jayasimma/Puzhavan")
    print("   ollama pull Jayasimma/gennai")
    print("   ollama pull Jayasimma/creaton-ai")
    print("   ollama pull Jayasimma/Buddyllama")
    print("   ollama pull Jayasimma/codemium_ai")
    print("   ollama pull conceptsintamil/tamil-llama-7b-instruct-v0.2\n")
    
    print("3. Generate icons and images:")
    print("   python favicon_generator.py\n")
    
    print("4. Run the application:")
    print("   python app.py\n")
    
    print("5. Open your browser:")
    print("   http://localhost:5000\n")
    
    print("="*60)
    print("  💡 For help, see the documentation or contact support")
    print("="*60 + "\n")

def main():
    """Main setup function"""
    print("\n" + "🚀 "*20)
    print("  MULTI-LLM PLATFORM - AUTOMATIC SETUP")
    print("🚀 "*20)
    
    # Check Python version
    if not check_python():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Setup failed at directory creation")
        sys.exit(1)
    
    # Install packages
    if not install_packages():
        print("\n⚠️  Some packages failed to install")
        print("Please try manually: pip install Flask Werkzeug ollama Pillow python-dotenv")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Package verification failed")
        print("Please install missing packages manually")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Initialize database (optional, can fail)
    initialize_database()
    
    # Check Ollama
    check_ollama()
    
    # Print next steps
    print_next_steps()
    
    print("✅ Setup script completed successfully!")
    print("\nYou can now run: python app.py")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)