#!/usr/bin/env python3
"""Simple GraphQL debug script"""

import httpx
import json


def test_simple_graphql():
    """Test GraphQL with the working formkey from the GUI"""
    
    print("🔍 Testing GraphQL with known working formkey...")
    
    # Use the formkey that's working in the GUI
    formkey = "c25281d6b4dfb3f76fb03c597e3e61aa"
    
    print(f"✅ Using formkey: {formkey[:10]}...")
    
    # Create session with the same settings as DirectPoeClient
    session = httpx.Client(
        http2=True,
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Poe-Formkey": formkey,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://poe.com",
            "Referer": "https://poe.com/",
        },
        timeout=30.0
    )
    
    # Test 1: Simple viewer query
    print("\n📊 Test 1: Simple viewer query")
    test_viewer_query(session)
    
    # Test 2: Conversations query
    print("\n📊 Test 2: Conversations query")
    test_conversations_query(session)
    
    # Test 3: Try different query structure
    print("\n📊 Test 3: Different query structure")  
    test_different_structure(session)
    
    session.close()


def test_viewer_query(session):
    """Test simple viewer query"""
    
    query = {
        "query": "query { viewer { id } }",
        "variables": {}
    }
    
    try:
        response = session.post("https://poe.com/api/gql_POST", json=query)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data}")
        else:
            print(f"❌ Failed: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")


def test_conversations_query(session):
    """Test the conversations query that's failing"""
    
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
    
    try:
        response = session.post("https://poe.com/api/gql_POST", json=query)
        print(f"Status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {len(data.get('data', {}).get('chats', {}).get('edges', []))} conversations")
            print(f"Response: {json.dumps(data, indent=2)[:1000]}...")
        else:
            print(f"❌ Failed: {response.text}")
            # Print request details for debugging
            print(f"Request URL: {response.request.url}")
            print(f"Request headers: {dict(response.request.headers)}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")


def test_different_structure(session):
    """Test with different query naming and structure"""
    
    # Try without variables first
    query1 = {
        "query": """
        query {
            chats(first: 5) {
                edges {
                    node {
                        id
                        title
                    }
                }
            }
        }
        """
    }
    
    print("Testing without variables...")
    try:
        response = session.post("https://poe.com/api/gql_POST", json=query1)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success without variables!")
            print(f"Response: {json.dumps(data, indent=2)[:500]}...")
        else:
            print(f"❌ Failed: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Try a completely different query
    query2 = {
        "query": """
        query {
            viewer {
                id
                subscription {
                    plan
                }
            }
        }
        """
    }
    
    print("\nTesting viewer subscription query...")
    try:
        response = session.post("https://poe.com/api/gql_POST", json=query2)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success with viewer query!")
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Failed: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    test_simple_graphql()
