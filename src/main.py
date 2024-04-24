#!python3

# Imports
import socket
import sys
import ftplib
from flask import Flask, render_template, request
import camera_dma

# Flask app setup
app = Flask(__name__, static_folder='static', template_folder='templates')

# Function to retrieve hostname and IP address
def get_device_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    tcpip_address = server_address
    ftp_address = "127.0.0.1"
    return {
        "hostname": hostname,
        "ip_address": ip_address,
        "tcpip_address": tcpip_address,
        "ftp_address": ftp_address
    }


# TCP/IP communication
tcp_ip_communication = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 10000)
try:
    tcp_ip_communication.connect(server_address)
except:
    print("TCP/IP connection refused from: " + server_address[0][0])


# Http request handling
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'savesettings' in request.form:
            settings_data = request.form["settings"]

    camera_dma.main()

    # Get device information
    device_information = get_device_info()
    return render_template('index.html', device_information=device_information)


# Main call
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)
