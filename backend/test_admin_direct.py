#!/usr/bin/env python3

"""
Simple test script to verify admin endpoint functionality
without pytest complications
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from fastapi.testclient import TestClient
from app.main import app
from app.utils.auth import create_access_token

def test_admin_endpoint():
    """Test the admin endpoint directly"""
    
    # Create test client
    client = TestClient(app)
    
    # Create admin token
    admin_token = create_access_token(
        data={
            "sub": "1",
            "email": "admin@sweetshop.com", 
            "role": "admin"
        }
    )
    
    # Test admin users endpoint
    print("Testing admin users endpoint...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/api/admin/users", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        print("✅ Admin endpoint working correctly!")
        return True
    else:
        print("❌ Admin endpoint failed!")
        return False

if __name__ == "__main__":
    success = test_admin_endpoint()
    sys.exit(0 if success else 1)
