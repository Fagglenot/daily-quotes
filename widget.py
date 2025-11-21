import tkinter as tk
import ctypes
import win32gui
import win32con
import win32api
from datetime import date

# -------------------------
# DAILY QUOTES
# -------------------------
QUOTES = [
    "Believe in yourself.",
    "You can do hard things.",
    "Small steps every day.",
    "Keep going — you're getting better.",
    "Progress, not perfection.",
]

def get_daily_quote():
    index = date.today().toordinal() % len(QUOTES)
    return QUOTES[index]


# -------------------------
# MAIN TRANSPARENT WIDGET
# -------------------------
root = tk.Tk()
root.overrideredirect(True)       # Remove title bar
root.wm_attributes("-transparentcolor", "white")
root.configure(bg="white")

# Window size
WIDTH, HEIGHT = 360, 140

canvas = tk.Canvas(root,
                   width=WIDTH,
                   height=HEIGHT,
                   bg="white",
                   highlightthickness=0)
canvas.pack()

# -------------------------
# DRAW GLASSMORPHISM BOX
# -------------------------
def draw_glass():
    # rounded rectangle (background)
    radius = 25
    x1, y1 = 0, 0
    x2, y2 = WIDTH, HEIGHT

    canvas.create_rectangle(
        x1, y1, x2, y2,
        fill="#FFFFFF20",   # transparent white (20% opacity)
        outline="#FFFFFF40",
        width=2
    )

    # text
    canvas.create_text(
        WIDTH//2,
        HEIGHT//2,
        text=get_daily_quote(),
        fill="white",
        font=("Segoe UI", 16, "bold"),
        width=300,
        justify="center"
    )

draw_glass()


# -------------------------
# MAKE WINDOW MOVABLE
# -------------------------
def start_move(event):
    root.x = event.x
    root.y = event.y

def do_move(event):
    deltax = event.x - root.x
    deltay = event.y - root.y
    newx = root.winfo_x() + deltax
    newy = root.winfo_y() + deltay
    root.geometry(f"+{newx}+{newy}")

canvas.bind("<ButtonPress-1>", start_move)
canvas.bind("<B1-Motion>", do_move)


# -------------------------
# SEND WINDOW TO DESKTOP LAYER
# -------------------------
root.update_idletasks()
hwnd = win32gui.FindWindow(None, str(root.title()))

# Put window behind icons (desktop level)
hdesktop = win32gui.FindWindow("Progman", None)
win32gui.SetParent(hwnd, hdesktop)

# Make click-through background but clickable inside
win32gui.SetWindowLong(hwnd,
                       win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                       | win32con.WS_EX_LAYERED)

win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)


# -------------------------
# CENTER ON SCREEN
# -------------------------
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
root.geometry(f"{WIDTH}x{HEIGHT}+{screen_w//2 - WIDTH//2}+{screen_h//2 - HEIGHT//2}")


root.mainloop()
