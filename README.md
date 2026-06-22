# Orion Humanoid Robot Assistant

Orion is a Raspberry Pi-based humanoid robot assistant created as my bachelor's final year capstone project. The robot uses voice input, camera vision, AI responses, text-to-speech, MQTT control, and Arduino movement commands.

The system allows the robot to listen to spoken questions, capture camera input, generate intelligent responses using OpenAI or Google Gemini, speak the answer out loud, and perform simple robot actions such as dancing or giving a high five.

## Features

* Voice recognition through a microphone
* Raspberry Pi camera vision
* AI responses using OpenAI GPT and Google Gemini
* Text-to-speech voice output
* Chat history saved locally
* MQTT mute/unmute control
* Bluetooth command control for robot movements
* USB fallback control for Arduino if Bluetooth fails
* Basic symbolic math integration using SymPy

## Hardware Used

* Raspberry Pi
* Raspberry Pi Camera
* Microphone
* Speaker
* Arduino or robot controller
* Bluetooth serial connection
* USB serial connection as backup
* Servo motors / humanoid robot body
* OLED display for robot eyes

## Robot Commands

The robot currently supports simple voice commands:

| Voice Command | Action                      | Sent Command |
| ------------- | --------------------------- | ------------ |
| "high five"   | Performs high five movement | `0`          |
| "dance"       | Performs dance movement     | `1`          |

The code first tries to send the movement command through Bluetooth. If Bluetooth fails, it automatically tries to send the command through USB using `/dev/ttyACM0`.

## Project Structure

```bash
orion_humanoid_robot/
├── main.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
└── arduino/
    └── ArduinoOledEyes/
        └── ArduinoOledEyes.ino
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Okassab/orion_humanoid_robot.git
cd orion_humanoid_robot
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Some Raspberry Pi packages, such as `picamera2` and `pyaudio`, may require system-level installation depending on your Raspberry Pi OS.

### 4. Create the environment file

Copy the example environment file:

```bash
cp .env.example .env
```

Then add your API keys inside `.env`:

```text
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
```

Do not upload your `.env` file to GitHub.

### 5. Run the project

```bash
python3 main.py
```

## How It Works

1. The Raspberry Pi starts the camera stream.
2. The microphone listens for speech in the background.
3. The spoken input is converted into text.
4. If the input is a robot command, such as "dance" or "high five", the command is sent to the Arduino.
5. If the input is a question, the assistant sends the prompt and camera image to an AI model.
6. The response is printed, saved to local history, published through MQTT, and spoken out loud using text-to-speech.

## MQTT Control

The project includes MQTT mute/unmute support.

Default MQTT settings:

```python
MQTT_HOST = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_MUTE_TOPIC = "orion/muteunmute"
MQTT_RESPONSE_TOPIC = "ORION/78908030"
```

Publishing `mute` to the mute topic will mute the microphone.
Publishing `unmute` will allow the microphone to listen again.

## Arduino OLED Eyes

The `arduino/ArduinoOledEyes/ArduinoOledEyes.ino` file controls the OLED eye animation for the robot face.

## Notes

This project was created as a final year humanoid robot project. The code is designed for Raspberry Pi hardware and may need small adjustments depending on the camera, microphone, speaker, Arduino port, or Bluetooth setup being used.

## Author

Created by Omar Kassab.
