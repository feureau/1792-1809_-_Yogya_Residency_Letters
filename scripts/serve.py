"""Local development web server for Yogyakarta Residency Letters 1792-1809.
Auto-detects an available port, launches the default browser, and serves the repository root.
"""
import os
import sys
import socket
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial

def find_free_port(start_port=8000, max_attempts=50):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start_port

def main():
    # Set directory to repository root (parent of scripts/)
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(repo_root)

    requested_port = 8000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        requested_port = int(sys.argv[1])

    port = find_free_port(requested_port)
    url = f"http://localhost:{port}/"

    handler = partial(SimpleHTTPRequestHandler, directory=repo_root)

    try:
        with ThreadingHTTPServer(('127.0.0.1', port), handler) as httpd:
            print("=" * 72)
            print("  Yogyakarta Residency Letters 1792–1809 (Peter Carey Archive)")
            print("  Local Web Server Running")
            print("=" * 72)
            print(f"\n  Portal / Home:            {url}")
            print(f"  Interactive Viewer:       {url}transcriptions.html")
            print(f"  Full Corpus Reader:       {url}full.html")
            print(f"  Historical Dictionary:    {url}dictionary.html")
            print("\n" + "-" * 72)
            print("  Serving files from: " + repo_root)
            print("  Press Ctrl+C in this console window anytime to stop the server.")
            print("=" * 72 + "\n")

            # Open default browser after a brief delay so server is actively listening
            def open_browser():
                time.sleep(0.6)
                webbrowser.open(url)

            # Only auto-open browser if --no-browser flag is not passed
            if "--no-browser" not in sys.argv:
                threading.Thread(target=open_browser, daemon=True).start()

            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped. Goodbye!")
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
