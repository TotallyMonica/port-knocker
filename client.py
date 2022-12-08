import socket
import time
import sys
import os
import threading

# Testing method that tests connectivity on each port
def test(address, port, timeout=60, verbose=False):
    time.sleep(1)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.settimeout(timeout)
        # In a try/except case as the connection has a chance to fail
        # Accept the received data and send it back to the server to confirm validity.
        try:
            if verbose:
                print(f"Trying to connect to {address}:{port}...")
            client.connect((address, port))
        except ConnectionRefusedError:
            client.close()
            return False
        except TimeoutError:
            client.close()
            return False
    
        # In a try/except case as the connection has a chance to fail
        # Accept the received data and send it back to the server to confirm validity.
        try:
            data = client.recv(2048).decode('utf-8')
            client.send(data.encode('utf-8'))
        except TimeoutError:
            client.close()
            return False
        
        if verbose:
            print(f'Connected to ({address}:{port})')

        client.close()
        return True

# Looping method to test every port
# Todo: Don't test known good ports
def loop(ports, address, timeout=10, verbose=False, knownGood=None):
    results = []
    checkedPorts = []

    if knownGood:
        for port in ports:
            if port not in knownGood:
                checkedPorts.append(port)
    
    else:
        checkedPorts = ports

    for port in checkedPorts:
        result = test(address, port, timeout, verbose)

        # Warn if the port failed and verbosity is true
        if not result and verbose:
            print(f'Warning: Port {port} failed!')
        
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

def main():
    timeout = 30
    knownGood = None
    verbose = True
    startPort = 1
    endPort = 65535

    # Address argument
    if '-a' in sys.argv or '--address' in sys.argv:
        index = sys.argv.index('-a')
        address = sys.argv[index + 1]
    else:
        print('An address needs to be provided.')
        print(f'Example: {sys.argv[0]} -a 192.168.144.120')
        sys.exit()

    # Timeout argument
    if '-t' in sys.argv or '--timeout' in sys.argv:
        index = sys.argv.index('-t')
        if sys.argv[index + 1].isdigit():
            timeout = float(sys.argv[index + 1])
        else:
            print(f'Invalid input, ignoring timeout variable and defaulting to {timeout} seconds')
            print(f'Valid usage: ')

    # Known good ports argument
    if '-g' in sys.argv or '--known-good' in sys.argv:
        index = sys.argv.index('-g')
        val = sys.argv[index + 1].split(',')

        # Validate it is a valid port
        for port in val:
            if val.isdigit():
                val = int(val)
            else:
                print(f'Specified port {port} is invalid, ignoring the value.')
                print('Valid usage: -g {Comma separated list of integers between 1 and 65535}')
            
            if val < 65536 and val > 0:
                knownGood = val
            else:
                print(f'Specified port {port} is outside the valid port range (1-65535). Provided port will be ignored.')
                print('Valid usage: -g {Comma separated list of integers between 1 and 65535}')
    
    if os.getuid() != 0:
        startPort = 1024
    
    results = beginThreading(startPort, endPort + 1, address, timeout, verbose, knownGood)
    print(results)

if __name__ == '__main__':
    main()