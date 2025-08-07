#!/usr/bin/env python3
"""
erpnext_connection_test.py
--------------------------
A minimal script to test and debug the connection to an ERPNext v15 instance.
"""

import sys

import requests
from frappeclient import FrappeClient

# --- 1. Connection Details ---
# Please double-check these for any typos or extra spaces.
ERPNEXT_URL = "https://erp.artisanclarinets.com"
ERPNEXT_API_KEY = "c3b80213c3bceac"
ERPNEXT_API_SECRET = "8d3ab94d6d8e3c6"


def main():
    """Main function to test the connection."""
    print("--- Starting ERPNext Connection Test ---")

    # Step 1: Check if the URL is reachable
    print(f"1. Pinging the server at {ERPNEXT_URL}...")
    try:
        response = requests.get(ERPNEXT_URL, timeout=15)
        response.raise_for_status()
        print("   ✅ SUCCESS: Server is reachable.\n")
    except requests.exceptions.RequestException as e:
        print("   ❌ FAILED: Could not reach the server.", file=sys.stderr)
        print(f"      Error: {e}", file=sys.stderr)
        print("      Please check the ERPNEXT_URL and your network connection.", file=sys.stderr)
        sys.exit(1)

    # Step 2: Attempt to authenticate with the API
    print("2. Authenticating with API credentials...")
    try:
        client = FrappeClient(ERPNEXT_URL, ERPNEXT_API_KEY, ERPNEXT_API_SECRET)
        # Verify the connection by fetching the current user's full name
        user_fullname = client.get_doc("User", client.user)["full_name"]
        print(f"   ✅ SUCCESS: Authenticated as user '{user_fullname}'.\n")
        print("🎉 Connection test passed! You can now proceed with the full script.")

    except Exception as e:
        print("   ❌ FAILED: Could not authenticate.", file=sys.stderr)
        print(f"      Error: {e}", file=sys.stderr)
        print("      This usually means the API Key or Secret is incorrect.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
