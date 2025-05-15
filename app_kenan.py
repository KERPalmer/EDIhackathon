import requests
import time
import os
from dotenv import load_dotenv

#load env variables
load_dotenv()


API_KEY = os.getenv("ELEVENLABS_API_KEY")

S2T_URL = "https://api.elevenlabs.io/v1/speech-to-text"
DUB_URL = "https://api.elevenlabs.io/v1/dubbing"
STATUS_URL_TEMPLATE = "https://api.elevenlabs.io/v1/dubbing/{}"
DUBBED_DOWNLOAD_URL = "https://api.elevenlabs.io/v1/dubbing/{}/audio/{}"


def find_audio_file(target_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    for file in os.listdir(script_dir):
        if file.lower() == target_name.lower():
            return os.path.join(script_dir, file)  # Return full absolute path
    raise FileNotFoundError(f"Could not find a file matching '{target_name}' in {script_dir}")

AUDIO_FILE = find_audio_file('final.m4a')


def remove_disfluencies(text) -> str:
    return text


def send_dub(file):
    headers = {
        "xi-api-key": API_KEY
    }

    with open(file, "rb") as audio:
        files = {
            "file": ("test2.m4a", audio, "audio/mpeg"),
        }
        data = {
            "target_lang": "es",
            "watermark" : False
        }
        response = requests.post(DUB_URL, headers=headers, data=data, files=files).json()

        if "dubbing_id" in response:
            dubbing_id = response["dubbing_id"]
            status_url = STATUS_URL_TEMPLATE.format(dubbing_id)
            print(f"dub url: {status_url}")
            return wait_for_completion_and_download(status_url, API_KEY)
             
        else:
            print("No dubbing_id found. Dubbing job was not started successfully.")

def wait_for_completion_and_download(status_url, api_key):
    headers = {
        "xi-api-key": api_key
    }

    print("Waiting for dubbing to complete...")

    while True:
        response = requests.get(status_url, headers=headers)
        status_data = response.json()
        print("Status Check:", status_data)

        status = status_data.get("status")
        if status == "dubbed":
            download_url = status_url+"/audio/es"
            if download_url:
                return download_dubbed_file(download_url)
            else:
                print("Dubbing completed but no download URL found.")
            break
        elif status == "failed":
            print("Dubbing failed.")
            break
        else:
            # Still processing, wait and try again
            time.sleep(5)  # Check every 5 seconds

def download_dubbed_file(download_url):

    output_filename = "dubbed_output.mp3"
    print(f"Downloading dubbed file from {download_url}...")

    download_response = requests.get(download_url)
    with open(output_filename, "wb") as f:
        f.write(download_response.content)

    print(f"Dubbed file downloaded as '{output_filename}'.")
    return output_filename


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
        #print(f"Response: {result}")
        return transcribed_text
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")


def conversion_pipeline():

    text = send_S2T(AUDIO_FILE)

    # Get audio file of input speech
    file_name = send_dub(AUDIO_FILE)
    # Convert Dub Audio To Speech
    text = send_S2T(file_name)
    return text


if __name__ == "__main__":
    conversion_pipeline()
