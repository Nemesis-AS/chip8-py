import argparse

def decode_opcode(opcode):
    nnn = opcode & 0x0FFF
    nn = opcode & 0x00FF
    n = opcode & 0x000F
    x = (opcode & 0x0F00) >> 8
    y = (opcode & 0x00F0) >> 4

    if opcode == 0x00E0:
        return "CLS"
    elif opcode == 0x00EE:
        return "RET"
    elif (opcode & 0xF000) == 0x0000:
        return f"SYS ${nnn:03X}"
    elif (opcode & 0xF000) == 0x1000:
        return f"JP ${nnn:03X}"
    elif (opcode & 0xF000) == 0x2000:
        return f"CALL ${nnn:03X}"
    elif (opcode & 0xF000) == 0x3000:
        return f"SE V{x:X}, ${nn:02X}"
    elif (opcode & 0xF000) == 0x4000:
        return f"SNE V{x:X}, ${nn:02X}"
    elif (opcode & 0xF00F) == 0x5000:
        return f"SE V{x:X}, V{y:X}"
    elif (opcode & 0xF000) == 0x6000:
        return f"LD V{x:X}, ${nn:02X}"
    elif (opcode & 0xF000) == 0x7000:
        return f"ADD V{x:X}, ${nn:02X}"
    elif (opcode & 0xF00F) == 0x8000:
        return f"LD V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x8001:
        return f"OR V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x8002:
        return f"AND V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x8003:
        return f"XOR V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x8004:
        return f"ADD V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x8005:
        return f"SUB V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x8006:
        return f"SHR V{x:X}"
    elif (opcode & 0xF00F) == 0x8007:
        return f"SUBN V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x800E:
        return f"SHL V{x:X}"
    elif (opcode & 0xF00F) == 0x9000:
        return f"SNE V{x:X}, V{y:X}"
    elif (opcode & 0xF000) == 0xA000:
        return f"LD I, ${nnn:03X}"
    elif (opcode & 0xF000) == 0xB000:
        return f"JP V0, ${nnn:03X}"
    elif (opcode & 0xF000) == 0xC000:
        return f"RND V{x:X}, ${nn:02X}"
    elif (opcode & 0xF000) == 0xD000:
        return f"DRW V{x:X}, V{y:X}, {n}"
    elif (opcode & 0xF0FF) == 0xE09E:
        return f"SKP V{x:X}"
    elif (opcode & 0xF0FF) == 0xE0A1:
        return f"SKNP V{x:X}"
    elif (opcode & 0xF0FF) == 0xF007:
        return f"LD V{x:X}, DT"
    elif (opcode & 0xF0FF) == 0xF00A:
        return f"LD V{x:X}, K"
    elif (opcode & 0xF0FF) == 0xF015:
        return f"LD DT, V{x:X}"
    elif (opcode & 0xF0FF) == 0xF018:
        return f"LD ST, V{x:X}"
    elif (opcode & 0xF0FF) == 0xF01E:
        return f"ADD I, V{x:X}"
    elif (opcode & 0xF0FF) == 0xF029:
        return f"LD F, V{x:X}"
    elif (opcode & 0xF0FF) == 0xF033:
        return f"LD B, V{x:X}"
    elif (opcode & 0xF0FF) == 0xF055:
        return f"LD [I], V{x:X}"
    elif (opcode & 0xF0FF) == 0xF065:
        return f"LD V{x:X}, [I]"

    return "UNKNOWN"

def disassemble(data, start_addr=0x200, mode="asm"):
    for offset in range(0, len(data) - 1, 2):
        opcode = (data[offset] << 8) | data[offset + 1]
        addr = start_addr + offset

        if mode == "asm":
            print(f"{addr:03X}: {opcode:04X}  {decode_opcode(opcode)}")
        elif mode == "hex":
            print(f"{addr:03X}: {opcode:04X}")
        elif mode == "bin":
            print(f"{addr:03X}: {opcode:016b}")

def main():
    parser = argparse.ArgumentParser(description="CHIP-8 Disassembler")
    parser.add_argument("rom", help="Path to CHIP-8 ROM")
    parser.add_argument(
        "--mode",
        choices=["asm", "hex", "bin"],
        default="asm",
        help="Output format",
    )
    parser.add_argument(
        "--base",
        default="0x200",
        help="Start address (default: 0x200)",
    )

    args = parser.parse_args()

    with open(args.rom, "rb") as f:
        rom = f.read()

    disassemble(
        rom,
        start_addr=int(args.base, 0),
        mode=args.mode,
    )

if __name__ == "__main__":
    main()