import os
import pygame
from tkinter import *
import tkinter
from threading import Thread
from time import sleep
from random import randint
import board
from adafruit_ht16k33.segments import Seg7x4
from digitalio import DigitalInOut, Direction, Pull
from adafruit_matrixkeypad import Matrix_Keypad

# Initialize pygame mixer for audio
pygame.mixer.init()
BASE_DIR = os.path.dirname(__file__)
SOUND_PATH = os.path.join(BASE_DIR, 'assets', 'sounds', 'pacman_siren.mp3')

# constants
COUNTDOWN       = 300   # initial countdown timer value (seconds)
MAX_PASS_LEN    = 11    # maximum passphrase length
STAR_CLEARS_PASS = True # does '*' clear the passphrase?

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
            text="Play Pac-Man", state=DISABLED, command=self.launch_pacman
        )
        self._lpacman.grid(row=6, column=0, columnspan=2, pady=20)

        self._lpause = tkinter.Button(
            self, bg="red", fg="white", font=("Courier New", 24),
            text="Pause", command=self.pause
        )
        self._lpause.grid(row=5, column=0, sticky=W, padx=25, pady=40)

        self._lquit = tkinter.Button(
            self, bg="red", fg="white", font=("Courier New", 24),
            text="Quit", command=self.quit
        )
        self._lquit.grid(row=5, column=1, sticky=W, padx=25, pady=40)

    def check_all_phases_complete(self):
        if self.wires_done and self.toggles_done and self.button_done:
            print("All phases complete. Enabling Pac-Man button.")
            self._lpacman.config(state=NORMAL)

    def launch_pacman(self):
        if self.pacman_app is None:
            self.master.withdraw()
            new_window = Toplevel()
            new_window.attributes('fullscreen', True)
            self.pacman_app = PacManApp(new_window)

    def setTimer(self, timer):
        self._timer = timer

    def setButton(self, button):
        self._button = button

    def pause(self):
        self._timer.pause()

    def quit(self):
        self._timer._display.blink_rate = 0
        self._timer._display.fill(0)
        for pin in self._button._rgb:
            pin.value = True
        exit(0)


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
        self._display.blink_rate = (2 if self._paused else 0)

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
        self._running = False

    def run(self):
        self._running = True
        while True:
            self._value = "".join(str(int(pin.value)) for pin in self._pins)
            self.lcd.after(0, self.lcd._lwires.config, {'text': f"Wires: {self._value}"})
            if self._value == self.correct_value:
                print("Correct wire order! Phase complete.")
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
        self._value = False
        self._state = state
        self._rgb = rgb

    def run(self):
        self._running = True
        rgb_index = 0
        rgb_counter = 0

        while True:
            self._rgb[0].value = (ogButton.colors[rgb_index] != "R")
            self._rgb[1].value = (ogButton.colors[rgb_index] != "G")
            self._rgb[2].value = (ogButton.colors[rgb_index] != "B")

            self._value = self._state.value
            if self._value and ogButton.colors[rgb_index] == "R":
                print("Button pressed while red — Phase complete")
                self.lcd.button_done = True
                self.lcd._lbutton.config(text="Button Complete!")
                self.lcd.check_all_phases_complete()
                break

            if self.lcd.wires_done and self.lcd.toggles_done:
                blink_threshold = 3
            else:
                blink_threshold = 10

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
        self._running = True

    def run(self):
        self._running = True
        while True:
            self._value = "".join(str(int(pin.value)) for pin in self._pins)
            self.lcd.after(0, self.lcd._ltoggles.config, {'text': f"Toggles: {self._value}"})
            if self._value == self.correct_value:
                print("Toggles Correct!")
                self.lcd.toggles_done = True
                self.lcd._ltoggles.config(text="Toggles Complete!")
                self.lcd.check_all_phases_complete()
                break
            sleep(0.1)
        self._running = False

    def __str__(self):
        return f"{self._value}/{int(self._value, 2)}"


class PacManApp(Frame):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.window.title("PacMan")

        # start background music
        pygame.mixer.music.load(SOUND_PATH)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.pack()
        self.canvas = Canvas(window, width=800, height=480, bg="black")
        self.canvas.pack()

        # Create Pac-Man & ghosts
        self.pacman = self.canvas.create_arc(100,320,140,360,start=45,extent=270,fill="yellow",outline="orange")
        self.ghost  = self.canvas.create_oval(600,410,630,440, fill="red", outline="pink")
        self.ghost2 = self.canvas.create_oval(10,10,40,40, fill="cyan")

        self.game_running = True

        # (Insert your obstacles & collectibles code here)

        # Bind keys (numeric keypad)
        self.window.bind("2", lambda e: self.move(0,-15))
        self.window.bind("4", lambda e: self.move(-15,0))
        self.window.bind("6", lambda e: self.move(15,0))
        self.window.bind("8", lambda e: self.move(0,15))

        # Start ghost movement loops
        self.chase_pacman()
        self.chase_pacman2()

        # Ensure music stops on window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        pygame.mixer.music.stop()
        self.window.destroy()

    def game_over(self, text):
        pygame.mixer.music.stop()
        self.canvas.create_text(350,225, text=text, fill="white", font=("Arial",90))
        self.game_running = False

    # Replace your win/lose logic to call self.game_over("You Win!") or self.game_over("Game Over")
    # … (move, chase_pacman, chase_pacman2, move_ghost_toward_pacman, is_collision) …

# ---- MAIN ----
window = Tk()
gui = Lcd(window)

# 7-segment timer
i2c = board.I2C()
display = Seg7x4(i2c)
display.brightness = 0.5
timer = Timer(COUNTDOWN, display)
gui.setTimer(timer)

# Keypad
keypad_cols = [DigitalInOut(i) for i in (board.D10,board.D9,board.D11)]
keypad_rows = [DigitalInOut(i) for i in (board.D5, board.D6, board.D13, board.D19)]
matrix_keypad = Matrix_Keypad(keypad_rows, keypad_cols, ((1,2,3),(4,5,6),(7,8,9),("*",0,"#")))
keypad = Keypad(matrix_keypad)

# Wires
wire_pins = [DigitalInOut(i) for i in (board.D14,board.D15,board.D18,board.D23,board.D24)]
for pin in wire_pins:
    pin.direction = Direction.INPUT
    pin.pull = Pull.DOWN
wires = Wires(gui, wire_pins)

# Button
button_input = DigitalInOut(board.D4)
button_input.direction = Direction.INPUT
button_input.pull = Pull.DOWN
button_RGB = [DigitalInOut(i) for i in (board.D17,board.D27,board.D22)]
for pin in button_RGB:
    pin.direction = Direction.OUTPUT
    pin.value = True
button = ogButton(gui, button_input, button_RGB)
gui.setButton(button)

# Toggles
toggle_pins = [DigitalInOut(i) for i in (board.D12,board.D16,board.D20,board.D21)]
for pin in toggle_pins:
    pin.direction = Direction.INPUT
    pin.pull = Pull.DOWN
toggles = Toggles(gui, toggle_pins)

# Start all phase threads
timer.start()
keypad.start()
wires.start()
button.start()
toggles.start()

window.mainloop()
