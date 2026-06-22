# A CHIP8 Emulator Written in Python

This is my first emulator I'm writing. So, or the sake of simplicity and learning I decided to write it in Python.

This emulator implements the core spec in `chip8.py` with the input, sound and graphics layer in `ray_wrapper.py` using Raylib.

## Usage

Load and run a ROM using the following:

```sh
python3 main.py <path-to-rom>
```

If no path is provided, it runs the `roms/1-chip8-logo.ch8` ROM which is just a static image.

## Passed Tests

- [x] CHIP-8 splash screen
- [x] IBM Logo
- [x] Corax+ opcode test
- [x] Flags test
- [x] Quirks test
- [x] Keypad test
- [x] Beep test
- [ ] Scrolling test (Not applicable for CHIP-8)

### Disassembler

For debugging purposes, I also wrote a simple disassembler to load and read CHIP-8 ROMs and print either the hex, asm or binary opcodes.

#### Usage:

```sh
python3 disassembler.py <path-to-rom> --mode hex|asm|bin
```

The default value for mode is asm.

## Desclaimer

I DO NOT own any of the ROMS used for testing here. Those are from [Timendus' CHIP8 Test Suite](https://github.com/Timendus/chip8-test-suite)
