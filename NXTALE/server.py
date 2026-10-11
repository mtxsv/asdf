#!/usr/bin/env python3
"""
Servidor web local para el juego HTML5 (NXTALE).
Colócalo en la misma carpeta que index.html y ejecútalo:

    python server.py            -> http://localhost:8080
    python server.py 3000       -> http://localhost:3000
    python server.py 8080 --lan -> accesible desde otros dispositivos de la red
"""
import http.server
import os
import socket
import socketserver
import sys
import threading
import webbrowser

# Carpeta que se sirve: la del propio script
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

PORT = 8080
LAN = False
for arg in sys.argv[1:]:
    if arg == "--lan":
        LAN = True
    elif arg.isdigit():
        PORT = int(arg)

HOST = "0.0.0.0" if LAN else "127.0.0.1"


class Handler(http.server.SimpleHTTPRequestHandler):
    # Tipos MIME correctos (en Windows a veces .js/.wasm salen mal)
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "application/javascript",
        ".mjs": "application/javascript",
        ".wasm": "application/wasm",
        ".json": "application/json",
        ".ogg": "audio/ogg",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ico": "image/x-icon",
        ".ini": "text/plain",
        "": "application/octet-stream",
    }

    def end_headers(self):
        # Sin caché, para ver siempre la última versión mientras desarrollas
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {fmt % args}")


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def main():
    try:
        httpd = Server((HOST, PORT), Handler)
    except OSError as e:
        print(f"No se pudo abrir el puerto {PORT}: {e}")
        print("Prueba con otro puerto, por ejemplo: python server.py 8081")
        sys.exit(1)

    print("=" * 50)
    print(f" Sirviendo: {ROOT}")
    print(f" Local:     http://localhost:{PORT}")
    if LAN:
        print(f" Red local: http://{local_ip()}:{PORT}")
    print(" Pulsa Ctrl+C para detener")
    print("=" * 50)

    threading.Timer(0.8, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()