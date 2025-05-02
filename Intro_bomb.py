#INTRO SCREEN BEFORE BOMB

import tkinter as tk

# Create main window
root = tk.Tk()
root.title("Black Text Screen")
root.configure(bg="black")
root.geometry("600x400")

# Create a read-only text display,
text_display = tk.Text(root, bg="black", fg="white", font=("Courier", 30), state='disabled', wrap = "word")
text_display.pack(expand=True, fill='both', padx=10, pady=10)

# Subroutine which gives type writer class which takes in text and delay and prints it depending on what you give it
def typewriter(text, delay=100, linebreak=True):
    def inner(i=0):
        if i < len(text):
            text_display.configure(state='normal')
            text_display.insert(tk.END, text[i])
            text_display.configure(state='disabled')
            text_display.see(tk.END)
            root.after(delay, inner, i+1)
        elif linebreak:
            text_display.configure(state='normal')
            text_display.insert(tk.END, "\n")
            text_display.configure(state='disabled')
            text_display.see(tk.END)
    inner()
    
    # Clear screen and show new message
def intro_phase1():
    text_display.configure(state='normal')
    text_display.delete('1.0', tk.END)
    text_display.configure(state='disabled')
    typewriter("PHASE 1", delay=100)
    root.after(2000, lambda: typewriter("OBJECTIVE: Eat all the Pac-Dots scattered throughout the maze to complete the level. Avoid the ghosts, contact with a ghost results in losing a life.", delay = 100))

#NEW OBJECTIVE: Eat all the Pac-Dots scattered throughout the maze to complete the level. Avoid the ghosts: Contact with a ghost results in losing a life.

#INTRO TO WHOLE BOMB DEFUSION
typewriter("DEFUSE THE BOMB", delay=100)
root.after(2500, lambda: typewriter("OBJECTIVE: COMPLETE ALL 4 PHASES QUICKLY IN ORDER TO DEFUSE THE BOMB. OR ELSE...", delay=80))

# After 15 seconds (15000 ms), switch to new screen
root.after(15000, intro_phase1)

# Run the GUI
root.mainloop()

import tkinter as tk
from threading import Thread
from main_bomb_code import run_main_gui  # ← define this below in your bomb code

# Create intro window
root = tk.Tk()
root.title("Black Text Screen")
root.configure(bg="black")
root.geometry("600x400")

# Create a read-only text display
text_display = tk.Text(root, bg="black", fg="white", font=("Courier", 30), state='disabled', wrap="word")
text_display.pack(expand=True, fill='both', padx=10, pady=10)

# Typewriter effect
def typewriter(text, delay=100, linebreak=True):
    def inner(i=0):
        if i < len(text):
            text_display.configure(state='normal')
            text_display.insert(tk.END, text[i])
            text_display.configure(state='disabled')
            text_display.see(tk.END)
            root.after(delay, inner, i + 1)
        elif linebreak:
            text_display.configure(state='normal')
            text_display.insert(tk.END, "\n")
            text_display.configure(state='disabled')
            text_display.see(tk.END)
    inner()

# Objective phase message
def intro_phase1():
    text_display.configure(state='normal')
    text_display.delete('1.0', tk.END)
    text_display.configure(state='disabled')
    typewriter("PHASE 1", delay=100)
    root.after(2000, lambda: typewriter(
        "OBJECTIVE: Eat all the Pac-Dots scattered throughout the maze to complete the level. Avoid the ghosts...",
        delay=80))

# Transition to main bomb GUI
def switch_to_main_gui():
    root.destroy()  # Close intro screen
    Thread(target=run_main_gui).start()  # Launch main GUI in a thread

# Intro sequence
typewriter("DEFUSE THE BOMB", delay=100)
root.after(2500, lambda: typewriter(
    "OBJECTIVE: COMPLETE ALL 4 PHASES QUICKLY IN ORDER TO DEFUSE THE BOMB. OR ELSE...", delay=80))

root.after(15000, intro_phase1)
root.after(25000, switch_to_main_gui)  # Launch main GUI after ~25 sec

root.mainloop()


