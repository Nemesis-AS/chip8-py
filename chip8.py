import random
from math import ceil

class CHIP8:
    MEMORY_SIZE = 4096  # 4KB
    DISPLAY_RESOLUTION = (64, 32)
    DISPLAY_SIZE = ceil(DISPLAY_RESOLUTION[0] * DISPLAY_RESOLUTION[1] / 8) # 64 x 32 pixel display

    memory = bytearray(MEMORY_SIZE)
    display = bytearray(DISPLAY_SIZE)
    pc = 0  # Program Counter
    i = 0  # Index Register
    stack = []

    delay = 0  # Delay timer
    sound = 0  # Sound Timer
    registers = bytearray(16)  # 16 single byte General Purpose Registers

    running = False
    draw_ready = True  # Cleared by a draw, set again each frame by the host (display wait quirk)

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

    KEYPRESS = [False for _ in range(16)]
    FX0A_KEY = None

    def __init__(self):
        self.boot()

    def boot(self):
        # put FONT into memory at FONT_START
        for offset in range(len(self.FONT)):
            self.memory[self.FONT_START + offset] = self.FONT[offset]

        # Set the PC to User Space
        self.pc = self.MEM_START

    def load(self, data):
        for offset in range(len(data)):
            self.memory[self.MEM_START + offset] = data[offset]

    def run(self):
        while True:
            if self.pc >= self.MEMORY_SIZE:
                print("PC Out of Memory!")
                break
            
            res = self.fdre()

            if not res:
                break

    def tick(self):
        print("Tick")

    def fdre(self):
        # Fetch
        ins = (self.memory[self.pc] << 8) + self.memory[self.pc + 1]
        # print(hex(ins), hex(self.memory[self.pc]), hex(self.memory[self.pc + 1]))
        self.pc += 2

        if ins == 0x0000:
            self.running = False
            return False

        # Decode
        match (ins & 0xF000):
            case 0x0000:
                if ins == 0x00E0:
                    # 0x00E0
                    # Clear Screen
                    for idx in range(self.DISPLAY_SIZE):
                        self.display[idx] = 0
                    # print("Screen cleared")
                elif ins == 0x00EE:
                    # 0x00EE
                    # Return from subroutine: Pop value from stack and set PC to it
                    if len(self.stack) == 0:
                        print("Cannot return from subroutine! Stack is empty!")
                        return
                    
                    self.pc = self.stack.pop()
                    # print("Returning from subroutine!")
            case 0x1000:
                # 0x1NNN
                # Set PC to NNN
                jmp_addr = ins & self.MASK_NNN
                self.pc = jmp_addr
                # print("Jumping to ", jmp_addr)
            case 0x2000:
                # 0x2NNN
                # Call a subroutine: Push PC to stack, and set PC to NNN
                self.stack.append(self.pc)
                routine_addr = ins & self.MASK_NNN
                self.pc = routine_addr
                # print("Subroutine called! Jumping to addr: ", hex(routine_addr))
            case 0x3000:
                # 0x3XNN
                # Skip next instruction if Reg VX == NN
                condition_reg = (ins & self.MASK_X) >> 8
                comp_value = ins & self.MASK_NN

                # print(f"Conditional Skip Encountered! Comparing Reg: {condition_reg}[{self.registers[condition_reg]}] to val: {comp_value}")
                if self.registers[condition_reg] == comp_value:
                    # print("Value matches! Skipping next instruction...")
                    self.pc += 2
            case 0x4000:
                # 0x4XNN
                # Skip next instruction if Reg VX != NN
                condition_reg = (ins & self.MASK_X) >> 8
                comp_value = ins & self.MASK_NN

                # print(f"Conditional Skip Encountered! Comparing Reg: {condition_reg}[{self.registers[condition_reg]}] to val: {comp_value}")
                if self.registers[condition_reg] != comp_value:
                    # print("Value does not match! Skipping next instruction...")
                    self.pc += 2
            case 0x5000:
                # 0x5XY0
                # Skip next instruction if Reg VX == Reg VY
                reg1 = (ins & self.MASK_X) >> 8
                reg2 = (ins & self.MASK_Y) >> 4

                # print(f"Conditional Skip Encountered! Comparing Reg: {reg1}[{self.registers[reg1]}] to Reg: {reg2}[{self.registers[reg2]}]")
                if self.registers[reg1] == self.registers[reg2]:
                    # print("Value matches! Skipping next instruction...")
                    self.pc += 2
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

                new_val = (self.registers[reg] + val) % 256

                self.registers[reg] = new_val
                # print(f"Adding {val} to register {reg}: {self.registers[reg]}")
            case 0x8000:
                # Arithmatic Operations
                x = (ins & self.MASK_X) >> 8
                y = (ins & self.MASK_Y) >> 4
                n = ins & self.MASK_N
                match n:
                    case 0x0:
                        # 0x8XY0
                        # Set VX to the value at VY
                        self.registers[x] = self.registers[y]
                    case 0x1:
                        # 0x8XY1
                        # Binary OR: Set VX to VX OR VY
                        self.registers[x] |= self.registers[y]
                        self.registers[self.VF] = 0
                    case 0x2:
                        # 0x8XY2
                        # Binary AND: Set VX to VX AND VY
                        self.registers[x] &= self.registers[y]
                        self.registers[self.VF] = 0
                    case 0x3:
                        # 0x8XY3
                        # Binary XOR
                        self.registers[x] ^= self.registers[y]
                        self.registers[self.VF] = 0
                    case 0x4:
                        # 0x8XY4
                        # Add: Set VX = VX + VY
                        res = self.registers[x] + self.registers[y]

                        self.registers[x] = res % 256
                        self.registers[self.VF] = 1 if res > 255 else 0
                    case 0x5:
                        # 0x8XY5
                        # Subtract: Set VX = VX - VY
                        vf = 1 if self.registers[x] >= self.registers[y] else 0
                        res = self.registers[x] - self.registers[y]

                        if res < 0:
                            res += 256

                        self.registers[x] = res
                        self.registers[self.VF] = vf
                    case 0x6:
                        # 0x8XY6
                        # Right Shift: Set VX = VY >> 1 OR VX = VX >> 1

                        # @todo! Do this if the emulator is configured
                        vf = self.registers[x] & 0x1 # Capture the shifted-out bit
                        self.registers[x] = self.registers[x] >> 1
                        # self.registers[x] = self.registers[y]
                        self.registers[x] &= 0xFF
                        self.registers[self.VF] = vf
                    case 0x7:
                        # 0x8XY7
                        # Subtract: Set VX = VY - VX
                        vf = 1 if self.registers[y] >= self.registers[x] else 0
                        res = self.registers[y] - self.registers[x]

                        if res < 0:
                            res += 256

                        self.registers[x] = res
                        self.registers[self.VF] = vf
                    case 0xE:
                        # 0x8XYE
                        # Left Shift: Set VX = VY << 1 OR VX = VX << 1

                        # @todo! Do this if the emulator is configured
                        self.registers[x] = self.registers[y]

                        vf = (self.registers[x] & 0x80) >> 7 # Capture the shifted-out bit
                        self.registers[x] = (self.registers[x] << 1) % 256
                        self.registers[self.VF] = vf
                    case _:
                        print("Unknown Arithmetic Instruction:", hex(ins))
            case 0x9000:
                # 0x9XY0
                # Skip next instruction if Reg VX != Reg VY
                reg1 = (ins & self.MASK_X) >> 8
                reg2 = (ins & self.MASK_Y) >> 4

                # print(f"Conditional Skip Encountered! Comparing Reg: {reg1}[{self.registers[reg1]}] to Reg: {reg2}[{self.registers[reg2]}]")
                if self.registers[reg1] != self.registers[reg2]:
                    # print("Value does not match! Skipping next instruction...")
                    self.pc += 2
            case 0xA000:
                # 0xANNN
                # Set Index Register I

                addr = ins & self.MASK_NNN
                self.i = addr
                # print(f"Setting Index register to {addr}")
            case 0xB000:
                # 0xBNNN
                # Jump with Offset: Jump to NNN + V0 OR XNN + VX
                # @todo! Make this configurable
                addr = ins & self.MASK_NNN
                # vx = (ins & self.MASK_X) >> 8
                offset = self.registers[self.V0] ## OR vx

                self.pc = addr + offset
            case 0xC000:
                # 0xCXNN
                # Random: Generate a random number and AND with NN. Store in VX
                nn = ins & self.MASK_NN
                vx = (ins & self.MASK_X) >> 8
                self.registers[vx] = random.randint(0, 255) & nn
            case 0xD000:
                # DXYN
                # Draw on Screen
                if not self.draw_ready:
                    # Display wait quirk: only one draw per frame, block until the next
                    self.pc -= 2
                    return True

                self.draw_ready = False

                x = self.registers[(ins & self.MASK_X) >> 8] % self.DISPLAY_RESOLUTION[0]
                y = self.registers[(ins & self.MASK_Y) >> 4] % self.DISPLAY_RESOLUTION[1]
                height = ins & self.MASK_N
                row_bytes = self.DISPLAY_RESOLUTION[0] // 8
                byte_offset = x % 8

                self.registers[self.VF] = 0

                for dy in range(height):
                    if y + dy >= self.DISPLAY_RESOLUTION[1]:
                        break  # clip off bottom edge

                    offset = ((y + dy) * row_bytes) + (x // 8)
                    sprite_byte = self.memory[self.i + dy]

                    before = self.display[offset]
                    self.display[offset] ^= sprite_byte >> byte_offset
                    if before & ~self.display[offset] & 0xFF:
                        self.registers[self.VF] = 1

                    if byte_offset != 0 and (x // 8) + 1 < row_bytes:
                        before = self.display[offset + 1]
                        self.display[offset + 1] ^= (sprite_byte << (8 - byte_offset)) % 256
                        if before & ~self.display[offset + 1] & 0xFF:
                            self.registers[self.VF] = 1
            case 0xE000:
                nn = ins & self.MASK_NN
                x = (ins & self.MASK_X) >> 8
                key = self.registers[x]

                match nn:
                    case 0x9E:
                        # 0xEX9E
                        # Skip if key corresponding to VX is pressed
                        if self.KEYPRESS[key]:
                            self.pc += 2
                    case 0xA1:
                        # 0xEXA1
                        # Skip if key corresponding to VX is not pressed
                        if not self.KEYPRESS[key]:
                            self.pc += 2
            case 0xF000:
                nn = ins & self.MASK_NN
                x = (ins & self.MASK_X) >> 8

                match nn:
                    case 0x07:
                        # 0xFX07
                        # Set value from delay timer to VX
                        self.registers[x] = self.delay % 256
                    case 0x15:
                        # 0xFX15
                        # Set value from VX to delay timer
                        self.delay = self.registers[x]
                    case 0x18:
                        # 0xFX18
                        # Set value from VX to sound timer
                        self.sound = self.registers[x]
                    case 0x1E:
                        # 0xFX1E
                        # Add to Index: Add value of VX to I
                        res = self.i + self.registers[x]

                        # self.registers[self.VF] = 1 if res > 255 else 0
                        self.i = res & 0xfff
                    case 0x0A:
                        # 0xFX0A
                        # Get Key: wait for a press, then block until that key is released
                        if self.FX0A_KEY is None:
                            for idx, key in enumerate(self.KEYPRESS):
                                if key:
                                    self.FX0A_KEY = idx
                                    break
                            self.pc -= 2
                        elif self.KEYPRESS[self.FX0A_KEY]:
                            self.pc -= 2
                        else:
                            self.registers[x] = self.FX0A_KEY
                            self.FX0A_KEY = None
                    case 0x29:
                        pass
                    case 0x33:
                        # 0xFX33
                        # Binary-coded decimal conversion
                        # Store individual digits of VX at I, I+1 and I+2
                        vx = self.registers[x]

                        self.memory[self.i] = (vx // 100) % 10
                        self.memory[self.i + 1] = (vx // 10) % 10
                        self.memory[self.i + 2] = vx % 10
                    case 0x55:
                        # 0xFX55
                        # Store: Stores values from V0..VX(Inclusive) into Mem starting from I
                        # @todo! Make this configurable
                        for offset in range(x + 1):
                            val = self.registers[offset]
                            self.memory[self.i + offset] = val
                        self.i = (self.i + x + 1) & 0xFFF
                    case 0x65:
                        # 0xFX65
                        # Load: Loads values from memory rom I to registers V0..Vx(Inclusive)
                        # @todo! Make this configurable
                        for offset in range(x + 1):
                            val = self.memory[self.i + offset] % 256
                            self.registers[offset] = val
                        self.i = (self.i + x + 1) & 0xFFF
        return True

    def debug_draw(self):
        for y in range(self.DISPLAY_RESOLUTION[1]):
            for x in range(self.DISPLAY_RESOLUTION[0] // 8):
                # print(x, y)
                offset = (y * self.DISPLAY_RESOLUTION[0] // 8) + x
                byte = self.display[offset]

                for o in range(7, -1 , -1):
                    bit = (byte & (1 << o)) >> o

                    if bit == 1:
                        print("█", end="")
                    else:
                        print(" ", end="")
            print("\n", end="")

if __name__ == "__main__":
    emu = CHIP8()
