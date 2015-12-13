
import hashlib
import time
import struct
import socket
import random

magic = 0xbd6b0cbf
#magic = 0xbf0cb6bd

#0xbf;
#0x0c;
#0x6b;
#0xbd;



# Returns byte string value, not hex string
def varint(n):
    if n < 0xfd:
        return struct.pack('<B', n)
    elif n < 0xffff:
        return struct.pack('<cH', '\xfd', n)
    elif n < 0xffffffff:
        return struct.pack('<cL', '\xfe', n)
    else:
        return struct.pack('<cQ', '\xff', n)


# Takes and returns byte string value, not hex string
def varstr(s):
    return varint(len(s)) + s


def netaddr(ipaddr, port):
    services = 1
    return (
        struct.pack(
            '<Q12s',
            services,
            '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff') +
        struct.pack(
            '>4sH',
            ipaddr,
            port))


def makeMessage(magic, command, payload):
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[0:4]
    return struct.pack(
        'L12sL4s',
        magic,
        command,
        len(payload),
        checksum) + payload


def getVersionMsg():
    version = 120055
    services = 1
    timestamp = int(time.time())
    addr_me = netaddr(socket.inet_aton("127.0.0.1"), 9999)
    addr_you = netaddr(socket.inet_aton("127.0.0.1"), 9999)
    nonce = random.getrandbits(64)
    sub_version_num = varstr('')
    start_height = 0

    payload = struct.pack(
        '<LQQ26s26sQsL',
        version,
        services,
        timestamp,
        addr_me,
        addr_you,
        nonce,
        sub_version_num,
        start_height)
    return makeMessage(magic, 'version', payload)
