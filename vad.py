import numpy as np
import librosa
from scipy.signal import lfilter

def SRH(specMat, nHarmonics, f0min, f0max):

    # return [F0,SRHVal]
    # Function to compute Summation of Residual harmonics function
    # on a spectrogram matrix, with each column corresponding to one
    # spectrum.

    # Initial settings
    N = int(np.shape(specMat)[1])
    SRHmat = np.zeros((int(f0max), N), dtype=float)

    fSeq = np.arange(f0min, f0max, 1)
    fSeq = fSeq.astype(int)
    fLen = len(fSeq)

    # Prepare harmonic indeces matrices.
    v = np.arange(1, nHarmonics+1, 1, dtype=int)
    vT = np.reshape(v, (nHarmonics, 1))
    q = np.arange(1, nHarmonics, 1, dtype=int)
    qT = np.reshape(q, (nHarmonics-1, 1))
    plusIdx1 = np.matlib.repmat(vT, 1, fLen)
    plusIdx2 = np.matlib.repmat(fSeq, nHarmonics, 1)
    plusIdx = np.multiply(plusIdx1, plusIdx2)
    plusIdx = plusIdx.astype(int)
    subtrIdx1 = np.matlib.repmat(qT+0.5, 1, fLen)
    subtrIdx2 = np.matlib.repmat(fSeq, nHarmonics-1, 1)
    subtrIdx12 = np.round(np.multiply(subtrIdx1, subtrIdx2))
    subtrIdx = subtrIdx12.astype(int)
    # avoid costly repmat operation by adjusting indices
    plusIdx = np.mod(plusIdx-1, np.shape(specMat)[0])  # +1;
    subtrIdx = np.mod(subtrIdx-1, np.shape(specMat)[0])  # +1
    # Do harmonic summation
    for n in range(0, N):
        specMatCur = specMat[:, n]
        SRHmat[fSeq, n] = np.conj(
            np.sum(specMatCur[plusIdx], axis=0) - np.sum(specMatCur[subtrIdx], axis=0))

    # Retrieve f0 and SRH value
    SRHVal = np.max(SRHmat, axis=0)
    F0 = np.argmax(SRHmat, axis=0)
    return F0, SRHVal, SRHmat
#    return SRHmat[f0min:,:]


def SRH_feature(specMat, nHarmonics, f0min, f0max):

    # return [F0,SRHVal]
    # Function to compute Summation of Residual harmonics function
    # on a spectrogram matrix, with each column corresponding to one
    # spectrum.

    # Initial settings
    N = int(np.shape(specMat)[1])
    SRHmat = np.zeros((int(f0max), N), dtype=float)

    fSeq = np.arange(f0min, f0max, 1)
    fSeq = fSeq.astype(int)
    fLen = len(fSeq)

    # Prepare harmonic indeces matrices.
    v = np.arange(1, nHarmonics+1, 1, dtype=int)
    vT = np.reshape(v, (nHarmonics, 1))
    q = np.arange(1, nHarmonics, 1, dtype=int)
    qT = np.reshape(q, (nHarmonics-1, 1))
    plusIdx1 = np.matlib.repmat(vT, 1, fLen)
    plusIdx2 = np.matlib.repmat(fSeq, nHarmonics, 1)
    plusIdx = np.multiply(plusIdx1, plusIdx2)
    plusIdx = plusIdx.astype(int)
    subtrIdx1 = np.matlib.repmat(qT+0.5, 1, fLen)
    subtrIdx2 = np.matlib.repmat(fSeq, nHarmonics-1, 1)
    subtrIdx12 = np.round(np.multiply(subtrIdx1, subtrIdx2))
    subtrIdx = subtrIdx12.astype(int)
    # avoid costly repmat operation by adjusting indices
    plusIdx = np.mod(plusIdx-1, np.shape(specMat)[0])  # +1;
    subtrIdx = np.mod(subtrIdx-1, np.shape(specMat)[0])  # +1
    # Do harmonic summation
    for n in range(0, N):
        specMatCur = specMat[:, n]
        SRHmat[fSeq, n] = np.conj(
            np.sum(specMatCur[plusIdx], axis=0) - np.sum(specMatCur[subtrIdx], axis=0))

    return SRHmat[f0min:, :]


def lpcresidual(x, L, shift, order):
    #    x=np.reshape(x,(x.size,1))
    shift = int(np.round(shift))
    order = int(np.round(order))
    start = 0
    L = int(np.round(L))
    stop = start+L
    res = np.zeros((len(x),), dtype=float)
    # LPCcoef=np.zeros((order+1,np.round(len(x)/shift)),dtype=float)

    win = np.hanning(L)
#    win=np.reshape(win,(L,1))
    while stop < x.size:
        segment = x[start:stop]
        segment = np.multiply(segment, win)
#        print(segment)
#        A,e,k=lpc(segment,order) #<-------- lpc based on
        A = librosa.lpc(segment, order=order)
        # LPCcoeff= not implemented
        inv = lfilter(A, 1, segment)
        numerator = np.sum(np.power(segment, 2))
        denominator = np.sum(np.power(inv, 2))
        inv = inv*np.sqrt(numerator/denominator)
        res[start:stop] = res[start:stop]+inv
        start = start+shift
        stop = stop+shift
    return res


def find_utterance_Idxs(keptIdxs, Ntf, NcontAct, Nelastic, Nfr):  # chanded in 16/7/2020
    Ns = keptIdxs[-1]
    Nstart = keptIdxs[0]
    utterIdxs = np.array(([Nstart, 0]), dtype=int, ndmin=2)

    for i in range(int(Nstart)+1, int(Ns)):
        if np.any(keptIdxs == i):
            if np.any(keptIdxs == i-1):
                utterIdxs[-1, 1] = i
            else:
                utterIdxs = np.vstack((utterIdxs, np.array((i, i), dtype=int)))

    Nutt = np.shape(utterIdxs)[0]
    utIdxs = np.zeros((0, 2), dtype=int)
    for u in range(Nutt):
        Nloc = utterIdxs[u, 1]-utterIdxs[u, 0]
        if Nloc >= NcontAct:
            utIdxs = np.vstack((utIdxs, [utterIdxs[u, 0], utterIdxs[u, 1]]))

    N3 = np.shape(utIdxs)[0]
    uIdxs = np.zeros((0, 2), dtype=int)
    for u in range(N3):
        Nloc = utIdxs[u, 1]-utIdxs[u, 0]
        if Nloc < Nfr:
            Nadd = np.ceil((Nfr-Nloc)/2)
            if (utIdxs[u, 0]-Nadd) >= 0 and (utIdxs[u, 1]+Nadd) <= (Ntf-1):
                idxMin = utIdxs[u, 0]-Nadd
                idxMax = utIdxs[u, 1]+Nadd
                uIdxs = np.vstack((uIdxs, [int(idxMin), int(idxMax)]))
        else:
            uIdxs = np.vstack((uIdxs, [utIdxs[u, 0], utIdxs[u, 1]]))

    N2 = np.shape(uIdxs)[0]
    if N2 > 1:
        m = 1
        while m < np.shape(uIdxs)[0]:
            if uIdxs[m, 0]-uIdxs[m-1, 1] <= Nelastic:
                uIdxs[m-1, 1] = uIdxs[m, 1]
                uIdxs = np.delete(uIdxs, m, axis=0)
            else:
                m += 1

    Nutters = np.shape(uIdxs)[0]
    return uIdxs, Nutters


def pitch_srh_preselect_vad(wave, fs, f0min, f0max, hopsize, frameDur):

    # %% Important settings
    # step=4
    nHarmonics = 4
    LPCorder = int(np.round(0.75*fs/1000))

# %% Compute LP residual
    res = lpcresidual(wave, int(np.round(25*fs/1000)),
                      int(np.round(5*fs/1000)), LPCorder)

    # Create frame matrix
    waveLen = len(wave)
    del wave

    # for better chainsaw detection use 250
    frameDuration = int(np.round(frameDur*fs/1000))-2
    # Enforce evenness of the frame's length
    frameDuration = int(np.round(frameDuration/2))*2
    shift = int(np.round(hopsize*fs/1000))
    halfDur = int(np.round(frameDuration/2))

    sampleIdxsIN = np.arange(halfDur+1, waveLen-halfDur, shift)

    N = len(sampleIdxsIN)
    Nkeep = N

    frameMat = np.zeros((frameDuration, N), dtype=float)

    for n in range(0, N):
        frameMat[:, n] = res[sampleIdxsIN[n] -
                             halfDur:sampleIdxsIN[n]+halfDur]  # -1]

    # Create window matrix and apply to frames
    win = np.blackman(frameDuration)
    win = np.reshape(win, (len(win), 1))
    frameMatWin = np.multiply(frameMat, win)
    # Do mean subtraction
    frameMean = frameMatWin.mean(axis=0)
    # frameMatWinMean = bsxfun(@minus, frameMatWin, frameMean);
    frameMatWinMean = frameMatWin-frameMean
    del frameMean, frameMatWin, frameMat
    # Compute spectrogram matrix
    specMat = np.zeros(
        (int(np.floor(fs/2)), int(np.shape(frameMatWinMean)[1])), dtype=float)
    idx = np.arange(0, np.floor(fs/2), 1, dtype=int)

    for i in range(0, N):
        frameIN = frameMatWinMean[:, i]
        fftFrame = np.fft.fft(frameIN, n=fs, axis=0)
        tmp = np.abs(fftFrame)
        specMat[:, i] = tmp[idx]

    del frameMatWinMean, tmp, idx
    specDenom = np.sqrt(np.sum(np.power(specMat, 2), axis=0))

    specMat = np.divide(specMat, specDenom)
    del specDenom

 # %% Estimate the pitch track in 2 iterations (commented out)
#    for Iter in range(0,Niter):

    SRHmatIN = SRH_feature(specMat, nHarmonics, f0min, f0max)
    del specMat
    SRHmatIN = SRHmatIN[:, :Nkeep]
    timeIN = 1.0*sampleIdxsIN/fs

    SRHval = np.max(SRHmatIN, axis=0)

    return SRHval, timeIN, sampleIdxsIN


def vad_mean_rms(s, fs, f0_min=70, f0_max=360, srhThreshold = 0.05):
    hopsize_ms = 60
    framesize_ms=180
    n_fr = 12  # associated to featureMtx
    N_cont_act = 2  # 7 or 6
    n_elastic = 5  # 21
    srh, timePoints, sampleIdxs = pitch_srh_preselect_vad(s, fs, f0_min, f0_max, hopsize_ms, framesize_ms)
    active_idxs = np.argwhere(srh > srhThreshold)
    frame_idxs, Nutters = find_utterance_Idxs(active_idxs[:, 0], len(active_idxs), N_cont_act, n_elastic, n_fr)
    total_samples = 0
    energy = 0
    for frame_idx in frame_idxs:
        start = sampleIdxs[frame_idx[0]]
        stop = sampleIdxs[frame_idx[1]]
        total_samples += stop - start
        s_part = s[start:stop]
        energy += np.sum(s_part ** 2)
    rms = np.sqrt(energy / total_samples)
    log_rms = 20 * np.log10(rms)
         
    
    return log_rms