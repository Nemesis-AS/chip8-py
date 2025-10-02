instructions = bytes([
    0x00, 0xE0, 0xA2, 0x2A, 0x60, 0x0C, 0x61, 0x08, 0xD0, 0x1F, 0x70, 0x09, 0xA2, 0x39, 0xD0, 0x1F, 
    0xA2, 0x48, 0x70, 0x08, 0xD0, 0x1F, 0x70, 0x04, 0xA2, 0x57, 0xD0, 0x1F, 0x70, 0x08, 0xA2, 0x66, 
    0xD0, 0x1F, 0x70, 0x08, 0xA2, 0x75, 0xD0, 0x1F, 0x12, 0x28, 0xFF, 0x00, 0xFF, 0x00, 0x3C, 0x00, 
    0x3C, 0x00, 0x3C, 0x00, 0x3C, 0x00, 0xFF, 0x00, 0xFF, 0xFF, 0x00, 0xFF, 0x00, 0x38, 0x00, 0x3F, 
    0x00, 0x3F, 0x00, 0x38, 0x00, 0xFF, 0x00, 0xFF, 0x80, 0x00, 0xE0, 0x00, 0xE0, 0x00, 0x80, 0x00, 
    0x80, 0x00, 0xE0, 0x00, 0xE0, 0x00, 0x80, 0xF8, 0x00, 0xFC, 0x00, 0x3E, 0x00, 0x3F, 0x00, 0x3B, 
    0x00, 0x39, 0x00, 0xF8, 0x00, 0xF8, 0x03, 0x00, 0x07, 0x00, 0x0F, 0x00, 0xBF, 0x00, 0xFB, 0x00, 
    0xF3, 0x00, 0xE3, 0x00, 0x43, 0xE5, 0x05, 0xE2, 0x00, 0x85, 0x07, 0x81, 0x01, 0x80, 0x02, 0x80, 
    0x07, 0xE1, 0x06, 0xE7
])

display = instructions[42:]

decoded = []
# print(len(decoded))

for idx in range(0, len(instructions), 2):
    decoded.append(f"{instructions[idx]:04x}{instructions[idx + 1]:04x}")

for i in range(0, len(instructions), 2):
    opcode = (instructions[i] << 8) | instructions[i + 1]
    nnn = opcode & 0x0FFF
    nn = opcode & 0x00FF
    n = opcode & 0x000F
    x = (opcode & 0x0F00) >> 8
    y = (opcode & 0x00F0) >> 4

    if opcode == 0x00E0:
        mnemonic = "CLS"
    elif opcode == 0x00EE:
        mnemonic = "RET"
    elif (opcode & 0xF000) == 0x0000:
        mnemonic = f"SYS ${nnn:03X}"
    elif (opcode & 0xF000) == 0x1000:
        mnemonic = f"JP ${nnn:03X}"
    elif (opcode & 0xF000) == 0x2000:
        mnemonic = f"CALL ${nnn:03X}"
    elif (opcode & 0xF000) == 0x3000:
        mnemonic = f"SE V{x:X}, ${nn:02X}"
    elif (opcode & 0xF000) == 0x4000:
        mnemonic = f"SNE V{x:X}, ${nn:02X}"
    elif (opcode & 0xF00F) == 0x5000:
        mnemonic = f"SE V{x:X}, V{y:X}"
    elif (opcode & 0xF000) == 0x6000:
        mnemonic = f"LD V{x:X}, ${nn:02X}"
    elif (opcode & 0xF000) == 0x7000:
        mnemonic = f"ADD V{x:X}, ${nn:02X}"
    elif (opcode & 0xF00F) == 0x8000:
        mnemonic = f"LD V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x8001:
        mnemonic = f"OR V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x8002:
        mnemonic = f"AND V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x8003:
        mnemonic = f"XOR V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x8004:
        mnemonic = f"ADD V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x8005:
        mnemonic = f"SUB V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x8006:
        mnemonic = f"SHR V{x:X}"
    elif (opcode & 0xF00F) == 0x8007:
        mnemonic = f"SUBN V{x:X}, V{y:X}"
    elif (opcode & 0xF00F) == 0x800E:
        mnemonic = f"SHL V{x:X}"
    elif (opcode & 0xF00F) == 0x9000:
        mnemonic = f"SNE V{x:X}, V{y:X}"
    elif (opcode & 0xF000) == 0xA000:
        mnemonic = f"LD I, ${nnn:03X}"
    elif (opcode & 0xF000) == 0xB000:
        mnemonic = f"JP V0, ${nnn:03X}"
    elif (opcode & 0xF000) == 0xC000:
        mnemonic = f"RND V{x:X}, ${nn:02X}"
    elif (opcode & 0xF000) == 0xD000:
        mnemonic = f"DRW V{x:X}, V{y:X}, {n}"
    elif (opcode & 0xF0FF) == 0xE09E:
        mnemonic = f"SKP V{x:X}"
    elif (opcode & 0xF0FF) == 0xE0A1:
        mnemonic = f"SKNP V{x:X}"
    elif (opcode & 0xF0FF) == 0xF007:
        mnemonic = f"LD V{x:X}, DT"
    elif (opcode & 0xF0FF) == 0xF00A:
        mnemonic = f"LD V{x:X}, K"
    elif (opcode & 0xF0FF) == 0xF015:
        mnemonic = f"LD DT, V{x:X}"
    elif (opcode & 0xF0FF) == 0xF018:
        mnemonic = f"LD ST, V{x:X}"
    elif (opcode & 0xF0FF) == 0xF01E:
        mnemonic = f"ADD I, V{x:X}"
    elif (opcode & 0xF0FF) == 0xF029:
        mnemonic = f"LD F, V{x:X}"
    elif (opcode & 0xF0FF) == 0xF033:
        mnemonic = f"LD B, V{x:X}"
    elif (opcode & 0xF0FF) == 0xF055:
        mnemonic = f"LD [I], V{x:X}"
    elif (opcode & 0xF0FF) == 0xF065:
        mnemonic = f"LD V{x:X}, [I]"
    else:
        mnemonic = "UNKNOWN"

    print(f"{i:04X}: {opcode:04X} {mnemonic}")

# print(decoded)

# text = ""

# for y in range(64):
#     # for x in range(128 // 8):
#         # print(x, y)
#         # offset = (y * 128 // 8) + x
#     byte = display[y]

#     if y % 15 == 0:
#         print("\n\n")

#     for o in range(7, -1 , -1):
#         bit = (byte & (1 << o)) >> o

#         if bit == 1:
#             print("█", end="")
#             # text += "█"
#         else:
#             print(" ", end="")
#             # text += " "

#         # if self.display[offset] > 0:
#         #     print("D", end="")
#         # else:
#         #     print(" ", end="")
#     print("\n", end="")
#     # text += "\n"

# with open("ascii.txt", "w", encoding="utf-8") as f:
#     f.write(text)