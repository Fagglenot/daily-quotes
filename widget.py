# desktop_glass_widget.py
import tkinter as tk
import datetime, json, os, random, sys
import ctypes
from ctypes import wintypes
import win32gui, win32con, win32api

# -----------------------------
# Quotes & storage
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
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("date") == today:
                return data.get("quote", random.choice(QUOTES))
        except Exception:
            pass
    quote = random.choice(QUOTES)
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump({"date": today, "quote": quote}, f)
    except Exception:
        pass
    return quote

# -----------------------------
# Windows helper: attach to desktop (WorkerW)
# -----------------------------
def get_workerw():
    # Send message to Progman to spawn WorkerW
    progman = win32gui.FindWindow("Progman", None)
    if not progman:
        return None

    # 0x052C = 1324 decimal. Known trick: send message to create a WorkerW behind desktop icons
    win32gui.SendMessageTimeout(progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)

    workerw = []

    def enum_windows_callback(hwnd, lParam):
        # find window that has a child SHELLDLL_DefView
        if win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None):
            workerw.append(hwnd)
        return True

    win32gui.EnumWindows(enum_windows_callback, None)

    # workerw[] may contain one or more; choose the first
    return workerw[0] if workerw else None

# -----------------------------
# Windows composition: blur/acrylic attempt (fallback to layered translucency)
# -----------------------------
# We try to apply a blur/acrylic-like effect using SetWindowCompositionAttribute (Windows 10+).
# If unavailable, we'll fallback to a semi-transparent layered window.

# Structures for SetWindowCompositionAttribute (ctypes)
class ACCENTPOLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_int),
        ("AnimationId", ctypes.c_int)
    ]

class WINCOMPATTRDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.POINTER(ACCENTPOLICY)),
        ("SizeOfData", ctypes.c_size_t)
    ]

# AccentState constants
ACCENT_DISABLED = 0
ACCENT_ENABLE_GRADIENT = 1
ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
ACCENT_ENABLE_BLURBEHIND = 3
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4  # supported on newer Windows 10/11 builds

# Attribute
WCA_ACCENT_POLICY = 19

_set_window_composition_attribute = None
user32 = ctypes.windll.user32

try:
    _set_window_composition_attribute = user32.SetWindowCompositionAttribute
    _set_window_composition_attribute.restype = wintypes.BOOL
except Exception:
    _set_window_composition_attribute = None

def enable_blur(hwnd):
    """Attempt to enable blur/acrylic. Return True on success, False if not available."""
    if not _set_window_composition_attribute:
        return False
    try:
        accent = ACCENTPOLICY()
        # Try acrylic first (may not work on older builds)
        accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.GradientColor = 0x99FFFFFF  # alpha + color (0xAABBGGRR)
        accent_ptr = ctypes.pointer(accent)
        data = WINCOMPATTRDATA()
        data.Attribute = WCA_ACCENT_POLICY
        data.Data = accent_ptr
        data.SizeOfData = ctypes.sizeof(accent)
        res = _set_window_composition_attribute(wintypes.HWND(hwnd), ctypes.byref(data))
        return bool(res)
    except Exception:
        # fallback to blur behind
        try:
            accent = ACCENTPOLICY()
            accent.AccentState = ACCENT_ENABLE_BLURBEHIND
            accent_ptr = ctypes.pointer(accent)
            data = WINCOMPATTRDATA()
            data.Attribute = WCA_ACCENT_POLICY
            data.Data = accent_ptr
            data.SizeOfData = ctypes.sizeof(accent)
            res = _set_window_composition_attribute(wintypes.HWND(hwnd), ctypes.byref(data))
            return bool(res)
        except Exception:
            return False

# -----------------------------
# Build the Tkinter widget
# -----------------------------
def build_widget():
    root = tk.Tk()
    root.title("Daily Quote (Desktop)")
    root.overrideredirect(True)  # no title bar
    root.geometry("360x140+50+50")
    root.attributes("-topmost", False)  # not topmost; we will parent to desktop
    # Add transparent background for shaped widget:
    root.configure(bg='systemTransparent' if sys.platform == "darwin" else "#000000")  # bg will be masked by canvas anyway

    WIDTH, HEIGHT, RADIUS = 360, 140, 20
    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, highlightthickness=0)
    canvas.pack()

    # draw rounded rectangle (smooth polygon) with semi-transparent fill via color hex with alpha not supported in Tk.
    # We'll draw a solid shape and set window layered alpha if blur not available.
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

    # Glassy base fill; we pick a light base color (it will be blended by Windows blur if enabled)
    base_fill = "#EAF6FF"  # pale-blue base (we will keep text white)
    round_rect(0, 0, WIDTH, HEIGHT, RADIUS, fill=base_fill, outline=base_fill)

    # Add translucent overlay to simulate glass
    # A slightly transparent white rectangle using a stipple pattern to simulate translucency in Tkinter
    # (True alpha blending for shape is not supported; Windows composition will help)
    overlay = canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#FFFFFF", stipple="gray25", outline="")

    # Quote
    quote = get_daily_quote()
    text_item = canvas.create_text(WIDTH/2, HEIGHT/2 - 6, text=quote, fill="#ffffff",
                                   font=("Segoe UI", 12, "bold"), width=300, justify="center")

    # small close "×"
    close_x = WIDTH - 26
    close_y = 26
    close_item = canvas.create_text(close_x, close_y, text="×", fill="#2a2a2a",
                                    font=("Segoe UI", 18, "bold"))

    def on_close(evt=None):
        root.destroy()

    canvas.tag_bind(close_item, "<Button-1>", on_close)

    # Dragging - start/dragging only when clicking outside close
    def start_move(event):
        # ignore if clicking on close symbol
        x, y = event.x, event.y
        coords = canvas.coords(close_item)
        if coords:
            cx, cy = coords[0], coords[1]
            if (x - cx)**2 + (y - cy)**2 <= (18**2):
                return
        root._drag_x = event.x
        root._drag_y = event.y

    def do_move(event):
        if getattr(root, "_drag_x", None) is None:
            return
        dx = event.x - root._drag_x
        dy = event.y - root._drag_y
        x = root.winfo_x() + dx
        y = root.winfo_y() + dy
        root.geometry(f"+{x}+{y}")

    def stop_move(event):
        root._drag_x = None
        root._drag_y = None

    canvas.bind("<ButtonPress-1>", start_move)
    canvas.bind("<B1-Motion>", do_move)
    canvas.bind("<ButtonRelease-1>", stop_move)

    # Return root and canvas so we can access window id
    return root, canvas

# -----------------------------
# Attach to desktop and apply blur/transparency
# -----------------------------
def attach_to_desktop(root):
    hwnd = wintypes.HWND(root.winfo_id())
    # Find WorkerW
    workerw = get_workerw()
    if not workerw:
        # fallback: try to set parent to Progman
        progman = win32gui.FindWindow("Progman", None)
        parent = progman or 0
    else:
        parent = workerw

    # Set the parent to the desktop (WorkerW) so window is behind other windows
    try:
        win32gui.SetParent(hwnd, parent)
    except Exception:
        # On failure, ignore and continue
        pass

    # Try to enable blur/acrylic
    applied = False
    try:
        applied = enable_blur(hwnd)
    except Exception:
        applied = False

    # If blur not available, fallback to layered translucency
    if not applied:
        # Make layered window and set alpha for translucency
        exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exstyle | win32con.WS_EX_LAYERED)
        # 230 alpha (0-255) for translucent glass feel
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 230, win32con.LWA_ALPHA)

    # Make sure window doesn't appear in taskbar
    try:
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style | win32con.WS_EX_TOOLWINDOW)
    except Exception:
        pass

# -----------------------------
# Main
# -----------------------------
def main():
    root, canvas = build_widget()
    root.update_idletasks()

    # Attach to desktop layer & try to apply composition/blur
    try:
        attach_to_desktop(root)
    except Exception as e:
        print("Warning: could not attach to desktop layer:", e)

    # Position the widget where you want on desktop initially
    # e.g. bottom-right-ish relative to primary monitor
    try:
        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)
        # place 50 px from right and 120 px from bottom
        x = screen_w - 50 - 360
        y = screen_h - 120 - 140
        root.geometry(f"+{x}+{y}")
    except Exception:
        return

    root.mainloop()

if __name__ == "__main__":
    main()
