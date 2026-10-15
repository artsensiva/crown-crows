"""Camera light and status light on the RGB module (or a single white light)."""

# Light outputs, BCM numbering. "rgb": a common-anode RGB module, three
# channels switched to ground by the GPIO (active-low). "white": one white
# light switched by a logic-level N-MOSFET on GPIO27 (active-high, with a
# gate pull-down so it stays off before software runs). See docs/LIGHTING.md.
LIGHTS = {
    "rgb": ((27, 22, 23), False),
    "white": ((27,), True),
}


def open_lights(stack, factory, kind):
    from gpiozero import LED

    pins, active_high = LIGHTS[kind]
    channels = []
    for pin in pins:
        channel = stack.enter_context(LED(pin, active_high=active_high, initial_value=False, pin_factory=factory))
        stack.callback(channel.off)
        channels.append(channel)
    return Lighting(channels)


class StatusLight:
    # Status signals on the RGB module (channels R, G, B = GPIO27, 22, 23),
    # which is also the camera light: signals only while starting, three
    # green flashes when ready, then dark during normal operation; red only
    # for problems. A background thread draws the pattern and sleeps until the
    # next change; on() and off() take over all channels as white camera
    # light and have priority.
    PATTERNS = {
        # mode: (colour (R, G, B), blink seconds, period seconds)
        "off": None,
        "starting": ((0, 0, 1), None, None),        # blue, steady
        "warmup": ((0, 0, 1), .1, 1.0),             # blue blink every second
        "degraded": ((1, 0, 0), .05, 5.0),          # red blip every 5 s: running without servo
        "error": ((1, 0, 0), .1, .5),               # red blinking: stopped by an error
    }

    def __init__(self, channels):
        import threading

        self.channels = channels
        self.lock = threading.Lock()
        self.mode = "off"
        self.flash_colour = None
        self.flash_until = 0.0
        self.camera = False
        self.changed = threading.Event()
        self.stopped = False
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _show(self, colour):
        for channel, on in zip(self.channels, colour):
            channel.value = bool(on)

    def _state(self, now):
        # Returns the colour to show now and the seconds until it changes, so
        # the thread sleeps between changes instead of waking constantly.
        if self.camera:
            return None, 3600
        if self.flash_colour and now < self.flash_until:
            return self.flash_colour, self.flash_until - now
        pattern = self.PATTERNS.get(self.mode)
        if pattern is None:
            return (0, 0, 0), 3600
        colour, blink, period = pattern
        if blink is None:
            return colour, 3600
        phase = now % period
        if phase < blink:
            return colour, blink - phase
        return (0, 0, 0), period - phase

    def _run(self):
        import time

        while True:
            with self.lock:
                if self.stopped:
                    return
                colour, wait = self._state(time.monotonic())
                if colour is not None:
                    self._show(colour)
            self.changed.wait(min(wait, 60))
            self.changed.clear()

    def set_mode(self, mode):
        with self.lock:
            self.mode = mode
        self.changed.set()

    def ready(self):
        # Three green flashes, then dark.
        import time

        for _ in range(3):
            self.flash((0, 1, 0), .25)
            time.sleep(.5)
        self.set_mode("off")

    def flash(self, colour, seconds):
        import time

        with self.lock:
            self.flash_colour = colour
            self.flash_until = time.monotonic() + seconds
        self.changed.set()

    def on(self):
        with self.lock:
            self.camera = True
            self._show((1, 1, 1))
        self.changed.set()

    def off(self):
        with self.lock:
            self.camera = False
            self._show((0, 0, 0))
        self.changed.set()

    def close(self):
        with self.lock:
            self.stopped = True
        self.changed.set()
        self.thread.join(1)
        with self.lock:
            self._show((0, 0, 0))


class Lighting:
    def __init__(self, channels):
        self.channels = channels

    def on(self):
        for channel in self.channels:
            channel.on()

    def off(self):
        errors = []
        for channel in self.channels:
            try:
                channel.off()
            except Exception as error:
                errors.append(error)
        if errors:
            raise RuntimeError("Unable to switch off every light channel") from errors[0]
