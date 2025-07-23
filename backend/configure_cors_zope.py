#!/usr/bin/env python
"""Configure CORS for Volto using environment variables"""

import os

# Set CORS environment variables before starting Plone
cors_env = {
    'CORS_ALLOW_ORIGIN': 'http://localhost:3000',
    'CORS_ALLOW_METHODS': 'DELETE,GET,OPTIONS,PATCH,POST,PUT',
    'CORS_ALLOW_CREDENTIALS': 'true',
    'CORS_ALLOW_HEADERS': 'Accept,Authorization,Content-Type,X-CSRF-TOKEN',
    'CORS_EXPOSE_HEADERS': 'Content-Length,X-My-Header',
    'CORS_MAX_AGE': '3600'
}

print("Setting CORS environment variables:")
for key, value in cors_env.items():
    os.environ[key] = value
    print(f"✓ {key} = {value}")

print("\nCORS environment variables set!")
print("Now start Plone with: runwsgi etc/zope.ini")
print("\nOr run directly:")
print("CORS_ALLOW_ORIGIN='http://localhost:3000' CORS_ALLOW_CREDENTIALS='true' runwsgi etc/zope.ini")