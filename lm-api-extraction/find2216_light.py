from pathlib import Path
from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN

path = Path.home() / "lords-2.201-analysis/native/libil2cpp.so"

with open(path, "rb") as f:
    elf = ELFFile(f)
    md = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)

    for seg in elf.iter_segments():
        if seg["p_type"] != "PT_LOAD" or seg["p_filesz"] == 0:
            continue

        f.seek(seg["p_offset"])
        data = f.read(seg["p_filesz"])

        for ins in md.disasm(data, seg["p_vaddr"]):
            if ins.mnemonic == "mov" and "#0x8a8" in ins.op_str:
                print(f"FOUND: 0x{ins.address:x}: {ins.mnemonic} {ins.op_str}", flush=True)
