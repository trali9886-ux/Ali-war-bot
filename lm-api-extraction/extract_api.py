"""Re-extract protocol IDs and verify native evidence for supplied build 692.

Requires capstone==5.0.9 and pyelftools==0.32 only for static extraction.
Does not connect to a device or server. Addresses are ELF virtual addresses.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

LIB_HASH = '2352799c07c1451b17ecf2bd6cb4e2e90e56ca65c0de45f741fc96837aa524fd'
META_HASH = 'f5d076f2c48f3abd6ff8daecedde77896241f0bd4ef779741ea6bcd033a4764a'
ROOT = Path(__file__).resolve().parent

# Each claim is tied to instructions in the supplied ARM64 image.
CHECKS = {
    0x44e65d4: ('mov', 'w9, #0x8c1'),
    0x44e65f4: ('bl', '#0x46bb52c'),
    0x332c47c: ('cmp', 'w8, #0x8ac'),
    0x332cbf4: ('b', '#0x43fa3a8'),
    0x44deaf8: ('mov', 'w9, #0x899'),
    0x44deafc: ('mov', 'w10, #0x8b9'),
    0x44deb14: ('ldrb', 'w1, [x19, #0x19]'),
    0x44deb4c: ('bl', '#0x46bb3a8'),
    0x44deb54: ('cmp', 'x22, #4'),
    0x44deb70: ('bl', '#0x46c23f4'),
    0x44debc8: ('bl', '#0x46c23f4'),
    0x44debe4: ('bl', '#0x46bb598'),
    0x44debe8: ('mov', 'w8, #0x3fc00000'),
    0x44debec: ('str', 'w8, [x19, #0x1e4]'),
    0x43fa5bc: ('sub', 'w8, w25, #0x16'),
    0x43fa5c4: ('b.lo', '#0x43fa600'),
    0x43fa678: ('ubfx', 'w22, w29, #0xc, #4'),
    0x43fa69c: ('bl', '#0x46bbe78'),
    0x43fa6cc: ('bl', '#0x46c27f0'),
    0x43fa800: ('strb', 'w0, [x20, #0x2f8]'),
    0x43fa824: ('strb', 'w0, [x20, #0x2f9]'),
    0x43fa828: ('ubfx', 'w8, w29, #6, #6'),
    0x43fb818: ('and', 'w8, w29, #0x3f'),
    0x43fcc20: ('cmp', 'w8, #0x17'),
    0x44df824: ('and', 'w8, w0, #0xfe'),
    0x44df828: ('cmp', 'w8, #8'),
    0x44d0284: ('mov', 'w1, #5'),
    0x46bb2bc: ('mov', 'w8, #4'),
    0x46bb844: ('mov', 'w1, #2'),
    0x46bb874: ('mov', 'w1, #4'),
    0x46bb8ac: ('bl', '#0x46c3058'),
    0x46c22f8: ('add', 'w1, w9, #1'),
    0x46c2304: ('b', '#0x46c1fa4'),
    0x46c310c: ('and', 'w3, w21, #0xfffffff8'),
    0x46cb3d4: ('sub', 'w8, w0, #4'),
    0x46cb3e4: ('cmp', 'w9, #0xffd'),
    0x46cb438: ('sub', 'w3, w25, #4'),
    0x46cb444: ('add', 'w2, w20, #4'),
    0x46ca27c: ('mov', 'w2, #1'),
    0x46ca280: ('mov', 'w3, #6'),
    0x46cb4b4: ('mov', 'w3, wzr'),
    0x46c30e8: ('b.lt', '#0x46c32ac'),
    0x33e5170: ('orr', 'w0, w10, w8, lsl #8'),
}
RANGES = {
    'minimap-request': (0x44e655c, 0xb8),
    'guest-map-dispatch-test': (0x332c474, 0x48),
    'guest-map-dispatch-tail': (0x332cb24, 0xd4),
    'socket-connect': (0x46ca25c, 0x40),
    'map-request': (0x44de8dc, 0x328),
    'bulk-header': (0x43fa5b8, 0x2b4),
    'bulk-player': (0x43faa04, 0x2ec),
    'bulk-player-tail': (0x43faf68, 0x98),
    'bulk-line': (0x43fb818, 0x444),
    'bulk-end': (0x43fcbdc, 0x98),
    'packet-sequence': (0x46c2284, 0x90),
    'packet-send': (0x46bb598, 0x340),
    'cipher': (0x46c3058, 0x310),
    'receive-frame': (0x46cb380, 0x188),
    'little-endian-u16': (0x33e5124, 0x60),
}


class Metadata:
    def __init__(self, data):
        self.data = data
        if struct.unpack_from('<II', data) != (0xfab11baf, 31):
            raise ValueError('expected IL2CPP metadata version 31')
        self.strings = self.table(24)
        self.types = self.table(160)
        self.fields = self.table(96)
        self.methods = self.table(48)
        self.constants = dict((i, (t, p)) for i, t, p in struct.iter_unpack('<iii', self.table(64)))
        self.constant_data = self.table(72)

    def table(self, position):
        offset, size = struct.unpack_from('<II', self.data, position)
        if offset + size > len(self.data):
            raise ValueError('metadata table outside file')
        return self.data[offset:offset+size]

    def string(self, offset):
        return self.strings[offset:self.strings.index(0, offset)].decode('utf-8')

    def protocol_catalog(self):
        matches = []
        for start in range(0, len(self.types), 88):
            if self.string(struct.unpack_from('<I', self.types, start)[0]) == 'Protocol':
                matches.append(start)
        if len(matches) != 1:
            raise ValueError('Protocol enum is ambiguous')
        start = matches[0]
        field_start = struct.unpack_from('<i', self.types, start+32)[0]
        field_count = struct.unpack_from('<H', self.types, start+68)[0]
        result = []
        for index in range(field_start, field_start+field_count):
            name, _, token = struct.unpack_from('<IiI', self.fields, index*12)
            name = self.string(name)
            if name == 'value__':
                continue
            type_index, data_index = self.constants[index]
            if type_index != 38224:  # Exact-build System.UInt16 default-value type.
                raise ValueError('unexpected Protocol constant width')
            result.append(dict(id=struct.unpack_from('<H', self.constant_data, data_index)[0],
                               name=name, field_index=index, token=token))
        return result

    def verify_method(self, binding):
        start = binding['index'] * 36  # v31 adds returnParameterToken.
        name, owner = struct.unpack_from('<Ii', self.methods, start)
        owner_name = self.string(struct.unpack_from('<I', self.types, owner*88)[0])
        if (self.string(name), owner, owner_name) != (binding['name'], binding['declaring_type'], binding['type']):
            raise ValueError('metadata method binding mismatch: ' + binding['name'])


def extract(library, metadata, output):
    from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
    from elftools.elf.elffile import ELFFile
    raw, meta = library.read_bytes(), metadata.read_bytes()
    if hashlib.sha256(raw).hexdigest() != LIB_HASH or hashlib.sha256(meta).hexdigest() != META_HASH:
        raise ValueError('APK build hash mismatch; offsets cannot be reused')
    md = Metadata(meta)
    bindings = json.loads((ROOT/'bindings.json').read_text())['methods']
    for binding in bindings:
        md.verify_method(binding)
    symbols = {int(m['address'], 16): m['type']+'.'+m['name'] for m in bindings}
    with library.open('rb') as source:
        elf = ELFFile(source)
        segments = [s for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']
    def read(address, size):
        segment = next(s for s in segments if s['p_vaddr'] <= address and address+size <= s['p_vaddr']+s['p_filesz'])
        offset = segment['p_offset'] + address - segment['p_vaddr']
        return raw[offset:offset+size]
    disassembler = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    verified = []
    for address, expected in CHECKS.items():
        ins = next(disassembler.disasm(read(address, 4), address))
        actual = ins.mnemonic, ins.op_str
        if actual != expected:
            raise ValueError(f'instruction mismatch at {address:#x}: {actual}')
        verified.append(dict(address=hex(address), instruction=' '.join(actual), bytes=bytes(ins.bytes).hex()))
    catalog = md.protocol_catalog()
    output.mkdir(parents=True, exist_ok=True)
    for name, (start, size) in RANGES.items():
        lines = []
        for ins in disassembler.disasm(read(start, size), start):
            target = int(ins.op_str[1:], 16) if ins.mnemonic in ('bl', 'b') and ins.op_str.startswith('#0x') else None
            lines.append(f'{ins.address:08x} {ins.mnemonic:8} {ins.op_str}' + (' ; '+symbols[target] if target in symbols else ''))
        (output/(name+'.asm')).write_text('\n'.join(lines)+'\n')
    (output/'protocols.json').write_text(json.dumps(dict(source='metadata v31 Protocol enum', protocols=catalog), indent=2)+'\n')
    (output/'verified.json').write_text(json.dumps(dict(library_sha256=LIB_HASH, metadata_sha256=META_HASH,
        methods=bindings, instruction_checks=verified, constructor_width_bytes=list(read(0x122c2d0, 4)),
        status='static extraction only; no server or live packet validation'), indent=2)+'\n')
    print(f'Extracted {len(catalog)} protocol constants; verified {len(bindings)} method names and {len(verified)} native instructions.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT/'evidence')
    args = parser.parse_args()
    extract(args.library, args.metadata, args.output)
