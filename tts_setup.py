
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from chatterbox.tts_turbo import ChatterboxTurboTTS

# English example
model = ChatterboxTTS.from_pretrained(device="cuda")
# model = ChatterboxTurboTTS.from_pretrained(device="cuda")

text = """
This was Roman law which set the minimum marriage age at 12 for girls as standard practice.
"""

wav = model.generate(text, exaggeration=0.7, cfg_weight=0.3)
ta.save("test-english.wav", wav, model.sr)


# If you want to synthesize with a different voice, specify the audio prompt
# AUDIO_PROMPT_PATH = "YOUR_FILE.wav"
# wav = model.generate(text, audio_prompt_path=AUDIO_PROMPT_PATH)
# ta.save("test-2.wav", wav, model.sr)


# from TTS.api import TTS

# # List available models
# print(TTS.list_models())

# # Load a model (example: XTTS v2 English)
# tts = TTS(model_name="tts_models/en/vctk/vits")

# # Generate audio
# tts.tts_to_file(text="Hello, this is a test narration.", file_path="test.wav")
