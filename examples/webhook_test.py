#!/usr/bin/env python3
"""
Webhook Command Testing Script for Makernaut Discord Bot

This script tests the webhook command functionality with proper HMAC signatures.
Make sure to set your WEBHOOK_SECRET_KEY environment variable before running.

Usage:
    # Set WEBHOOK_SECRET_KEY in your .env file
    # Update the configuration section with your webhook URL and IDs
    python examples/webhook_test.py
"""

import os
import time
import hmac
import hashlib
import requests
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Configuration - UPDATE THESE VALUES FOR YOUR SETUP
WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
USER_ID = "123456789012345678"    # Replace with actual user ID to test
ROLE_ID = "987654321098765432"    # Replace with actual role ID to test
CHANNEL_ID = "555666777888999000" # Replace with actual channel ID to test

# Test data
TEST_COMMANDS = [
    {
        "name": "GET_USER_INFO",
        "command": "GET_USER_INFO",
        "params": [USER_ID],
        "description": "Get user information"
    },
    {
        "name": "ASSIGN_ROLE",
        "command": "ASSIGN_ROLE",
        "params": [USER_ID, ROLE_ID],
        "description": "Assign role to user"
    },
    {
        "name": "REMOVE_ROLE",
        "command": "REMOVE_ROLE",
        "params": [USER_ID, ROLE_ID],
        "description": "Remove role from user"
    },
    {
        "name": "SEND_MESSAGE",
        "command": "SEND_MESSAGE",
        "params": [CHANNEL_ID, "Test message from webhook script"],
        "description": "Send message to channel"
    }
]

def generate_hmac_signature(message: str, secret_key: str) -> str:
    """Generate HMAC-SHA256 signature for webhook message"""
    return hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def build_webhook_message(request_id: str, command: str, params: list, secret_key: str) -> str:
    """Build complete webhook message with HMAC signature"""
    timestamp = str(int(time.time()))

    # Build message without signature
    parts = ["BOT_CMD", request_id, command] + params + [timestamp]
    message_without_signature = ":".join(parts)

    # Generate HMAC signature
    signature = generate_hmac_signature(message_without_signature, secret_key)

    # Return complete message
    return f"{message_without_signature}:{signature}"

def send_webhook_command(message: str) -> Dict[str, Any]:
    """Send webhook command to Discord and return response info"""
    payload = {"content": message}

    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        return {
            "success": response.status_code == 204,
            "status_code": response.status_code,
            "response_text": response.text if response.text else "No content",
            "error": None
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "status_code": None,
            "response_text": None,
            "error": str(e)
        }

def test_webhook_commands():
    """Test all webhook commands with proper HMAC signatures"""

    # Load environment variables from .env file
    load_dotenv()

    # Get secret key from environment
    secret_key = os.getenv('WEBHOOK_SECRET_KEY', '').strip()
    if not secret_key:
        print("[ERROR] WEBHOOK_SECRET_KEY not found!")
        print("   Add it to your .env file: WEBHOOK_SECRET_KEY='your_secret_key_here'")
        return

    # Validate configuration
    if "YOUR_WEBHOOK" in WEBHOOK_URL:
        print("[ERROR] Please update WEBHOOK_URL in the configuration section")
        return

    print("Testing Makernaut Webhook Commands")
    print("=" * 50)
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Secret Key: {secret_key[:8]}...{secret_key[-8:] if len(secret_key) > 16 else secret_key}")
    print(f"Test User ID: {USER_ID}")
    print(f"Test Role ID: {ROLE_ID}")
    print(f"Test Channel ID: {CHANNEL_ID}")
    print("=" * 50)

    for i, test in enumerate(TEST_COMMANDS, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"   Description: {test['description']}")

        # Generate request ID
        request_id = f"test{i:03d}"

        # Build webhook message with HMAC
        try:
            message = build_webhook_message(
                request_id,
                test['command'],
                test['params'],
                secret_key
            )

            print(f"   Message: {message}")

            # Send webhook command
            print("   Sending...", end=" ")
            result = send_webhook_command(message)

            if result['success']:
                print("[OK] Sent successfully")
                print(f"   Status: {result['status_code']}")
            else:
                print("[FAIL] Failed to send")
                print(f"   Status: {result['status_code']}")
                print(f"   Error: {result['error'] or result['response_text']}")

        except Exception as e:
            print(f"[ERROR] Error building message: {e}")

        # Wait between requests to avoid rate limiting
        if i < len(TEST_COMMANDS):
            print("   Waiting 2 seconds...")
            time.sleep(2)

    print("\n" + "=" * 50)
    print("[COMPLETE] Testing complete!")
    print("\nCheck the bot channel for:")
    print("   - Successful commands show: [OK] BOT_RESPONSE:...")
    print("   - Failed commands show: [ERR] BOT_RESPONSE:...")
    print("   - HMAC errors show: [ERR] HMAC_VALIDATION_FAILED:...")

def validate_hmac_example():
    """Show example of HMAC validation that matches bot logic"""
    print("\nHMAC Validation Example")
    print("-" * 30)

    # Load environment variables from .env file
    load_dotenv()
    secret_key = os.getenv('WEBHOOK_SECRET_KEY', 'example_key')
    request_id = "example"
    command = "GET_USER_INFO"
    params = [USER_ID]
    timestamp = str(int(time.time()))

    # Build message parts
    parts = ["BOT_CMD", request_id, command] + params + [timestamp]
    message_without_signature = ":".join(parts)

    # Generate signature
    signature = generate_hmac_signature(message_without_signature, secret_key)
    complete_message = f"{message_without_signature}:{signature}"

    print(f"Secret Key: {secret_key}")
    print(f"Message (no sig): {message_without_signature}")
    print(f"HMAC-SHA256: {signature}")
    print(f"Complete Message: {complete_message}")

if __name__ == "__main__":
    # Show HMAC example first
    validate_hmac_example()

    # Run tests
    test_webhook_commands()
