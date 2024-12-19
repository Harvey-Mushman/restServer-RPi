#!/usr/bin/python3
import glob
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

# Function to read DS18B20 probe
def Read_DS18B20(SensorID):
    try:
        with open(f"/sys/bus/w1/devices/{SensorID}/w1_slave") as fichier:
            texte = fichier.read()
        ligne1 = texte.split("\n")[0]
        crc = ligne1.split("crc=")[1]
        if crc.find("YES") < 0:
            return None
    except:
        return None
    ligne2 = texte.split("\n")[1]
    texte_temp = ligne2.split(" ")[9]
    return float(texte_temp[2:]) / 1000.0

# Function to convert Celsius to Fahrenheit
def Celsius_to_Fahrenheit(celsius):
    return (celsius * 9/5) + 32

# Detect sensors
sensors = []
for sensor in glob.glob("/sys/bus/w1/devices/28-*"):
    sensors.append(sensor.split('/')[5])

# Function to generate HTML content with a gauge
def generate_html():
    if not sensors:
        return "<html><body><h1>No DS18B20 sensors detected</h1></body></html>"

    # Map sensor IDs to their locations
    sensor_locations = {
        "28-00000094e360": "solarRoofReturn",
        "28-0000006c9953": "primarySupply",
        "28-0000006b72c8": "solarArrayReturn",
        "28-0000006b00cf": "primaryReturn",
        "28-00000094ea53": "DHW_Storage",
    }

    sensor_html = ""
    sensor_data_js = ""

    for sensor_id in sensors:
        temp_c = Read_DS18B20(sensor_id)
        location = sensor_locations.get(sensor_id, "Unknown Location")  # Default to 'Unknown Location' if not mapped
        if temp_c is None:
            temp_display = "Error"
            temp_f = 0  # Default to 0 for the gauge in case of an error
        else:
            temp_f = Celsius_to_Fahrenheit(temp_c)
            temp_display = f"{temp_f:.1f}"

        # HTML for each sensor
        sensor_html += f"""
        <div>
            <h2>{location} ({sensor_id})</h2>
            <canvas id="gauge_{sensor_id}" width="300" height="300"></canvas>
            <p>Temperature: {temp_display}&deg;F</p>
        </div>
        """

        # JavaScript data for each sensor
        sensor_data_js += f"""
        {{
            id: 'gauge_{sensor_id}',
            tempF: {temp_f:.1f}
        }},
        """

    # Full HTML with a single JavaScript block for all gauges
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Temperature Monitor</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                text-align: center;
                margin: 20px;
            }}
            canvas {{
                display: block;
                margin: 20px auto;
            }}
            div {{
                margin-bottom: 40px;
            }}
        </style>
    </head>
    <body>
        <h1>Temperature Monitor</h1>
        {sensor_html}
        <script>
            const sensors = [{sensor_data_js}];

            sensors.forEach(sensor => {{
                const ctx = document.getElementById(sensor.id).getContext('2d');
                const tempF = sensor.tempF;
                const maxTemp = 212;

                new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        datasets: [{{
                            data: [tempF, maxTemp - tempF],
                            backgroundColor: ['#FF6384', '#DDDDDD'],
                            borderWidth: 0,
                        }}],
                        labels: ['Temperature (�F)', 'Remaining'],
                    }},
                    options: {{
                        rotation: -90,
                        circumference: 180,
                        plugins: {{
                            tooltip: {{
                                callbacks: {{
                                    label: function(tooltipItem) {{
                                        return tooltipItem.label + ': ' + tooltipItem.raw + '�F';
                                    }}
                                }}
                            }}
                        }}
                    }},
                    cutout: '70%',
                    responsive: false,
                }});
            }});
        </script>
    </body>
    </html>
    """
    return html

# HTTP server handler
class TemperatureHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html_content = generate_html()
        self.wfile.write(html_content.encode("utf-8"))

# Start the HTTP server
def run_server():
    server_address = ("", 8080)  # Listen on port 8080
    httpd = HTTPServer(server_address, TemperatureHandler)
    print("Server started at http://localhost:8080")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
