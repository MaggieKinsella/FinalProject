from tkinter import *
import tkinter
from threading import Thread
from time import sleep
from random import randint
import board
from adafruit_ht16k33.segments import Seg7x4
from digitalio import DigitalInOut, Direction, Pull
from adafruit_matrixkeypad import Matrix_Keypad
import pygame

# constants
COUNTDOWN = 300
MAX_PASS_LEN = 11
STAR_CLEARS_PASS = True

class Lcd(Frame):
    def __init__(self, window):
        super().__init__(window, bg="black")
        window.after(500, window.attributes, '-fullscreen', 'True')
        self._timer = None
        self._button = None
        self.pacman_app = None
        self.wires_done = False
        self.toggles_done = False
        self.button_done = False
        self.matrix_keypad = None
        self.setup()

    def setup(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.pack(fill=BOTH, expand=True)

        self._ltimer = Label(self, bg="black", fg="white", font=("Courier New", 24), text="Time left: ")
        self._ltimer.grid(row=0, column=0, columnspan=2, sticky=W)

        self._lkeypad = Label(self, bg="black", fg="white", font=("Courier New", 24), text="Combination: ")
        self._lkeypad.grid(row=1, column=0, columnspan=2, sticky=W)

        self._lwires = Label(self, bg="black", fg="white", font=("Courier New", 24), text="Wires: ")
        self._lwires.grid(row=2, column=0, columnspan=2, sticky=W)

        self._lbutton = Label(self, bg="black", fg="white", font=("Courier New", 24), text="Button: ")
        self._lbutton.grid(row=3, column=0, columnspan=2, sticky=W)

        self._ltoggles = Label(self, bg="black", fg="white", font=("Courier New", 24), text="Toggles: ")
        self._ltoggles.grid(row=4, column=0, columnspan=2, sticky=W)

        self._lpacman = tkinter.Button(
            self, bg="green", fg="white", font=("Courier New", 24),
            text="Play Pac-Man", state=DISABLED, command=self.launch_pacman)
        self._lpacman.grid(row=6, column=0, columnspan=2, pady=20)

        self._lpause = tkinter.Button(
            self, bg="red", fg="white", font=("Courier New", 24),
            text="Pause", command=self.pause)
        self._lpause.grid(row=5, column=0, sticky=W, padx=25, pady=40)

        self._lquit = tkinter.Button(
            self, bg="red", fg="white", font=("Courier New", 24),
            text="Quit", command=self.quit)
        self._lquit.grid(row=5, column=1, sticky=W, padx=25, pady=40)

    def setTimer(self, timer):
        self._timer = timer

    def setButton(self, button):
        self._button = button

    def setMatrixKeypad(self, matrix_keypad):
        self.matrix_keypad = matrix_keypad

    def check_all_phases_complete(self):
        if self.wires_done and self.toggles_done and self.button_done:
            self._lpacman.config(state=NORMAL)

    def pause(self):
        self._timer.pause()

    def quit(self):
        self._timer._display.blink_rate = 0
        self._timer._display.fill(0)
        for pin in self._button._rgb:
            pin.value = True
        exit(0)

    def launch_pacman(self):
        if self.pacman_app is None:
            self.master.withdraw()
            window = Tk()
            window.attributes('-fullscreen', True)
            self.pacman_app = PacManApp(window, self.matrix_keypad)
            window.mainloop()

class PhaseThread(Thread):
    def __init__(self, name):
        super().__init__(name=name, daemon=True)
        self._running = False
        self._value = None

    def reset(self):
        self._value = None

class Timer(PhaseThread):
    def __init__(self, value, display, name="Timer"):
        super().__init__(name)
        self._value = value
        self._display = display
        self._paused = False

    def update(self):
        self._min = f"{self._value // 60}".zfill(2)
        self._sec = f"{self._value % 60}".zfill(2)

    def run(self):
        self._running = True
        while True:
            if not self._paused:
                self.update()
                self._display.print(str(self))
                sleep(1)
                if self._value == 0:
                    break
                self._value -= 1
            else:
                sleep(0.1)
        self._running = False

    def pause(self):
        self._paused = not self._paused
        self._display.blink_rate = 2 if self._paused else 0

    def __str__(self):
        return f"{self._min}:{self._sec}"

class Keypad(PhaseThread):
    def __init__(self, keypad, name="Keypad"):
        super().__init__(name)
        self._value = ""
        self._keypad = keypad

    def run(self):
        self._running = True
        while True:
            if self._keypad.pressed_keys:
                while self._keypad.pressed_keys:
                    try:
                        key = self._keypad.pressed_keys[0]
                    except:
                        key = ""
                    sleep(0.1)
                if key == "*" and STAR_CLEARS_PASS:
                    self._value = ""
                elif len(self._value) < MAX_PASS_LEN:
                    self._value += str(key)
            sleep(0.1)
        self._running = False

    def __str__(self):
        return self._value

class Wires(PhaseThread):
    def __init__(self, lcd, pins, name="Wires"):
        super().__init__(name)
        self.lcd = lcd
        self.correct_value = "11010"
        self._pins = pins
        self._value = ""

    def run(self):
        self._running = True
        while True:
            self._value = "".join(str(int(pin.value)) for pin in self._pins)
            self.lcd.after(0, lambda: self.lcd._lwires.config(text=f"Wires: {self._value}"))
            if self._value == self.correct_value:
                self.lcd.wires_done = True
                self.lcd._lwires.config(text="Wires Complete")
                self.lcd.check_all_phases_complete()
                break
            sleep(0.1)
        self._running = False

    def reset(self):
        self._running = False

class ogButton(PhaseThread):
    colors = ["R", "G", "B"]
    def __init__(self, lcd, state, rgb, name="Button"):
        super().__init__(name)
        self.lcd = lcd
        self._state = state
        self._rgb = rgb
        self._value = False

    def run(self):
        self._running = True
        rgb_index = rgb_counter = 0
        while True:
            # LED color
            self._rgb[0].value = (ogButton.colors[rgb_index] != "R")
            self._rgb[1].value = (ogButton.colors[rgb_index] != "G")
            self._rgb[2].value = (ogButton.colors[rgb_index] != "B")
            # button press check
            self._value = self._state.value
            if self._value and ogButton.colors[rgb_index] == "R":
                self.lcd.button_done = True
                self.lcd._lbutton.config(text="Button Complete!")
                self.lcd.check_all_phases_complete()
                break
            blink_threshold = 5 if (self.lcd.wires_done and self.lcd.toggles_done) else 10
            rgb_counter += 1
            if rgb_counter >= blink_threshold:
                rgb_index = (rgb_index + 1) % len(ogButton.colors)
                rgb_counter = 0
            sleep(0.1)
        self._running = False

    def __str__(self):
        return "Pressed" if self._value else "Released"

class Toggles(PhaseThread):
    def __init__(self, lcd, pins, name="Toggles"):
        super().__init__(name)
        self.lcd = lcd
        self.correct_value = "1101"
        self._pins = pins
        self._value = ""

    def run(self):
        self._running = True
        while True:
            self._value = "".join(str(int(pin.value)) for pin in self._pins)
            self.lcd.after(0, lambda: self.lcd._ltoggles.config(text=f"Toggles: {self._value}"))
            if self._value == self.correct_value:
                self.lcd.toggles_done = True
                self.lcd._ltoggles.config(text="Toggles Complete!")
                self.lcd.check_all_phases_complete()
                break
            sleep(0.1)
        self._running = False

    def __str__(self):
        return f"{self._value}/{int(self._value, 2)}"

class PacManApp(Frame):
    def __init__(self, window, matrix_keypad):
        super().__init__(window)
        self.window = window
        self.matrix_keypad = matrix_keypad
        self.window.title("PacMan")
        self.pack()
        self.canvas = Canvas(window, width=800, height=480, bg="black")
        self.canvas.pack()

        # Create Pac-Man
        self.pacman = self.canvas.create_arc(100, 320, 140, 360,
                                             start=45, extent=270,
                                             fill="yellow", outline="orange")
        # Create ghosts
        self.ghost  = self.canvas.create_oval(600, 410, 630, 440,
                                              fill="red", outline="pink")
        self.ghost2 = self.canvas.create_oval(10, 10, 40, 40,
                                              fill="cyan")

        # Obstacles
        self.obstacles = [
            self.canvas.create_rectangle(60, 60, 120, 75, outline="blue", width=5),
            self.canvas.create_rectangle(60, 60, 75, 180, outline="blue", width=5),
            self.canvas.create_rectangle(60, 375, 120, 390, outline="blue", width=5),
            self.canvas.create_rectangle(60, 375, 75, 255, outline="blue", width=5),
            self.canvas.create_rectangle(180, 0, 195, 75, outline="blue", width=5),
            self.canvas.create_rectangle(180, 375, 195, 450, outline="blue", width=5),
            self.canvas.create_rectangle(265, 60, 435, 75, outline="blue", width=5),
            self.canvas.create_rectangle(265, 375, 435, 390, outline="blue", width=5),
            self.canvas.create_rectangle(505, 0, 520, 75, outline="blue", width=5),
            self.canvas.create_rectangle(505, 375, 520, 450, outline="blue", width=5),
            self.canvas.create_rectangle(625, 60, 580, 75, outline="blue", width=5),
            self.canvas.create_rectangle(625, 60, 640, 180, outline="blue", width=5),
            self.canvas.create_rectangle(640, 390, 580, 375, outline="blue", width=5),
            self.canvas.create_rectangle(640, 390, 625, 255, outline="blue", width=5),
            self.canvas.create_rectangle(505, 165, 570, 180, outline="blue", width=5),
            self.canvas.create_rectangle(505, 255, 570, 270, outline="blue", width=5),
            self.canvas.create_rectangle(265, 165, 305, 180, outline="blue", width=5),
            self.canvas.create_rectangle(265, 165, 280, 270, outline="blue", width=5),
            self.canvas.create_rectangle(280, 255, 435, 270, outline="blue", width=5),
            self.canvas.create_rectangle(420, 180, 435, 270, outline="blue", width=5),
            self.canvas.create_rectangle(395, 165, 435, 180, outline="blue", width=5),
            self.canvas.create_rectangle(130, 165, 180, 180, outline="blue", width=5),
            self.canvas.create_rectangle(130, 255, 180, 270, outline="blue", width=5),
            # borders
            self.canvas.create_rectangle(0, 0, 0, 450, fill="black"),
            self.canvas.create_rectangle(0, 0, 700, 0, fill="black"),
            self.canvas.create_rectangle(700, 0, 700, 450, fill="black"),
            self.canvas.create_rectangle(0, 450, 800, 450, fill="black"),
        ]

        # Collectibles
        self.collectibles = [
            self.canvas.create_oval(25, 70, 35, 80, fill="pink"),
            self.canvas.create_oval(150, 210, 160, 220, fill="pink"),
            self.canvas.create_oval(350, 30, 360, 40, fill="pink"),
            self.canvas.create_oval(315, 322, 325, 332, fill="pink"),
            self.canvas.create_oval(600, 420, 610, 430, fill="pink"),
            self.canvas.create_oval(590, 100, 600, 110, fill="pink"),
            self.canvas.create_oval(370, 215, 380, 225, fill="pink"),
            self.canvas.create_oval(70, 415, 80, 425, fill="pink"),
        ]

        # Keyboard fallback
        self.window.bind("2", lambda e: self.move(0, -15))
        self.window.bind("4", lambda e: self.move(-15, 0))
        self.window.bind("6", lambda e: self.move(15, 0))
        self.window.bind("8", lambda e: self.move(0, 15))

        # Start polling hardware keypad
        self.check_keypad()

        # Start ghost loops
        self.chase_pacman()
        self.chase_pacman2()

    def check_keypad(self):
        keys = self.matrix_keypad.pressed_keys
        if keys:
            for key in keys:
                if key == 2:
                    self.move(0, -15)
                elif key == 8:
                    self.move(0, 15)
                elif key == 4:
                    self.move(-15, 0)
                elif key == 6:
                    self.move(15, 0)
        self.window.after(100, self.check_keypad)

    def move(self, dx, dy):
        # If game over or win, ignore
        if not getattr(self, "game_running", True):
            return

        coords = self.canvas.coords(self.pacman)
        new_coords = [coords[0]+dx, coords[1]+dy, coords[2]+dx, coords[3]+dy]

        # Collision with walls
        for obstacle in self.obstacles:
            if self.is_collision(new_coords, self.canvas.coords(obstacle)):
                return

        # Move Pac-Man
        self.canvas.move(self.pacman, dx, dy)

        # Collectibles
        for c in self.collectibles[:]:
            if self.is_collision(new_coords, self.canvas.coords(c)):
                self.canvas.delete(c)
                self.collectibles.remove(c)

        # Win?
        if not self.collectibles:
            self.game_running = False
            self.canvas.create_text(350, 225,
                text="You Win!", fill="white", font=("Arial", 90))

    def chase_pacman(self):
        if not getattr(self, "game_running", True):
            return
        self.move_ghost_toward_pacman(self.ghost)
        self.window.after(110, self.chase_pacman)

    def chase_pacman2(self):
        if not getattr(self, "game_running", True):
            return
        self.move_ghost_toward_pacman(self.ghost2)
        # Collision ghost2
        if self.is_collision(self.canvas.coords(self.ghost2),
                              self.canvas.coords(self.pacman)):
            self.game_running = False
            self.canvas.create_text(350, 225,
                text="Game Over", fill="white", font=("Arial", 90))
        self.window.after(100, self.chase_pacman2)

    def move_ghost_toward_pacman(self, ghost):
        ghost_coords = self.canvas.coords(ghost)
        pac_coords   = self.canvas.coords(self.pacman)
        ghost_x = (ghost_coords[0]+ghost_coords[2])/2
        ghost_y = (ghost_coords[1]+ghost_coords[3])/2
        pac_x   = (pac_coords[0]+pac_coords[2])/2
        pac_y   = (pac_coords[1]+pac_coords[3])/2

        if ghost == self.ghost:
            moves = []
            if ghost_x < pac_x: moves.append((5,0))
            elif ghost_x > pac_x: moves.append((-5,0))
            if ghost_y < pac_y: moves.append((0,5))
            elif ghost_y > pac_y: moves.append((0,-5))
        else:
            moves = []
            if ghost_y < pac_y: moves.append((0,5))
            elif ghost_y > pac_y: moves.append((0,-5))
            if ghost_x < pac_x: moves.append((5,0))
            elif ghost_x > pac_x: moves.append((-5,0))

        for dx,dy in moves:
            nc = [ghost_coords[0]+dx, ghost_coords[1]+dy,
                  ghost_coords[2]+dx, ghost_coords[3]+dy]
            collision = False
            for obs in self.obstacles:
                if self.is_collision(nc, self.canvas.coords(obs)):
                    collision = True
                    break
            if ghost == self.ghost2 and not collision:
                if self.is_collision(nc, self.canvas.coords(self.ghost)):
                    collision = True
            if not collision:
                self.canvas.move(ghost, dx, dy)
                break

        # ghost touches Pac-Man?
        if self.is_collision(self.canvas.coords(ghost),
                              self.canvas.coords(self.pacman)):
            self.game_running = False
            self.canvas.create_text(350, 225,
                text="Game Over", fill="white", font=("Arial", 90))

    def is_collision(self, a, b):
        return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

# ──────── MAIN ─────────────────────────────────────────────────────────────────

window = Tk()
gui = Lcd(window)

# Timer
i2c = board.I2C()
display = Seg7x4(i2c)
display.brightness = 0.5
timer = Timer(COUNTDOWN, display)
gui.setTimer(timer)

# Keypad hardware
keypad_cols = [DigitalInOut(i) for i in (board.D10, board.D9, board.D11)]
keypad_rows = [DigitalInOut(i) for i in (board.D5, board.D6, board.D13, board.D19)]
for pin in keypad_cols + keypad_rows:
    pin.direction = Direction.INPUT
    pin.pull = Pull.DOWN
keypad_keys = ((1,2,3),(4,5,6),(7,8,9),('*',0,'#'))
matrix_keypad = Matrix_Keypad(keypad_rows, keypad_cols, keypad_keys)
gui.setMatrixKeypad(matrix_keypad)
keypad = Keypad(matrix_keypad)

# Wires
wire_pins = [DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
for pin in wire_pins:
    pin.direction = Direction.INPUT
    pin.pull = Pull.DOWN
wires = Wires(gui, wire_pins)

# Button
button_in  = DigitalInOut(board.D4)
button_in.direction = Direction.INPUT
button_in.pull = Pull.DOWN
button_rgb = [DigitalInOut(i) for i in (board.D17, board.D27, board.D22)]
for pin in button_rgb:
    pin.direction = Direction.OUTPUT
    pin.value = True
button = ogButton(gui, button_in, button_rgb)
gui.setButton(button)

# Toggles
toggle_pins = [DigitalInOut(i) for i in (board.D12, board.D16, board.D20, board.D21)]
for pin in toggle_pins:
    pin.direction = Direction.INPUT
    pin.pull = Pull.DOWN
toggles = Toggles(gui, toggle_pins)

# Start all phases
timer.start()
keypad.start()
wires.start()
button.start()
toggles.start()

window.mainloop()
