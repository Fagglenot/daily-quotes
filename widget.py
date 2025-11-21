import tkinter as tk
import win32gui
import win32con
from datetime import date
import requests

def get_quote():
    try:
        r = requests.get("https://zenquotes.io/api/random", timeout=5)
        data = r.json()[0]
        quote = data['q']
        author = data['a']
        return f"“{quote}”\n— {author}"
    except Exception as e:
        # fallback if internet is down or API fails
        return "“Keep going, everything you need will come at the perfect time.”\n— Unknown"


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
    idx = date.today().toordinal() % len(QUOTES)
    return QUOTES[idx]


# -------------------------
# TRANSPARENT WIDGET
# -------------------------
root = tk.Tk()
root.overrideredirect(True)
root.config(bg="white")
root.wm_attributes("-transparentcolor", "white")

WIDTH, HEIGHT = 360, 140

canvas = tk.Canvas(
    root,
    width=WIDTH,
    height=HEIGHT,
    bg="white",
    highlightthickness=0
)
canvas.pack()


# -------------------------
# ROUNDED RECT UTIL
# -------------------------
def round_rect(x1, y1, x2, y2, r, fill, outline):
    points = [
        x1+r, y1,
        x2-r, y1,
        x2, y1+r,
        x2, y2-r,
        x2-r, y2,
        x1+r, y2,
        x1, y2-r,
        x1, y1+r
    ]
    return canvas.create_polygon(
        points, smooth=True,
        fill=fill, outline=outline, width=2
    )


# -------------------------
# DRAW GLASS CARD
# -------------------------
def draw_ui():
    glass = "#F0F0F0"
    border = "#FFFFFF"
    shadow = "#D0D0D0"

    # shadow layer
    round_rect(3, 3, WIDTH-3, HEIGHT-3, 25, shadow, shadow)

    # main card
    round_rect(0, 0, WIDTH, HEIGHT, 25, glass, border)

    # quote text
    canvas.create_text(
        WIDTH//2, HEIGHT//2,
        text=get_quote(),
        fill="#FFFFFF",
        font=("Segoe UI", 16, "bold"),
        width=300,
        justify="center"
    )

draw_ui()


# -------------------------
# MOVE BY DRAGGING
# -------------------------
def start_move(e):
    root.x = e.x
    root.y = e.y

def do_move(e):
    dx = e.x - root.x
    dy = e.y - root.y
    root.geometry(f"+{root.winfo_x() + dx}+{root.winfo_y() + dy}")

canvas.bind("<ButtonPress-1>", start_move)
canvas.bind("<B1-Motion>", do_move)


# -------------------------
# FORCE WIDGET TO ALWAYS STAY BEHIND OTHER WINDOWS
# -------------------------
def push_to_back():
    hwnd = win32gui.GetForegroundWindow()
    my_hwnd = win32gui.FindWindow(None, str(root.title()))

    # place window at bottom of Z-order
    win32gui.SetWindowPos(
        my_hwnd,
        win32con.HWND_BOTTOM,
        0, 0, 0, 0,
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
    )

    root.after(500, push_to_back)

root.after(500, push_to_back)


# -------------------------
# CENTER ON SCREEN
# -------------------------
sw = root.winfo_screenwidth()
sh = root.winfo_screenheight()
root.geometry(f"{WIDTH}x{HEIGHT}+{sw//2 - WIDTH//2}+{sh//2 - HEIGHT//2}")

root.mainloop()
