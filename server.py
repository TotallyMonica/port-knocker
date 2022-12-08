#!/usr/bin/env python3

import socket
import threading
from time import time
import sys
import os
import csv

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
        
        if result == True:
            results.append([port, "Pass"])
        elif result == False:
            results.append([port, "Fail"])
        else:
            results.append([port, result])
        
    
    return results

# The stupid way I have to get the return value because I can't just do it natively
def newThread(output, threadNum, startPort, endPort, address, timeout, verbose, knownGood):
    output[threadNum] = loop(range(startPort, endPort), address, timeout, verbose, knownGood)

# Begin threading, restricted to 8 threads as of right now
# TODO: Clean this spaghetti code up
def beginThreading(startPort, endPort, address, timeout, verbose, knownGood):
    output = [None, None, None, None, None, None, None, None]
    offset = int( (endPort - startPort) / 8 )
    nextStartingPort = startPort

    # Calculate the port ranges
    portRanges = []
    for i in range(8):
        portRanges.append([
                nextStartingPort,
                nextStartingPort + offset
            ])
        nextStartingPort += offset
    
    print(portRanges)

    thread1 = threading.Thread(target=newThread, args=(output, 0, portRanges[0][0], portRanges[0][1], address, timeout, verbose, knownGood))
    thread2 = threading.Thread(target=newThread, args=(output, 1, portRanges[1][0], portRanges[1][1], address, timeout, verbose, knownGood))
    thread3 = threading.Thread(target=newThread, args=(output, 2, portRanges[2][0], portRanges[2][1], address, timeout, verbose, knownGood))
    thread4 = threading.Thread(target=newThread, args=(output, 3, portRanges[3][0], portRanges[3][1], address, timeout, verbose, knownGood))
    thread5 = threading.Thread(target=newThread, args=(output, 4, portRanges[4][0], portRanges[4][1], address, timeout, verbose, knownGood))
    thread6 = threading.Thread(target=newThread, args=(output, 5, portRanges[5][0], portRanges[5][1], address, timeout, verbose, knownGood))
    thread7 = threading.Thread(target=newThread, args=(output, 6, portRanges[6][0], portRanges[6][1], address, timeout, verbose, knownGood))
    thread8 = threading.Thread(target=newThread, args=(output, 7, portRanges[7][0], portRanges[7][1], address, timeout, verbose, knownGood))
    
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
    thread6.start()
    thread7.start()
    thread8.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()
    thread6.join()
    thread7.join()
    thread8.join()

    return output

# Configure the server to check ports
def main():
    interface = '0.0.0.0'
    timeout = 10
    knownGood = None
    verbose = True
    startPort = 1
    endPort = 65535

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

    if os.getuid() != 0:
        startPort = 1024
    
    results = beginThreading(startPort, endPort + 1, interface, timeout, verbose, knownGood)
    print(results)

    with open('results.csv', 'w') as filp:
        writer = csv.writer(filp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['port', 'result'])
        for row in results:
            writer.writerow(row)

    print(results)

if __name__ == '__main__':
    main()