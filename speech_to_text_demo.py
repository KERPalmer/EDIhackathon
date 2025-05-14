import requests
import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

# ElevenLabs API Key (Consider moving this to an environment variable for security)

load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")
URL = "https://api.elevenlabs.io/v1/speech-to-text"

def find_audio_file(target_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    for file in os.listdir(script_dir):
        if file.lower() == target_name.lower():
            return os.path.join(script_dir, file)  # Return full absolute path
    raise FileNotFoundError(f"Could not find a file matching '{target_name}' in {script_dir}")

AUDIO_FILE = find_audio_file('Test.m4a')

def speech_to_text():
    headers = {
        "xi-api-key": API_KEY,
    }
    data = {
        "model_id" : "scribe_v1"
    }

    with open(AUDIO_FILE, "rb") as audio_file:
        files = {
            "file": audio_file
        }
        response = requests.post(URL, headers=headers, data=data,  files=files)

    if response.status_code == 200:
        result = response.json()
        transcribed_text = result.get("text", "")
        print(f'text:{transcribed_text}')
        print(f"Response: {result}")
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    print("Starting transcription...")
    speech_to_text()
