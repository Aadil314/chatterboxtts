import torch
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
# from chatterbox.tts_turbo import ChatterboxTurboTTS
import re

AUDIO_PROMPT_PATH = "sample_1.wav"


def split_script(filename, min_chars=250):
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read().strip()

    # Initial split into individual sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    result = []
    buffer = ""

    for s in sentences:
        if buffer:
            buffer += " " + s
        else:
            buffer = s

        if len(buffer) >= min_chars:
            result.append(buffer)
            buffer = "" 

    if buffer:
        if result:
            result[-1] += " " + buffer
        else:
            result.append(buffer)

    return result

# print(split_script("full_script.txt"))


print("🚀 Initializing Chatterbox TTS model...")
model = ChatterboxTurboTTS.from_pretrained(device="cuda")
print("✅ Model loaded on CUDA")

segmented_texts = split_script("full_script.txt")

print("🔇 Preparing silence buffer (0.5s)")
silence = torch.zeros((1, int(model.sr * 0.5))).to("cuda")

# audio_segments = []

print(f"⏳ Starting synthesis ({len(segmented_texts)} segments)\n")

for i, text in enumerate(segmented_texts):
    print(f"🔊 Segment {i+1}/{len(segmented_texts)}")
    print(f"📝 Text: {text}███")
    print("🎙️ Synthesizing voice...")
    
    wav = model.generate(
        text,
        audio_prompt_path=AUDIO_PROMPT_PATH,
        exaggeration=0.3,
        cfg_weight=0.1,
        temperature=0.6
    )

    # audio_segments.append(wav.cpu())
    ta.save(f"segment_{i}.wav", wav, model.sr)

    print("✅ Segment synthesized\n")

    # if i < len(segmented_texts) - 1:
    #     audio_segments.append(silence)


# if audio_segments:
#     print("🔗 Concatenating audio segments...")
#     final_wav = torch.cat(audio_segments, dim=-1)

#     ta.save("sample_chunk.wav", final_wav.cpu(), model.sr)
#     print("🎉 Successfully saved final audio → sample_chunk.wav")
# else:
#     print("⚠️ No text segments found — nothing was generated")


# combined_audio = AudioSegment.empty()

# for i in range(len(segmented_texts)):
#     file_path = f"segment_{i}.wav"
#     if os.path.exists(file_path):
#         segment = AudioSegment.from_wav(file_path)
#         combined_audio += segment
        
#         if i < len(segmented_texts) - 1:
#             combined_audio += AudioSegment.silent(duration=500)

# combined_audio.export("final_output.wav", format="wav")
# print("📂 Final audio exported as final_output.wav")

# for i in range(len(segmented_texts)):
#     file_path = f"segment_{i}.wav"
#     if os.path.exists(file_path):
#         os.remove(file_path)
#         print(f"🗑️ Deleted {file_path}")
