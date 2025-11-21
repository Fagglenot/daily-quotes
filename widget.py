import tkinter as tk
import datetime
import json
import os
import random

# -----------------------------
# Quotes list
# -----------------------------
QUOTES = [
    "Believe in yourself!",
    "You can do hard things.",
    "Start before you're ready.",
    "Small steps every day lead to big results.",
    "Your future is created by what you do today."
]

SAVE_FILE = "daily_quote.json"


# -----------------------------
# Load or generate today's quote
# -----------------------------
def get_daily_quote():
    today = datetime.date.today().isoformat()

    # if save file exists, check the date
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            if data["date"] == today:
                return data["quote"]

    # otherwise pick a new quote
    quote = random.choice(QUOTES)

    with open(SAVE_FILE, "w") as f:
        json.dump({"date": today, "quote": quote}, f)

    return quote


# -----------------------------
# UI Setup
# -----------------------------
root = tk.Tk()
root.title("Daily Quote")
root.geometry("350x130")
root.resizable(False, False)
root.attributes("-topmost", True)  # always on top
root.overrideredirect(True)        # hide title bar

# Make window draggable
def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None

def do_move(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")

root.bind("<ButtonPress-1>", start_move)
root.bind("<ButtonRelease-1>", stop_move)
root.bind("<B1-Motion>", do_move)

# UI Background
frame = tk.Frame(root, bg="#f2f2f2", bd=2, relief="flat")
frame.pack(fill="both", expand=True)

# Quote Label
quote_text = get_daily_quote()
label = tk.Label(frame, text=quote_text, font=("Segoe UI", 12), bg="#f2f2f2",
                 wraplength=320, justify="center")
label.pack(pady=20)

root.mainloop()
