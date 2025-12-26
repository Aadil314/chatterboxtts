import os
import torch
import torchaudio

# -----------------------------
# Configuration
# -----------------------------
NUM_SEGMENTS = 2               # number of segment_*.wav files
MAX_PAUSE_SEC = 0.7            # safety cap
MIN_PAUSE_SEC = 0.25           # minimum human pause

# -----------------------------
# Helper functions
# -----------------------------
def rms_energy(waveform: torch.Tensor) -> float:
    """Compute RMS energy of waveform."""
    return waveform.pow(2).mean().sqrt().item()


def crossfade(a, b, sr, fade_ms=80):
    fade_samples = int(sr * fade_ms / 1000)

    fade_out = torch.linspace(1.0, 0.0, fade_samples)
    fade_in  = torch.linspace(0.0, 1.0, fade_samples)

    a_end = a[:, -fade_samples:] * fade_out
    b_start = b[:, :fade_samples] * fade_in

    blended = a_end + b_start

    return torch.cat([
        a[:, :-fade_samples],
        blended,
        b[:, fade_samples:]
    ], dim=1)

def room_tone(num_channels, pause_sec, sr, noise_level=0.001):
    samples = int(sr * pause_sec)

    # Gaussian noise as room tone
    tone = torch.randn((num_channels, samples)) * noise_level

    # Very gentle fade-in (prevents click)
    fade_samples = int(sr * 0.05)
    fade = torch.linspace(0.0, 1.0, fade_samples)
    tone[:, :fade_samples] *= fade

    return tone

def generate_room_tone(duration_sec, sr, noise_level=0.0008):
    samples = int(sr * duration_sec)

    # Start with white noise
    noise = torch.randn(1, samples) * noise_level

    # Low-pass filter to remove hiss (very important)
    noise = torchaudio.functional.lowpass_biquad(
        noise,
        sr,
        cutoff_freq=3500
    )

    return noise

def room_tone_slice(room_tone, start_sample, length):
    return room_tone[:, start_sample:start_sample + length]

def shaped_silence(num_channels, pause_sec, sr, fade_in_ms=60):
    total_samples = int(sr * pause_sec)
    silence = torch.zeros((num_channels, total_samples))

    fade_samples = int(sr * fade_in_ms / 1000)
    fade_in = torch.linspace(0.0, 1.0, fade_samples)

    silence[:, :fade_samples] *= fade_in
    return silence

def pause_from_energy(waveform: torch.Tensor, sr: int) -> float:
    """
    Compute natural pause duration based on:
    - segment duration
    - audio energy (emphasis/emotion)
    """
    duration = waveform.shape[1] / sr
    energy = rms_energy(waveform)

    # Base pause grows gently with duration
    pause = MIN_PAUSE_SEC + min(duration * 0.02, 0.25)

    # Louder / emotional segments get more recovery time
    if energy > 0.04:
        pause += 0.15

    return min(pause, MAX_PAUSE_SEC)

# -----------------------------
# Load, merge, and pause
# -----------------------------
segments = []
target_sample_rate = None

ROOM_TONE_DURATION = 30  # seconds, plenty
room_tone = generate_room_tone(
    duration_sec=ROOM_TONE_DURATION,
    sr=target_sample_rate or 24000,
    noise_level=0.0008
)
room_cursor = 0

for i in range(NUM_SEGMENTS):
    file_path = f"segment_{i}.wav"

    if not os.path.exists(file_path):
        print(f"⚠️ Missing: {file_path}")
        continue

    waveform, sr = torchaudio.load(file_path)

    if target_sample_rate is None:
        target_sample_rate = sr

    if not segments:
        segments.append(waveform)
    else:
        segments[-1] = crossfade(
            segments[-1],
            waveform,
            sr,
            fade_ms=40
        )

    # Add natural pause after each segment except the last
    if i < NUM_SEGMENTS - 1:
        pause_sec = pause_from_energy(waveform, sr)
        pause_samples = int(sr * pause_sec)

        tone = room_tone_slice(
            room_tone,
            room_cursor,
            pause_samples
        )
        room_cursor += pause_samples

        segments[-1] = crossfade(
            segments[-1],
            tone,
            sr,
            fade_ms=80
        )

        print(f"⏸️  Pause after segment {i}: {pause_sec:.2f}s")

# -----------------------------
# Export final audio
# -----------------------------
if segments:
    final_audio = torch.cat(segments, dim=1)
    output_file = "final_output.wav"
    torchaudio.save(output_file, final_audio.cpu(), target_sample_rate)
    print(f"📂 Final audio exported as {output_file}")
else:
    print("❌ No audio segments found.")

# --- Cleanup Logic ---
# Using a fixed range to match your creation logic
# for i in range(6):
#     file_path = f"segment_{i}.wav"
#     if os.path.exists(file_path):
#         os.remove(file_path)
#         print(f"🗑️ Deleted {file_path}")