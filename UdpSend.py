import socket
import struct

IP_ADDRESS_REDQUEEN = "192.168.1.101"
IP_ADDRESS_MAC_HOME = "192.168.1.113"
IP_ADDRESS_MAC_AEROTIM = "192.168.1.76"

IP_ADDRESS = IP_ADDRESS_MAC_AEROTIM
PORT = 5202

udpSocket: socket.socket = None

def connect():
    global udpSocket
    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def disconnect():
    global udpSocket
    udpSocket.close()

def send_angles(angles):
    global udpSocket
    data = struct.pack('%sf' % len(angles), *angles)
    udpSocket.sendto(data, (IP_ADDRESS, PORT))
