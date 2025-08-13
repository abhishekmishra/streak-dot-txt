"""
Test script for the Streak API
Run this after starting the API server to test basic functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_api():
    """Test the basic API endpoints"""
    print("Testing Streak API...")

    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except requests.exceptions.ConnectionError:
        print(
            "API server is not running. Start it with: uvicorn streak_api.main:app --reload"
        )
        return

    # Test root endpoint
    response = requests.get(f"{BASE_URL}/")
    print(f"Root endpoint: {response.status_code} - {response.json()}")

    # Test config endpoint
    response = requests.get(f"{BASE_URL}/api/v1/config")
    print(f"Config endpoint: {response.status_code}")
    if response.status_code == 200:
        config = response.json()
        print(f"Streaks directory: {config['streaks_directory']}")
        print(f"Directory exists: {config['directory_exists']}")
        print(f"Total streak files: {config['total_streak_files']}")

    # Test get all streaks
    response = requests.get(f"{BASE_URL}/api/v1/streaks")
    print(f"Get all streaks: {response.status_code}")
    if response.status_code == 200:
        streaks = response.json()
        print(f"Found {len(streaks)} streaks")
        for streak in streaks:
            print(f"  - {streak['name']} ({streak['tick_type']})")

    # Test create a new streak
    test_streak = {
        "name": "test-api-streak",
        "tick_type": "Daily",
        "description": "Test streak created via API",
    }

    response = requests.post(f"{BASE_URL}/api/v1/streaks", json=test_streak)
    print(f"Create streak: {response.status_code}")
    if response.status_code == 200:
        created_streak = response.json()
        print(f"Created streak: {created_streak['name']}")

        # Test adding a tick
        response = requests.post(f"{BASE_URL}/api/v1/streaks/test-api-streak/tick")
        print(f"Add tick: {response.status_code} - {response.json()}")

        # Test getting the specific streak
        response = requests.get(f"{BASE_URL}/api/v1/streaks/test-api-streak")
        print(f"Get specific streak: {response.status_code}")
        if response.status_code == 200:
            streak_data = response.json()
            print(f"Streak has {len(streak_data['ticks'])} ticks")

    print("API test completed!")


if __name__ == "__main__":
    test_api()
