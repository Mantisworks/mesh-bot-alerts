# Meshtastic Alert System Bot (Brindisi JN80XP)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Meshtastic](https://img.shields.io/badge/mesh-Meshtastic-green.svg)](https://meshtastic.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Uno script Python avanzato per integrare i nodi **LoraItalia** con servizi di monitoraggio ambientale e sismico in tempo reale. Progettato specificamente per la zona di **Brindisi**, gestisce allerte critiche e risponde a comandi interattivi sulla rete LoRa.

---

## 🇮🇹 Descrizione Progetto

Il gateway monitora le API dell'**INGV** e di **Open-Meteo**, fungendo da nodo informativo automatico. In caso di eventi avversi, invia notifiche sul canale Mesh per avvisare gli utenti locali.

### 🛠️ Logica di Funzionamento
* **Monitoraggio Sismico:** Controllo eventi INGV con Magnitudo > 3.0.
* **Standard Protezione Civile:** Allerte vento basate sulle soglie ufficiali (Gialla/Arancione/Rossa).
* **Analisi Propagazione:** Stima della qualità del segnale radio 868MHz basata su parametri troposferici.
* **Flood Control:** Limite di un'allerta automatica ogni 2 ore per preservare il Duty Cycle LoRa.

### 💬 Comandi Disponibili
| Comando | Descrizione |
| :--- | :--- |
| `!meteo` | Report meteo completo (Temp, Umidità, Pressione, Vento). |
| `!prop` | Analisi della propagazione radio (Ducting) sulla banda 868MHz. |
| `!ping` | Risponde con PONG e dati tecnici di ricezione (RSSI/SNR). |
| `!vicini` | Mostra il numero di nodi rilevati dal gateway. |

---

## 🇬🇧 Project Description

This script provides real-time monitoring of **INGV** seismic data and **Open-Meteo** weather services. It features an automated alert system and interactive radio propagation analysis.

### 🛠️ Key Features
* **Seismic & Wind Monitoring:** Automated alerts based on magnitude and wind speed.
* **Radio Propagation:** Estimates 868MHz signal enhancement (Tropospheric Ducting).
* **Bandwidth Management:** Built-in "Flood Control" to respect LoRa limits.

---

## 🚀 Requisiti e Installazione / Installation

### Requirements
* Python 3.8+
* Nodo Meshtastic connesso via USB (Serial)
* Librerie: `pip install meshtastic requests pypubsub psutil`

### Setup
1. **Clona la repository:**
```bash
git clone https://github.com/Mantisworks/mesh-bot-alerts.git


