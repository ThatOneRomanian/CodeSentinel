"""
Sample Python application with intentional security issues for CodeSentinel testing.

Copyright (c) 2025 Andrei Antonescu
SPDX-License-Identifier: MIT
"""

# Hardcoded API keys and tokens (for testing)
api_key = "sk_test_1234567890abcdefghijklmnop"
secret_key = "my_super_secret_key_12345"
stripe_key = "sk_live_1234567890abcdefghijklmnop"
github_token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"

# Database connection strings with credentials
database_url = "postgresql://user:password123@localhost:5432/mydb"
mysql_conn = "mysql://admin:adminpass@localhost:3306/appdb"
redis_url = "redis://user:redispass@localhost:6379/0"

# Configuration with sensitive data
config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "username": "app_user",
        "password": "my_database_password_123",
        "database": "production_db"
    },
    "api": {
        "stripe_secret": "sk_test_9876543210zyxwvutsrqponm",
        "aws_access_key": "AKIAIOSFODNN7EXAMPLE",
        "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }
}

# Function with hardcoded credentials
def connect_to_database():
    """Connect to database with hardcoded credentials."""
    username = "db_user"
    password = "secure_password_456"
    host = "prod-db.internal"
    port = 5432
    
    # This is just for testing - never do this in real code!
    connection_string = f"postgresql://{username}:{password}@{host}:{port}/app"
    return connection_string

# OAuth tokens and authentication data
oauth_tokens = {
    "google": "ya29.a0AfH6SMBxExampleGoogleOAuthToken",
    "facebook": "EAACEdEose0cBAExampleFacebookAccessToken",
    "slack": "xoxb-1234567890-1234567890-1234567890-abcdefghijkl"
}

# This is a safe function without any security issues
def safe_function():
    """This function doesn't contain any security issues."""
    safe_variable = "This is safe"
    return safe_variable

if __name__ == "__main__":
    print("This is a test application for CodeSentinel scanning")