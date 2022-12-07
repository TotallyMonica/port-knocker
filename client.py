import socket
import time
import sys
import os

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
            print(f'Received: {data}')

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

def main():
    timeout = 30
    knownGood = None
    verbose = True
    address = '45.33.10.75'

    # Address argument
    # if '-a' in sys.argv or '--address' in sys.argv:
    #     index = sys.argv.index('-a')
    #     address = sys.argv[index + 1]
    # else:
    #     print('An address needs to be provided.')
    #     print(f'Example: {sys.argv[0]} -a 192.168.144.120')

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
    
    if os.getuid() == 0:
        portRange = range(1, 65536)
    else:
        portRange = range(1024, 65536)

    results = loop(portRange, address, timeout, verbose, knownGood)
    print(results)

if __name__ == '__main__':
    main()