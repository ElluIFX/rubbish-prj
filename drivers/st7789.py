import time

import cv2
import mraa
import numpy as np
import spidev


class _CMD:
    # refer to ST7789V datasheet for details
    NOP = 0x00
    SWRESET = 0x01
    RDDID = 0x04
    RDDST = 0x09

    SLPIN = 0x10
    SLPOUT = 0x11
    PTLON = 0x12
    NORON = 0x13

    INVOFF = 0x20
    INVON = 0x21
    DISPOFF = 0x28
    DISPON = 0x29

    CASET = 0x2A
    RASET = 0x2B
    RAMWR = 0x2C
    RAMRD = 0x2E

    PTLAR = 0x30
    MADCTL = 0x36
    COLMOD = 0x3A

    RAMCTRL = 0xB0
    FRMCTR1 = 0xB1
    FRMCTR2 = 0xB2
    FRMCTR3 = 0xB3
    INVCTR = 0xB4
    DISSET5 = 0xB6

    GCTRL = 0xB7
    GTADJ = 0xB8
    VCOMS = 0xBB

    LCMCTRL = 0xC0
    IDSET = 0xC1
    VDVVRHEN = 0xC2
    VRHS = 0xC3
    VDVS = 0xC4
    VMCTR1 = 0xC5
    FRCTRL2 = 0xC6
    CABCCTRL = 0xC7

    RDID1 = 0xDA
    RDID2 = 0xDB
    RDID3 = 0xDC
    RDID4 = 0xDD

    GMCTRP1 = 0xE0
    GMCTRN1 = 0xE1

    PWCTR6 = 0xFC

    MADCTL_BGR = 0x08
    MADCTL_MV = 0x20
    MADCTL_MX = 0x40
    MADCTL_MY = 0x80


class ST7789(object):
    """Representation of an ST7789 TFT LCD."""

    def __init__(
        self,
        spi_channel=1,
        spi_port=0,
        pin_dc=13,
        pin_backlight=18,
        pin_rst=16,
        width=320,
        height=172,
        invert=True,
        bgr=False,
        fps=60,
        rotation=90,
        spi_speed_hz=100000000,
        bk_pwm_control=True,
        bk_pwm_port=(4, 0),
        offset_left=0,
        offset_top=34,
    ):
        """
        Create an instance of the ST7789V3 display using SPI communication.

        Must provide the GPIO pin number for the D/C pin and the SPI driver.

        Can optionally provide the GPIO pin number for the reset pin as the rst parameter.

        :param spi_channel: SPI channel number
        :param spi_port: SPI port number
        :param pin_dc: GPIO pin number for the D/C pin
        :param pin_backlight: Pin for controlling backlight
        :param pin_rst: Reset pin for ST7789
        :param width: Width of display connected to ST7789
        :param height: Height of display connected to ST7789
        :param rotation: Rotation of display connected to ST7789
        :param invert: Invert display
        :param bgr: Use BGR color order
        :param fps: Frames per second
        :param spi_speed_hz: SPI speed (in Hz)
        :param bk_pwm_control: Use Software PWM to control backlight
        :param bk_pwm_port: Backlight PWM (chipid,pin)
        """

        self._spi = spidev.SpiDev(spi_channel, spi_port)
        self._spi.mode = 0b00
        self._spi.lsbfirst = False
        self._spi.max_speed_hz = spi_speed_hz
        # self._spi = mraa.Spi(spi_channel)
        # self._spi.frequency(spi_speed_hz)
        # self._spi.mode(0)

        self._pin_dc = mraa.Gpio(pin_dc)
        self._pin_rst = mraa.Gpio(pin_rst)
        self._pin_dc.dir(mraa.DIR_OUT)
        self._pin_rst.dir(mraa.DIR_OUT)
        self._pin_dc.write(1)  # DC keeps in high
        self._pin_rst.write(1)  # RST keeps in high

        self._bk_pwm_control = bk_pwm_control
        if self._bk_pwm_control:
            self._bk_pwm = mraa.Pwm(chipid=bk_pwm_port[0], pin=bk_pwm_port[1])
            set_hz = 500
            self._bk_pwm.period_us(int(1000000 / set_hz))
            self._bk_pwm.enable(True)
        else:
            self._pin_bk = mraa.Gpio(pin_backlight)
            self._pin_bk.dir(mraa.DIR_OUT)

        self._width = width
        self._height = height
        self._invert = invert
        self._bgr = bgr
        self._fps = fps
        self._rotation = rotation

        self._offset_left = offset_left
        self._offset_top = offset_top

        self._last_window = (self._width, self._height)

        self.set_brightness(0)
        self._reset()
        self._init()
        self.clear()
        self.set_brightness(1)

    def _send(self, data):
        self._spi.writebytes2(data)
        # data = bytearray(data)
        # for i in range(0, len(data), 4096):
        #     self._spi.write(data[i : i + 4096])

    def set_brightness(self, brightness: float):
        """
        Set the brightness of the backlight.
        Only works if enabled software PWM control,
        otherwise can only control on or off.
        """
        if self._bk_pwm_control:
            brightness = max(0, min(brightness, 1.0))
            self._bk_pwm.write(brightness)
        else:
            self._pin_dc.write(int(brightness > 0))

    def _command(self, data):
        self._pin_dc.write(0)
        self._send([data & 0xFF])
        self._pin_dc.write(1)

    def _data(self, data):
        self._send([data & 0xFF])

    def _reset(self):
        if self._pin_rst is not None:
            self._pin_rst.write(1)
            time.sleep(0.1)
            self._pin_rst.write(0)
            time.sleep(0.1)
            self._pin_rst.write(1)
            time.sleep(0.1)

    def _init(self):
        # Initialize the display.

        self._command(_CMD.SWRESET)  # Software reset
        time.sleep(0.15)

        self._set_param(self._bgr, self._rotation, self._invert)

        self._command(_CMD.FRMCTR2)  # Frame rate ctrl - idle mode
        self._data(0x0C)
        self._data(0x0C)
        self._data(0x00)
        self._data(0x33)
        self._data(0x33)

        self._command(_CMD.COLMOD)
        self._data(0x05)

        self._command(_CMD.GCTRL)
        self._data(0x14)

        self._command(_CMD.VCOMS)
        self._data(0x37)

        self._command(_CMD.LCMCTRL)  # Power control
        self._data(0x2C)

        self._command(_CMD.VDVVRHEN)  # Power control
        self._data(0x01)

        self._command(_CMD.VRHS)  # Power control
        self._data(0x13)

        self._command(_CMD.VDVS)  # Power control
        self._data(0x20)

        self._command(0xD0)
        self._data(0xA4)
        self._data(0xA1)

        self._command(_CMD.FRCTRL2)  # FPS control
        self._data(0x0F)  # 60Hz

        self._command(_CMD.GMCTRP1)  # Set Gamma
        self._data(0xD0)
        self._data(0x04)
        self._data(0x0D)
        self._data(0x11)
        self._data(0x13)
        self._data(0x2B)
        self._data(0x3F)
        self._data(0x54)
        self._data(0x4C)
        self._data(0x18)
        self._data(0x0D)
        self._data(0x0B)
        self._data(0x1F)
        self._data(0x23)

        self._command(_CMD.GMCTRN1)  # Set Gamma
        self._data(0xD0)
        self._data(0x04)
        self._data(0x0C)
        self._data(0x11)
        self._data(0x13)
        self._data(0x2C)
        self._data(0x3F)
        self._data(0x44)
        self._data(0x51)
        self._data(0x2F)
        self._data(0x1F)
        self._data(0x1F)
        self._data(0x20)
        self._data(0x23)

        self._command(_CMD.RAMCTRL)  # Set RAM Control
        self._data(0x00)
        self._data(0xC8)  # little endian and 65K RGB565

        self._command(_CMD.SLPOUT)

        self._command(_CMD.DISPON)  # Display on
        time.sleep(0.1)
        self.set_window(0, 0)

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        """
        Partial refresh for the given window.
        Affects will be kept until the next setting be set.
        """
        if x1 is None:
            x1 = self._width - 1
        else:
            x1 -= 1

        if y1 is None:
            y1 = self._height - 1
        else:
            y1 -= 1

        self._last_window = (x1 - x0 + 1, y1 - y0 + 1)

        y0 += self._offset_top
        y1 += self._offset_top

        x0 += self._offset_left
        x1 += self._offset_left

        self._command(_CMD.CASET)  # Column addr set
        self._data(x0 >> 8)
        self._data(x0)  # XSTART
        self._data(x1 >> 8)
        self._data(x1)  # XEND
        self._command(_CMD.RASET)  # Row addr set
        self._data(y0 >> 8)
        self._data(y0)  # YSTART
        self._data(y1 >> 8)
        self._data(y1)  # YEND
        self._command(_CMD.RAMWR)  # write to RAM

    def _set_param(self, bgr, rotation, invert):
        data = 0x02
        # data |= 0x04  # Latch Data Order
        data |= 0x10  # Line Address Order
        if bgr:
            data |= _CMD.MADCTL_BGR
        if rotation == 90:
            data |= _CMD.MADCTL_MV | _CMD.MADCTL_MY
        elif rotation == 180:
            data |= _CMD.MADCTL_MX | _CMD.MADCTL_MY
        elif rotation == 270:
            data |= _CMD.MADCTL_MX | _CMD.MADCTL_MV
        elif rotation == 0:
            pass
        else:
            raise ValueError("Invalid rotation value: %s" % self._rotation)
        self._command(_CMD.MADCTL)
        self._data(data & 0xFF)
        if invert:
            self._command(_CMD.INVON)  # Invert display
        else:
            self._command(_CMD.INVOFF)  # Don't invert display

    def display(self, image):
        """
        Write the provided image to the hardware.
        image: OpenCV image in BGR format and same as screen resolution
        """
        # data = image.astype("uint16")
        # red = (data[..., [2]] & 0xF8) << 8
        # green = (data[..., [1]] & 0xFC) << 3
        # blue = (data[..., [0]] & 0xF8) >> 3
        # data = red | green | blue
        data = cv2.cvtColor(image, cv2.COLOR_BGR2BGR565)  # It actually trans to RGB565
        self._send(np.array(data).astype(int).flatten().tolist())

    def fit_display(self, image, keep_ratio=True, no_enlarge=True):
        """
        Write the provided image to the hardware.
        image: OpenCV image in BGR format in any resolution
        """
        image = self._fit_image(image, keep_ratio, no_enlarge)
        self._fit_window(image)
        self.display(image)

    def _fit_image(self, image, keep_ratio=True, no_enlarge=True):
        """
        Change image resolution to fit screen resolution
        """
        target_size = (self._width, self._height)
        image_size = (image.shape[1], image.shape[0])
        if target_size == image_size:
            return image
        if not keep_ratio:
            image = cv2.resize(image, target_size)
            return image
        x_ratio = target_size[0] / image_size[0]
        y_ratio = target_size[1] / image_size[1]
        min_ratio = min(x_ratio, y_ratio)
        if min_ratio >= 1 and no_enlarge:
            pass
        elif min_ratio >= 1:
            image = cv2.resize(image, dsize=(0, 0), fx=min_ratio, fy=min_ratio)
        else:
            image = cv2.resize(image, dsize=(0, 0), fx=min_ratio, fy=min_ratio)
        return image

    def _fit_window(self, image):
        target_size = (self._width, self._height)
        image_size = (image.shape[1], image.shape[0])
        assert (
            image_size[0] <= target_size[0] and image_size[1] <= target_size[1]
        ), "Image is too large"
        dx = target_size[0] - image_size[0]
        dy = target_size[1] - image_size[1]
        x0 = dx // 2
        y0 = dy // 2
        x1 = x0 + image_size[0]
        y1 = y0 + image_size[1]
        self.set_window(x0, y0, x1, y1)

    def clear(self):
        """
        Clear all frame buffer
        """
        self.set_window(0, 0)
        self._send(
            np.zeros((self._width, self._height, 2)).astype(int).flatten().tolist()
        )

    def clear_window(self):
        """
        Clear the current window
        """
        self._send(
            np.zeros((self._last_window[0], self._last_window[1], 2))
            .astype(int)
            .flatten()
            .tolist()
        )

    def turn_off(self):
        """
        Turn off the display
        """
        self.clear()
        self._command(_CMD.DISPOFF)
        self.set_brightness(0)


if __name__ == "__main__":

    screen = ST7789()
    print("screen initialized")

    class fps_counter:
        def __init__(self, max_sample=40) -> None:
            self.t = time.time()
            self.max_sample = max_sample
            self.t_list = []

        def update(self) -> None:
            self.t_list.append(time.time() - self.t)
            self.t = time.time()
            if len(self.t_list) > self.max_sample:
                self.t_list.pop(0)

        def get(self) -> float:
            length = len(self.t_list)
            sum_t = sum(self.t_list)
            if length == 0:
                return 0.0
            else:
                return length / sum_t

    def circle_test():
        width = screen._width
        height = screen._height
        test_img = np.zeros((height, width, 3), dtype=np.uint8)
        fps = fps_counter()
        screen.display(test_img)
        start_time = time.time()
        circle_num = 3
        x = [width // 2 for _ in range(circle_num)]
        y = [height // 2 for _ in range(circle_num)]
        add_x = [1, 2, -2, -3]
        add_y = [1, -3, 1, -4]
        r = [60, 30, 20, 10]
        colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 0, 255),
            (255, 255, 0),
            (0, 255, 255),
        ]
        bright = 1
        add = False
        while True:
            img = test_img.copy()
            for i in range(circle_num):
                x[i] += add_x[i]
                y[i] += add_y[i]
                if x[i] >= width - r[i] or x[i] <= r[i]:
                    add_x[i] = -add_x[i]
                if y[i] >= height - r[i] or y[i] <= r[i]:
                    add_y[i] = -add_y[i]
                cv2.circle(img, (int(x[i]), int(y[i])), r[i], colors[i], 2)
            cv2.putText(
                img,
                f"FPS: {fps.get():.2f} Ts: {time.time() - start_time:.0f}",
                (30, 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 0),
                1,
            )
            t0 = time.time()
            screen.display(img)
            dt = time.time() - t0
            print(f"FPS: {fps.get():.2f} dt: {dt:.3f}")
            fps.update()
            bright *= 0.9 if not add else 1.1
            if bright < 0.1 or bright > 1:
                bright = max(0.1, min(1, bright))
                add = not add
            #screen.set_brightness(bright)

    try:
        circle_test()
    except KeyboardInterrupt:
        screen.turn_off()
