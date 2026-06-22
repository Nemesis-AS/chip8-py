import argparse
from ray_wrapper import CHIP8Ray

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

def main():
    parser = argparse.ArgumentParser(description="CHIP-8 Emulator")
    parser.add_argument("rom", help="Path to CHIP-8 ROM", default=ROMS[0], nargs="?")

    emu = CHIP8Ray()

    args = parser.parse_args()

    with open(args.rom, "rb") as file:
        data = file.read()
        emu.load(data)
        emu.run()

if __name__ == "__main__":
    main()
