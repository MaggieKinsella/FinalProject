help me fix the keypad phase so that 2 is up, 4 is left, 6 is right and 8 is down for the pacman game for pacman to move:
from tkinter import \*
import tkinter
from threading import Thread
from time import sleep
from random import randint
import board
from adafruit\_ht16k33.segments import Seg7x4
from digitalio import DigitalInOut, Direction, Pull
from adafruit\_matrixkeypad import Matrix\_Keypad

# from bomb\_GUI\_PacMan import PacManApp  # Import your PacManApp here

# constants

# the bomb's initial countdown timer value (seconds)

COUNTDOWN = 300

# the maximum passphrase length

MAX\_PASS\_LEN = 11

# does the asterisk (\*) clear the passphrase?

STAR\_CLEARS\_PASS = True

# the LCD display "GUI"

class Lcd(Frame):
def **init**(self, window):
super().**init**(window, bg="black")
window\.after(500, window\.attributes, '-fullscreen', 'True')
self.\_timer = None
self.\_button = None
self.pacman\_app = None
self.wires\_done = False
self.toggles\_done = False
self.button\_done = False
self.setup()

```
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

    self._lpacman = tkinter.Button(self, bg="green", fg="white", font=("Courier New", 24),
                                   text="Play Pac-Man", state=DISABLED, command=self.launch_pacman)
    self._lpacman.grid(row=6, column=0, columnspan=2, pady=20)

    self._lpause = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 24), text="Pause", command=self.pause)
    self._lpause.grid(row=5, column=0, sticky=W, padx=25, pady=40)

    self._lquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 24), text="Quit", command=self.quit)
    self._lquit.grid(row=5, column=1, sticky=W, padx=25, pady=40)

def check_all_phases_complete(self):
```

# print("Phase completion status:", self.wires\_done, self.toggles\_done, self.button\_done)

```
    if self.wires_done and self.toggles_done and self.button_done:
```

# print("All phases complete. Enabling Pac-Man button.")

```
        self._lpacman.config(state=NORMAL)

def launch_pacman(self):
    if self.pacman_app is None:
        self.master.withdraw()
        window = Tk()
        window.attributes('-fullscreen', True)
        self.pacman_app = PacManApp(window)
        window.mainloop()

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
```

# template (superclass) for various bomb components/phases

class PhaseThread(Thread):
def **init**(self, name):
super().**init**(name=name, daemon=True)
\# initially, the phase thread isn't running
self.\_running = False
\# phases can have values (e.g., a pushbutton can be True or False, a keypad passphrase can be some string, etc)
self.\_value = None

```
# resets the phase's value
def reset(self):
    self._value = None
```

# the timer phase

class Timer(PhaseThread):
def **init**(self, value, display, name="Timer"):
super().**init**(name)
self.\_value = value
\# the LCD display object
self.\_display = display
\# initially, the timer isn't paused
self.\_paused = False

```
# updates the timer
def update(self):
    self._min = f"{self._value // 60}".zfill(2)
    self._sec = f"{self._value % 60}".zfill(2)

# runs the thread
def run(self):
    self._running = True
    while (True):
        if (not self._paused):
            # update the timer and display its value on the 7-segment display
            self.update()
            self._display.print(str(self))
            # wait 1s and continue
            sleep(1)
            # stop if the timer has expired
            if (self._value == 0):
                break
            # otherwise, 1s has elapsed
            self._value -= 1
        else:
            sleep(0.1)
    self._running = False

# pauses and unpauses the timer
def pause(self):
    self._paused = not self._paused
    # blink the 7-segment display when paused
    self._display.blink_rate = (2 if self._paused else 0)

def __str__(self):
    return f"{self._min}:{self._sec}"
```

# the keypad phase

class Keypad(PhaseThread):
def **init**(self, keypad, name="Keypad"):
super().**init**(name)
self.\_value = ""
\# the keypad pins
self.\_keypad = keypad

```
# runs the thread
def run(self):
    self._running = True
    while (True):
        # process keys when keypad key(s) are pressed
        if (self._keypad.pressed_keys):
            # debounce
            while (self._keypad.pressed_keys):
                try:
                    key = self._keypad.pressed_keys[0]
                except:
                    key = ""
                sleep(0.1)
            # do we have an asterisk (*) (and it resets the passphrase)?
            if (key == "*" and STAR_CLEARS_PASS):
                self._value = ""
            # we haven't yet reached the max pass length (otherwise, we just ignore the keypress)
            elif (len(self._value) < MAX_PASS_LEN):
                # log the key
                self._value += str(key)
        sleep(0.1)
    self._running = False

def __str__(self):
    return self._value
```

# the jumper wires phase

class Wires(PhaseThread):
def **init**(self, lcd, pins, name="Wires"):
super().**init**(name)
self.lcd = lcd
self.correct\_value = "11010" #set the correct wire order
self.\_pins = pins
self.\_value = ""
self.\_running = False

```
def run(self):
    self._running = True
    while (True):
        #Read each wire and build a binary string
        self._value = "".join([str(int(pin.value)) for pin in self._pins])
        self.lcd.after(0, lambda: self.lcd._lwires.config(text=f"Wires: {self._value}"))
        
        if self._value == self.correct_value:
            print("Correct wire order! Phase complete.")
            self.lcd.wires_done = True
            self.lcd._lwires.config(text="Wires Complete")
            self.lcd.check_all_phases_complete()
            self._running = False
    
        sleep(0.1)

def reset(self):
    self._running = False
```

# the pushbutton phase

class ogButton(PhaseThread):
colors = \[ "R", "G", "B" ]  # the button's possible colors

```
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
        # 1) Set the LED pins according to current color
        self._rgb[0].value = (ogButton.colors[rgb_index] != "R")
        self._rgb[1].value = (ogButton.colors[rgb_index] != "G")
        self._rgb[2].value = (ogButton.colors[rgb_index] != "B")

        # 2) Check for a valid press *and* correct timing (only completes on red)
        self._value = self._state.value
        if self._value and ogButton.colors[rgb_index] == "R":
```

# print("Button pressed while red — Phase complete")

```
            self.lcd.button_done = True
            self.lcd._lbutton.config(text="Button Complete!")
            self.lcd.check_all_phases_complete()
            break

        # 3) Determine blink speed:
        #    - before wires+toggles: 1s per color (threshold=10 loops @0.1s)
        #    - after wires+toggles: 0.5s per color    (threshold=5 loops @0.1s)
        if self.lcd.wires_done and self.lcd.toggles_done:
            blink_threshold = 5
        else:
            blink_threshold = 10

        # 4) Advance the color when we've hit the threshold
        rgb_counter += 1
        if rgb_counter >= blink_threshold:
            rgb_index = (rgb_index + 1) % len(ogButton.colors)
            rgb_counter = 0

        sleep(0.1)

    self._running = False

def __str__(self):
    return "Pressed" if self._value else "Released"
```

# the toggle switches phase

class Toggles(PhaseThread):
def **init**(self, lcd, pins, name="Toggles"):
super().**init**(name)
self.lcd = lcd
self.correct\_value = "1101"
\# the toggle switch pins
self.\_pins = pins
self.\_value = ""
self.\_running = True

```
# runs the thread
def run(self):
    self._running = True
    while (True):
        # get the toggle switch values (0->False, 1->True)
        self._value = "".join([str(int(pin.value)) for pin in self._pins])
        self.lcd.after(0, lambda: self.lcd._ltoggles.config(text=f"Toggles: {self._value}"))
        
        if self._value == self.correct_value:
```

# print("Toggles Correct!")

```
            self.lcd.toggles_done = True
            self.lcd._ltoggles.config(text="Toggles Complete!")
            self.lcd.check_all_phases_complete()
            self._running = False
        sleep(0.1)
    self._running = False

def __str__(self):
    return f"{self._value}/{int(self._value, 2)}"

def reset(self):
    self._running = False
    
```

from tkinter import \*

class PacManApp(Frame):
def **init**(self, window):
super().**init**(window)
self.window = window
self.window\.title("PacMan")
self.pack()

```
    self.canvas = Canvas(window, width=800, height=480, bg="black")
    self.canvas.pack()

    # Create Pac-Man
    self.pacman = self.canvas.create_arc(100, 320, 140, 360, start=45, extent=270, fill="yellow", outline="orange")\
    
    # Create ghost (red)
    self.ghost = self.canvas.create_oval(600, 410, 630, 440, fill="red", outline="pink")
    # Create second ghost (cyan)
    self.ghost2 = self.canvas.create_oval(10, 10, 40, 40, fill="cyan")

    self.game_running = True

    # Create obstacles (list of canvas rectangle IDs)
    self.obstacles = [
        # (x1, y1),(x2, y2)
        # 1st obsticle (top left)
        self.canvas.create_rectangle(60, 60, 120, 75, fill="black", outline="blue", width=5), # horizontal
        self.canvas.create_rectangle(60, 60, 75, 180, fill="black", outline="blue", width=5), # verticle
        
        # 2nd obsticle (bottom left)
        self.canvas.create_rectangle(60, 375, 120, 390, fill="black", outline="blue", width=5), # horizontal
        self.canvas.create_rectangle(60, 375, 75, 255, fill="black", outline="blue", width=5), # verticle
        
        # 3rd obsticle (top middle left)
        self.canvas.create_rectangle(180, 0, 195, 75, fill="black", outline="blue", width=5), # verticle
        
        # 4th obsticle (bottom middle left)
        self.canvas.create_rectangle(180, 375, 195, 450, fill="black", outline="blue", width=5), # verticle
        
        # 5th obsticle (top middle)
        self.canvas.create_rectangle(265, 60, 435, 75, fill="black", outline="blue", width=5), # horizontal
        
        # 6th obsticle (bottom middle)
        self.canvas.create_rectangle(265, 375, 435, 390, fill="black", outline="blue", width=5), # horizontal
        
        # 7th obsticle (top middle right)
        self.canvas.create_rectangle(505, 0, 520, 75, fill="black", outline="blue", width=5), # verticle
        
        # 8th obsticle (bottom middle right)
        self.canvas.create_rectangle(505, 375, 520, 450, fill="black", outline="blue", width=5), # verticle
        
        # 9th obsticle (top right)
        self.canvas.create_rectangle(625, 60, 580, 75, fill="black", outline="blue", width=5), # horizontal
        self.canvas.create_rectangle(625, 60, 640, 180, fill="black", outline="blue", width=5), # verticle
        
        # 10th obsticle (bottom right)
        self.canvas.create_rectangle(640, 390, 580, 375, fill="black", outline="blue", width=5), # horizontal
        self.canvas.create_rectangle(640, 390, 625, 255, fill="black", outline="blue", width=5), # verticle
        
        # 11th obsticle (top right center)
        self.canvas.create_rectangle(505, 165, 570, 180, fill="black", outline="blue", width=5), # horizontal
        
        # 12th obsticle (bottom right center)
        self.canvas.create_rectangle(505, 255, 570, 270, fill="black", outline="blue", width=5), # horizontal
        
        # 13th obsticle (center)
        self.canvas.create_rectangle(265, 165, 305, 180, fill="black", outline="blue", width=5), # horizontal
        self.canvas.create_rectangle(265, 165, 280, 270, fill="black", outline="blue", width=5), # verticle
        self.canvas.create_rectangle(280, 255, 435, 270, fill="black", outline="blue", width=5), # horizontal
        self.canvas.create_rectangle(420, 180, 435, 270, fill="black", outline="blue", width=5), # verticle
        self.canvas.create_rectangle(395, 165, 435, 180, fill="black", outline="blue", width=5), # horizontal
        
        # 14th obsticle (top left center)
        self.canvas.create_rectangle(130, 165, 180, 180, fill="black", outline="blue", width=5), # horizontal
        
        # 15th obsticle (bottom left center)
        self.canvas.create_rectangle(130, 255, 180, 270, fill="black", outline="blue", width=5), # horizontal
        
        # Left Border Wall
        self.canvas.create_rectangle(0, 0, 0, 450, fill="black", outline="black"), # verticle
        
        # Top Border Wall
        self.canvas.create_rectangle(0, 0, 700, 0, fill="black", outline="black"), # horizontal
        
        # Right Border Wall
        self.canvas.create_rectangle(700, 0, 700, 450, fill="black", outline="black"), # verticle
        
        # Bottom Border Wall
        self.canvas.create_rectangle(0, 450, 800, 450, fill="black", outline="black"), # horizontal
        
    ]

    # Create collectibles (list of canvas oval IDs)
    self.collectibles = [
        self.canvas.create_oval(25, 70, 35, 80, fill="pink", outline="pink"),
        self.canvas.create_oval(150, 210, 160, 220, fill="pink", outline="pink"),
        self.canvas.create_oval(350, 30, 360, 40, fill="pink", outline="pink"),
        self.canvas.create_oval(315, 322, 325, 332, fill="pink", outline="pink"),
        self.canvas.create_oval(600, 420, 610, 430, fill="pink", outline="pink"),
        self.canvas.create_oval(590, 100, 600, 110, fill="pink", outline="pink"),
        self.canvas.create_oval(370, 215, 380, 225, fill="pink", outline="pink"),
        self.canvas.create_oval(70, 415, 80, 425, fill="pink", outline="pink"),

    ]

    # Bind keys
    # Control up, down, left, right
    self.window.bind("2", lambda event: self.move(0, -15))  # Up
    self.window.bind("4", lambda event: self.move(-15, 0))  # Left
    self.window.bind("6", lambda event: self.move(15, 0))   # Right
    self.window.bind("8", lambda event: self.move(0, 15))   # Down
    
    
    def check_keypad(self):
        keys = self.matrix_keypad.pressed_keys
        if keys:
            for key in keys:
                if key ==2:
                    self.move(0,-10) #UP
                elif key ==8:
                    self.move(0,10)  #DOWN 
                elif key == 4:
                    self.move(-10,0) #LEFT
                elif key ==6:
                    self.move(10,0)  #RIGHT
        self.window.after(100,self.check_keypad)
    
    
    # Start ghost movement
    self.chase_pacman()
    self.chase_pacman2()
    
    self.update()

def move(self, dx, dy):
    if not self.game_running:
        return
    
    # Get Pac-Man's current position
    coords = self.canvas.coords(self.pacman)
    new_coords = [coords[0]+dx, coords[1]+dy, coords[2]+dx, coords[3]+dy]

    # Check for collisions with obstacles
    for obstacle in self.obstacles:
        if self.is_collision(new_coords, self.canvas.coords(obstacle)):
            return  # Block movement

    # Move Pac-Man
    self.canvas.move(self.pacman, dx, dy)

    # Check for collectible collisions
    for collectible in self.collectibles[:]:  # Copy to avoid modifying while iterating
        if self.is_collision(new_coords, self.canvas.coords(collectible)):
            self.canvas.delete(collectible)
            self.collectibles.remove(collectible)
    
     # Check win condition
    if not self.collectibles:
        self.game_running = False
        self.canvas.create_text(350, 225, text="You Win!", fill="white", font=("Arial", 90))
    
# ghost chase
def chase_pacman(self):
    if not self.game_running:
        return
    
    self.move_ghost_toward_pacman(self.ghost)
    self.window.after(110, self.chase_pacman)

# ghost2 chase
def chase_pacman2(self):
    if not self.game_running:
        return

    self.move_ghost_toward_pacman(self.ghost2)
    
    # Check collision with Pac-Man
    if self.is_collision(self.canvas.coords(self.ghost2), self.canvas.coords(self.pacman)):
        self.game_running = False
        self.canvas.create_text(350, 225, text="Game Over", fill="white", font=("Arial", 90))

    self.window.after(100, self.chase_pacman2)

# Ghost movements
def move_ghost_toward_pacman(self, ghost):
    ghost_coords = self.canvas.coords(ghost)
    pacman_coords = self.canvas.coords(self.pacman)

    ghost_x = (ghost_coords[0] + ghost_coords[2]) / 2
    ghost_y = (ghost_coords[1] + ghost_coords[3]) / 2
    pacman_x = (pacman_coords[0] + pacman_coords[2]) / 2
    pacman_y = (pacman_coords[1] + pacman_coords[3]) / 2

    # Determines the ghosts movements
    if ghost == self.ghost:
        # Red ghost: prioritize horizontal movement
        move_options = []
        if ghost_x < pacman_x:
            move_options.append((5, 0))
        elif ghost_x > pacman_x:
            move_options.append((-5, 0))
        if ghost_y < pacman_y:
            move_options.append((0, 5))
        elif ghost_y > pacman_y:
            move_options.append((0, -5))
    else:
        # Cyan ghost: prioritize vertical movement
        move_options = []
        if ghost_y < pacman_y:
            move_options.append((0, 5))
        elif ghost_y > pacman_y:
            move_options.append((0, -5))
        if ghost_x < pacman_x:
            move_options.append((5, 0))
        elif ghost_x > pacman_x:
            move_options.append((-5, 0))

    for dx, dy in move_options:
        new_coords = [ghost_coords[0]+dx, ghost_coords[1]+dy,
                      ghost_coords[2]+dx, ghost_coords[3]+dy]

        # Avoid walls
        collision = False
        for obstacle in self.obstacles:
            if self.is_collision(new_coords, self.canvas.coords(obstacle)):
                collision = True
                break

        # Also avoid ghost1 if ghost2 is moving
        if ghost == self.ghost2 and not collision:
            ghost1_coords = self.canvas.coords(self.ghost)
            if self.is_collision(new_coords, ghost1_coords):
                collision = True

        if not collision:
            self.canvas.move(ghost, dx, dy)
            break

    # Game Over if ghost touches Pac-Man
    if self.is_collision(self.canvas.coords(ghost), pacman_coords):
        self.game_running = False
        self.canvas.create_text(350, 225, text="Game Over", fill="white", font=("Arial", 90))

# Collision check
def is_collision(self, coords1, coords2):
    # Simple bounding box collision
    x1, y1, x2, y2 = coords1
    a1, b1, a2, b2 = coords2
    return not (x2 < a1 or x1 > a2 or y2 < b1 or y1 > b2)
```

######

# MAIN

WIDTH = 800
HEIGHT = 600
window = Tk()
gui = Lcd(window)

# 7-segment timer

i2c = board.I2C()
display = Seg7x4(i2c)
display.brightness = 0.5
timer = Timer(COUNTDOWN, display)
gui.setTimer(timer)

# Keypad

keypad\_cols = \[DigitalInOut(i) for i in (board.D10, board.D9, board.D11)]
keypad\_rows = \[DigitalInOut(i) for i in (board.D5, board.D6, board.D13, board.D19)]
keypad\_keys = ((1, 2, 3), (4, 5, 6), (7, 8, 9), ("\*", 0, "#"))
matrix\_keypad = Matrix\_Keypad(keypad\_rows, keypad\_cols, keypad\_keys)
keypad = Keypad(gui, matrix\_keypad)

# Jumper wires

wire\_pins = \[DigitalInOut(i) for i in (board.D14, board.D15, board.D18, board.D23, board.D24)]
for pin in wire\_pins:
pin.direction = Direction.INPUT
pin.pull = Pull.DOWN
wires = Wires(gui, wire\_pins)

# Pushbutton

button\_input = DigitalInOut(board.D4)
button\_RGB = \[DigitalInOut(i) for i in (board.D17, board.D27, board.D22)]
button\_input.direction = Direction.INPUT
button\_input.pull = Pull.DOWN
for pin in button\_RGB:
pin.direction = Direction.OUTPUT
pin.value = True
button = ogButton(gui, button\_input, button\_RGB)
gui.setButton(button)

# Toggle switches

toggle\_pins = \[DigitalInOut(i) for i in (board.D12, board.D16, board.D20, board.D21)]
for pin in toggle\_pins:
pin.direction = Direction.INPUT
pin.pull = Pull.DOWN
toggles = Toggles(gui, toggle\_pins)

# Start all phase threads

timer.start()
keypad.start()
wires.start()
button.start()
toggles.start()

# Start main GUI loop

window\.mainloop()
