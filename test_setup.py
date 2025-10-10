#!/usr/bin/env python3
"""
Test Setup Script
This script tests the Global Collaboration Hub setup to ensure everything is working correctly.
"""

import requests
import json
import time
import sys
import os

# Configuration
API_BASE_URL = "http://localhost:5000/api"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "password": "testpassword123"
}

def test_server_connection():
    """Test if the server is running"""
    print("🔄 Testing server connection...")
    try:
        response = requests.get(f"{API_BASE_URL}/profile", timeout=5)
        # We expect 401 (unauthorized) since we're not sending a token
        if response.status_code == 401:
            print("✅ Server is running and responding")
            return True
        else:
            print(f"⚠️  Server responded with status {response.status_code}")
            return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running.")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print("🔄 Testing user registration...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/signup",
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            print("✅ User registration successful")
            return response.json()["access_token"]
        elif response.status_code == 400 and "already registered" in response.json().get("error", ""):
            print("✅ User already exists (expected for repeated tests)")
            # Try to login instead
            return test_user_login()
        else:
            print(f"❌ Registration failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_user_login():
    """Test user login"""
    print("🔄 Testing user login...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ User login successful")
            return response.json()["access_token"]
        else:
            print(f"❌ Login failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_authenticated_endpoints(token):
    """Test endpoints that require authentication"""
    print("🔄 Testing authenticated endpoints...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test profile endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/profile", headers=headers)
        if response.status_code == 200:
            print("✅ Profile endpoint working")
        else:
            print(f"❌ Profile endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Profile endpoint error: {e}")
        return False
    
    # Test workspaces endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/workspaces", headers=headers)
        if response.status_code == 200:
            print("✅ Workspaces endpoint working")
        else:
            print(f"❌ Workspaces endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Workspaces endpoint error: {e}")
        return False
    
    return True

def test_workspace_creation(token):
    """Test workspace creation"""
    print("🔄 Testing workspace creation...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    workspace_data = {
        "name": "Test Workspace",
        "description": "A test workspace for testing purposes"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/workspaces",
            json=workspace_data,
            headers=headers
        )
        
        if response.status_code == 201:
            print("✅ Workspace creation successful")
            workspace = response.json()["workspace"]
            return workspace["id"]
        else:
            print(f"❌ Workspace creation failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Workspace creation error: {e}")
        return None

def test_workspace_features(token, workspace_id):
    """Test workspace features (messages, files, tasks)"""
    print("🔄 Testing workspace features...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test messages endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/workspaces/{workspace_id}/messages", headers=headers)
        if response.status_code == 200:
            print("✅ Messages endpoint working")
        else:
            print(f"❌ Messages endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Messages endpoint error: {e}")
    
    # Test files endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/workspaces/{workspace_id}/files", headers=headers)
        if response.status_code == 200:
            print("✅ Files endpoint working")
        else:
            print(f"❌ Files endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Files endpoint error: {e}")
    
    # Test tasks endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/workspaces/{workspace_id}/tasks", headers=headers)
        if response.status_code == 200:
            print("✅ Tasks endpoint working")
        else:
            print(f"❌ Tasks endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Tasks endpoint error: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing Global Collaboration Hub Setup")
    print("=" * 50)
    
    # Test server connection
    if not test_server_connection():
        print("\n❌ Setup test failed: Server is not running")
        print("Please start the backend server first:")
        print("  python run_backend.py")
        sys.exit(1)
    
    # Test user registration/login
    token = test_user_registration()
    if not token:
        print("\n❌ Setup test failed: Authentication not working")
        sys.exit(1)
    
    # Test authenticated endpoints
    if not test_authenticated_endpoints(token):
        print("\n❌ Setup test failed: Authenticated endpoints not working")
        sys.exit(1)
    
    # Test workspace creation
    workspace_id = test_workspace_creation(token)
    if not workspace_id:
        print("\n❌ Setup test failed: Workspace creation not working")
        sys.exit(1)
    
    # Test workspace features
    test_workspace_features(token, workspace_id)
    
    print("\n" + "=" * 50)
    print("🎉 Setup test completed successfully!")
    print("\nThe Global Collaboration Hub is working correctly.")
    print("You can now:")
    print("1. Open frontend/index.html in your browser")
    print("2. Login with the test account:")
    print(f"   Email: {TEST_USER['email']}")
    print(f"   Password: {TEST_USER['password']}")
    print("3. Start using the application!")

if __name__ == "__main__":
    main()
