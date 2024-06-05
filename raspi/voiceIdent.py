import numpy as np
import librosa
import joblib
import os
import argparse



def removeSilence(audio, silence_threshold = 0.05):
    '''The `removeSilence` function removes silent segments from an audio signal based on a specified
    silence threshold.
    
    Parameters
    ----------
    audio
        The `removeSilence` function you provided is designed to remove segments of silence from an audio
    signal based on a specified silence threshold. The function takes two parameters:
    silence_threshold
        The `silence_threshold` parameter in the `removeSilence` function represents the minimum amplitude
    value below which a segment of audio is considered as silence. Any audio samples with absolute
    values less than this threshold are identified as silence and removed from the audio signal. By
    adjusting this threshold, you can control
    
    Returns
    -------
        The function `removeSilence` returns the audio signal with silence segments removed based on the
    specified silence threshold.
    
    '''
    
    
    
    # Encontrar los índices de los segmentos de silencio
    silence_indices = np.where(np.abs(audio) < silence_threshold)[0]

    # Crear una máscara para mantener los segmentos que no son de silencio
    mask = np.ones_like(audio, dtype=bool)
    mask[silence_indices] = False

    # Aplicar la máscara al audio para eliminar los segmentos de silencio
    audio_sin_silencio = audio[mask]

    if audio_sin_silencio.size == 0:
        return audio
    return audio_sin_silencio


def lowPassFilter(audio, sr, cutoff_freq = 3000):
    '''The function `lowPassFilter` applies a low-pass filter to an audio signal in the frequency domain to
    remove high-frequency components above a specified cutoff frequency.
    
    Parameters
    ----------
    audio
        The `audio` parameter is the input audio signal that you want to filter using a low-pass filter. It
    is typically represented as a one-dimensional array of audio samples.
    sr
        The `sr` parameter in the `lowPassFilter` function stands for the sampling rate of the audio
    signal. It represents the number of samples taken per second when the audio signal was recorded or
    processed. The sampling rate is typically measured in Hertz (Hz).
    cutoff_freq
        The `cutoff_freq` parameter in the `lowPassFilter` function represents the frequency at which you
    want to filter out higher frequencies from the audio signal. Frequencies above the `cutoff_freq`
    will be attenuated or removed from the signal, effectively creating a low-pass filter that allows
    only
    
    Returns
    -------
        The function `lowPassFilter` returns the filtered audio signal in the time domain after applying a
    low-pass filter in the frequency domain.
    
    '''
    y_fft = np.fft.fft(audio)

    freqs = np.fft.fftfreq(len(audio), 1 / sr)
    lowpass_filter = np.abs(freqs) <= cutoff_freq

    # Aplicar el filtro pasa bajos multiplicando la señal en el dominio de la frecuencia por el filtro
    y_fft_filtered = y_fft * lowpass_filter

    # Aplicar la Transformada Inversa de Fourier para obtener la señal filtrada en el dominio del tiempo
    y_filtered = np.real(np.fft.ifft(y_fft_filtered))
    
    return y_filtered


def spec(y, sr, spec = 'wavelet'):
    '''This Python function generates different types of spectrograms based on the specified type.
    
    Parameters
    ----------
    y
        The function `spec` you provided seems to be a spectrogram generator that can produce different
    types of spectrograms based on the specified `spec` parameter. However, there are a couple of issues
    in the code:
    sr
        The `sr` parameter in the `spec` function stands for the sampling rate of the audio signal. It
    represents the number of samples of audio carried per second, typically measured in Hz (Hertz).
    spec, optional
        The `spec` function you provided seems to be a spectrogram generator that can produce different
    types of spectrograms based on the `spec` parameter provided. The spectrogram types it supports are
    'wavelet', 'linear', 'log', 'mel', and 'cqt'.
    
    Returns
    -------
        the spectrogram based on the specified type of spectrogram calculation method (wavelet, linear,
    log, mel, or cqt).
    
    '''
    

    if spec == 'linear'  : spectogram = np.abs(librosa.stft(y))

    elif spec == 'log' : spectogram = np.abs(librosa.stft(y))
    
    elif spec == 'mel' : spectogram = librosa.feature.melspectrogram(y=y, sr=sr)
    
    elif spec == 'cqt' : spectogram = np.abs(librosa.cqt(y, sr=sr))
    
    elif spec == 'wavelet' : spectogram = np.abs(librosa.cqt(y, sr=sr, fmin=librosa.note_to_hz('C1')))
    
    else: return None
    return spectogram

def extrapolate_audio(y, sr, desired_duration):
    '''The function extrapolates an audio signal to a desired duration by repeating or truncating the
    original signal accordingly.
    
    Parameters
    ----------
    y
        The parameter `y` in the `extrapolate_audio` function represents the audio signal as a
    one-dimensional NumPy array.
    sr
        The `sr` parameter in the `extrapolate_audio` function stands for the sampling rate of the audio
    signal. It represents the number of samples of audio carried per second, typically measured in Hz
    (Hertz). This parameter is used to determine the duration of the audio signal and to ensure that
    desired_duration
        The `desired_duration` parameter in the `extrapolate_audio` function represents the target duration
    in seconds that you want the audio to be extrapolated or truncated to. This parameter is used to
    determine whether the input audio `y` should be repeated or truncated to match the desired duration.
    
    Returns
    -------
        The function `extrapolate_audio` returns extrapolated audio data that either repeats the input
    audio until the desired duration is reached or truncates the input audio to the desired duration.
    The function also returns the sampling rate `sr` of the audio.
    
    '''
    audio_duration = librosa.get_duration(y=y, sr=sr)
    if audio_duration < desired_duration:
        # Repeat the audio until desired duration is reached
        repetitions = int(desired_duration / audio_duration) + 1
        extrapolated_audio = np.tile(y, repetitions)[:desired_duration * sr]
    else:
        # Truncate the audio to the desired duration
        extrapolated_audio = y[:desired_duration * sr]
    return extrapolated_audio, sr


def windowing(image, max_size, despl=0):
    '''The function `windowing` creates a matrix of windows from an input image by rearranging its columns.
    
    Parameters
    ----------
    image
        The `image` parameter is a 2D numpy array representing an image. Each element in the array
    corresponds to a pixel value in the image.
    max_size
        The `max_size` parameter in the `windowing` function represents the maximum size of the window
    matrix that will be created. This parameter determines the number of rows in the window matrix,
    while the number of columns will be the same as the number of columns in the input `image` matrix.
    
    Returns
    -------
        A matrix of windows with the same number of rows as the maximum size provided and the same number
    of columns as the input image. Each column of the matrix corresponds to a window extracted from the
    input image.
    
    '''
    
    if despl == 0 : windows = np.zeros((max_size, image.shape[0]))  # Crear matriz de ventanas con el mismo número de columnas que la imagen
    else: windows = np.zeros((max_size, image.shape[0], despl))
    for i in np.arange(0, image.shape[1]):
        if i + despl >= image.shape[1]:
            break
        if despl == 0: windows[i, :] = image[: , i]
        else: windows[ i, :, :] = image[: , i :i + despl]
    return windows



def normalize_audio(y, target_rms):
    """
    Normalize the audio signal to a target root mean square (RMS) value.

    Parameters:
    - y (ndarray): The input audio signal.
    - target_rms (float): The desired RMS value for the normalized audio.

    Returns:
    - y_normalized (ndarray): The normalized audio signal.

    """
    current_rms = np.sqrt(np.mean(y**2))
    gain = target_rms / current_rms
    y_normalized = y * gain
    return y_normalized



def apply_compression(y, threshold=0.5, ratio=4):
    """
    Applies compression to the input signal.

    Parameters:
    - y: numpy array
        The input signal to be compressed.
    - threshold: float, optional (default=0.5)
        The threshold value for compression. Values above this threshold will be compressed.
    - ratio: int, optional (default=4)
        The compression ratio. Determines the amount of compression applied to values above the threshold.

    Returns:
    - y_compressed: numpy array
        The compressed signal.
    """
    y_compressed = np.copy(y)
    y_compressed[np.abs(y) > threshold] = threshold + (np.abs(y_compressed[np.abs(y) > threshold]) - threshold) / ratio
    return np.sign(y) * y_compressed



def extract_features(y, sr):
    '''The function `extract_features` calculates various audio features from a given audio signal using
    the librosa library and returns them as a list.
    
    Parameters
    ----------
    y
        The parameter `y` in the `extract_features` function represents the audio time series. It is the
    audio signal as a one-dimensional NumPy array.
    sr
        The `sr` parameter in the `extract_features` function stands for the sampling rate of the audio
    signal. It represents the number of samples of audio carried per second, typically measured in Hz
    (Hertz). It is an important parameter in audio processing as it determines the quality and fidelity
    of the audio
    
    Returns
    -------
        The function `extract_features` returns a list of mean values of various audio features extracted
    using Librosa library functions. The features include chroma_stft, spectral centroid, spectral
    bandwidth, spectral rolloff, zero crossing rate, spectral flatness, and root mean square (RMS)
    energy.
    
    '''
    features = []
    features.append(np.mean(librosa.feature.chroma_stft(y=y, sr=sr)))
    features.append(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    features.append(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
    features.append(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
    features.append(np.mean(librosa.feature.zero_crossing_rate(y)))
    features.append(np.mean(librosa.feature.spectral_flatness(y=y)))
    features.append(np.mean(librosa.feature.rms(y=y)))
  
    
    return features


def predict(algorithm='windowing', dataType='ruido', model='svm', filter=False, audio='aux.mp3'):
    """
    Predicts the output based on the given parameters.

    Parameters:
    - algorithm (str): The algorithm to use for prediction. Default is 'windowing'.
    - dataType (str): The type of data to use for prediction. Default is 'ruido'.
    - model (str): The model to use for prediction. Default is 'svm'.
    - filter (bool): Whether to apply a filter or not. Default is False.
    - audio (str): The path to the audio file. Default is 'aux.mp3'.

    Returns:
    - y_pred (numpy.ndarray): The predicted output.

    Raises:
    - FileNotFoundError: If the audio file does not exist.
    - ValueError: If the combination of algorithm, dataType, and model is not supported.

    """
    if not os.path.exists(audio):
        return -1
    
    if algorithm == 'windowing':
        if model != 'rf':
            return -1
        
        m = joblib.load(f'./modelos/{dataType}/{algorithm}/modelos/{model}_{algorithm}_filter_{str(filter)}.pkl')
        scaler = joblib.load(f'./modelos/{dataType}/{algorithm}/scalers/scaler_{algorithm}_filter_{str(filter)}.pkl')
        
        y, sr = librosa.load(audio)
        
        if dataType == 'ruidoNorm':
            average_rms = joblib.load(f'./modelos/{dataType}/average_rms.pkl')
            y = normalize_audio(y, average_rms)
            y = apply_compression(y)
        
        y = lowPassFilter(y, sr)
        y = removeSilence(y, 0.01)
        image = spec(y, sr, spec='mel')
        windows = windowing(image, 320, despl=0)
        X = windows[np.mean(windows, axis=1) != 0]
        X = scaler.transform(X)
        y_pred = m.predict(X)
        y_pred = np.array(y_pred)
        return y_pred, np.bincount(y_pred).argmax()
    
    if algorithm == 'specsModel':
        if filter and dataType == 'ruidoNorm':
            return -1
        if model != 'cnn':
            return -1
        
        model = joblib.load(f'./modelos/{dataType}/{algorithm}/modelos/cnn_{algorithm}_filter_{str(filter)}.pkl')
        y, sr = librosa.load(audio)
        
        if dataType == 'ruidoNorm':
            average_rms = joblib.load(f'./modelos/{dataType}/average_rms.pkl')
            y = normalize_audio(y, average_rms)
            y = apply_compression(y)
        
        y = removeSilence(y, 0.01)
        y = lowPassFilter(y, sr)
        y, sr = extrapolate_audio(y, sr, 6)
        image = spec(y, sr, spec='wavelet')
        
        size = {'original': 32, 'ruido': 128, 'ruidoNorm': 256}[dataType]
        
        test = np.zeros((size, image.shape[0], image.shape[1]))
        test[0] = image
        y_pred = model.predict(test)
        return y_pred[0]
    
    if algorithm == 'featureModel':
        if model not in ['svc', 'lr', 'rf']:
            return -1
        
        model = joblib.load(f'./modelos/{dataType}/{algorithm}/modelos/{model}_{algorithm}_filter_{str(filter)}.pkl')
        scaler = joblib.load(f'./modelos/{dataType}/{algorithm}/scalers/scaler_{algorithm}_filter_{str(filter)}.pkl')
        y, sr = librosa.load(audio)
        
        if dataType == 'ruidoNorm':
            average_rms = joblib.load(f'./modelos/{dataType}/average_rms.pkl')
            y = normalize_audio(y, average_rms)
            y = apply_compression(y)
        
        y = lowPassFilter(y, sr)
        y = removeSilence(y, 0.02)
        features = extract_features(y, sr)
        features = np.array(features).reshape(1, -1)
        features = scaler.transform(features)
        y_pred = model.predict(features)
        return y_pred[0]
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Predict output from audio file.')
    parser.add_argument('--algorithm', type=str, default='windowing', help='Algorithm to use for prediction (default: windowing)')
    parser.add_argument('--dataType', type=str, default='ruido', help='Type of data to use for prediction (default: ruido)')
    parser.add_argument('--model', type=str, default='svm', help='Model to use for prediction (default: svm)')
    parser.add_argument('--filter', type=bool, default=False, help='Whether to apply a filter or not (default: False)')
    parser.add_argument('--audio', type=str, default='aux.mp3', help='Path to the audio file (default: aux.mp3)')
    args = parser.parse_args()

    result = predict(algorithm=args.algorithm, dataType=args.dataType, model=args.model, filter=args.filter, audio=args.audio)
    print(f'Prediction result: {result}')