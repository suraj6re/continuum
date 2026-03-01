"""
Quick script to check if MongoDB is running
"""

import subprocess
import sys

def check_mongodb():
    print("Checking MongoDB status...")
    print("=" * 60)
    
    # Check if MongoDB service exists
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-Service MongoDB -ErrorAction SilentlyContinue"],
            capture_output=True,
            text=True
        )
        
        if "MongoDB" in result.stdout:
            print("✓ MongoDB service found")
            if "Running" in result.stdout:
                print("✓ MongoDB is RUNNING")
                print("\nYou can start the backend server now:")
                print("  python main.py")
                return True
            else:
                print("✗ MongoDB service exists but is NOT running")
                print("\nStart MongoDB with:")
                print("  Start-Service MongoDB")
                return False
        else:
            print("✗ MongoDB service not found")
            print("\nMongoDB might not be installed or not running as a service")
    except Exception as e:
        print(f"Could not check service: {e}")
    
    # Check if MongoDB port is listening
    print("\nChecking if port 27017 is listening...")
    try:
        result = subprocess.run(
            ["powershell", "-Command", "netstat -an | Select-String '27017'"],
            capture_output=True,
            text=True
        )
        
        if "27017" in result.stdout and "LISTENING" in result.stdout:
            print("✓ MongoDB port 27017 is LISTENING")
            print("\nMongoDB is running! You can start the backend server:")
            print("  python main.py")
            return True
        else:
            print("✗ Port 27017 is not listening")
    except Exception as e:
        print(f"Could not check port: {e}")
    
    print("\n" + "=" * 60)
    print("MongoDB is NOT running!")
    print("\nOptions:")
    print("1. Install MongoDB: https://www.mongodb.com/try/download/community")
    print("2. Start MongoDB service: Start-Service MongoDB")
    print("3. Or run mongod manually: mongod --dbpath C:\\data\\db")
    print("=" * 60)
    
    return False

if __name__ == "__main__":
    is_running = check_mongodb()
    sys.exit(0 if is_running else 1)
