"""
Inspects network interfaces and local IP addresses.
"""
import socket
import subprocess

def get_ips():
    print("Hostname:", socket.gethostname())
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        primary_ip = s.getsockname()[0]
        s.close()
        print("Primary outbound IP:", primary_ip)
    except Exception as e:
        print("Could not determine outbound IP:", e)
        
    try:
        res = subprocess.run(["hostname", "-I"], capture_output=True, text=True)
        print("All interface IPs (`hostname -I`):", res.stdout.strip())
    except Exception:
        pass

if __name__ == '__main__':
    get_ips()
