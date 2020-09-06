import struct


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def receive_json(sock):
    lengthbuf = recvall(sock, 4)
    if lengthbuf is None:
        return None
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)


def send_json(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)
