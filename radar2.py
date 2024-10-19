import subprocess
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import math
import random
import re

# Fungsi untuk mendapatkan detail jaringan Wi-Fi di sekitar
def get_wifi_signal_details():
    try:
        command = "netsh wlan show networks mode=bssid"
        results = subprocess.check_output(command, shell=True, text=True).splitlines()

        # Debug: print hasil dari perintah netsh untuk melihat format output
        for line in results:
            print(line)

        wifi_details = {}
        ssid = ""
        for line in results:
            line = line.strip()
            if line.startswith("SSID") and "BSSID" not in line:
                ssid = line.split(":")[1].strip()
                wifi_details[ssid] = {}
            elif "Signal" in line:
                signal_strength = line.split(":")[1].strip()
                wifi_details[ssid]["Signal"] = signal_strength
            elif "BSSID" in line:
                bssid = line.split(":")[1].strip()
                wifi_details[ssid]["BSSID"] = bssid
            elif "Network type" in line:
                wifi_details[ssid]["Type"] = line.split(":")[1].strip()
            elif "Radio type" in line:
                wifi_details[ssid]["Band"] = line.split(":")[1].strip()
            elif "Channel" in line:
                wifi_details[ssid]["Channel"] = line.split(":")[1].strip()
            elif "Speed" in line:
                wifi_details[ssid]["Speed"] = line.split(":")[1].strip()

        return wifi_details
    except subprocess.CalledProcessError as e:
        print("Error fetching Wi-Fi signal details: ", e)
        return {}


# Fungsi untuk mendapatkan informasi IP dan lainnya dari `ipconfig`
def get_ip_details():
    try:
        command = "ipconfig"
        results = subprocess.check_output(command, shell=True, text=True)
        ipv4 = re.findall(r"IPv4 Address[. ]*: (\d+\.\d+\.\d+\.\d+)", results)
        return ipv4[0] if ipv4 else "N/A"
    except subprocess.CalledProcessError as e:
        print("Error fetching IP details: ", e)
        return "N/A"

# Inisialisasi grafik radar
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.set_ylim(0, 100)  # Radius maksimum untuk radar (representasi kekuatan sinyal 0-100%)

# Garis lingkaran pada radar
ax.set_yticks([100, 80, 60, 40, 20])  # Marking the radial ticks for signal strength
ax.set_yticklabels(['100%', '80%', '60%', '40%', '20%'])

# Daftar jaringan yang akan ditampilkan di radar
wifi_points = []
wifi_details_map = {}

# Fungsi untuk memperbarui visualisasi radar
def update(frame):
    global wifi_points
    ax.clear()  # Bersihkan radar setiap kali memperbarui
    ax.set_ylim(0, 100)
    
    # Garis lingkaran pada radar
    ax.set_yticks([100, 80, 60, 40, 20])  # Marking the radial ticks for signal strength
    ax.set_yticklabels(['100%', '80%', '60%', '40%', '20%'])

    # Sudut dari "scan" radar yang akan berputar
    theta = np.deg2rad(frame % 360)

    # Jalankan pemindaian Wi-Fi setiap beberapa frame
    if frame % 60 == 0:
        wifi_points = []
        wifi_details_map.clear()
        wifi_details = get_wifi_signal_details()
        
        # Tentukan posisi jaringan berdasarkan sudut acak dan radius (kekuatan sinyal)
        for ssid, details in wifi_details.items():
            signal = int(details.get("Signal", "0").replace("%", ""))
            angle = random.uniform(0, 2 * math.pi)  # Acak sudut untuk jaringan
            wifi_points.append((angle, signal, ssid))  # Tambahkan titik jaringan di radar
            wifi_details_map[ssid] = details  # Simpan detail untuk setiap SSID

    # Tampilkan radar scan (garis bergerak)
    ax.plot([theta, theta], [0, 100], color='green', lw=2)

    # Tampilkan jaringan Wi-Fi di sekitar sebagai titik pada radar
    for point in wifi_points:
        angle, radius, ssid = point
        ax.scatter(angle, radius, c='red')  # Titik Wi-Fi
        ax.text(angle, radius, ssid, fontsize=8, ha='right', picker=True)  # Nama SSID, set picker=True for interaction

# Fungsi untuk menangani klik pada teks (SSID)
def on_click(event):
    if event.artist:
        # Dapatkan teks SSID yang diklik
        ssid = event.artist.get_text()
        # Tampilkan informasi jaringan yang sesuai
        if ssid in wifi_details_map:
            details = wifi_details_map[ssid]
            ip_address = get_ip_details()  # Ambil detail IP
            print(f"SSID: {ssid}")
            print(f"Signal: {details.get('Signal', 'N/A')}")
            print(f"BSSID: {details.get('BSSID', 'N/A')}")
            print(f"Type: {details.get('Type', 'N/A')}")
            print(f"Band: {details.get('Band', 'N/A')}")
            print(f"Channel: {details.get('Channel', 'N/A')}")
            print(f"Speed: {details.get('Speed', 'N/A')}")
            print(f"IP Address: {ip_address}")
            print()

# Fungsi animasi untuk membuat radar berputar dan memperbarui data
ani = FuncAnimation(fig, update, frames=np.arange(0, 360), interval=100)

# Hubungkan event klik dengan fungsi on_click
fig.canvas.mpl_connect('pick_event', on_click)

plt.show()
