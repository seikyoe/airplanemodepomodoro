import tkinter as tk
from tkinter import messagebox, scrolledtext
import time
import subprocess
import ctypes
import sys

# Default values (in minutes)
DEFAULT_WORK = 25
DEFAULT_SHORT_BREAK = 5
DEFAULT_LONG_BREAK = 15

# Global variables
current_time = DEFAULT_WORK * 60
work_time = DEFAULT_WORK * 60
short_break = DEFAULT_SHORT_BREAK * 60
long_break = DEFAULT_LONG_BREAK * 60
pomodoro_count = 0
is_running = False
timer = None
wifi_enabled = True

# Dark mode colors
BG_COLOR = "#2E3440"
FG_COLOR = "#D8DEE9"
BUTTON_BG = "#4C566A"
BUTTON_FG = "#ECEFF4"
BUTTON_ACTIVE_BG = "#5E81AC"
ENTRY_BG = "#3B4252"
ENTRY_FG = "#E5E9F0"
NOTES_BG = "#3B4252"
NOTES_FG = "#E5E9F0"

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
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
    subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "admin=enable"], shell=True)

def disable_wifi():
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
    current_time = work_time
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
            if pomodoro_count % 4 == 0:
                messagebox.showinfo("Pomodoro", "Time for a long break!")
                current_time = long_break
            elif pomodoro_count % 2 == 0:
                messagebox.showinfo("Pomodoro", "Time for a short break!")
                current_time = short_break
            else:
                messagebox.showinfo("Pomodoro", "Time to work!")
                current_time = work_time
            update_display()
            start_timer()

def update_display():
    minutes, seconds = divmod(current_time, 60)
    timer_label.config(text=f"{minutes:02}:{seconds:02}")

def save_settings():
    global work_time, short_break, long_break
    try:
        new_work = int(work_entry.get()) * 60
        new_short = int(short_entry.get()) * 60
        new_long = int(long_entry.get()) * 60

        if new_work <= 0 or new_short <= 0 or new_long <= 0:
            raise ValueError

        work_time = new_work
        short_break = new_short
        long_break = new_long
        reset_timer()
        messagebox.showinfo("Settings Saved", "New times have been applied!")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter positive numbers only")
        reset_fields()

def save_notes():
    with open("pomodoro_notes.txt", "w") as f:
        f.write(notes_text.get("1.0", tk.END))
    messagebox.showinfo("Notes Saved", "Your notes have been saved!")

def reset_fields():
    work_entry.delete(0, tk.END)
    work_entry.insert(0, DEFAULT_WORK)
    short_entry.delete(0, tk.END)
    short_entry.insert(0, DEFAULT_SHORT_BREAK)
    long_entry.delete(0, tk.END)
    long_entry.insert(0, DEFAULT_LONG_BREAK)

if not run_as_admin():
    print("This script requires administrator privileges.")
    sys.exit(1)

# GUI Setup
window = tk.Tk()
window.title("Pomodoro Timer with Notes")
window.geometry("800x500")
window.configure(bg=BG_COLOR)

# Main container
main_frame = tk.Frame(window, bg=BG_COLOR)
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Left Panel (Pomodoro)
left_frame = tk.Frame(main_frame, bg=BG_COLOR)
left_frame.grid(row=0, column=0, padx=20, sticky="nsew")

# Timer Display
timer_label = tk.Label(left_frame, text="25:00", font=("Helvetica", 48, "bold"), bg=BG_COLOR, fg=FG_COLOR)
timer_label.pack(pady=20)

# Control Buttons
control_frame = tk.Frame(left_frame, bg=BG_COLOR)
control_frame.pack(pady=10)

start_button = tk.Button(control_frame, text="Start", command=start_timer, bg=BUTTON_BG, fg=BUTTON_FG,
                         font=("Helvetica", 12), padx=20, pady=10, relief="flat", activebackground=BUTTON_ACTIVE_BG)
start_button.grid(row=0, column=0, padx=10)

reset_button = tk.Button(control_frame, text="Reset", command=reset_timer, bg=BUTTON_BG, fg=BUTTON_FG,
                         font=("Helvetica", 12), padx=20, pady=10, relief="flat", activebackground=BUTTON_ACTIVE_BG)
reset_button.grid(row=0, column=1, padx=10)

# Settings Frame
settings_frame = tk.LabelFrame(left_frame, text="Settings", bg=BG_COLOR, fg=FG_COLOR, font=("Helvetica", 12, "bold"))
settings_frame.pack(pady=20, padx=20, fill="x")

# Work Time Setting
tk.Label(settings_frame, text="Work (min):", bg=BG_COLOR, fg=FG_COLOR).grid(row=0, column=0, padx=5, pady=5)
work_entry = tk.Entry(settings_frame, width=5, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG_COLOR, relief="flat")
work_entry.grid(row=0, column=1, padx=5, pady=5)
work_entry.insert(0, DEFAULT_WORK)

# Short Break Setting
tk.Label(settings_frame, text="Short Break (min):", bg=BG_COLOR, fg=FG_COLOR).grid(row=1, column=0, padx=5, pady=5)
short_entry = tk.Entry(settings_frame, width=5, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG_COLOR, relief="flat")
short_entry.grid(row=1, column=1, padx=5, pady=5)
short_entry.insert(0, DEFAULT_SHORT_BREAK)

# Long Break Setting
tk.Label(settings_frame, text="Long Break (min):", bg=BG_COLOR, fg=FG_COLOR).grid(row=2, column=0, padx=5, pady=5)
long_entry = tk.Entry(settings_frame, width=5, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG_COLOR, relief="flat")
long_entry.grid(row=2, column=1, padx=5, pady=5)
long_entry.insert(0, DEFAULT_LONG_BREAK)

# Save Button
save_button = tk.Button(settings_frame, text="Save Settings", command=save_settings, bg=BUTTON_BG, fg=BUTTON_FG,
                        font=("Helvetica", 10), padx=10, pady=5, relief="flat", activebackground=BUTTON_ACTIVE_BG)
save_button.grid(row=3, columnspan=2, pady=10)

# Wi-Fi Button
wifi_button = tk.Button(left_frame, text="Disable Wi-Fi", command=toggle_wifi, bg=BUTTON_BG, fg=BUTTON_FG,
                        font=("Helvetica", 12), padx=20, pady=10, relief="flat", activebackground=BUTTON_ACTIVE_BG)
wifi_button.pack(pady=10)

# Right Panel (Notes)
right_frame = tk.Frame(main_frame, bg=BG_COLOR)
right_frame.grid(row=0, column=1, padx=20, sticky="nsew")

# Notes Label
notes_label = tk.Label(right_frame, text="Session Notes", bg=BG_COLOR, fg=FG_COLOR, font=("Helvetica", 14, "bold"))
notes_label.pack(pady=10)

# Notes Text Area
notes_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, width=40, height=20,
                                      bg=NOTES_BG, fg=NOTES_FG, insertbackground=FG_COLOR,
                                      font=("Helvetica", 12))
notes_text.pack(fill=tk.BOTH, expand=True)

# Load existing notes
try:
    with open("pomodoro_notes.txt", "r") as f:
        notes_text.insert(tk.END, f.read())
except FileNotFoundError:
    pass

# Save Notes Button
save_notes_btn = tk.Button(right_frame, text="Save Notes", command=save_notes,
                          bg=BUTTON_BG, fg=BUTTON_FG, font=("Helvetica", 12),
                          padx=15, pady=8, relief="flat", activebackground=BUTTON_ACTIVE_BG)
save_notes_btn.pack(pady=10)

# Configure grid weights
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)
main_frame.grid_rowconfigure(0, weight=1)

window.mainloop()
