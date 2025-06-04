import http.client
import json
import time
from datetime import datetime
import os

# Test the health endpoints
def test_health( ):
    print("Testing API health...")
    conn = http.client.HTTPConnection("localhost", 8000 )
    conn.request("GET", "/health")
    response = conn.getresponse()
    data = response.read().decode()
    print(f"Status: {response.status}, Response: {data}")
    
    print("\nTesting Business service health...")
    conn = http.client.HTTPConnection("localhost", 8001 )
    conn.request("GET", "/health")
    response = conn.getresponse()
    data = response.read().decode()
    print(f"Status: {response.status}, Response: {data}")
    
    print("\nTesting Integration service health...")
    conn = http.client.HTTPConnection("localhost", 8002 )
    conn.request("GET", "/health")
    response = conn.getresponse()
    data = response.read().decode()
    print(f"Status: {response.status}, Response: {data}")

if __name__ == "__main__":
    print("Starting basic LBaaS testing...")
    test_health()
    print("\nTesting complete!")
