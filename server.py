#!/usr/bin/env python3

import socket
from time import time
import sys
import os

# Testing method
def test(port, interface='0.0.0.0', timeout=60, verbose=False):
    # Create the test string to be used to confirm connectivity
    data = f'The cat is out of the bag'

    # Socket connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.settimeout(timeout)

        # Bind and then listen, informing the user
        try:
            srv.bind((interface, port))
        except OSError:
            return False

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
        conn.send(data.encode('utf-8'))
        test = conn.recv(2048).decode('utf-8')
        if test == data:
            return True
        
        return False
    
# Loop tests all the ports, handles the logging
def loop(ports, interface='0.0.0.0', timeout=10, verbose=False, knownGood=None):
    results = []
    checkedPorts = []

    if knownGood:
        for port in ports:
            if port not in knownGood:
                checkedPorts.append(port)
    
    else:
        checkedPorts = ports

    for port in checkedPorts:
        result = test(port, interface, timeout, verbose)

        # Warn if the port failed and the  
        if not result and verbose:
            print(f'Warning: Port {port} failed!')
        results.append([port, result])
    
    return results

# Configure the server to check ports
def main():
    interface = '0.0.0.0'
    timeout = 10
    knownGood = None
    verbose = True

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
        knownGood = []
        index = sys.argv.index('-g')
        val = sys.argv[index + 1].split(',')

        # Validate it is a valid port
        for port in val:
            if port.isdigit():
                port = int(port)
            else:
                print(f'Specified port {port} is invalid, ignoring the value.')
                print('Valid usage: -g {Comma separated list of integers between 1 and 65535}')
                val.remove(port)

                break
            
            if port < 65536 and port > 0:
                knownGood.append(port)
            else:
                print(f'Specified port {port} is outside the valid port range (1-65535). Provided port will be ignored.')
                print('Valid usage: -g {Comma separated list of integers between 1 and 65535}')
                val.remove(port)

    if os.getuid() == 0:
        portRange = range(1, 65536)
    else:
        portRange = range(1024, 65536)

    results = loop(portRange, interface, timeout, verbose, knownGood)
    print(results)

if __name__ == '__main__':
    main()