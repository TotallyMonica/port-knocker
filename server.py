#!/usr/bin/env python3

import socket
import threading
from time import time
import sys
import os
import csv

__VERSION__ = '0.1.1'

def test_udp(port, interface='0.0.0.0', timeout=60, verbose=False):
    data = f'Test to see if UDP traffic is working'

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as srv:
        # srv.settimeout(timeout)

        try:
            srv.bind((interface, port))
        except OSError:
            return "In use"

        if verbose:
            print(f"Waiting for a connection on {interface}:{port}...")
        
        try:
            # If there's a connection, confirm connectivity by sending the received data back.   
            # This part is the part that emulates TCP  
            msg, addr = srv.recvfrom(2048)
            if verbose:
                print(f"Connection from {addr}")
            srv.sendto(msg, addr)
            test, addr = srv.recvfrom(2048)

            # Ensure it matches the expected data
            if test.decode('utf-8') == data:
                return True
        except TimeoutError:
            return False
   
        return "Malformed"

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
    
# Loop tests all the ports, handles the logging
def loop(ports, interface='0.0.0.0', proto='tcp', timeout=10, verbose=False, knownGood=None):
    results = []
    checkedPorts = []

    if knownGood:
        for port in ports:
            if port not in knownGood:
                checkedPorts.append(port)
    
    else:
        checkedPorts = ports

    if proto == 'tcp':
        for port in checkedPorts:
            result = test_tcp(port, interface, timeout, verbose)

            # Warn if the port failed and the  
            if not result and verbose:
                print(f'Warning: Port {port} failed!')
            
            if result == True:
                results.append([port, "Pass"])
            elif result == False:
                results.append([port, "Fail"])
            else:
                results.append([port, result])
    
    elif proto == 'udp':
        for port in checkedPorts:
            result = test_udp(port, interface, timeout, verbose)

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
def newThread(output, threadNum, startPort, endPort, address, proto, timeout, verbose, knownGood):
    output[threadNum] = loop(range(startPort, endPort), address, proto, timeout, verbose, knownGood)

# Begin threading, restricted to 8 threads as of right now
# TODO: Clean this spaghetti code up
def beginThreading(startPort, endPort, address, proto, timeout, verbose, knownGood):
    output = []
    offset = int( (endPort - startPort) / 8 )
    nextStartingPort = startPort

    output.append( loop(range(startPort, endPort), address, proto, timeout, verbose, knownGood) )

    # Calculate the port ranges
    # portRanges = []
    # for i in range(8):
    #     portRanges.append([
    #             nextStartingPort,
    #             nextStartingPort + offset
    #         ])
    #     nextStartingPort += offset
    
    # print(portRanges)

    # thread1 = threading.Thread(target=newThread, args=(output, 0, portRanges[0][0], portRanges[0][1], address, proto, timeout, verbose, knownGood))
    # thread2 = threading.Thread(target=newThread, args=(output, 1, portRanges[1][0], portRanges[1][1], address, proto, timeout, verbose, knownGood))
    # thread3 = threading.Thread(target=newThread, args=(output, 2, portRanges[2][0], portRanges[2][1], address, proto, timeout, verbose, knownGood))
    # thread4 = threading.Thread(target=newThread, args=(output, 3, portRanges[3][0], portRanges[3][1], address, proto, timeout, verbose, knownGood))
    # thread5 = threading.Thread(target=newThread, args=(output, 4, portRanges[4][0], portRanges[4][1], address, proto, timeout, verbose, knownGood))
    # thread6 = threading.Thread(target=newThread, args=(output, 5, portRanges[5][0], portRanges[5][1], address, proto, timeout, verbose, knownGood))
    # thread7 = threading.Thread(target=newThread, args=(output, 6, portRanges[6][0], portRanges[6][1], address, proto, timeout, verbose, knownGood))
    # thread8 = threading.Thread(target=newThread, args=(output, 7, portRanges[7][0], portRanges[7][1], address, proto, timeout, verbose, knownGood))
    
    # thread1.start()
    # thread2.start()
    # thread3.start()
    # thread4.start()
    # thread5.start()
    # thread6.start()
    # thread7.start()
    # thread8.start()

    # thread1.join()
    # thread2.join()
    # thread3.join()
    # thread4.join()
    # thread5.join()
    # thread6.join()
    # thread7.join()
    # thread8.join()

    return output

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