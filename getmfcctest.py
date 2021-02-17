import mfcc
import glob
import numpy as np

target = mfcc.mfcc_analysis('patch-25.wav')
target2 = mfcc.mfcc_analysis('scrum.wav')

target = np.mean(target)
target2 = np.mean(target2)

end = abs(target - target2)
print(end)

