# # # restServer_v1.py

import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from getTemperatureSensors import get_cached_temperatures, get_last_update, read_all_temperatures
from getPressureSensor import read_pressure

class SensorAPIHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        """Set standard headers for all responses, including CORS headers."""
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")  # Allow requests from any origin
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")  # Allow specific HTTP methods
        self.send_header("Access-Control-Allow-Headers", "Content-Type")  # Allow specific headers

    def do_OPTIONS(self):
        """Handle preflight CORS requests."""
        self.send_response(200)
        self._set_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/sensors/cached":
            self.send_response(200)
            self._set_headers()
            self.end_headers()

            temperature_data = get_cached_temperatures()
            if not temperature_data:
                print("Cache is empty in REST server; falling back to live read.")
                temperature_data = read_all_temperatures()
                last_update_time = time.time()
            else:
                last_update_time = get_last_update()  # Fetch safely using the getter function

            response_data = {
                "last_update": last_update_time,
                "pressure": read_pressure(),                
                "temperature": temperature_data,
            }
            self.wfile.write(json.dumps(response_data).encode("utf-8"))

        elif self.path == "/api/sensors/live":
            self.send_response(200)
            self._set_headers()
            self.end_headers()

            temperature_data = read_all_temperatures()
            pressure_data = read_pressure()
            response_data = {
                "last_update": time.time(),
                "pressure": pressure_data,
                "temperature": temperature_data,
            }
            self.wfile.write(json.dumps(response_data).encode("utf-8"))

# Start the REST server
def run_server():
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, SensorAPIHandler)
    print("Server started at http://localhost:8080")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
