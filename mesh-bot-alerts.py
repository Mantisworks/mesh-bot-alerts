
import os
import threading
import time
import requests
import psutil
import subprocess
import meshtastic
import meshtastic.serial_interface
from pubsub import pub
from datetime import datetime

# --- CONFIG ---
SERIAL_PORT = "/dev/ttyUSB0"
CH_INDEX = 1
CITY = "Brindisi"
REGION = "Puglia"
LATITUDE = 40.63
LONGITUDE = 17.93


interface = None
is_connected = False
last_earthquake_id = None
last_weather_alert_time = 0  # Timestamp forecast alerts limit

def log_debug(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

# --- WIND LOGIC ---
def get_wind_alert_level(speed_kmh):
    """
    Standard indicativi Protezione Civile per raffiche/vento:
    Gialla: > 62 km/h (Burrasca)
    Arancione: > 88 km/h (Tempesta)
    Rossa: > 102 km/h (Uragano/Violenta Tempesta)
    """
    if speed_kmh >= 102:
        return "🔴 ALLERTA ROSSA (Vento Estremo)"
    elif speed_kmh >= 88:
        return "🟠 ALLERTA ARANCIONE (Vento Intenso)"
    elif speed_kmh >= 62:
        return "🟡 ALLERTA GIALLA (Vento Forte)"
    return None

# --- WEATHER FORECAST LOGIC ---
def get_weather_report(full=True):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,relative_humidity_2m,weather_code,surface_pressure,wind_speed_10m,wind_gusts_10m"
        d = requests.get(url, timeout=10).json()["current"]
        code = d['weather_code']

        # Icons
        if code == 0: sky = "Sereno ☀️"
        elif code in [1, 2, 3]: sky = "Poco Nuvoloso 🌤"
        elif code in [51, 53, 55, 61, 63, 65]: sky = "Pioggia 🌧"
        elif code >= 95: sky = "Temporale ⛈"
        else: sky = "Nuvoloso ☁️"

        report = (f"📍 Meteo {CITY}\n"
                  f"🌡 Temp: {d['temperature_2m']}°C\n"
                  f"☁️ Cielo: {sky}\n"
                  f"💧 Umidità: {d['relative_humidity_2m']}%\n"
                  f"💨 Vento: {d['wind_speed_10m']} km/h")

        if full:
            report += (f"\n🌪 Raffiche: {d['wind_gusts_10m']} km/h\n"
                       f"⏲ Press: {d['surface_pressure']} hPa")

        return report, d
    except: return "⚠️ Meteo non disponibile.", None

# --- MONITOR (EARTHQUAKE + WEATHER/WIND) ---
def auto_monitor_task():
    global last_earthquake_id, last_weather_alert_time
    log_debug("MONITOR: Avvio thread automatico (Sisma + Meteo + Vento).")
    while True:
        if is_connected and interface:
            # 1. Controllo Terremoti
            try:
                eq_url = "https://webservices.ingv.it/fdsnws/event/1/query?format=json&minmag=3.0&limit=1"
                eq_res = requests.get(eq_url, timeout=10).json()
                if "features" in eq_res and len(eq_res["features"]) > 0:
                    eq = eq_res["features"][0]
                    if eq["id"] != last_earthquake_id:
                        p = eq["properties"]
                        msg = f"⚠️ ALERT SISMA INGV\n📊 Mag: {p['mag']}\n📍 {p['place']}\n📢 Nodo Mesh {CITY}"
                        interface.sendText(msg, channelIndex=CH_INDEX)
                        last_earthquake_id = eq["id"]
            except: pass

            # 2. Controllo Meteo e Vento (Standard Prot. Civile)
            try:
                current_time = time.time()
                if (current_time - last_weather_alert_time) > 7200:
                    _, w_data = get_weather_report()
                    if w_data:
                        alert_sent = False

                        # Controllo Vento (Raffiche)
                        wind_level = get_wind_alert_level(w_data['wind_gusts_10m'])

                        if wind_level:
                            msg = f"⚠️ {wind_level}\n🌪 Raffica: {w_data['wind_gusts_10m']} km/h\n📍 Zona {CITY}"
                            interface.sendText(msg, channelIndex=CH_INDEX)
                            alert_sent = True

                        # Controllo Pioggia (se non è già partito l'allerta vento)
                        elif w_data['weather_code'] >= 51:
                            interface.sendText(f"⚠️ ALERT {REGION}: Pioggia o Temporale a {CITY}! 🌧", channelIndex=CH_INDEX)
                            alert_sent = True

                        if alert_sent:
                            last_weather_alert_time = current_time
                            log_debug("MONITOR: Alert critico inviato su MeshTastic.")
            except: pass

        time.sleep(900) # Check ogni 15 minuti

# --- CALLBACK RICEZIONE ---
def on_receive(packet, interface):
    try:
        if 'decoded' not in packet: return
        sender_id = packet.get('fromId') or f"!{hex(packet.get('from', 0))[2:]}"

        meta = packet.get('rx_metadata') or (packet.get('rx_metadata_list')[0] if packet.get('rx_metadata_list') else {})
        rssi, snr = meta.get('rssi'), meta.get('snr')
        is_local = 'rx_metadata' in packet
        tag = "📡 RF" if is_local else "🌐 MQTT"

        decoded = packet.get('decoded', {})
        if decoded.get('portnum') != 'TEXT_MESSAGE_APP': return
        payload = str(decoded.get('text', '')).strip()
        payload_l = payload.lower()
        ch = packet.get('channel', 0)

        log_debug(f"IN: {sender_id} -> {payload} [{tag}]")

        if payload_l.startswith("!"):
            if "!meteo" in payload_l:
                report, _ = get_weather_report(full=True)
                interface.sendText(report, channelIndex=ch)

            elif "!ping" in payload_l:
                interface.sendText(f"🏓 PONG!\n👤 {sender_id}\n📶 RSSI: {rssi or 'N/D'}\n📡 SNR: {snr or 'N/D'}", channelIndex=ch)

            elif "!vicini" in payload_l:
                n_count = len(interface.nodes) if interface.nodes else 0
                interface.sendText(f"👥 Nodi: {n_count}\n📍 Monitor Sisma/Vento attivo.", channelIndex=ch)

            elif "!prop" in payload_l:
                prog_msg = get_radio_propagation()
                interface.sendText(prog_msg, channelIndex=ch)

    except Exception as e: log_debug(f"ERR: {e}")

def get_radio_propagation():
    try:
        # Recuperiamo dati di pressione e umidità
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current=relative_humidity_2m,surface_pressure,is_day&hourly=pressure_msl"
        d = requests.get(url, timeout=10).json()
        curr = d["current"]

        pres = curr['surface_pressure']
        hum = curr['relative_humidity_2m']

        # Logica semplificata basata su parametri di propagazione troposferica:
        # Alta pressione (>1020 hPa) e alta umidità favoriscono il ducting
        if pres > 1020 and hum > 70:
            status = "Eccellente (Ducting probabile) 🚀"
            desc = "Possibile copertura extra-orizzonte."
        elif pres > 1013:
            status = "Buona (Stabile) 📈"
            desc = "Segnale stabile entro il raggio visivo."
        else:
            status = "Standard (Instabile) ☁️"
            desc = "Propagazione limitata dalle condizioni meteo."

        report = (f"📡 PROPAGAZIONE 868MHz\n"
                  f"📊 Stato: {status}\n"
                  f"⏲ Press: {pres} hPa\n"
                  f"💧 Umidità: {hum}%\n"
                  f"📝 {desc}")
        return report
    except:
        return "⚠️ Dati propagazione non disponibili."

# --- START UP ---
def connect_and_monitor():
    global interface, is_connected
    while True:
        if not is_connected:
            try:
                subprocess.run(["fuser", "-k", SERIAL_PORT], capture_output=True)
                interface = meshtastic.serial_interface.SerialInterface(devPath=SERIAL_PORT, noNodes=True)
                threading.Thread(target=lambda: (time.sleep(10), interface.showNodes()), daemon=True).start()
                time.sleep(5)
                pub.subscribe(on_receive, "meshtastic.receive")
                is_connected = True
                log_debug("SERIALE: ✅ Connessione attiva.")
            except: is_connected = False; time.sleep(15)
        else:
            try:
                time.sleep(60)
                if not interface or interface.noProto: raise Exception()
            except: is_connected = False
        time.sleep(1)

log_debug("=== AVVIO MESH-GATEWAY V10 (SOLO MESH) ===")
threading.Thread(target=auto_monitor_task, daemon=True).start()
connect_and_monitor()
