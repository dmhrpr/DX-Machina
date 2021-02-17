import numpy as np
from python_speech_features import mfcc
import scipy.io.wavfile as wav

def delta(feat, N):
    if N < 1:
        raise ValueError('N must be an integer >= 1')
    NUMFRAMES = len(feat)
    denominator = 2 * sum([i**2 for i in range(1, N+1)])
    delta_feat = np.empty_like(feat)
    padded = np.pad(feat, ((N, N), (0, 0)), mode='edge')   # padded version of feat
    for t in range(NUMFRAMES):
        delta_feat[t] = np.dot(np.arange(-N, N+1), padded[t : t+2*N+1]) / denominator   # [t : t+2*N+1] == [(N+t)-N : (N+t)+N+1]
    return delta_feat

def mfcc_analysis(audio_file): 
    (rate,sig) = wav.read(audio_file)
    mfcc_data = mfcc(sig,rate)

    delta_data = delta(mfcc_data, 2)
    delta2_data = delta(delta_data, 2)

    mfcc_analysis = np.vstack((mfcc_data, delta_data, delta2_data))
    
    mfcc_analysis = (mfcc_analysis - np.min(mfcc_analysis)) / (np.max(mfcc_analysis) - np.min(mfcc_analysis))

    mfcc_analysis = mfcc_analysis.mean(axis=1)

    return mfcc_analysis
