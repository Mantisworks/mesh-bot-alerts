# Meshtastic alert system bot (Brindisi JN80XP)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Meshtastic](https://img.shields.io/badge/mesh-Meshtastic-green.svg)](https://meshtastic.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Uno script Python avanzato per integrare i nodi **LoraItalia** con servizi di monitoraggio ambientale e sismico in tempo reale. Progettato specificamente per la zona di **Brindisi**, gestisce allerte critiche e risponde a comandi interattivi direttamente sulla rete LoRa.

---

## 🇮🇹 Descrizione Progetto

Il gateway monitora costantemente le API dell'**INGV** (terremoti) e di **Open-Meteo**, fungendo da nodo informativo per la comunità locale. In caso di eventi avversi, invia notifiche automatiche sul canale Mesh senza necessità di intervento umano.

### 🛠️ Logica di Funzionamento
* **Monitoraggio Sismico:** Controllo eventi INGV con Magnitudo > 3.0.
* **Standard Protezione Civile:** Gestione allerte vento basate sulle soglie ufficiali:
    * 🟡 **Gialla** (> 62 km/h)
    * 🟠 **Arancione** (> 88 km/h)
    * 🔴 **Rossa** (> 102 km/h)
* **Flood Control:** Sistema di prevenzione per evitare la saturazione della banda LoRa (max 1 allerta meteo ogni 2 ore).

### 💬 Comandi Disponibili
Gli utenti possono interagire con il nodo inviando i seguenti messaggi:
| Comando | Descrizione |
| :--- | :--- |
| `!meteo` | Report meteo completo di Brindisi (Temp, Umidità, Pressione, Vento). |
| `!ping` | Risponde con PONG e i dati tecnici della ricezione (RSSI/SNR). |
| `!vicini` | Mostra il numero di nodi rilevati nella tabella del dispositivo. |

---

## 🇬🇧 Project Description

This Python script turns a Meshtastic node into an automated information gateway. It provides real-time monitoring of **INGV** seismic data and **Open-Meteo** weather services for the **Brindisi** area.

### 🛠️ Key Features
* **Seismic Monitoring:** Real-time polling of INGV events (Magnitude > 3.0).
* **Wind Alert Standards:** Automated alerts based on Italian Civil Protection thresholds:
    * 🟡 **Yellow** (> 62 km/h - Gale)
    * 🟠 **Orange** (> 88 km/h - Storm)
    * 🔴 **Red** (> 102 km/h - Violent Storm/Hurricane)
* **Bandwidth Management:** Built-in "Flood Control" (max 1 weather alert every 2 hours) to respect LoRa duty cycles.

### 💬 User Commands
| Command | Description |
| :--- | :--- |
| `!meteo` | Detailed weather report for Brindisi. |
| `!ping` | Returns PONG along with signal metrics (RSSI/SNR). |
| `!vicini` | Shows the number of nodes stored in the device's nodeDB. |

---

## Requisiti e Installazione / Installation

### Requirements
* Python 3.8+
* Un nodo Meshtastic connesso via USB (Serial)
* Librerie necessarie:
    ```bash
    pip install meshtastic requests pypubsub psutil
    ```

### Setup
1. Clona la repository:
   ```bash
   git clone [https://github.com/Mantisworks/meshtastic-puglia-gateway.git](https://github.com/Mantisworks/meshtastic-puglia-gateway.git)
2. Configura la porta seriale nel file main.py:
   ```bash
   SERIAL_PORT = "/dev/ttyUSB0"  # Cambia in base al tuo sistema
3. Avvia lo script:
   ```bash
   nohup python3 mesh-bot-alerts.py &

## Personalizzazione Località / Localization

Lo script è preconfigurato per la città di **Brindisi**. Per cambiare la località del monitoraggio meteo, è necessario modificare le coordinate (Latitudine e Longitudine) all'interno delle funzioni dello script.

### 1. Trovare le coordinate
Puoi trovare le coordinate della tua città su Google Maps o tramite servizi come [LatLong.net](https://www.latlong.net/).

### 2. Modifica del Codice
Apri il file `mesh-bot-alerts.py` e cerca l'URL all'interno della funzione `get_weather_report()`. Sostituisci i valori di latitudine e longitudine con quelli della tua città:

```python
# Esempio per Brindisi: latitude=40.63&longitude=17.93
url = "[https://api.open-meteo.com/v1/forecast?latitude=XX.XX&longitude=YY.YY&current=](https://api.open-meteo.com/v1/forecast?latitude=XX.XX&longitude=YY.YY&current=)..."
