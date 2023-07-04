#!/usr/bin/env python3

import socket
import threading
from time import time
import sys
import os
import csv
import json
import ast

__VERSION__ = '0.1.2a01'

# Testing method
def test_tcp(port, interface='0.0.0.0', timeout=60, verbose=False):
    # Create the test string to be used to confirm connectivity
    data = f'The cat is out of the bag'

    # Socket connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.settimeout(timeout)

        # Bind and then listen, informing the user
        try:
            srv.bind((interface, port))
        except OSError:
            return "In use"

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
        
        return "Malformed"

# Spin up master thread
def communicate(master, verbose, interface='0.0.0.0'):
    master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Ensure port isn't taken
    try:
        master_socket.bind((interface, master))
    except OSError:
        raise OSError("Port in use. Please use a different master port.")

    master_socket.listen()
    if verbose:
        print(f"Master connection listening on {interface}:{master}...")

    master_conn, master_addr = master_socket.accept()
    if verbose:
        print(f"Connection from {master_addr}")

    # Receive the test information from the client
    received = master_conn.recv(2048)
    server_info = json.loads(received.decode('utf-8'))

    # Begin test loop
    tested_port = server_info['start_port']
    if os.getuid() != 0 and tested_port < 1024:
        raise OSError("Server is not running as root but client requested root only ports")

    while tested_port <= server_info['end_port']:
        # Build the test parameters and inform the client.
        test_info = {
            'protocol': server_info['protocol'],
            'timeout': server_info['timeout'],
            'tested_port': tested_port,
            'continue_testing': True
        }
        master_socket.send(json.dumps(test_info).encode('utf-8'))
        result = test_tcp(tested_port, interface, server_info['timeout'], verbose)

        # Take the test results and send them to the client.
        test_results = {
            'protocol': server_info['protocol'],
            'port': tested_port,
            'results': result
        }
        master_socket.send(json.dumps(test_results).encode('utf-8'))

        # We're done testing, increment the port
        tested_port += 1

    # Wrap up testing
    test_info = {
        'continue_testing': False
    }
    master_socket.send(json.dumps(test_info).encode('utf-8'))
    master_socket.close()

# Configure the server to check ports
def main():
    PROTO_DEFAULT = 'tcp'
    interface = '0.0.0.0'
    timeout = 10
    knownGood = None
    verbose = True
    startPort = 1
    endPort = 65535
    proto = PROTO_DEFAULT

    if '-h' in sys.argv or '--help' in sys.argv:
        print(f"Port knocker v{__VERSION__}")
        print(f"\nUsage:")
        print(f"\t-p, --protocol: specify the protocol used (Default: TCP)")
        print(f"\t-i, --interface: specify the interface to use (Default: 0.0.0.0)")
        print(f"\t-t, --timeout: specify the timeout period (default: 10 seconds)")
        print(f"\t-g, --known-good: specify known good ports, comma delimited")
        sys.exit(0)

    if '-p' in sys.argv or '--protocol' in sys.argv:
        try:
            index = sys.argv.index('-p')
        except ValueError:
            index = sys.argv.index('--protocol')
        
        try:
            proto = sys.argv[index + 1]
        except IndexError:
            print(F"No protocol provided, defaulting to {PROTO_DEFAULT}")
        
        if proto.lower() == 'tcp' or proto.lower() == 'udp':
            pass
        else:
            print(f"Invalid or unsupported protocol {proto}, defaulting to TCP")

    if '-i' in sys.argv or '--interface' in sys.argv:
        try:
            index = sys.argv.index('-i')
        except ValueError:
            index = sys.argv.index('--interface')
        interface = sys.argv[index + 1]

    if '-t' in sys.argv or '--timeout' in sys.argv:
        try:
            index = sys.argv.index('-t')
        except ValueError:
            index = sys.argv.index('--timeout')

        if sys.argv[index + 1].isdigit():
            timeout = int(sys.argv[index + 1])
        else:
            print('Invalid input, ignoring timeout variable')

    if '-g' in sys.argv or '--known-good' in sys.argv:
        knownGood = []
        try:
            index = sys.argv.index('-g')
        except ValueError:
            index = sys.argv.index('--known-good')
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

    if os.getuid() != 0:
        startPort = 1024
    
    results = beginThreading(startPort, endPort + 1, interface, proto, timeout, verbose, knownGood)
    print(results)

    with open(f'results-{proto}.csv', 'w') as filp:
        writer = csv.writer(filp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['port', 'result'])
        for row in results:
            writer.writerow(row)

    print(results)

if __name__ == '__main__':
    main()