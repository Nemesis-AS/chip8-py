from chip8 import CHIP8

emu = CHIP8()
emu.boot()

with open("./roms/1-chip8-logo.ch8", "rb") as file:
    data = file.read()
    emu.load(data)
    emu.run()
    emu.debug_draw()

# with open("./roms/2-ibm-logo.ch8", "rb") as file:
#     data = file.read()
#     emu.load(data)
#     emu.run()
#     emu.debug_draw()