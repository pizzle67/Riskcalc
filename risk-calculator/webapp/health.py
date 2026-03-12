"""Health check script for Docker / Nomad / Consul service health monitoring."""

import sys
import urllib.request
import urllib.error


def health_check(host="localhost", port=5000):
    try:
        url = f"http://{host}:{port}/health"
        with urllib.request.urlopen(url, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


if __name__ == "__main__":
    if health_check():
        print("health check successful!")
        sys.exit(0)
    else:
        print("health check failed!")
        sys.exit(1)
