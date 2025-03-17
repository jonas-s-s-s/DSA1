import sys
import socket

def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <UDP_IP> <UDP_PORT> <MESSAGE>")
        sys.exit(1)

    UDP_IP = sys.argv[1]
    try:
        UDP_PORT = int(sys.argv[2])
    except ValueError:
        print("Error: UDP_PORT must be an integer.")
        sys.exit(1)

    MESSAGE = sys.argv[3]

    print("UDP target IP:", UDP_IP)
    print("UDP target port:", UDP_PORT)
    print("Message:", MESSAGE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.sendto(MESSAGE.encode('utf-8'), (UDP_IP, UDP_PORT))
    print("Message sent successfully.")

if __name__ == "__main__":
    main()
