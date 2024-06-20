from pydub import AudioSegment

def get_peak_volume(audio_path):
    """Return the peak volume of the given audio file."""
    audio = AudioSegment.from_file(audio_path, format="mp3")
    peak_amplitude = audio.max
    return peak_amplitude

def get_max_volumes(audio1, audio2, audio3, audio4):
    """
    Given 4 audio paths, return the path of the audio with the highest peak volume.
    Each audio is represented as a dictionary with the key being the microphone ID
    and the value being a tuple of the audio path and its direction.
    """
    audios = [audio1, audio2, audio3, audio4]
    max_peak = None
    max_audio = None
    direction = None

    for audio in audios:
        for key, (path, dir) in audio.items():
            peak = get_peak_volume(path)
            print(peak)
            if max_peak is None or peak > max_peak:
                max_peak = peak
                max_audio = key
                direction = dir
    
    print(f"Max peak volume: {max_peak}")
    return max_audio, direction

def main():
    input_path = "audio/"

    # Define cada microfono con un id y su dirección
    audio_files = {
        "mic01fr": (input_path + 'audio_channel_0_20240606_122858.mp3', "front-right"),
        "mic02fl": (input_path + 'audio_channel_1_20240606_122914.mp3', "front-left"),
        "mic03br": (input_path + 'audio_channel_7_20240606_122914.mp3', "back-right"),
        "mic04bl": (input_path + '1m_audios/audio_ruido_ambiental.mp3', "back-left")
    }

    max_audio, audio_direction = get_max_volumes(
        {"mic01fr": audio_files["mic01fr"]},
        {"mic02fl": audio_files["mic02fl"]},
        {"mic03br": audio_files["mic03br"]},
        {"mic04bl": audio_files["mic04bl"]}
    )

    print(f"The audio with the highest peak volume is from: {audio_direction}, microphone {max_audio}")

if __name__ == "__main__":
    main()
