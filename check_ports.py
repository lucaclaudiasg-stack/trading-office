"""
Checks candidate ports availability on localhost.
"""
import socket

candidate_ports = [8765, 8088, 8888, 5173, 8080]
for p in candidate_ports:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect(('127.0.0.1', p))
        print(f"Port {p}: IN USE")
        s.close()
    except Exception:
        print(f"Port {p}: FREE")
