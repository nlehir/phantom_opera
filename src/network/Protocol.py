import struct
from socket import socket


def recvall(sock: socket, count: int):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def receive(sock: socket):
    lengthbuf = recvall(sock, 4)
    if lengthbuf is None:
        return None
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)


def send(sock: socket, data: bytes):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)


def receive_string(sock: socket):
    data = receive(sock)
    if data is None:
        return data
    return data.decode('utf-8')


def send_string(sock: socket, data: str):
    send(sock, data.encode('utf-8'))
