#!/usr/bin/env python3
"""Debug GraphQL queries to Poe.com"""

import httpx
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from poe_search.utils.config import get_credentials


def test_graphql_queries():
    """Test different GraphQL queries and see what works"""
    
    print("🔍 Testing GraphQL queries to debug conversation fetching...")
    
    # Get credentials
    creds = get_credentials()
    if not creds or not creds.get('formkey'):
        print("❌ No credentials found")
        return
    
    formkey = creds['formkey']
    p_b_cookie = creds.get('p_b', '')
    
    print(f"✅ Using formkey: {formkey[:10]}...")
    print(f"✅ Using p-b cookie: {p_b_cookie[:10]}..." if p_b_cookie else "⚠️ No p-b cookie")
    
    # Create session
    session = httpx.Client(
        http2=True,
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        },
        cookies={"p-b": p_b_cookie} if p_b_cookie else {},
        timeout=30.0
    )
    
    # Test 1: Simple viewer query
    print("\n📊 Test 1: Simple viewer query")
    test_simple_query(session, formkey)
    
    # Test 2: Check if we need different headers
    print("\n📊 Test 2: Query with additional headers")
    test_with_headers(session, formkey)
    
    # Test 3: Try different GraphQL endpoints
    print("\n📊 Test 3: Try different endpoints")
    test_different_endpoints(session, formkey)
    
    # Test 4: Check what a working browser request looks like
    print("\n📊 Test 4: Analyze request format")
    test_request_format(session, formkey)
    
    session.close()

def test_simple_query(session, formkey):
    """Test a simple viewer query"""
    
    query = {
        "query": "query { viewer { id } }",
        "variables": {}
    }
    
    headers = {
        "Poe-Formkey": formkey,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://poe.com",
        "Referer": "https://poe.com/",
    }
    
    try:
        response = session.post(
            "https://poe.com/api/gql_POST",
            json=query,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data}")
        else:
            print(f"❌ Failed: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_with_headers(session, formkey):
    """Test with additional headers that might be required"""
    
    query = {
        "query": """
        query ChatListPaginationQuery($count: Int!) {
            chats(first: $count) {
                edges {
                    node {
                        id
                        title
                        creationTime
                        lastMessageTime
                        bot {
                            nickname
                            displayName
                        }
                    }
                }
            }
        }
        """,
        "variables": {"count": 5}
    }
    
    headers = {
        "Poe-Formkey": formkey,
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://poe.com",
        "Referer": "https://poe.com/",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Requested-With": "XMLHttpRequest",
    }
    
    try:
        response = session.post(
            "https://poe.com/api/gql_POST",
            json=query,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {len(data.get('data', {}).get('chats', {}).get('edges', []))} conversations")
        else:
            print(f"❌ Failed: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_different_endpoints(session, formkey):
    """Test different GraphQL endpoints"""
    
    endpoints = [
        "https://poe.com/api/gql_POST",
        "https://poe.com/api/graphql",
        "https://poe.com/graphql",
    ]
    
    query = {
        "query": "query { viewer { id } }",
        "variables": {}
    }
    
    headers = {
        "Poe-Formkey": formkey,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://poe.com",
        "Referer": "https://poe.com/",
    }
    
    for endpoint in endpoints:
        print(f"Testing: {endpoint}")
        try:
            response = session.post(endpoint, json=query, headers=headers)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ Success!")
            else:
                print(f"  ❌ Failed: {response.text[:200]}")
        except Exception as e:
            print(f"  ❌ Exception: {e}")

def test_request_format(session, formkey):
    """Test if the request format needs to be different"""
    
    # Try sending as form data instead of JSON
    query_string = json.dumps({
        "query": "query { viewer { id } }",
        "variables": {}
    })
    
    headers = {
        "Poe-Formkey": formkey,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Origin": "https://poe.com",
        "Referer": "https://poe.com/",
    }
    
    try:
        response = session.post(
            "https://poe.com/api/gql_POST",
            data={"query": query_string},
            headers=headers
        )
        
        print(f"Form data format - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Form data success: {data}")
        else:
            print(f"❌ Form data failed: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Form data exception: {e}")
        
    # Also try the original JSON format but with different content-type
    headers["Content-Type"] = "application/json; charset=utf-8"
    
    query = {
        "query": "query { viewer { id } }",
        "variables": {}
    }
    
    try:
        response = session.post(
            "https://poe.com/api/gql_POST",
            json=query,
            headers=headers
        )
        
        print(f"JSON with charset - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Charset success: {data}")
        else:
            print(f"❌ Charset failed: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Charset exception: {e}")

if __name__ == "__main__":
    test_graphql_queries()
