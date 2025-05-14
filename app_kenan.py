import requests
import os
from dotenv import load_dotenv

#load env variables
load_dotenv()


API_KEY = os.getenv("ELEVENLABS_API_KEY")

S2T_URL = "https://api.elevenlabs.io/v1/speech-to-text"
DUB_URL = "https://api.elevenlabs.io/v1/dubbing"

def find_audio_file(target_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    for file in os.listdir(script_dir):
        if file.lower() == target_name.lower():
            return os.path.join(script_dir, file)  # Return full absolute path
    raise FileNotFoundError(f"Could not find a file matching '{target_name}' in {script_dir}")

AUDIO_FILE = find_audio_file('Test2.m4a')


def remove_disfluencies(text) -> str:
    return text



def send_dub():
    headers = {
        "xi-api-key": API_KEY
    }

    with open(AUDIO_FILE, "rb") as audio:
        files = {
            "file": ("test2.m4a", audio, "audio/mpeg"),
        }
        data = {
            "target_lang": "es",
            "watermark" : True
        }
        response = requests.post(DUB_URL, headers=headers, data=data, files=files)
        print(response.json())


def send_S2T(file=None) -> str:

    headers = {
        "xi-api-key": API_KEY,
    }
    data = {
        "model_id" : "scribe_v1"
    }
    with open(file, "rb") as audio:
        files = {
            "file": audio
        }
        response = requests.post(S2T_URL, headers=headers, data=data,  files=files)

    if response.status_code == 200:
        result = response.json()
        transcribed_text = result.get("text", "")
        print(f'text:{transcribed_text}')
        print(f"Response: {result}")
        return transcribed_text
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")


def conversion_pipeline():
    # Get audio file of input speech

    # Convert to Dub

    # Remove disfluencies (uh, um, err, etc)

    # Convert Dub Audio To Speech

    return None


if __name__ == "__main__":
    send_dub()
