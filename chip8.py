# import random
# import time


class CHIP8:
    MEMORY_SIZE = 4096  # 4KB
    DISPLAY_RESOLUTION = (128, 64)
    DISPLAY_SIZE = DISPLAY_RESOLUTION[0] * DISPLAY_RESOLUTION[1] // 8 # 64 x 32 pixel display

    memory = bytearray(MEMORY_SIZE)
    display = bytearray(DISPLAY_SIZE)
    pc = 0  # Program Counter
    i = 0  # Index Register
    stack = []
    delay = bytearray([0])  # Delay timer
    sound = bytearray([0])  # Sound Timer
    registers = bytearray(16)  # 16 single byte General Purpose Registers

    # General Purpose Register Indices
    V0 = 0
    V1 = 1
    V2 = 2
    V3 = 3
    V4 = 4
    V5 = 5
    V6 = 6
    V7 = 7
    V8 = 8
    V9 = 9
    VA = 10
    VB = 11
    VC = 12
    VD = 13
    VE = 14
    VF = 15

    # Instruction Masks
    MASK_X = 0x0F00  # Second Nibble
    MASK_Y = 0x00F0  # Third  Nibble
    MASK_N = 0x000F  # Fourth Nibble
    MASK_NN = 0x00FF  # Second Byte
    MASK_NNN = 0x0FFF  # Second, Third and Fourth Nibble

    MEM_START = 0x200
    FONT_START = 0x050  # End at 0x09F

    FONT = [
        0xF0,
        0x90,
        0x90,
        0x90,
        0xF0,
        0x20,
        0x60,
        0x20,
        0x20,
        0x70,
        0xF0,
        0x10,
        0xF0,
        0x80,
        0xF0,
        0xF0,
        0x10,
        0xF0,
        0x10,
        0xF0,
        0x90,
        0x90,
        0xF0,
        0x10,
        0x10,
        0xF0,
        0x80,
        0xF0,
        0x10,
        0xF0,
        0xF0,
        0x80,
        0xF0,
        0x90,
        0xF0,
        0xF0,
        0x10,
        0x20,
        0x40,
        0x40,
        0xF0,
        0x90,
        0xF0,
        0x90,
        0xF0,
        0xF0,
        0x90,
        0xF0,
        0x10,
        0xF0,
        0xF0,
        0x90,
        0xF0,
        0x90,
        0x90,
        0xE0,
        0x90,
        0xE0,
        0x90,
        0xE0,
        0xF0,
        0x80,
        0x80,
        0x80,
        0xF0,
        0xE0,
        0x90,
        0x90,
        0x90,
        0xE0,
        0xF0,
        0x80,
        0xF0,
        0x80,
        0xF0,
        0xF0,
        0x80,
        0xF0,
        0x80,
        0x80,
    ]

    # Additional Options
    FPS = 60
    FRAME_TIME = 1.0 / FPS

    def boot(self):
        # put FONT into memory at FONT_START
        for offset in range(len(self.FONT)):
            self.memory[self.FONT_START + offset] = self.FONT[offset]

        # @temp Add garbage value to mem
        # for addr in range(len(self.memory)):
        #     self.memory[addr] = random.randint(0, 20)

        # Set the PC to User Space
        self.pc = self.MEM_START + 2

    def load(self, data):
        for offset in range(len(data)):
            self.memory[self.MEM_START + offset] = data[offset]
        
        # print(self.memory)

    def run(self):
        iteration  = 0

        while True:
            if self.pc >= self.MEMORY_SIZE:
                print("PC Out of Memory!")
                break

            
            res = self.fdre()

            if not res:
                break

            iteration += 1

            if (iteration > 5000):
                break
        
        # print(self.display)

        # next_frame = time.perf_counter()
        # while True:
        #     self.tick()

        #     next_frame += self.FRAME_TIME
        #     sleep = next_frame - time.perf_counter()
        #     if sleep > 0:
        #         time.sleep(sleep)

    def tick(self):
        print("Tick")

    def fdre(self):
        # Fetch
        ins = (self.memory[self.pc] << 8) + self.memory[self.pc + 1]
        # print(hex(ins), hex(self.memory[self.pc]), hex(self.memory[self.pc + 1]))
        self.pc += 2

        if ins == 0x0000:
            return False

        # Decode
        match (ins & 0xF000):
            case 0x0000:
                # Clear Screen
                if ins == 0x00E0:
                    for idx in range(self.DISPLAY_SIZE):
                        self.display[idx] = 0
                    # print("Screen cleared")
            case 0x1000:
                jmp_addr = ins & self.MASK_NNN
                self.pc = jmp_addr
                # print("Jumping to ", jmp_addr)
                # print("Instruction at JMP: ", hex(self.memory[self.pc]), hex(self.memory[self.pc + 1]))
                # return False
            case 0x2000:
                pass
            case 0x3000:
                pass
            case 0x4000:
                pass
            case 0x5000:
                pass
            case 0x6000:
                # 0x6XNN
                # Set Register X to value NN
                reg = (ins & self.MASK_X) >> 8
                val = ins & self.MASK_NN

                self.registers[reg] = val
                # print(f"Setting register {reg} to {val}")
            case 0x7000:
                # 0x7XNN
                # Add Value NN to Register X
                reg = (ins & self.MASK_X) >> 8
                val = ins & self.MASK_NN

                self.registers[reg] += val
                # print(f"Adding {val} to register {reg}: {self.registers[reg]}")
            case 0x8000:
                pass
            case 0x9000:
                pass
            case 0xA000:
                # 0xANNN
                # Set Index Register I

                addr = ins & self.MASK_NNN
                self.i = addr
                # print(f"Setting Index register to {addr}")
            case 0xB000:
                pass
            case 0xC000:
                pass
            case 0xD000:
                # DXYN
                # Draw on Screen
                # print(f"{ins:04x}", self.registers[(ins & 0x00F0) >> 4])
                # print("Y: ", f"{((self.memory[self.pc - 2] << 2) + self.memory[self.pc - 1]):08x}")
                x = self.registers[(ins & self.MASK_X) >> 8] % self.DISPLAY_RESOLUTION[1]
                y = self.registers[(ins & self.MASK_Y) >> 4]
                # print("Y:")
                height = ins & self.MASK_N

                # print(f"Setting coords ({x}, {y})")

                for dy in range(height):
                    offset = ((y + dy) * (self.DISPLAY_RESOLUTION[0] // 8)) + (x // 8)

                    if x % 8 == 0:
                        # Perfectly aligned
                        self.display[offset] ^= self.memory[self.i + dy]
                    else:
                        byte_offset = x % 8
                        # print(self.display[offset + 1])
                        self.display[offset] ^= self.memory[self.i + dy] >> byte_offset
                        self.display[offset + 1] ^= (self.memory[self.i + dy] << (8 - byte_offset)) % 256
                        pass

                # offset = x * self.DISPLAY_RESOLUTION[0] + y
                # self.display[offset] = n
                # print(f"Setting coords ({x}, {y})")

                # print(self.display)
            case 0xE000:
                pass
            case 0xF000:
                pass
        
        return True

    def debug_draw(self):
        text = ""

        for y in range(self.DISPLAY_RESOLUTION[1]):
            for x in range(self.DISPLAY_RESOLUTION[0] // 8):
                # print(x, y)
                offset = (y * self.DISPLAY_RESOLUTION[0] // 8) + x
                byte = self.display[offset]

                for o in range(7, -1 , -1):
                    bit = (byte & (1 << o)) >> o

                    if bit == 1:
                        print("█", end="")
                        text += "█"
                    else:
                        print(" ", end="")
                        text += " "

                # if self.display[offset] > 0:
                #     print("D", end="")
                # else:
                #     print(" ", end="")
            print("\n", end="")
            text += "\n"

        # with open("ascii.txt", "w", encoding="utf-8") as f:
        #     f.write(text)

if __name__ == "__main__":
    emu = CHIP8()
    emu.boot()
