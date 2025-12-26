from google import genai
from google.genai import types
import wave
import time
import random

entry = "4"

entries = [1]

txt_data = {
    f"{entry}-{e}.wav": open(f"{e}.txt", "r", encoding="utf-8").read() 
    for e in entries
}

# Set up the wave file to save the output:
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
   with wave.open(filename, "wb") as wf:
      wf.setnchannels(channels)
      wf.setsampwidth(sample_width)
      wf.setframerate(rate)
      wf.writeframes(pcm)

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key="AIzaSyDnxteCvHyAYnGLXQyV86v2QycZx2hnolo")
# AIzaSyDnxteCvHyAYnGLXQyV86v2QycZx2hnolo
# AIzaSyAvYRr8bq1q42_M5Q0QRsFB-_RY0iy6bFE

# Configuration for Retries
MAX_RETRIES = 5
BASE_DELAY = 2  # Seconds

for file_nm, speech in txt_data.items():
    print(f"Generating {file_nm}...")
    
    success = False
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=f"Read aloud in a warm and friendly tone: {speech}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name='Enceladus',
                            )
                        )
                    ),
                )
            )

            # Extract audio data
            data = response.candidates[0].content.parts[0].inline_data.data
            
            # Save the file
            file_path = f"D:/coinandchronicle/Audio/{file_nm}"
            wave_file(file_path, data)
            
            print(f"✅ Completed {file_nm}")
            success = True
            break  # Exit the retry loop on success

        except Exception as e:
            # Check if we should retry (e.g., Rate Limits or Server Errors)
            wait_time = (BASE_DELAY * (4 ** attempt)) + random.uniform(0, 1)
            
            print(f"⚠️ Error on attempt {attempt + 1} for {file_nm}: {e}")
            
            if attempt < MAX_RETRIES - 1:
                print(f"🔄 Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                print(f"❌ Failed to process {file_nm} after {MAX_RETRIES} attempts.")

    # Optional: Small breather between different files to avoid hitting limits
    time.sleep(1)