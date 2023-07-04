import socket
import time
import sys
import os
import json
from datetime import datetime

__VERSION__ = '0.1.2a02'

def encode_data(data):
    to_str = json.dumps(data)
    encoded = to_str.encode("utf-8")
    return encoded

def decode_data(data):
    decoded = data.decode("utf-8")
    to_dict = json.loads(decoded)
    return to_dict

# Testing method that tests connectivity on each port
def test_tcp(address, port, timeout=60, verbose=False):
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

def test_udp(address, port, timeout=60, verbose=False):
    time.sleep(1)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        client.settimeout(timeout)
        data = f'Test to see if UDP traffic is working'

        try:
            if verbose:
                print(f"Trying to connect to server at {address}:{port}...")
            client.sendto(data.encode('utf-8'), (address, port))
            msg, udp_addr = client.recvfrom(2048)
            client.sendto(msg, udp_addr)
        except ConnectionRefusedError:
            client.close()
            return False
        except TimeoutError:
            client.close()
            return False

        client.close()
        return True

# Spin up master thread
def communicate(startPort, endPort, address, master, proto, timeout, verbose, knownGood):
    # Check the port used
    if proto.lower() == 'udp':
        raise ValueError(f"UDP is currently not supported")
    elif proto.lower() != 'tcp':
        raise ValueError(f"Invalid protocol {proto}")

    # Build the parameters for testing as a whole
    server_info = {
        'protocol': proto,
        'timeout': timeout,
        'known_good': knownGood,
        'start_port': startPort,
        'end_port': endPort
    }

    # Build the socket
    master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    master_socket.settimeout(timeout)
    # In a try/except case as the connection has a chance to fail
    # Accept the received data and send it back to the server to confirm validity.
    try:
        if verbose:
            print(f"Trying to connect to the master server at {address}:{master}...")
        master_socket.connect((address, master))
    except ConnectionRefusedError:
        master_socket.close()
        return False
    except TimeoutError:
        master_socket.close()
        return False

    master_socket.send(encode_data(server_info))

    overall_results = []
    continue_testing = True
    while continue_testing:
        test_info = decode_data(master_socket.recv(2048))
        print(test_info)
        if not test_info['continue_testing']:
            continue_testing = False
            break
        test_tcp(address, test_info['tested_port'], timeout, verbose)
        test_result = decode_data(master_socket.recv(2048))
        print(test_result)
        overall_results.append(test_result)

    master_socket.close()

    with open(f"results_{str(datetime.now()).replace(' ', '_')[:-7]}.txt", 'w') as results_file:
        results_file.write(json.dumps(overall_results))

def main():
    PROTO_DEFAULT = 'tcp'
    timeout = 10
    known_good = None
    verbose = True
    start_port = 1
    endPort = 65535
    proto = PROTO_DEFAULT
    predefined_port = False

    if '-h' in sys.argv or '--help' in sys.argv:
        print(f"Port knocker v{__VERSION__}")
        print(f"\nUsage:")
        print(f"---Required---")
        print(f"\t-a, --address: specify the address to connect to.")
        print(f"\t-m, --master-port: specify a master port")
        print(f"---Optional---")
        print(f"\t-p, --protocol: specify the protocol used (Default: TCP)")
        print(f"\t-t, --timeout: specify the timeout period (default: 10 seconds)")
        print(f"\t-g, --known-good: specify known good ports, comma delimited")
        print(f"\t-s, --start-port: specify the port to start from (Default: 1 if privileged, 1024 if unprivileged)")
        sys.exit(0)

    #
    # --Required arguments--
    #
    # Address argument
    if '-a' in sys.argv or '--address' in sys.argv:
        try:
            index = sys.argv.index('-a')
        except ValueError:
            index = sys.argv.index('--address')
        
        address = sys.argv[index + 1]
    else:
        print('An address needs to be provided.')
        print(f'Example: {sys.argv[0]} -a 192.168.144.120')
        sys.exit()

    # Master port argument
    if '-m' in sys.argv or '--master-port' in sys.argv:
        try:
            index = sys.argv.index('-m')
        except ValueError:
            index = sys.argv.index('--master-port')

        master = int(sys.argv[index + 1])
    else:
        print('A master port needs to be provided.')
        print(f'Example: {sys.argv[0]} -m 19315')
        sys.exit()

    #
    # --Required arguments--
    #
    # Timeout argument
    if '-t' in sys.argv or '--timeout' in sys.argv:
        try:
            index = sys.argv.index('-t')
        except ValueError:
            index = sys.argv.index('--timeout')
        if sys.argv[index + 1].isdigit():
            timeout = float(sys.argv[index + 1])
        else:
            print(f'Invalid input, ignoring timeout variable and defaulting to {timeout} seconds')
            print(f'Valid usage: {sys.argv[index]} 30')

    # Known good ports argument
    if '-g' in sys.argv or '--known-good' in sys.argv:
        try:
            index = sys.argv.index('-g')
        except ValueError:
            index = sys.argv.index('--known-good')

        val = sys.argv[index + 1].split(',')

        known_good = []
        # Validate it is a valid port
        for port in val:
            if port.isdigit():
                port = int(port)
            else:
                print(f'Specified port {port} is invalid, ignoring the value.')
                print('Valid usage: -g {Comma separated list of integers between 1 and 65535}')
            
            if 65536 > port > 0:
                known_good.append(port)
            else:
                print(f'Specified port {port} is outside the valid port range (1-65535). Provided port will be ignored.')
                print('Valid usage: {} {Comma separated list of integers between 1 and 65535}', sys.argv[index])

    # Start port
    if '-s' in sys.argv or '--start-port' in sys.argv:
        try:
            index = sys.argv.index('-s')
        except ValueError:
            index = sys.argv.index('--start-port')

        val = sys.argv[index + 1]

        # Validate it is a valid port
        if val.isdigit():
            start_port = int(port)
        else:
            print(f'Specified port {port} is invalid, ignoring the value.')
            print('Valid usage: -s {Start port}')

        if not 65536 > port > 0:
            print(
                f'Specified port {port} is outside the valid port range (1-65535). Provided port will be ignored.')
            print('Valid usage: {} {Comma separated list of integers between 1 and 65535}', sys.argv[index])
        elif os.getuid() !=0 and port < 1024:
            print(f"Requested start port {port} requires root, defaulting to 1024.")
        else:
            predefined_port = True

    if os.getuid() != 0 and not predefined_port:
        start_port = 1024
    
    results = communicate(start_port, endPort + 1, address, master, proto, timeout, verbose, known_good)
    print(results)

if __name__ == '__main__':
    main()