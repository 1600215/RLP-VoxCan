import librosa

from scipy.signal import find_peaks
import scipy

import numpy as np

def reduce_noise(audio, sr, ruido_amb):
    """
    Limpia el ruido acústico de un audio grabado.

    Args:
        audio: Array de audio que contiene la señal de voz.
        sr: Frecuencia de muestreo del audio.

    Returns:
        audio_limpio: Array de audio con el ruido reducido.
    """

    # Calcular la transformada de Fourier de corto plazo (STFT)
    # Convertir el audio a dominio espectral
    Y = librosa.stft(audio)

    # Calcular la máscara de Wiener
    mascara = np.abs(Y) / (np.abs(ruido_amb) + 1e-8)
    mascara = np.clip(mascara, 0, 1)

    # Aplicar la máscara a la señal espectral
    Y_denoised = Y * mascara

    # Convertir la señal espectral denoizada a dominio temporal
    audio_denoised = librosa.istft(Y_denoised)

    return audio_denoised


def amplificar_voz(audio, ganancia):
  """
  Amplifica la señal de voz de un audio.

  Argumentos:
    audio (ndarray): Array de NumPy con los datos de audio.
    ganancia (float): Factor de amplificación.

  Devuelve:
    ndarray: Array de NumPy con el audio con la voz amplificada.
  """
  # Extraer la envolvente de la señal de audio
  envelope = librosa.get_envelope(audio)

  # Aplicar la ganancia a la envolvente
  envelope = envelope * ganancia

  # Sintetizar la señal de audio a partir de la envolvente amplificada
  audio_amplificado = librosa.reconstruct_audio(envelope, audio)

  return audio_amplificado


def main():
    input_path = "audio/1m_audios/"
    output_path = "audio/clean_audios/"


    # Cargar el audio grabado
    audio, sr = librosa.load(input_path + 'audio_20240530_194904.mp3')
    audio_amb, sr_amb = librosa.load(input_path + 'audio_ruido_ambiental.mp3')
    
    # Limpiar el ruido acústico
    audio_limpio = reduce_noise(audio, sr, audio_amb)

    # Amplificar la voz
    ganancia = 2.0  # Ajustar la ganancia según se desee
    audio_amplificado = elevar_voz(audio_denoised, ganancia)

    # Guardar el audio procesado
    sf.write(output_path + "audio_good.mp3", audio_amplificado, sr)

    print(f"Audio procesado y guardado en: {ruta_salida}")
  



if __name__ == "__main__":
    print("Cleaning audios ...")
    main()
