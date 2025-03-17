import subprocess
import socket
import struct


def get_ip(prefix):
    """
    Gets an ip with a given prefix
    (Use this to get Vagrant IP)
    :param prefix:
    :return: IP of given prefix
    """
    command = "ifconfig | awk '/inet / {print $2}'"
    output = subprocess.check_output(command, shell=True, text=True)
    ip_addresses = output.strip().split("\n")
    return next((s for s in ip_addresses if s.startswith(prefix)), None)


def ip_to_long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]


def get_ip_distance(ip1, ip2):
    """
    Compare IP addresses
    :param ip1:
    :param ip2:
    :return: Positive number (ip2 is higher than ip1), Negative number (ip2 is lower than ip1), Zero (ips are the same)
    """
    return ip_to_long(ip2) - ip_to_long(ip1)
