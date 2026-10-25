"""
Storm sounds synthesised from noise (no recordings needed): a seamless rain loop and three thunder
claps of different distance.

    D:\\AI\\Hunyuan3D-2\\.venv\\Scripts\\python.exe Scripts/Tools/make_sounds.py

Output: SourceArt/Audio/S_<Name>.wav (16-bit mono 44.1 kHz), imported by Scripts/Editor/import_art.py.
"""

import os
import wave

import numpy as np

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "SourceArt", "Audio")
RATE = 44100


def lowpass(x, cutoff):
    """One-pole low-pass filter, cutoff in Hz."""
    a = np.exp(-2 * np.pi * cutoff / RATE)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def fast_lowpass(x, cutoff, passes=1):
    """Same filter via an exponential kernel convolution (much faster for long signals)."""
    a = np.exp(-2 * np.pi * cutoff / RATE)
    n = int(np.log(1e-4) / np.log(a)) + 1
    kernel = (1 - a) * a ** np.arange(n)
    for _ in range(passes):
        x = np.convolve(x, kernel)[: len(x)]
    return x


def rain_loop(seconds=12.0, seed=1):
    """Steady rain: filtered noise hiss plus thousands of tiny drop ticks; cross-faded to loop."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    fade = int(1.0 * RATE)
    total = n + fade
    hiss = rng.standard_normal(total)
    hiss = hiss - fast_lowpass(hiss, 900)                 # high-pass: keep the hiss
    hiss = fast_lowpass(hiss, 7000) * 0.25
    drops = np.zeros(total)
    for t in rng.integers(0, total - 400, int(seconds * 900)):
        length = rng.integers(60, 300)
        env = np.exp(-np.arange(length) / (length / 5))
        drops[t:t + length] += rng.uniform(0.05, 0.4) * env * rng.standard_normal(length)
    drops = fast_lowpass(drops, 5000)
    rumble = fast_lowpass(rng.standard_normal(total), 120, passes=2) * 2.0
    sig = hiss + drops * 0.6 + rumble
    # Seamless loop: blend the extra tail into the start.
    ramp = np.linspace(0, 1, fade)
    out = sig[:n].copy()
    out[:fade] = sig[:fade] * ramp + sig[n:n + fade] * (1 - ramp)
    return out


def thunder(seconds, distance, seed):
    """A crack (near) and a long rolling rumble; distance 0..1 softens and delays the high end."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    t = np.arange(n) / RATE
    noise = rng.standard_normal(n)
    crack = fast_lowpass(noise, 3000 * (1 - distance) + 300) * np.exp(-t / 0.25) * (1 - distance)
    rumble = fast_lowpass(rng.standard_normal(n), 90, passes=3) * 9.0
    # Rolling: a few swells of the rumble.
    swells = np.zeros(n)
    for k in range(rng.integers(3, 6)):
        c = rng.uniform(0.1, 0.7) * seconds
        w = rng.uniform(0.3, 1.2)
        swells += rng.uniform(0.5, 1.0) * np.exp(-((t - c) / w) ** 2)
    env = (1 - np.exp(-t / 0.05)) * np.exp(-t / (seconds * 0.45))
    sig = crack * 0.8 + rumble * (0.4 + swells) * env
    return sig


def save(name, sig, peak=0.85):
    os.makedirs(OUT, exist_ok=True)
    sig = sig / (np.abs(sig).max() + 1e-9) * peak
    data = (sig * 32767).astype(np.int16)
    path = os.path.join(OUT, name + ".wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(data.tobytes())
    print("saved", path, "%.1f s" % (len(sig) / RATE))


def main():
    save("S_RainLoop", rain_loop(), peak=0.6)
    save("S_Thunder_Near", thunder(6.0, 0.1, 11))
    save("S_Thunder_Mid", thunder(7.0, 0.45, 12))
    save("S_Thunder_Far", thunder(8.0, 0.85, 13), peak=0.7)


if __name__ == "__main__":
    main()
