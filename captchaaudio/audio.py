#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  Reference: https://github.com/dchest/captcha

import os
import copy
import wave
import struct
import random
import operator
import sys

from captchaaudio import launcher

# Python 2/3 compatibility for reduce function
if sys.version_info[0] != 2:
    import functools

    reduce = functools.reduce

__all__ = ["AudioCaptcha"]

# Constants for wave file generation
WAVE_SAMPLE_RATE = 8000  # HZ
WAVE_HEADER = bytearray(
    b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
    b"@\x1f\x00\x00@\x1f\x00\x00\x01\x00\x08\x00data"
)
WAVE_HEADER_LENGTH = len(WAVE_HEADER) - 4  # Length of the header excluding the size
DATA_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "data"
)  # Default data directory


# Utility Functions
def _read_wave_file(filepath):
    """Reads a .wav file and returns its byte content."""
    with wave.open(filepath) as w:
        data = w.readframes(-1)  # Read all frames
    return bytearray(data)  # Convert to bytearray for easier manipulation


def patch_wave_header(body):
    """Patch header to the given wave body.

    :param body: the wave content body, it should be bytearray.
    """
    length = len(body)
    padded = length + length % 2  # Ensure even length
    total = WAVE_HEADER_LENGTH + padded

    # Copy the WAVE_HEADER and insert the total length
    header = copy.copy(WAVE_HEADER)
    header[4:8] = bytearray(struct.pack("<I", total))  # Set total length in header
    header += bytearray(struct.pack("<I", length))  # Set body length

    data = header + body  # Append body to header

    # If body length is odd, pad with 0 byte to make it even
    if length != padded:
        data = data + bytearray([0])

    return data  # Return the complete wave file with header


# Sound Manipulation Functions
def change_speed(body, speed=1):
    """Change the voice speed of the wave body."""
    if speed == 1:
        return body  # No change if speed is 1

    length = int(len(body) * speed)  # New length based on speed factor
    rv = bytearray(length)  # Resulting byte array for the modified wave

    step = 0
    for v in body:
        i = int(step)
        while i < int(step + speed) and i < length:
            rv[i] = v  # Copy value to new array for the desired speed
            i += 1
        step += speed
    return rv


def change_sound(body, level=1):
    """Change the sound level of the wave body."""
    if level == 1:
        return body  # No change if level is 1

    body = copy.copy(body)  # Create a copy to avoid modifying the original
    for i, v in enumerate(body):
        # Increase or decrease the amplitude depending on the level
        if v > 128:
            v = (v - 128) * level + 128
            v = max(int(v), 128)  # Prevent values below 128
            v = min(v, 255)  # Prevent values above 255
        elif v < 128:
            v = 128 - (128 - v) * level
            v = min(int(v), 128)  # Prevent values above 128
            v = max(v, 0)  # Prevent values below 0
        body[i] = v  # Set the modified value
    return body


def create_noise(length, level=4):
    """Create white noise for background."""
    noise = bytearray(length)
    adjust = 128 - int(level / 2)  # Adjust noise level
    for i in range(length):
        v = random.randint(0, 256)  # Random noise value
        noise[i] = v % level + adjust  # Adjust the noise to fit the level
    return noise


def create_silence(length):
    """Create a piece of silence."""
    return bytearray([128] * length)  # Silence is represented as 128 (neutral value)


def mix_wave(src, dst):
    """Mix two wave bodies into one, blending their sound."""
    if len(src) > len(dst):
        dst, src = src, dst  # Ensure the destination is longer or equal in length

    # Mix the two waves together element by element
    for i, sv in enumerate(src):
        dv = dst[i]
        if sv < 128 and dv < 128:
            dst[i] = int(sv * dv / 128)  # Quiet sounds are multiplied
        else:
            dst[i] = int(2 * (sv + dv) - sv * dv / 128 - 256)  # Loud sounds are added
    return dst


# Predefined Audio Clips
BEEP = _read_wave_file(os.path.join(DATA_DIR, "beep.wav"))
END_BEEP = change_speed(BEEP, 1.4)  # Slow down the beep sound slightly at the end
SILENCE = create_silence(int(WAVE_SAMPLE_RATE / 5))  # Short silence to separate sounds


# AudioCaptcha Class
class AudioCaptcha(object):
    """Class to generate an audio CAPTCHA."""

    def __init__(self, voicedir=None):
        """Initialize the AudioCaptcha instance with a voice library directory."""
        if voicedir is None:
            voicedir = DATA_DIR  # Default directory for voice data

        self._voicedir = voicedir  # Directory containing voice files
        self._cache = {}  # Cache to store preloaded voice data
        self._choices = []  # List of characters available for CAPTCHA generation

    @property
    def choices(self):
        """Available choices for characters to be generated in the CAPTCHA."""
        if self._choices:
            return self._choices  # Return cached choices

        for n in os.listdir(self._voicedir):
            if len(n) == 1 and os.path.isdir(os.path.join(self._voicedir, n)):
                self._choices.append(n)  # Add valid directory names (characters)
        return self._choices

    def random(self, length=6):
        """Generate a random string with the given length."""
        return random.sample(self.choices, length)  # Randomly sample characters

    def load(self):
        """Load all voice data into memory for faster access."""
        for name in self.choices:
            self._load_data(name)

    def _load_data(self, name):
        """Load .wav files for a specific character and store them in cache."""
        dirname = os.path.join(self._voicedir, name)
        data = []
        for f in os.listdir(dirname):
            filepath = os.path.join(dirname, f)
            if f.endswith(".wav") and os.path.isfile(filepath):
                data.append(
                    _read_wave_file(filepath)
                )  # Add the .wav file content to data
        self._cache[name] = data  # Cache the loaded data

    def _twist_pick(self, key):
        """Pick a random voice clip for a character and apply random speed and sound changes."""
        voice = random.choice(self._cache[key])
        speed = random.randrange(90, 120) / 100.0  # Random speed between 90% and 120%
        voice = change_speed(voice, speed)  # Apply speed change
        level = (
            random.randrange(80, 120) / 100.0
        )  # Random sound level between 80% and 120%
        voice = change_sound(voice, level)  # Apply sound level change
        return voice

    def _noise_pick(self):
        """Pick a random noise clip, reverse it, and apply speed and sound modifications."""
        key = random.choice(self.choices)
        voice = random.choice(self._cache[key])
        voice = copy.copy(voice)
        voice.reverse()  # Reverse the noise clip for variability

        speed = random.randrange(8, 16) / 10.0  # Random speed between 0.8x and 1.6x
        voice = change_speed(voice, speed)  # Apply speed change

        level = random.randrange(2, 6) / 10.0  # Random sound level between 20% and 60%
        voice = change_sound(voice, level)  # Apply sound level change
        return voice

    def create_background_noise(self, length, chars):
        """Generate background noise to be mixed with the characters."""
        noise = create_noise(length, 4)  # Create white noise
        pos = 0
        while pos < length:
            sound = self._noise_pick()  # Pick a noise clip
            end = pos + len(sound) + 1  # Calculate position to mix
            noise[pos:end] = mix_wave(
                sound, noise[pos:end]
            )  # Mix noise with background
            pos = end + random.randint(
                0, int(WAVE_SAMPLE_RATE / 10)
            )  # Move to the next position
        return noise

    def create_wave_body(self, chars):
        """Generate the wave body by combining characters and background noise."""
        voices = []
        inters = []
        for key in chars:
            voices.append(self._twist_pick(key))  # Pick voice clips for each character
            inters.append(
                random.randint(WAVE_SAMPLE_RATE, WAVE_SAMPLE_RATE * 3)
            )  # Random interval

        durations = map(lambda a: len(a), voices)  # Get the duration of each voice clip
        length = max(durations) * len(chars) + reduce(
            operator.add, inters
        )  # Total length of the sound

        bg = self.create_background_noise(length, chars)  # Generate background noise

        # Mix the voices with the background noise
        pos = inters[0]
        for i, v in enumerate(voices):
            end = pos + len(v) + 1
            bg[pos:end] = mix_wave(v, bg[pos:end])
            pos = end + inters[i]

        return (
            BEEP + SILENCE + BEEP + SILENCE + BEEP + bg + END_BEEP
        )  # Final audio sequence

    def generate(self, chars):
        """Generate audio CAPTCHA data as a bytearray."""
        if not self._cache:
            self.load()  # Load voice data if not already cached
        body = self.create_wave_body(chars)  # Create the audio body for the CAPTCHA
        return patch_wave_header(body)  # Add wave header to the body

    def write(self, chars, output):
        """Generate and write audio CAPTCHA data to the output file."""
        data = self.generate(chars)  # Generate the CAPTCHA audio data
        try:
            with open(output, "wb") as f:
                return f.write(data)  # Write data to the specified file
        except Exception:
            # Print error message if something goes wrong
            print(launcher.BIRed + "\t [-] Fault detected ... " + launcher.White)
