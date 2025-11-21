import tkinter as tk
import datetime
import json
import os
import random

# -----------------------------
# Quotes
# -----------------------------
QUOTES = [
    "Believe in yourself!",
    "You can do hard things.",
    "Start before you're ready.",
    "Small steps every day lead to big results.",
    "Your future is created by what you do today."
]

SAVE_FILE = "daily_quote.json"


def get_daily_quote():
    today = datetime.date.today().isoformat()

    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            if data["date"] == today:
                return data["quote"]

    quote = random.choice(QUOTES)

    with open(SAVE_FILE, "w") as f:
        json.dump({"date": today, "quote": quote}, f)

    return quote


# -----------------------------
# UI Setup
# -----------------------------
root = tk.Tk()
root.title("Daily Quote Widget")
root.overrideredirect(True)
root.attributes("-topmost", True)

WIDTH = 360
HEIGHT = 140
RADIUS = 20

# Create rounded-corner frame using a canvas mask
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, highlightthickness=0, bg="white")
canvas.pack()

# Rounded rectangle helper
def round_rect(x1, y1, x2, y2, r, **kwargs):
    points = [
        x1+r, y1,
        x2-r, y1,
        x2, y1,
        x2, y1+r,
        x2, y2-r,
        x2, y2,
        x2-r, y2,
        x1+r, y2,
        x1, y2,
        x1, y2-r,
        x1, y1+r,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


# Light blue background
round_rect(0, 0, WIDTH, HEIGHT, RADIUS, fill="#67B8FF", outline="#67B8FF")

# Quote text
quote = get_daily_quote()
text = canvas.create_text(
    WIDTH/2,
    HEIGHT/2 - 10,
    text=quote,
    fill="white",
    font=("Segoe UI", 12, "bold"),
    width=300,
    justify="center"
)

# Close button (small circle)
def close_widget(event=None):
    root.destroy()

canvas.create_text(WIDTH - 25, 25, text="×", fill="white",
                   font=("Segoe UI", 20, "bold"), tags="close")
canvas.tag_bind("close", "<Button-1>", close_widget)

# Make window draggable
def start_move(event):
    root.x = event.x
    root.y = event.y

def do_move(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")

canvas.bind("<ButtonPress-1>", start_move)
canvas.bind("<B1-Motion>", do_move)

root.mainloop()
