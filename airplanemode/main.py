import tkinter as tk
from tkinter import messagebox
import time
import subprocess
import ctypes
import sys

# Constants
WORK_TIME = 25 * 60  # 25 minutes in seconds
SHORT_BREAK = 5 * 60  # 5 minutes in seconds
LONG_BREAK = 15 * 60  # 15 minutes in seconds
POMODOROS_PER_SET = 4

# Global variables
current_time = WORK_TIME
pomodoro_count = 0
is_running = False
timer = None
wifi_enabled = True  # Track Wi-Fi state

# Functions
def run_as_admin():
    """Request administrator privileges."""
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        # Re-launch the script with administrator privileges
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return False

def toggle_wifi():
    global wifi_enabled
    if wifi_enabled:
        disable_wifi()
        wifi_button.config(text="Enable Wi-Fi")
    else:
        enable_wifi()
        wifi_button.config(text="Disable Wi-Fi")
    wifi_enabled = not wifi_enabled

def enable_wifi():
    """Enable Wi-Fi adapter on Windows."""
    subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "admin=enable"], shell=True)

def disable_wifi():
    """Disable Wi-Fi adapter on Windows."""
    subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "admin=disable"], shell=True)

def start_timer():
    global is_running
    if not is_running:
        is_running = True
        countdown()

def reset_timer():
    global current_time, pomodoro_count, is_running
    if timer:
        window.after_cancel(timer)
    is_running = False
    current_time = WORK_TIME
    pomodoro_count = 0
    update_display()

def countdown():
    global current_time, pomodoro_count, is_running, timer
    if is_running:
        if current_time > 0:
            minutes, seconds = divmod(current_time, 60)
            timer_label.config(text=f"{minutes:02}:{seconds:02}")
            current_time -= 1
            timer = window.after(1000, countdown)
        else:
            is_running = False
            pomodoro_count += 1
            if pomodoro_count % POMODOROS_PER_SET == 0:
                messagebox.showinfo("Pomodoro", "Time for a long break!")
                current_time = LONG_BREAK
            elif pomodoro_count % 2 == 0:
                messagebox.showinfo("Pomodoro", "Time for a short break!")
                current_time = SHORT_BREAK
            else:
                messagebox.showinfo("Pomodoro", "Time to work!")
                current_time = WORK_TIME
            update_display()
            start_timer()

def update_display():
    minutes, seconds = divmod(current_time, 60)
    timer_label.config(text=f"{minutes:02}:{seconds:02}")

# Check for administrator privileges
if not run_as_admin():
    print("This script requires administrator privileges.")
    sys.exit(1)

# GUI Setup
window = tk.Tk()
window.title("Pomodoro Timer")
window.geometry("400x300")  # Set a fixed window size
window.resizable(False, False)  # Disable resizing
window.configure(bg="#f0f0f0")  # Set a light background color

# Custom Styles for Buttons
button_style = {
    "font": ("Helvetica", 12),
    "bg": "#4CAF50",  # Green background
    "fg": "white",    # White text
    "borderwidth": 0,
    "relief": "flat",
    "padx": 20,
    "pady": 10,
    "activebackground": "#45a049",  # Darker green when pressed
    "activeforeground": "white",
}

# Timer Label
timer_label = tk.Label(window, text="25:00", font=("Helvetica", 48, "bold"), bg="#f0f0f0", fg="#333333")
timer_label.pack(pady=20)

# Buttons Frame
button_frame = tk.Frame(window, bg="#f0f0f0")
button_frame.pack(pady=10)

# Start Button
start_button = tk.Button(button_frame, text="Start", command=start_timer, **button_style)
start_button.grid(row=0, column=0, padx=10)

# Reset Button
reset_button = tk.Button(button_frame, text="Reset", command=reset_timer, **button_style)
reset_button.config(bg="#f44336", activebackground="#d32f2f")  # Red background
reset_button.grid(row=0, column=1, padx=10)

# Wi-Fi Button
wifi_button = tk.Button(window, text="Disable Wi-Fi", command=toggle_wifi, **button_style)
wifi_button.config(bg="#2196F3", activebackground="#1976D2")  # Blue background
wifi_button.pack(pady=10)

# Run the app
window.mainloop()
