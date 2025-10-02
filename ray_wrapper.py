import numpy as np
import pyray as pr
from PIL import Image

from chip8 import CHIP8


class CHIP8Ray(CHIP8):
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

    def draw_static(self, scale: int = 16):
        display_data = self.serialize_display()

        img = Image.fromarray(display_data)
        img = img.resize(
            (self.DISPLAY_RESOLUTION[0] * scale, self.DISPLAY_RESOLUTION[1] * scale),
            Image.Resampling.NEAREST,
        )
        img_data = np.array(img.convert("RGBA"))

        pr.init_window(
            self.DISPLAY_RESOLUTION[0] * scale,
            self.DISPLAY_RESOLUTION[1] * scale,
            "CHIP8 Emulator",
        )

        r_img = pr.Image(
            img_data,
            self.DISPLAY_RESOLUTION[0] * scale,
            self.DISPLAY_RESOLUTION[1] * scale,
            1,
            pr.PixelFormat.PIXELFORMAT_UNCOMPRESSED_R8G8B8A8,
        )
        tex = pr.load_texture_from_image(r_img)

        pr.unload_image(r_img)

        while not pr.window_should_close():
            pr.begin_drawing()
            pr.clear_background(pr.RAYWHITE)
            pr.draw_texture(tex, 0, 0, pr.WHITE)
            pr.end_drawing()

        pr.close_window()
