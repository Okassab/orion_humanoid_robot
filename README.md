# Orion Humanoid Robot Assistant -                                                                                                       Jan. 2025 - May. 2025

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
* Arduino
* Bluetooth serial connection
* USB serial connection as backup
* Servo motors
* 3D printed humanoid robot body
* OLED display for robot eyes

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

## Author

Created by Omar Kassab
