import requests
from moviepy.editor import VideoFileClip, AudioFileClip
import os

# ElevenLabs API Key
API_KEY = "your_elevenlabs_api_key"

def generate_dubbed_audio(text, voice="Rachel", language="es"):  # Spanish as an example
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {"stability": 0.75, "similarity_boost": 0.75},
        "model_id": "eleven_multilingual_v2"
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        with open("dubbed_audio.mp3", "wb") as f:
            f.write(response.content)
        return "dubbed_audio.mp3"
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

def dub_video(video_path, translated_text):
    # Extract video without audio
    video = VideoFileClip(video_path).without_audio()
    
    # Generate dubbed audio
    audio_path = generate_dubbed_audio(translated_text)
    audio = AudioFileClip(audio_path)
    
    # Combine video with new audio
    final_video = video.set_audio(audio)
    output_path = "dubbed_video.mp4"
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    print(f"Dubbed video saved as {output_path}")

# Example usage
translated_text = "Hola, bienvenidos a nuestro canal de tecnología."  # Example Spanish translation
dub_video("input_video.mp4", translated_text)

