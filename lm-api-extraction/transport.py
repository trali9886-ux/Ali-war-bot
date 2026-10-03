"""Inspect the verified main-channel frame envelope; payload remains opaque."""
import struct
from protocol import DecodeError, Reader


def decode_frames(data):
    """Parse complete concatenated main-channel frames, each 4..4096 bytes.

    Socket chunks must first be reassembled. This does not decrypt payloads,
    remove an outgoing sequence, authenticate, or identify a live endpoint.
    """
    reader = Reader(data)
    frames = []
    while reader.offset < len(reader.data):
        offset = reader.offset
        size, protocol = reader.unpack('HH')
        if not 4 <= size <= 4096:
            raise DecodeError(f'invalid main-channel frame size {size} at offset {offset}')
        payload = reader.take(size-4)
        frames.append(dict(offset=offset, frame_length=size, protocol=protocol,
                           body_hex=payload.hex(), body_interpretation='opaque transport body'))
    return frames
