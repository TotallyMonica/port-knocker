import socket
from time import time
import sys

# Testing method that tests connectivity on each port
def test(address, port, timeout=60, verbose=False):
    # Set timeout
    socket.timeout(timeout)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        # In a try/except case as the connection has a chance to fail
        # Accept the received data and send it back to the server to confirm validity.
        try:
            client.connect((address, port))
        except ConnectionRefusedError:
            return False
    
        # In a try/except case as the connection has a chance to fail
        # Accept the received data and send it back to the server to confirm validity.
        data = client.recv(2048).decode('utf-8')
        client.send(data.encode('utf-8'))
        
        if verbose:
            print(f'Received: {data.decode("utf-8")}')
        return True

# Looping method to test every port
# Todo: Don't test known good ports
def loop(ports, address, timeout=10, verbose=False, knownGood=None):
    results = []

    for port in ports:
        result = test(port, address, timeout, verbose)

        # Warn if the port failed and verbosity is true
        if not result and verbose:
            print(f'Warning: Port {port} failed!')
        
        results.append([port, result])
    
    return results

def main():
    timeout = 10
    knownGood = None

    if '-a' in sys.argv or '--address' in sys.argv:
        index = sys.argv.index('-i')
        address = sys.argv[index + 1]
    else:
        print('An address needs to be provided.')
        print(f'Example: {sys.argv[0]} -a 192.168.144.120')

    if '-t' in sys.argv or '--timeout' in sys.argv:
        index = sys.argv.index('-t')
        if sys.argv[index + 1].isdigit():
            timeout = float(sys.argv[index + 1])
        else:
            print(f'Invalid input, ignoring timeout variable and defaulting to {timeout} seconds')
            print(f'Valid usage: ')

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
    
    results = loop(range(1, 65536), address, timeout, knownGood)

if __name__ == '__main__':
    main()