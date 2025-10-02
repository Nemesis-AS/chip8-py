from ray_wrapper import CHIP8Ray

emu = CHIP8Ray()

ROMS = [
    "./roms/1-chip8-logo.ch8",
    "./roms/2-ibm-logo.ch8",
    "./roms/3-corax+.ch8",
    "./roms/4-flags.ch8",
    "./roms/5-quirks.ch8",
    "./roms/6-keypad.ch8",
    "./roms/7-beep.ch8",
    "./roms/8-scrolling.ch8",
]

with open(ROMS[1], "rb") as file:
    SCALE = 16

    data = file.read()
    emu.load(data)
    emu.run()
    emu.draw_static(SCALE)
