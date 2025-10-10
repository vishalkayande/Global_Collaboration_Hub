#!/usr/bin/env python3
"""
Debug the issues with student details and workspace creation
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_user_registration():
    """Test user registration"""
    print("🔍 Testing User Registration...")
    
    # Register a student
    student_data = {
        "username": "debug_student",
        "email": "debug_student@test.com",
        "password": "password123",
        "first_name": "Debug",
        "last_name": "Student",
        "role": "student"
    }
    response = requests.post(f"{BASE_URL}/signup", json=student_data)
    print(f"Student registration: {response.status_code}")
    if response.status_code == 201:
        student_token = response.json().get("access_token")
        print(f"Student token: {student_token[:20]}...")
        return student_token
    else:
        print(f"Error: {response.text}")
    return None

def test_external_agency_registration():
    """Test external agency registration"""
    print("\n🔍 Testing External Agency Registration...")
    
    agency_data = {
        "username": "debug_agency",
        "email": "debug_agency@test.com",
        "password": "password123",
        "first_name": "Debug",
        "last_name": "Agency",
        "role": "external"
    }
    response = requests.post(f"{BASE_URL}/signup", json=agency_data)
    print(f"Agency registration: {response.status_code}")
    if response.status_code == 201:
        agency_token = response.json().get("access_token")
        print(f"Agency token: {agency_token[:20]}...")
        return agency_token
    else:
        print(f"Error: {response.text}")
    return None

def test_students_list(agency_token):
    """Test getting students list"""
    print("\n🔍 Testing Students List...")
    
    if not agency_token:
        print("No agency token available")
        return
    
    headers = {"Authorization": f"Bearer {agency_token}"}
    response = requests.get(f"{BASE_URL}/students", headers=headers)
    print(f"Students list status: {response.status_code}")
    if response.status_code == 200:
        students = response.json()
        print(f"Found {len(students)} students")
        for student in students:
            print(f"  - {student['first_name']} {student['last_name']} ({student['email']})")
    else:
        print(f"Error: {response.text}")

def test_workspace_creation(agency_token):
    """Test workspace creation"""
    print("\n🔍 Testing Workspace Creation...")
    
    if not agency_token:
        print("No agency token available")
        return
    
    headers = {"Authorization": f"Bearer {agency_token}"}
    workspace_data = {
        "name": "Debug Workspace",
        "description": "A debug workspace for testing"
    }
    response = requests.post(f"{BASE_URL}/workspaces", json=workspace_data, headers=headers)
    print(f"Workspace creation status: {response.status_code}")
    if response.status_code == 201:
        workspace = response.json().get("workspace")
        print(f"Workspace created: {workspace}")
        return workspace.get("id") if workspace else None
    else:
        print(f"Error: {response.text}")
    return None

def test_workspace_list(agency_token):
    """Test getting workspaces list"""
    print("\n🔍 Testing Workspaces List...")
    
    if not agency_token:
        print("No agency token available")
        return
    
    headers = {"Authorization": f"Bearer {agency_token}"}
    response = requests.get(f"{BASE_URL}/workspaces", headers=headers)
    print(f"Workspaces list status: {response.status_code}")
    if response.status_code == 200:
        workspaces = response.json()
        print(f"Found {len(workspaces)} workspaces")
        for workspace in workspaces:
            print(f"  - {workspace['name']} (Role: {workspace['role']}, Status: {workspace['status']})")
    else:
        print(f"Error: {response.text}")

def main():
    print("=" * 60)
    print("🐛 DEBUGGING NGO COLLABORATION HUB ISSUES")
    print("=" * 60)
    
    # Test user registration
    student_token = test_user_registration()
    agency_token = test_external_agency_registration()
    
    # Test students list
    test_students_list(agency_token)
    
    # Test workspace creation
    workspace_id = test_workspace_creation(agency_token)
    
    # Test workspace list
    test_workspace_list(agency_token)
    
    print("\n" + "=" * 60)
    print("📋 DEBUG SUMMARY:")
    print("=" * 60)
    print(f"Student registration: {'✅' if student_token else '❌'}")
    print(f"Agency registration: {'✅' if agency_token else '❌'}")
    print(f"Students list access: {'✅' if agency_token else '❌'}")
    print(f"Workspace creation: {'✅' if workspace_id else '❌'}")
    
    if not student_token:
        print("\n❌ Issue: Student registration failed")
    if not agency_token:
        print("\n❌ Issue: Agency registration failed")
    if not workspace_id:
        print("\n❌ Issue: Workspace creation failed")

if __name__ == "__main__":
    main()

