# MQTT Server Applications and Scripts

This repository contains various applications and scripts related to the **MQTT** server. They can be used in a wide range of contexts, from smart home systems to security systems. The MQTT protocol is a lightweight and efficient protocol used for message exchange between IoT devices. These projects include various MQTT scenarios and functional applications.

## Project Contents

### 1. **guvenlikApp.py**: iCe Notification Panel
This application is a notification panel developed for **iCe** security systems. It provides a GUI interface using libraries such as **customtkinter** and **paho.mqtt.client**. This interface displays notifications based on incoming MQTT messages and provides audio alerts in critical situations.

#### Key Features:
- Establishing a connection with the MQTT client.
- Processing incoming messages in JSON format and forwarding them to relevant components.
- Displaying notifications through a user-friendly interface.
- Audio alarms for emergencies (using pygame).

#### Application Flow:
- When the application opens, it connects to the MQTT server and listens for messages from specified channels.
- Incoming messages are analyzed, and details like color and alert text are presented to the user through the GUI.
- In critical situations, users are informed via audio alerts and notifications.

---

### 2. **kutu_alert.py**: Box Alarm Notification
This script sends notifications to users by publishing MQTT messages under certain conditions. For example, it monitors changes in the status of a device or sensor data and communicates with the server based on these changes.

#### Key Features:
- Tracking status information by analyzing MQTT messages.
- Alarm and notification functions for significant situations.
- Parsing JSON-formatted messages to process detailed information.

#### Application Flow:
- When the script is run, it listens for messages from MQTT channels.
- It analyzes information like `color`, `ircom`, `irval` in the message content and generates status reports.
- In critical situations, notifications are sent to relevant parties.

## About Development
This repository will be useful for developers who want to learn about the MQTT protocol and adapt it to different scenarios. Each application or script is designed for use in real-time communication and automation systems. The applications are developed in the Python programming language and facilitate communication between devices using the MQTT protocol.
