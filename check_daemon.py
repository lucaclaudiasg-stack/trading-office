"""
Checks if dashboard backend is listening on port 8765.
"""
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1.0)
try:
    s.connect(('127.0.0.1', 8765))
    print("PORT 8765 IS OPEN AND ACTIVE")
    s.close()
except Exception as e:
    print("PORT 8765 IS NOT RESPONDING:", e)
