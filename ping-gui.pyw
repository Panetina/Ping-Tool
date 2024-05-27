import subprocess
import time
import matplotlib.pyplot as plt
import os
from threading import Thread, Lock
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import simpledialog

plt.style.use('fivethirtyeight')
plt.rcParams.update({'figure.autolayout': True})

log_lines = []
log_lock = Lock()

def ping_address(address):
    try:
        ping_output = subprocess.Popen(['ping', '-n', '1', address], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW).communicate()
        ping_output = ping_output[0].decode('utf-8').split('\n')
        for line in ping_output:
            if 'time=' in line:
                ping_time = float(line.split('time=')[1].split('ms')[0])
                return ping_time
    except Exception as e:
        pass
    return None

def update(frame, ping_times, time_stamps, line, address):
    global log_lines
    ping_time = ping_address(address)
    current_time = time.strftime('%H:%M:%S')
    if ping_time is not None:
        ping_times.append(ping_time)
        time_stamps.append(current_time)
        if len(ping_times) > 50:
            ping_times.pop(0)
            time_stamps.pop(0)
    else:
        ping_times.append(0)
        time_stamps.append(current_time)
        if len(ping_times) > 50:
            ping_times.pop(0)
            time_stamps.pop(0)

    line.set_data(range(len(ping_times)), ping_times)
    ax.set_xticks(range(len(time_stamps)))
    ax.set_xticklabels(time_stamps, rotation=90, ha='center', fontsize=6)
    plt.xlim(0, len(ping_times))
    plt.ylim(0, 50)

    log_line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {ping_time if ping_time is not None else 0} ms\n"
    with log_lock:
        log_lines.append(log_line)

    return line,

def log_writer(logfile):
    global log_lines
    while True:
        time.sleep(5)
        with log_lock:
            if log_lines:
                with open(logfile, 'a') as file:
                    file.writelines(log_lines)
                log_lines = []

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    popup = tk.Toplevel()
    popup.withdraw()

    width = int(popup.winfo_screenwidth() * 0.115)
    height = int(popup.winfo_screenheight() * 0.07)

    popup.geometry(f"{width}x{height}")

    x_pos = (popup.winfo_screenwidth() - width) // 2
    y_pos = (popup.winfo_screenheight() - height) // 2

    popup.geometry(f"+{x_pos}+{y_pos}")

    popup.configure(bg='#2E3440')
    popup.tk_setPalette(background='#2E3440', foreground='#D8DEE9')

    tk.Label(popup, text="Enter the address to ping:", bg='#2E3440', fg='#D8DEE9').pack()
    address_var = tk.StringVar()
    address_var.set("8.8.8.8")
    address_entry = tk.Entry(popup, textvariable=address_var, justify="center", bg='#4C566A', fg='#D8DEE9')
    address_entry.pack()

    def retrieve_input():
        global address
        address = address_entry.get()
        popup.destroy()

    confirm_button = tk.Button(popup, text="OK", command=retrieve_input, bg='#4C566A', fg='#D8DEE9')
    confirm_button.pack()

    popup.deiconify()
    
    popup.wait_window()

    if address:
        ping_times = []
        time_stamps = []

        output_folder = 'Output'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        logfile = os.path.join(output_folder, f'{address}_ping_output_{time.strftime("%Y%m%d_%H%M%S")}.txt')

        fig, ax = plt.subplots(figsize=(6, 4))
        line, = ax.plot([], [], marker='o')
        plt.xlabel('Timp (HH:MM:SS)')
        plt.ylabel('Ping (ms)')
        plt.title(f'Pinging the IP adress: {address}')
        plt.grid(True)
        
        fig.canvas.manager.set_window_title('Panetina - Ping Tool')  

        icon_path = 'icon.ico'
        if os.path.exists(icon_path):
            fig.canvas.manager.window.iconbitmap(icon_path)
        
        fig.canvas.toolbar.pack_forget()

        log_thread = Thread(target=log_writer, args=(logfile,), daemon=True)
        log_thread.start()

        ani = FuncAnimation(fig, update, fargs=(ping_times, time_stamps, line, address), interval=1000, cache_frame_data=False)

        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

        plt.show()
    else:
        print("No address entered. Exiting...")
