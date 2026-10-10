"""Discover the RFCOMM channel for one specific Bluetooth service UUID."""
import socket
import struct
import uuid

LINK_UUID = '7ca9012e-6d15-4802-a320-a1b2c3d4e501'


def element(data, offset=0):
    if offset >= len(data):
        raise ValueError('Missing SDP data element')
    header = data[offset]
    offset += 1
    kind, size_code = header >> 3, header & 7
    if kind == 0:
        size = 0
    elif size_code < 5:
        size = 1 << size_code
    else:
        count = 1 << (size_code - 5)
        size = int.from_bytes(data[offset:offset + count], 'big')
        offset += count
    end = offset + size
    if end > len(data):
        raise ValueError('Truncated SDP data element')
    if kind in (6, 7):
        value = []
        while offset < end:
            child, offset = element(data, offset)
            if offset > end:
                raise ValueError('SDP child exceeds its sequence')
            value.append(child)
    elif kind in (1, 2, 3):
        value = int.from_bytes(data[offset:end], 'big', signed=kind == 2)
    else:
        value = data[offset:end]
    return (kind, value), end


def find_channel(address, service=LINK_UUID):
    service_bytes = uuid.UUID(service).bytes
    if service_bytes[:2] == b'\x00\x00' and service_bytes[4:] == bytes.fromhex('00001000800000805f9b34fb'):
        query = bytes.fromhex('350319') + service_bytes[2:4]
    else:
        query = bytes.fromhex('35111c') + service_bytes
    attributes = bytearray()
    continuation = b'\x00'
    with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP) as sock:
        sock.settimeout(15)
        sock.connect((address, 1))
        for transaction in range(1, 17):
            parameters = query + bytes.fromhex('ffff35050a0000ffff') + continuation
            sock.send(struct.pack('>BHH', 6, transaction, len(parameters)) + parameters)
            response = sock.recv(65535)
            if len(response) < 8:
                raise ValueError('Short SDP response')
            opcode, reply_id, length = struct.unpack('>BHH', response[:5])
            if opcode != 7 or reply_id != transaction or length != len(response) - 5:
                raise ValueError('Unexpected SDP response')
            count = int.from_bytes(response[5:7], 'big')
            attributes.extend(response[7:7 + count])
            continuation = response[7 + count:]
            if not continuation or len(continuation) != continuation[0] + 1:
                raise ValueError('Invalid SDP continuation')
            if continuation == b'\x00':
                break
        else:
            raise ValueError('Too many SDP continuation pages')
    root, end = element(attributes)
    if root[0] != 6 or end != len(attributes):
        raise ValueError('Invalid SDP attribute list')
    for kind, record in root[1]:
        if kind != 6:
            continue
        for index in range(0, len(record) - 1, 2):
            attribute, value = record[index:index + 2]
            if attribute == (1, 4) and value[0] == 6:
                for protocol_kind, protocol in value[1]:
                    if protocol_kind == 6 and len(protocol) >= 2 and protocol[0] == (3, 3):
                        channel = protocol[1][1]
                        if protocol[1][0] == 1 and 1 <= channel <= 30:
                            return channel
    raise RuntimeError('Requested service ' + service + ' has no advertised RFCOMM channel')
