#!/usr/bin/env python3

import socket
from time import time
import sys

# Testing method
def test(port, interface='0.0.0.0', timeout=60, verbose=False):
    # Create the test string to be used to confirm connectivity
    data = f'The cat is out of the bag'

    # Socket connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.timeout(timeout)

        # Bind and then listen, informing the user
        srv.bind((interface, port))
        srv.listen()

        if verbose:
            print(f"Waiting for a connection on {interface}:{port}...")
        
        # Wait for a connection, returning false if it times out
        try:
            conn, addr = srv.accept()
        except TimeoutError:
            return False

        if verbose:
            print(f"Connection from {addr}")

        # If there's a connection, confirm connectivity by sending the received data back.
        if conn:
            conn.send(data.encode('utf-8'))
            test = data.recv(2048).decode('utf-8')
            if test == data:
                return True
        
        return False
    
# Loop tests all the ports, handles the logging
def loop(ports, interface='0.0.0.0', timeout=10, verbose=False, knownGood=None):
    results = []
    checkedPorts = []

    for port in ports:
        if port not in knownGood:
            checkedPorts.append(port)

    for port in checkedPorts:
        result = test(port, interface, timeout)

        # Warn if the port failed and the  
        if not result and verbose:
            print(f'Warning: Port {port} failed!')
        results.append([port, result])
    
    return results

# Configure the 
def main():
    interface = '0.0.0.0'
    timeout = 10
    knownGood = None

    if '-i' in sys.argv or '--interface' in sys.argv:
        index = sys.argv.index('-i')
        interface = sys.argv[index + 1]

    if '-t' in sys.argv or '--timeout' in sys.argv:
        index = sys.argv.index('-t')
        if sys.argv[index + 1].isdigit():
            timeout = int(sys.argv[index + 1])
        else:
            print('Invalid input, ignoring timeout variable')

    if '-g' in sys.argv or '--known-good' in sys.argv:
        index = sys.argv.index('-g')
        val = sys.argv[index + 1]
        if val.isdigit():
            val = int(val)
        else:
            print('Invalid port provided, ignoring provided port')
            print('Valid usage: -g {Comma separated list of integers between 1 and 65535}')
        
        if val < 65536 and val > 0:
            knownGood = val
        else:
            print('Port is outside the valid port range (1-65535). Provided port will be ignored.')
            print('Valid usage: -g {Comma separated list of integers between 1 and 65535}')
    
    results = loop(range(1, 65536), interface, timeout, knownGood)

if __name__ == '__main__':
    main()