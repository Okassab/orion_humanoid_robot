import base64
import cv2
import openai
import serial
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
from picamera2 import Picamera2 
from sympy import symbols, integrate , sympify
from threading import Lock, Thread, Event 
from pyaudio import PyAudio, paInt16
from speech_recognition import Recognizer, Microphone, UnknownValueError
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.messages import SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY is missing. Add it to your .env file.")

# If Bluetooth does not work, use this to connect it by USB
ARDUINO_PORT = "/dev/ttyACM0"

print("Working directory:", os.getcwd())

MUTED = False

BLUETOOTH_PORT = "/dev/rfcomm0"
BLUETOOTH_BAUDRATE = 9600

MQTT_HOST = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_MUTE_TOPIC = "orion/muteunmute"
MQTT_RESPONSE_TOPIC = "ORION/78908030"

#######################################################################################################

#######################################################################################################

openai_model = ChatOpenAI(
    model="gpt-4o",
    openai_api_key=openai_api_key
)

google_model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    api_key=google_api_key
)

#######################################################################################################

#######################################################################################################

HIGH_FIVE_COMMAND = "0"
DANCE_COMMAND = "1"

def send_robot_command(command):
    try:
        with serial.Serial(BLUETOOTH_PORT, BLUETOOTH_BAUDRATE) as bt:
            bt.write(command.encode())
            print(f"Sent over Bluetooth: {command}")
    except serial.SerialException:
        print("Bluetooth failed. Trying USB...")
        try:
            with serial.Serial(ARDUINO_PORT, BLUETOOTH_BAUDRATE) as arduino:
                arduino.write(command.encode())
                print(f"Sent over USB: {command}")
        except serial.SerialException as e:
            print(f"Both Bluetooth and USB failed: {e}")

def detect_best_model(prompt):
    prompt = prompt.lower()
    if any(keyword in prompt for keyword in ["search", "define", "news", "fact", "today", "what is"]):
        return "google"
    return "openai"
    
def load_chat_history_from_file(filepath="history.txt"):
    history = ChatMessageHistory()
    if not os.path.exists(filepath):
        return history

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    user_msg, assistant_msg = "", ""
    for line in lines:
        if line.startswith("User:"):
            user_msg = line[len("User:"):].strip()
        elif line.startswith("Assistant:"):
            assistant_msg = line[len("Assistant:"):].strip()
            if user_msg and assistant_msg:
                history.add_user_message(user_msg)
                history.add_ai_message(assistant_msg)
                user_msg, assistant_msg = "", ""
    return history

shared_chat_history = load_chat_history_from_file()

def get_assistant(preferred_model):
    if preferred_model == "google":
        return Assistant(google_model, shared_chat_history)
    else:
        return Assistant(openai_model, shared_chat_history)

def send_mqtt_message(topic, message, host=MQTT_HOST, port=MQTT_PORT):
    client = mqtt.Client(protocol=mqtt.MQTTv311)  # MQTT v3.1.1 (protocol version 4)
    try:
        client.connect(host, port, 60)
        client.publish(topic, message)
        client.disconnect()
    except Exception as e:
        print(f"mqtt error: {e}")

def on_mqtt_message(client, userdata, msg):
    global MUTED
    try:
        if msg.topic == MQTT_MUTE_TOPIC:
            payload = msg.payload.decode().strip().lower()
            if payload == "mute":
                MUTED = True
                print("Microphone muted via MQTT.")
            elif payload == "unmute":
                MUTED = False
                print("Microphone unmuted via MQTT.")
    except Exception as e:
        print(f"MQTT message handling error: {e}")

def setup_mqtt_listener():
    client = mqtt.Client()
    client.on_message = on_mqtt_message
    try:
        client.connect(MQTT_HOST, MQTT_PORT)
        client.subscribe(MQTT_MUTE_TOPIC)
        client.loop_start()
        print("MQTT listener for mute/unmute started.")
    except Exception as e:
        print(f"MQTT setup error: {e}")

def solve_integration(expression: str, variable: str = 'x'):
    try:
        x = symbols(variable)
        expr = sympify(expression)
        result = integrate(expr, x)
        return str(result)
    except Exception as e:
        return f"Error solving integration: {e}"

def audio_callback(recognizer, audio):
    
    try:
        if MUTED:

            print("Microphone Muted")
            return
        prompt = recognizer.recognize_google(audio)

        # Arduino/Bluetooth commands:
        # '0' = high five movement
        # '1' = dance movement

        if "high five" in prompt.lower():
            send_robot_command(HIGH_FIVE_COMMAND)
            return
            
        if "dance" in prompt.lower():
            send_robot_command(DANCE_COMMAND)
            return
        
        # print(f"[DEBUG] Heard: {prompt}")
        preferred_model = detect_best_model(prompt)
        assistant = get_assistant(preferred_model)
        assistant.answer(prompt, webcam_stream.read(encode=True))

    except UnknownValueError:
            pass

#######################################################################################################

#######################################################################################################

class WebcamStream:

    def __init__(self):
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(main={"format": "RGB888", "size": (1280, 720)})

        # config["crop"] = (0 , 0 , 1 , 1)
        self.picam2.configure(config)

        self.frame = None
        self.running = False
        self.lock = Lock()
        self.stop_event = Event()

    def start(self):
        self.picam2.start()
        self.running = True
        self.thread = Thread(target=self.update, daemon=True)
        self.thread.start()
        return self

    def update(self):
        while not self.stop_event.is_set():
            frame = self.picam2.capture_array()
            with self.lock:
                self.frame = frame

    def read(self, encode=False):
        with self.lock:
            frame = self.frame.copy() if self.frame is not None else None

        if encode and frame is not None:
            _, buffer = cv2.imencode(".jpeg", frame)
            return base64.b64encode(buffer)

        return frame

    def stop(self):
        self.stop_event.set()
        self.running = False
        self.picam2.stop()

#######################################################################################################

#######################################################################################################

class Assistant:

    """AI Assistant for generating responses based on user prompts and webcam input."""

    def __init__(self, model, chat_message_history):

        self.chat_message_history = chat_message_history
        self.chain = self._create_inference_chain(model)

    def answer(self, prompt, image):

        """Generates an answer based on the prompt and image."""

        if not prompt:
            return
          
        # Check for integration request
        if "integrate" in prompt.lower():
            try:
                # Extract the expression after "integrate"
                expr = prompt.lower().split("integrate", 1)[1].strip()
                result = solve_integration(expr)
                response = f"The integral of {expr} is: {result}"
            except Exception as e:
                response = f"Could not solve integration: {e}"
        else:
          print("User:", prompt)
          response = self.chain.invoke(
              {"prompt": prompt, "image_base64": image.decode() if image else ""},  #  CHANGED HERE PRT 1
              config={"configurable": {"session_id": "unused"}}
          ).strip()

        print("Orion:", response)

        # Save prompt and response to history.txt
        with open("history.txt", "a", encoding="utf-8") as f:
          f.write(f"User: {prompt}\nAssistant: {response}\n\n")
        print("Saved to history.txt")

        if response:
            send_mqtt_message(MQTT_RESPONSE_TOPIC, response)
            self._tts(response)

    def _tts(self, response):
        """Speaks response and moves servo motor at the same time."""

        openai.api_key = openai_api_key
        audio_stream = PyAudio().open(format=paInt16, channels=1, rate=24000, output=True)


        try:
            with openai.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="alloy",
                response_format="pcm",
                input=response
            ) as stream:
                for chunk in stream.iter_bytes(chunk_size=1024):
                    audio_stream.write(chunk)

        finally:
            # Stop the servo right after speech ends
            # stop_event.set()
            # servo_thread.join()
            audio_stream.close()


    def _create_inference_chain(self, model):

        """Creates a chain for inference using Langchain and the selected model."""
        

        SYSTEM_PROMPT = """
        You are Orion, a witty but intelligent math tutor for students.

        You're friendly, speak informally, and love helping with math problems, even tricky ones.

        If the user asks for help with a math topic, explain it clearly and give a simple example. If they ask for the answer only, give it briefly.

        Sometimes joke a little when appropriate. Don't be too formal.

        If the user asks a fun or random question, feel free to be playful and show personality.

        Avoid using emojis. Keep answers short unless explanation is needed.

        Don't mention the webcam image unless it's directly relevant to the question.

        """
        prompt_template = ChatPromptTemplate.from_messages(

            [
                SystemMessage(content=SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "human",
                    [
                        {"type": "text", "text": "{prompt}"},
                        {"type": "image_url", "image_url": "data:image/jpeg;base64,{image_base64}"},
                    ],
                ),
            ]
        )


        chain = prompt_template | model | StrOutputParser()
        # chat_message_history = ChatMessageHistory()


        return RunnableWithMessageHistory(
            chain,
            lambda _: self.chat_message_history,  # <-- use existing history
            input_messages_key="prompt",
            history_messages_key="chat_history"
        )
        

#######################################################################################################

#######################################################################################################

def main():
    global webcam_stream

    # Initialize the webcam stream
    webcam_stream = WebcamStream().start()

    # Start MQTT listener
    setup_mqtt_listener()

    # Set up speech recognizer
    recognizer = Recognizer()
    microphone = Microphone()

    # Adjust for ambient noise
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)

    # Start listening for audio input
    stop_listening = recognizer.listen_in_background(microphone, audio_callback)

    try:
        while True:
            frame = webcam_stream.read()

            if frame is not None:
                cv2.imshow("Webcam", frame)

            key = cv2.waitKey(1)

            if key in [27, ord("q")]:
                break

    finally:
        webcam_stream.stop()
        cv2.destroyAllWindows()
        stop_listening(wait_for_stop=False)


if __name__ == "__main__":
    main()

