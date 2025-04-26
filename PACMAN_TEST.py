from tkinter import *
import random

class PacManApp(Frame):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.window.title("PacMan")
        
        # Size of screen
        self.canvas = Canvas(window, width=800, height=480, bg="black")
        self.canvas.pack()

        # Create Pac-Man
        self.pacman = self.canvas.create_arc(100, 320, 140, 360, start=45, extent=270, fill="yellow", outline="orange")

        # Create ghost (red)
        self.ghost = self.canvas.create_oval(600, 410, 630, 440, fill="red", outline="pink")
        # Create second ghost (cyan)
        self.ghost2 = self.canvas.create_oval(10, 10, 40, 40, fill="cyan")

        self.game_running = True
        self.direction = "Stop"  # <-- Add this!

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
            self.canvas.create_rectangle(0, 0, 1, 450, fill="black", outline="black"), # verticle
            
            # Top Border Wall
            self.canvas.create_rectangle(0, 0, 700, 1, fill="black", outline="black"), # horizontal
            
            # Right Border Wall
            self.canvas.create_rectangle(699, 0, 700, 450, fill="black", outline="black"), # verticle
            
            # Bottom Border Wall
            self.canvas.create_rectangle(0, 449, 800, 450, fill="black", outline="black"), # horizontal
            
        ]

        # Collectibles (same)
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

        # Bind keys properly
        self.window.bind("<Up>", self.go_up)
        self.window.bind("<Down>", self.go_down)
        self.window.bind("<Left>", self.go_left)
        self.window.bind("<Right>", self.go_right)

        # Start movement updates
        self.chase_pacman()
        self.chase_pacman2()
        self.update()

    # Direction setting functions
    def go_up(self, event=None):
        self.direction = "Up"
    def go_down(self, event=None):
        self.direction = "Down"
    def go_left(self, event=None):
        self.direction = "Left"
    def go_right(self, event=None):
        self.direction = "Right"

    # Same move logic
    def move(self, dx, dy):
        if not self.game_running:
            return
        coords = self.canvas.coords(self.pacman)
        new_coords = [coords[0]+dx, coords[1]+dy, coords[2]+dx, coords[3]+dy]

        # Collision check
        for obstacle in self.obstacles:
            if self.is_collision(new_coords, self.canvas.coords(obstacle)):
                return
        self.canvas.move(self.pacman, dx, dy)

        # Collectibles
        for collectible in self.collectibles[:]:
            if self.is_collision(new_coords, self.canvas.coords(collectible)):
                self.canvas.delete(collectible)
                self.collectibles.remove(collectible)
        
        if not self.collectibles:
            self.game_running = False
            self.canvas.create_text(350, 225, text="Winner!", fill="white", font=("Arial", 90))

    def move_pacman(self):
        dx, dy = 0, 0
        if self.direction == "Left":
            dx = -10
        elif self.direction == "Right":
            dx = 10
        elif self.direction == "Up":
            dy = -10
        elif self.direction == "Down":
            dy = 10
        
        self.move(dx, dy)

    def update(self):
        if not self.game_running:
            return
        self.move_pacman()
        self.window.after(100, self.update)

    def chase_pacman(self):
        if not self.game_running:
            return
        self.move_ghost_toward_pacman(self.ghost)
        self.window.after(100, self.chase_pacman)

    def chase_pacman2(self):
        if not self.game_running:
            return
        self.move_ghost_toward_pacman(self.ghost2)
        if self.is_collision(self.canvas.coords(self.ghost2), self.canvas.coords(self.pacman)):
            self.game_running = False
            self.canvas.create_text(350, 225, text="Game Over", fill="white", font=("Arial", 90))
        self.window.after(90, self.chase_pacman2)

    def move_ghost_toward_pacman(self, ghost):
        # Ghost movement logic (you already wrote this well!)

        ghost_coords = self.canvas.coords(ghost)
        pacman_coords = self.canvas.coords(self.pacman)

        ghost_x = (ghost_coords[0] + ghost_coords[2]) / 2
        ghost_y = (ghost_coords[1] + ghost_coords[3]) / 2
        pacman_x = (pacman_coords[0] + pacman_coords[2]) / 2
        pacman_y = (pacman_coords[1] + pacman_coords[3]) / 2
        
        move_options = []
        if ghost == self.ghost:
            if ghost_x < pacman_x:
                move_options.append((5, 0))
            elif ghost_x > pacman_x:
                move_options.append((-5, 0))
            if ghost_y < pacman_y:
                move_options.append((0, 5))
            elif ghost_y > pacman_y:
                move_options.append((0, -5))
        else:
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
            collision = False
            for obstacle in self.obstacles:
                if self.is_collision(new_coords, self.canvas.coords(obstacle)):
                    collision = True
                    break

            if ghost == self.ghost2 and not collision:
                ghost1_coords = self.canvas.coords(self.ghost)
                if self.is_collision(new_coords, ghost1_coords):
                    collision = True

            if not collision:
                self.canvas.move(ghost, dx, dy)
                break

        if self.is_collision(self.canvas.coords(ghost), pacman_coords):
            self.game_running = False
            self.canvas.create_text(350, 225, text="Game Over", fill="white", font=("Arial", 90))

    def is_collision(self, coords1, coords2):
        x1, y1, x2, y2 = coords1
        a1, b1, a2, b2 = coords2
        return not (x2 < a1 or x1 > a2 or y2 < b1 or y1 > b2)

# --- Run the game ---
window = Tk()
app = PacManApp(window)
window.mainloop()
