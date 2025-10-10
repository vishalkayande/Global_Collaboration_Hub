#!/usr/bin/env python3
"""
Global Collaboration Hub Setup Script
This script helps set up the development environment for the Global Collaboration Hub.
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_mysql():
    """Check if MySQL is installed and running"""
    print("🗄️ Checking MySQL...")
    try:
        result = subprocess.run("mysql --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MySQL is installed")
            return True
        else:
            print("❌ MySQL is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ MySQL is not installed")
        return False

def install_backend_dependencies():
    """Install Python dependencies for the backend"""
    print("📦 Installing backend dependencies...")
    os.chdir("backend")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return False
    
    # Activate virtual environment and install dependencies
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    commands = [
        f"{pip_cmd} install --upgrade pip",
        f"{pip_cmd} install -r requirements.txt"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Running: {cmd}"):
            return False
    
    os.chdir("..")
    return True

def setup_database():
    """Set up the MySQL database"""
    print("🗄️ Setting up database...")
    
    # Check if database exists
    try:
        result = subprocess.run(
            "mysql -u root -p -e \"SHOW DATABASES LIKE 'global_collab_hub';\"",
            shell=True, capture_output=True, text=True
        )
        if "global_collab_hub" in result.stdout:
            print("✅ Database already exists")
            return True
    except:
        pass
    
    # Create database
    print("📝 Please enter your MySQL root password when prompted:")
    if not run_command(
        "mysql -u root -p < database/schema.sql",
        "Creating database and tables"
    ):
        print("❌ Failed to create database. Please run the SQL script manually:")
        print("   mysql -u root -p < database/schema.sql")
        return False
    
    return True

def create_env_file():
    """Create environment configuration file"""
    print("⚙️ Creating environment configuration...")
    
    env_content = """# Database Configuration
DATABASE_URL=mysql+pymysql://root:password@localhost/global_collab_hub

# Security Keys (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-string-change-in-production

# Server Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    env_path = "backend/.env"
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write(env_content)
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Global Collaboration Hub...")
    print("=" * 50)
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_mysql():
        print("⚠️  MySQL is required but not found. Please install MySQL and try again.")
        print("   Download from: https://dev.mysql.com/downloads/mysql/")
        sys.exit(1)
    
    # Install dependencies
    if not install_backend_dependencies():
        print("❌ Failed to install backend dependencies")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("❌ Failed to setup database")
        sys.exit(1)
    
    # Create environment file
    if not create_env_file():
        print("❌ Failed to create environment file")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update the database credentials in backend/.env if needed")
    print("2. Start the backend server:")
    print("   cd backend")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("   python app.py")
    print("3. Open frontend/index.html in your web browser")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()
