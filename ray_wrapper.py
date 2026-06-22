import time
import numpy as np
import pyray as pr
import math
from PIL import Image

from chip8 import CHIP8


class CHIP8Ray(CHIP8):
    # Additional Options
    FPS = 60
    FRAME_TIME = 1.0 / FPS
    INSTRUCTIONS_PER_FRAME = 12
    INSTRUCTIONS_PER_SECOND = FPS * INSTRUCTIONS_PER_FRAME  # For debug purposes
    SCALE = 16

    SAMPLE_RATE = 44100
    BEEP_DURATION = 0.1
    BEEP_FREQUENCY = 440
    BEEP_SOUND = None

    INPUT_MAP = [
        pr.KEY_X,
        pr.KEY_ONE,
        pr.KEY_TWO,
        pr.KEY_THREE,
        pr.KEY_Q,
        pr.KEY_W,
        pr.KEY_E,
        pr.KEY_A,
        pr.KEY_S,
        pr.KEY_D,
        pr.KEY_Z,
        pr.KEY_C,
        pr.KEY_FOUR,
        pr.KEY_R,
        pr.KEY_F,
        pr.KEY_V
    ]

    def run(self):
        self.running = True

        # Initialize Window
        pr.init_window(
            self.DISPLAY_RESOLUTION[0] * self.SCALE,
            self.DISPLAY_RESOLUTION[1] * self.SCALE,
            "CHIP8 Emulator",
        )
        pr.init_audio_device()
        self._init_beep()

        last_time = time.perf_counter()

        while not pr.window_should_close():
            # Read Input
            for idx, key in enumerate(self.INPUT_MAP):
                self.KEYPRESS[idx] = True if pr.is_key_down(key) else False

            self.draw_ready = True

            for _ in range(self.INSTRUCTIONS_PER_FRAME):
                self.fdre()

            # Update Timers
            if self.delay > 0:
                self.delay -= 1

            if self.sound > 0:
                if not pr.is_sound_playing(self.BEEP_SOUND):
                    pr.play_sound(self.BEEP_SOUND)
                self.sound -= 1

            # Update screen
            self.draw(self.SCALE)

            now = time.perf_counter()
            frame_time = now - last_time

            remaining = self.FRAME_TIME - frame_time
            if remaining > 0:
                time.sleep(remaining)

            last_time = time.perf_counter()

        self.running = False
        pr.close_audio_device()
        pr.close_window()

    def serialize_display(self):
        display_bytes = np.zeros(
            (self.DISPLAY_RESOLUTION[1], self.DISPLAY_RESOLUTION[0]), dtype=np.uint8
        )

        for y in range(self.DISPLAY_RESOLUTION[1]):
            for x in range(self.DISPLAY_RESOLUTION[0] // 8):
                byte_offset = y * (self.DISPLAY_RESOLUTION[0] // 8) + x
                for i in range(8):
                    display_bytes[y][(x * 8) + i] = (
                        (self.display[byte_offset] >> (7 - i)) & 0x01
                    ) * 255

        return display_bytes

    def draw(self, scale: int = 16):
        display_data = self.serialize_display()
        img = Image.fromarray(display_data)
        img = img.resize(
            (self.DISPLAY_RESOLUTION[0] * scale, self.DISPLAY_RESOLUTION[1] * scale),
            Image.Resampling.NEAREST,
        )
        img_data = np.array(img.convert("RGBA"))

        r_img = pr.Image(
            img_data,
            self.DISPLAY_RESOLUTION[0] * scale,
            self.DISPLAY_RESOLUTION[1] * scale,
            1,
            pr.PixelFormat.PIXELFORMAT_UNCOMPRESSED_R8G8B8A8,
        )
        tex = pr.load_texture_from_image(r_img)

        pr.begin_drawing()
        pr.clear_background(pr.RAYWHITE)
        pr.draw_texture(tex, 0, 0, pr.WHITE)
        pr.end_drawing()

        pr.unload_texture(tex)

    def _init_beep(self):
        sample_count = int(self.SAMPLE_RATE * self.BEEP_DURATION)
        samples = []

        for idx in range(sample_count):
            t = idx / self.SAMPLE_RATE

            samples.append(12000 if math.sin(2 * math.pi * self.BEEP_FREQUENCY * t) > 0 else -12000)
        
        sample_buf = pr.ffi.new("short[]", samples)
        wave = pr.Wave(sample_count, self.SAMPLE_RATE, 16, 1, sample_buf)
        self.BEEP_SOUND = pr.load_sound_from_wave(wave)

