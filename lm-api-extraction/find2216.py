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
        insns = list(md.disasm(data, seg["p_vaddr"]))

        for i, ins in enumerate(insns):
            if ins.mnemonic == "mov" and "#0x8a8" in ins.op_str:
                print("\n--- candidate ---")
                for x in insns[max(0, i-12):i+18]:
                    print(f"0x{x.address:x}: {x.mnemonic:<7} {x.op_str}")
