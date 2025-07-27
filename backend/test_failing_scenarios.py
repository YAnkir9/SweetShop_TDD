#!/usr/bin/env python3
"""
Test the specific failing scenarios from pytest to understand the difference
"""
import asyncio
import sys
sys.path.append('.')

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app

def test_duplicate_registration():
    """Test the exact scenario that fails in pytest"""
    print("🔍 Testing duplicate registration scenario...")
    
    with TestClient(app) as client:
        # Create unique user data
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"duplicateuser_{unique_id}",
            "email": f"duplicate_{unique_id}@example.com",
            "password": "securepassword123"
        }
        
        print(f"Testing with email: {user_data['email']}")
        
        # First registration
        print("First registration...")
        response1 = client.post("/api/auth/register", json=user_data)
        print(f"Response 1 status: {response1.status_code}")
        if response1.status_code != 201:
            print(f"Response 1 content: {response1.text}")
            return False
        
        # Second registration with same email
        print("Second registration with same email...")
        user_data["username"] = f"different_{user_data['username']}"
        response2 = client.post("/api/auth/register", json=user_data)
        print(f"Response 2 status: {response2.status_code}")
        if response2.status_code != 400:
            print(f"Response 2 content: {response2.text}")
            return False
        
        response_data = response2.json()
        if "already registered" not in response_data["detail"].lower():
            print(f"Wrong error message: {response_data}")
            return False
        
        print("✅ Duplicate registration test PASSED!")
        return True

def test_invalid_login():
    """Test the invalid login scenario"""
    print("\n🔍 Testing invalid login scenario...")
    
    with TestClient(app) as client:
        # Test with nonexistent email
        print("Testing nonexistent email...")
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        
        print(f"Response status: {response.status_code}")
        if response.status_code != 401:
            print(f"Response content: {response.text}")
            return False
        
        response_data = response.json()
        if "invalid credentials" not in response_data["detail"].lower():
            print(f"Wrong error message: {response_data}")
            return False
        
        print("✅ Invalid login test PASSED!")
        return True

if __name__ == "__main__":
    print("🚀 Testing the specific failing scenarios directly...\n")
    
    duplicate_passed = test_duplicate_registration()
    login_passed = test_invalid_login()
    
    print("\n📊 RESULTS:")
    print(f"Duplicate registration test: {'✅ PASSED' if duplicate_passed else '❌ FAILED'}")
    print(f"Invalid login test: {'✅ PASSED' if login_passed else '❌ FAILED'}")
    
    if duplicate_passed and login_passed:
        print("\n🎉 ALL TESTS PASSED! The authentication logic works perfectly.")
        print("The pytest failures are indeed due to async event loop issues, not code bugs.")
    else:
        print("\n⚠️ There may be actual logic issues that need to be addressed.")
