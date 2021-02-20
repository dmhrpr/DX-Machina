from matplotlib import pyplot as plt
import matplotlib.cm as cm
import os
import math
import numpy as np
import librosa
import soundfile as sf
import librosa.display
from sklearn.manifold import TSNE
import json
import ffmpeg

def get_features(y, sr):
    y = y[0:sr]  # analyze just first second
    S = librosa.feature.melspectrogram(y, sr=sr, n_mels=128)
    log_S = librosa.amplitude_to_db(S, ref=np.max)
    mfcc = librosa.feature.mfcc(S=log_S, n_mfcc=13)
    delta_mfcc = librosa.feature.delta(mfcc, mode='nearest')
    delta2_mfcc = librosa.feature.delta(mfcc, order=2, mode='nearest')
    feature_vector = np.concatenate((np.mean(mfcc,1), np.mean(delta_mfcc,1), np.mean(delta2_mfcc,1)))
    feature_vector = (feature_vector-np.mean(feature_vector)) / np.std(feature_vector)
    return feature_vector

source_audio = 'original.wav'

hop_length = 512
y, sr = librosa.load(source_audio)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)

times = [hop_length * beat / sr for beat in beats]

# where to save our new clips to


# make new directory to save them 


# grab each interval, extract a feature vector, and save the new clip to our above path
feature_vectors = []
for i in range(len(beats)-1):
    idx_y1 = beats[i  ] * hop_length  # first sample of the interval
    idx_y2 = beats[i+1] * hop_length  # last sample of the interval
    y_interval = y[idx_y1:idx_y2]
    features = get_features(y_interval, sr)   # get feature vector for the audio clip between y1 and y2
    file_path = 'beat_%d.wav' % (i)   # where to save our new audio clip
    feature_vectors.append({"file":file_path, "features":features})   # append to a feature vector
    sf.write(file_path, y_interval, sr)   # save to disk
    if i % 50 == 0:
        print("analyzed %d/%d = %s"%(i+1, len(beats)-1, file_path))

# save results to this json file
tsne_path = "data/example-audio-tSNE-onsets.json"

# feature_vectors has both the features and file paths in it. let's pull out just the feature vectors
features_matrix = [f["features"] for f in feature_vectors]

# calculate a t-SNE and normalize it
model = TSNE(n_components=2, learning_rate=150, perplexity=30, verbose=2, angle=0.1).fit_transform(features_matrix)
x_axis, y_axis = model[:,0], model[:,1] # normalize t-SNE
x_norm = (x_axis - np.min(x_axis)) / (np.max(x_axis) - np.min(x_axis))
y_norm = (y_axis - np.min(y_axis)) / (np.max(y_axis) - np.min(y_axis))

data = [[f['file'], float(x), float(y)] for f, x, y in zip(feature_vectors, x_norm, y_norm)]


# saves clip and clip most similar to it into a list

print(len(data))

order = []
first_clip = data[0][0]

order.append(first_clip)

data2 = [s for s in data]

for x in data2:
    for y in data:
        if y[0] == order[-1]:
            x1 = y[1]
            y1 = y[2]

            all_else = data[:data.index(y)]+data[data.index(y)+1:]

            for z in all_else:
                x2 = z[1]
                y2 = z[2]
                distance = math.sqrt(((x1-x2)**2)+((y1-y2)**2))
                dist_list = []
                dist_list.append([z[0], distance]) 

            dist_list2 = [s[1] for s in dist_list]
            dist_list3 = [s[0] for s in dist_list]
            closest = min(dist_list2)
            next_clip = dist_list3[dist_list2.index(closest)]

            order.append(next_clip)
            data.remove(y)
            

order = order[:-1]

for f in order:
    os.rename(f, 'wavs/' + str(order.index(f)).zfill(4) + '.wav')
