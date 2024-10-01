from natsort import natsort_keygen
from source.vad import vad_mean_rms
import os
import librosa
import json
import soundfile as sf
import numpy as np
from scipy.signal import bilinear, lfilter

class Car:
    """
    A class to represent a car and the recordings associated with it.\
    The class provides methods to load and process the recordings.

    Args:
    path (str): The path to the folder with the recordings for the particular car.
    fs (int): The sampling frequency of the recordings. Default is 16000 Hz.
    json_info (bool): A boolean indicating whether the car information is stored in a json file inside path. Defaults to True.
    info_dict (dict): A dictionary containing the car information. Defaults to None. Is *json_info* is True, *info_dict* is ignored.
    """
    def __init__(self, path, fs=16000, json_info=True, info_dict =None):
        self.__path = path
        self.__json_info = json_info
        self.__fs = fs
        # if json_info, ignore info_dict
        if self.__json_info:
            info_file = os.path.join(self.__path, 'info.json')
            with open(info_file, 'r') as f:
                info_dict = json.load(f)          
        # else:
        self.__in_dict = info_dict
        self.__make = info_dict['make']
        self.__model = info_dict['model']
        self.__year = info_dict['year']
        if 'version' in info_dict.keys():
            self.__version = info_dict['version']
        else:
            self.__version = None
        
        self.__mic_setups = self.__find_folders()
        self.__irs = {}
        self.__noises = {}
        self.__radio_irs = {}
        self.__references = {}
        self.__ventilation = {}
        natsort_key = natsort_keygen(key=lambda y: y.lower()) 

        for mic_setup in self.__mic_setups:
            # IRs
            wav_list = os.listdir(os.path.join(self.__path, mic_setup, 'IRs'))
            self.__irs[mic_setup] = sorted([wav[:-4] for wav in wav_list], key=natsort_key)

            # Noise
            wav_list = os.listdir(os.path.join(self.__path, mic_setup, 'noise'))
            self.__noises[mic_setup] = sorted([wav[:-4] for wav in wav_list], key=natsort_key)
            
            # Radio IRs
            try:
                wav_list = os.listdir(os.path.join(self.__path, mic_setup, 'radio_IRs'))
                self.__radio_irs[mic_setup] = sorted([wav[:-4] for wav in wav_list], key=natsort_key)
            except :
                self.__radio_irs[mic_setup] = None

            # Ventilation
            wav_list = os.listdir(os.path.join(self.__path, mic_setup, 'ventilation'))
            self.__ventilation[mic_setup] = sorted([wav[:-4] for wav in wav_list], key=natsort_key)

            # References
            ref_file = os.path.join('source', 'references_16kHz', self.__make + '_' + self.__model, mic_setup, 'reference.json')
            with open(ref_file, 'r') as f:
                self.__references[mic_setup] = json.load(f)

            # Correction gains
            gains_file = os.path.join('source', 'correction_gains', 'gains.json')
            with open(gains_file, 'r') as f:
                self.__correction_gains = json.load(f)

    def __repr__(self):
        return f'Car(path={self.__path!r}, json_info=False, info_dict={self.__in_dict!r})'
        
        
    def __str__(self):
        if self.__version:
            return f'{self.make} {self.model} {self.year} {self.version}'
        return f'{self.make} {self.model} {self.year}'
    
    # properties
    @property
    def make(self):
        """Returns a string containing the make of the car."""
        return self.__make
    
    @make.setter
    def make(self, value):
        """Prevents setting the make of the car."""
        raise AttributeError('Cannot set make.')
    
    @property
    def model(self):
        """Returns a string containing  the model of the car."""
        return self.__model
    
    @model.setter
    def model(self, value):
        """Prevents setting the model of the car."""
        raise AttributeError('Cannot set model.')
    
    @property
    def version(self):
        """Returns a string containing the model's version of the car."""
        return self.__version
    
    @version.setter
    def version(self, value):
        """Prevents setting the version of the car."""
        raise AttributeError('Cannot set version.')
    
    @property
    def year(self):
        """Returns an integer with the year of the car."""
        return self.__year
    
    @year.setter
    def year(self, value):
        """Prevents setting the year of the car."""
        raise AttributeError('Cannot set year.')
    
    @property
    def fs(self):
        """Returns the sampling frequency."""
        return self.__fs
    
    @fs.setter
    def fs(self, value):
        """Sets the sampling frequency."""
        self.__fs = value
    
    @property
    def mic_setups(self):
        """Returns a list of available microphone configurations."""
        return self.__mic_setups
    
    @mic_setups.setter
    def mic_setups(self, value):
        """Prevents setting the microphone configurations."""
        raise AttributeError('Cannot set mic_setups.')
    
    @property
    def irs(self, setup=None):
        """Returns a dictionary of available IR conditions per microphone configuration."""
        return self.__irs
        
    
    @irs.setter
    def irs(self, value):
        """Prevents setting the IRs."""
        raise AttributeError('Cannot set irs.')
    
    @property
    def noise_recordings(self):
        """Returns a dictionary of available noise condition recordings per microphone configuration."""
        return self.__noises
    
    @noise_recordings.setter
    def noise_recordings(self, value):
        """Prevents setting the noise recordings."""
        raise AttributeError('Cannot set noise_recordings.')
    
    @property
    def radio_irs(self):
        """Returns a dictionary of available car audio IR conditions per microphone configuration."""
        return self.__radio_irs
    
    @radio_irs.setter
    def radio_irs(self, value):
        """Prevents setting the radio IRs."""
        raise AttributeError('Cannot set radio_irs.')
    
    @property
    def __reference_mic(self):
        """Returns a dictionary of the reference microphone per microphone configuration."""
        reference_mics = {
            'AlfaRomeo_146': {'array': None, 'distributed': 2},
            'Honda_CR-V': {'array': 4, 'distributed': 2},
            'Smart_forfour': {'array': 4, 'distributed': 0},
            'Volkswagen_Golf': {'array': 4, 'distributed': 0},
        }
        return reference_mics[self.make + '_' + self.model]
    
    @__reference_mic.setter
    def __reference_mic(self, value):
        """Prevents setting the reference microphone."""
        raise AttributeError('Cannot set reference_mic.')
    
    @property
    def ventilation_recordings(self):
        """Returns a dictionary of available ventilation conditions recordings per microphone configuration."""
        return self.__ventilation
    
    @ventilation_recordings.setter
    def ventilation_recordings(self, value):
        """Prevents setting the ventilation recordings."""
        raise AttributeError('Cannot set ventilation_recordings.')
    
    @property
    def speaker_locations(self):
        """Returns a dictionary of available speaker locations per microphone configuration."""
        natsort_key = natsort_keygen(key=lambda y: y.lower())
        locations = {}
        for mic_setup in self.mic_setups:
            locations[mic_setup] = sorted(list(set([s.split('w')[0][:-1] for s in self.irs[mic_setup]])), key=natsort_key)
        return locations
    
    @speaker_locations.setter
    def speaker_locations(self, value):
        """Prevents setting the speaker locations."""
        raise AttributeError('Cannot set speaker_locations.')  
    
    @property
    def correction_gains(self):
        """Returns a dictionary with the correction gains of all microphones."""
        return self.__correction_gains
    
    @correction_gains.setter
    def correction_gains(self, value):
        """Prevents setting the correction gains."""
        raise AttributeError('Cannot set correction_gains.')
        
    
    # private methods
    def __find_folders(self, condition=None):
        """
        This function returns a list of folders in self.__path that match a given condition.

        Parameters:
        condition (str, optional): The condition that folder names must match. If no condition is provided, all folders in the path are returned.

        Returns:
        list: A list of folder names that match the condition. If no folders match the condition, a message is printed and None is returned.
        """
        items = [f for f in os.listdir(self.__path) if os.path.isdir(os.path.join(self.__path, f))]
        if not condition:
            return items
        cond_items = [item for item in items if os.path.isdir(os.path.join(self.__path, item)) and condition in item]
        if cond_items:
            return cond_items
        else:
            print(f"No folders found with {condition} in their names.")
            return None
        
    def __A_weighting_filter(self, s, fs):
        """Design of an A-weighting filter.
        b, a = A_weighting(fs) designs a digital A-weighting filter for sampling frequency `fs`. Usage: y = scipy.signal.lfilter(b, a, x).
        Warning: `fs` should normally be higher than 20 kHz. For example,
        fs = 48000 yields a class 1-compliant filter.
        References:
        [1] IEC/CD 1672: Electroacoustics-Sound Level Meters, Nov. 1996.
        """
        # Definition of analog A-weighting filter according to IEC/CD 1672.
        f1 = 20.598997
        f2 = 107.65265
        f3 = 737.86223
        f4 = 12194.217
        A1000 = 1.9997

        NUMs = [(2*np.pi * f4)**2 * (10**(A1000/20)), 0, 0, 0, 0]
        DENs = np.polymul([1, 4*np.pi * f4, (2*np.pi * f4)**2],
                    [1, 4*np.pi * f1, (2*np.pi * f1)**2])
        DENs = np.polymul(np.polymul(DENs, [1, 2*np.pi * f3]),
                                    [1, 2*np.pi * f2])

        b, a = bilinear(NUMs, DENs, fs)
           
        return lfilter(b, a, s)
        
    @classmethod
    def __calculate_rms(cls, x):
        """
        Calculates the root mean square (RMS) of the given array.

        This method computes the RMS  of the input array `x`. The RMS  is 
        calculated as the square root of the mean of the squares of the elements 
        in `x`.

        Args:
            x (numpy.ndarray): A numpy array for which the RMS is to be calculated.

        Returns:
            float: The RMS of the input array.
        """
        return np.sqrt(np.sum(np.square(x))/len(x))
        

    # class methods
    @classmethod
    def match_duration(cls, n: list, fs):
        """
        Matches the duration of elements in the list `n` to the duration of the first element.

        This method adjusts the duration of each element in the list `n` to match the duration 
        of the first element in the list. If an element is longer than the first element, it is 
        truncated. If an element is shorter, it is looped using crossfading to match the duration.

        Args:
            n (list): A list of numpy arrays where each array represents a signal.
            fs (int): The sampling frequency of the signals.

        Returns:
            list: A list of numpy arrays with matched durations.

        Notes:
            - If the list `n` contains only one element, it is returned as is.
            - Crossfading is used to loop shorter elements. The crossfade duration is set to 1 second.
            - The crossfade is achieved using the first quarter of sine and cosine functions.

        Example:
            >>> signals = [np.array([1, 2, 3, 4, 5]), np.array([1, 2, 3])]
            >>> fs = 44100
            >>> matched_signals = Car.match_duration(signals, fs)
        """
        if len(n) == 1:
            return n
        
        # Check if all arrays have the same number of columns
        num_columns = n[0].shape[1] if len(n[0].shape) > 1 else 1
        for component in n:
            if (len(component.shape) > 1 and component.shape[1] != num_columns) or (len(component.shape) == 1 and num_columns != 1):
                raise ValueError("All components must have the same number of columns.")
        
        def create_sine_cosine_masks(period):
            '''Create the first quarter of sine and cosine functions for crossfading. 
            period must be 4*crossfade_seconds.
            '''
            f = 1 / period
            samples = np.arange(period * fs) / fs
            sine = np.sin(2 * np.pi * f * samples)
            cos = np.cos(2 * np.pi * f * samples)
            # return the first quarter of each function
            return sine[:int(len(samples)/4)], cos[:int(len(samples)/4)]
        
        x = n.pop(0)
        if num_columns == 1:
            for i, element in enumerate(n):
                if len(element) >= len(x):
                    n[i] = element[:len(x)]
                elif len(element) < len(x):
                    crossfade_seconds = 1
                    crossfade_samples = int(crossfade_seconds*fs) # Number of samples for crossfade
            
                    # Create sine and cosine masks for crossfading. 
                    # We want the first quarter of each function, 
                    # so the length should be 4*crossfade_seconds.
                    sine, cos = create_sine_cosine_masks(4*crossfade_seconds)

                    start = element[0:crossfade_samples]
                    middle = element[crossfade_samples:len(element)-crossfade_samples]
                    end = element[len(element)-crossfade_samples:]
                    cf = start * sine + end * cos 
                
                    result = np.concatenate((start, middle, cf))
                    while len(result) < len(x):
                        result = np.concatenate((result, middle))
                        if len(result) + len(cf) > len(x):
                            result = np.concatenate((result, end))
                        else:
                            result = np.concatenate((result, cf))
                    
                    # Cut result to match the length of x
                    n[i] = result[:len(x)]
            n.insert(0, x)
            return n
        else:
            reference_len = len(x[:, 0])
            out = []
            for i, element in enumerate(n):
                if len(element[:, 0]) >= reference_len:
                    out.append(element[:reference_len, :])
                elif len(element[:, 0]) < reference_len:
                    crossfade_seconds = 1
                    crossfade_samples = int(crossfade_seconds*fs)
                    sine, cos = create_sine_cosine_masks(4*crossfade_seconds)
                    
                    crossfaded_mic = np.zeros((reference_len, num_columns))
                    for j in range(num_columns):
                        start = element[0:crossfade_samples, j]
                        middle = element[crossfade_samples:len(element)-crossfade_samples, j]
                        end = element[len(element)-crossfade_samples:, j]
                        cf = start * sine + end * cos 
                    
                        result = np.concatenate((start, middle, cf))
                        while len(result) < reference_len:
                            result = np.concatenate((result, middle), axis=0)
                            if len(result) + len(cf) > len(x):
                                result = np.concatenate((result, end), axis=0)
                            else:
                                result = np.concatenate((result, cf), axis=0)
                        
                        # Cut result to match the length of reference
                        crossfaded_mic[:, j] = result[:reference_len]
                    out.append(crossfaded_mic)
            out.insert(0, x)
            return out
        
        

    # instance methods
    def speaker_locations_angles(self, mic_setup):
        """
        Returns the speaker locations and their corresponding angles with respect to the center of the microphone array.
        
        Args:
            mic_setup (str): The microphone setup to use.
        
        Returns:
            dict or None: A dictionary with speaker locations as keys and their corresponding angles as values.
                          Returns None if the microphone setup is 'distributed'.
        
        Raises:
            ValueError: If the make and model combination is not recognized.
        """
        if mic_setup == 'distributed':
            return None
        if self.make + '_' + self.model == 'Smart_forfour':
            angles = { 
                    'd50': -28,
                    'fp60': 26,
                    'fp80': 18,
                    'prl': -12,
                    'prm': 0,
                    'prr': 12
                    }
        if self.make + '_' + self.model == 'Volkswagen_Golf':
            angles = {
                    'd': -25,
                    'fp': 25,
                    'prl': -13,
                    'prm': 0,
                    'prr': 13,
                    'prm10l': -4,
                    'prm10r': 4
            }
        return angles
    

    def load_noise(self, mic_setup: str, condition):
        """
        Loads the noise recording channels for a given microphone setup and noise condition.

        Args:
            mic_setup (str): The microphone setup to load the noise recording for.
            condition (str): The specific noise condition to load ("speed condition_window condition").

        Returns:
            tuple: A tuple containing the noise data as a NumPy array (N_samples x M_channels) and the sampling frequency of noise recording.

        Raises:
            ValueError: If the given noise condition is not available for the given microphone setup.
        """
        if condition not in self.noise_recordings[mic_setup]:
            new_condition = condition + '_ver1'
            if new_condition not in self.noise_recordings[mic_setup]:
                raise ValueError(f"Noise condition {condition} is not available in Car.noise_recordings[mic_setup].")
            condition = new_condition
        noise_path = os.path.join(self.__path, mic_setup, 'noise', condition + '.wav')
        noise, fs_noise = sf.read(noise_path)
        # resample
        if fs_noise != self.fs:
            noise = librosa.resample(noise, orig_sr=fs_noise, target_sr=self.fs, axis=0)
            fs_noise = self.fs
        return noise, fs_noise
    
    def load_ir(self, mic_setup: str, condition):
        """
        Loads the impulse response (IR) channels for a given microphone setup and IR condition.
        
        Args:
            mic_setup (str): The microphone setup to load the IR for.
            condition (str): The specific IR condition to load ("speaker location_window condition").
        
        Returns:
            tuple: A tuple containing the IR data as a NumPy array (N_samples x M_channels) and the sampling frequency of IR.
        
        Raises:
            ValueError: If the given IR condition is not available for the given microphone setup.
        """
        if condition not in self.irs[mic_setup]:
            raise ValueError(f"IR condition {condition} is not in Car.irs[mic_setup].")
        ir_path = os.path.join(self.__path, mic_setup, 'IRs', condition + '.wav')
        ir, fs_ir = sf.read(ir_path)
        # resample
        if fs_ir != self.fs:
            ir = librosa.resample(ir, orig_sr=fs_ir, target_sr=self.fs, axis=0)
            fs_ir = self.fs
        return ir, fs_ir
    
    def load_radio_ir(self, mic_setup: str, condition):
        """
        Loads the radio impulse response (IR) channels for a given microphone setup and radio condition.
        
        Args:
            mic_setup (str): The microphone setup to load the IR for.
            condition (str): The specific IR condition to load ("window condition").
        
        Returns:
            tuple: A tuple containing the IR data as a NumPy array (N_samples x M_channels) and the sampling frequency of radio IR.
        
        Raises:
            ValueError: If radio IRs are not available.
            ValueError: If the given radio IR condition is not available for the given microphone configuration.
        """
        if not self.radio_irs[mic_setup]:
            raise ValueError(f"Radio IRs not available for this car.")
        if condition not in self.radio_irs[mic_setup]:
            raise ValueError(f"Radio IR condition {condition} is not in Car.radio_irs[condition].")
        ir_path = os.path.join(self.__path, mic_setup, 'radio_IRs', condition + '.wav')
        ir, fs_ir = sf.read(ir_path) 
        # resmaple
        if fs_ir != self.fs:
            ir = librosa.resample(ir, orig_sr=fs_ir, target_sr=self.fs, axis=0)
            fs_ir = self.fs   
        return ir, fs_ir
    

    def load_ventilation(self, mic_setup: str, condition):
        """
        Loads the ventilation recording for a given microphone setup and condition.
        
        Args:
            mic_setup (str): The microphone setup to load the ventilation recording for.
            condition (str): The specific ventilation condition to load ("ventilation level_window condition").
        
        Returns:
            tuple: A tuple containing the ventilation data as a NumPy array (N_samples x M_channels) and the sampling frequency.
        
        Raises:
            ValueError: If the given ventilation condition is not available for the given microphone setup.
        """
        if condition not in self.ventilation_recordings[mic_setup]:
            raise ValueError(f"Ventilation condition {condition} is not in Car.ventilation_recordings[condition].")
        ventilation_path = os.path.join(self.__path, mic_setup, 'ventilation', condition + '.wav')
        ventilation, fs_ventilation = sf.read(ventilation_path)
        # resample
        if fs_ventilation != self.fs:
            ventilation = librosa.resample(ventilation, orig_sr=fs_ventilation, target_sr=self.fs, axis=0)
            fs_ventilation = self.fs
        return ventilation, fs_ventilation


    def get_speech(self, mic_setup: str, location: str, window:int, ls: float, dry_speech, mics=None, use_correction_gains=True):
        """
        Generates the convolved speech signal with the corresponding impulse response for a given microphone setup, location, and condition.
        
        Args:
            mic_setup (str): The microphone setup to use.
            location (str): The location of the speaker.
            window (int): The window condition.
            ls (float): The speech effort level.
            dry_speech (numpy.ndarray): The input speech signal vector.
            mics (int or list of int, optional): The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.
            use_correction_gains (bool, optional): A boolean indicating whether to use the correction gains. Defaults to True.
        
        Returns:
            numpy.ndarray: The processed speech signal for the specified microphones.
        
        Raises:
            ValueError: If the microphone setup is not available.
            ValueError: If the location is not available.
            ValueError: If the speech effort is negative.
            ValueError: If the window condition is invalid.
            ValueError: If mics is not an integer or a list of integers.
        """
        if mic_setup not in self.mic_setups:
            raise ValueError(f"Microphone setup {mic_setup} is not available.")
        if location not in self.speaker_locations[mic_setup]:
            raise ValueError(f"location {location} is not available.")
        if ls < 0:
            raise ValueError(f"Speech effort must be positive.")
        if window not in [0, 1, 2, 3]:
            raise ValueError(f"Window condition in condition must be 0, 1, 2 or 3.")
        if not (isinstance(mics, list) and all(isinstance(item, int) for item in mics)) and not isinstance(mics, int) and mics is not None:
            raise ValueError(f"mics must be an integer or a list of integers.")
        ir_condition = f'{location}_w{window}'
        ir, _ = self.load_ir(mic_setup, ir_condition) #check if ir_fs = car.fs!
        ir_reference = ir[:, self.__reference_mic[mic_setup]]
        convolved_reference_signal = np.convolve(dry_speech, ir_reference, mode='full')
        convolved_reference_signal = self.__A_weighting_filter(convolved_reference_signal, self.fs)
        #################
        # NO VAD
        # Calculate RMS
        convolved_reference_rms = Car.__calculate_rms(convolved_reference_signal)
        # to dB
        convolved_reference_level = 20 * np.log10(convolved_reference_rms)
        print('no vad:', convolved_reference_level)
        #################
        # VAD
        convolved_reference_level = vad_mean_rms(convolved_reference_signal, self.fs, srhThreshold = 0.1)
        print('vad:', convolved_reference_level)
        #################
        reference = self.__references[mic_setup][ir_condition] + (ls - 72.5)
        # Calculate correction factor
        correction_factor = reference - convolved_reference_level
        gain = 10 ** (correction_factor / 20)

        if not isinstance(mics, list):
            mics = [mics]
        if mics is None:
            mics = range(ir.shape[1])
        result = []
        for mic in mics:
            # Apply correction factor to selected microphone
            convolved_x = np.convolve(dry_speech, ir[:, mic], mode='full')
            # apply correction gain
            if use_correction_gains:
                mic_gain = gain * self.correction_gains[str(mic)]
                convolved_x *= mic_gain
            else:
                convolved_x *= gain
         
            result.append(convolved_x)

        result = np.array(result).T
        return result
    

    def get_noise(self, mic_setup:str, speed:int, window:int, version:str=None, mics=None, use_correction_gains=True):
        """
        Retrieves the in-motion noise recording for a given microphone setup, condition, and microphone index.
        
        Args:
            mic_setup (str): The microphone setup to use.
            speed (int): The speed condition.
            window (int): The window condition.
            version (str, optional): The version of the noise recording in case there are multiple versions. Defaults to None. Must be "ver1", "ver2", etc or "coarse". 
            mics (int or list of int, optional): The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.
            use_correction_gains (bool, optional): A boolean indicating whether to use the correction gains. Defaults to True.
        
        Returns:
            numpy.ndarray: The processed noise signal.
        
        Raises:
            ValueError: If the specified microphone setup is not available.
            ValueError: If mics is not an integer or a list of integers.
        """
        if mic_setup not in self.mic_setups:
            raise ValueError(f"Microphone setup {mic_setup} is not available.")
        if not (isinstance(mics, list) and all(isinstance(item, int) for item in mics)) and not isinstance(mics, int) and mics is not None:
            raise ValueError(f"mics must be an integer or a list of integers.")
        if window not in [0, 1, 2, 3]:
            raise ValueError(f"Window condition in condition must be 0, 1, 2 or 3.")
        condition = f's{speed}_w{window}'
        if version:
            condition += f'_{version}'
        noise, _ = self.load_noise(mic_setup, condition)

        if not isinstance(mics, list):
            mics = [mics]
        if mics is None:
            mics = range(noise.shape[1])
        noise = noise[:, mics] 
        # apply correction gain
        if use_correction_gains:
            gains = [self.correction_gains[str(mic)] for mic in mics]
            noise = noise * np.array(gains)

        return noise
    

    def get_radio(self, mic_setup: str, window:int, la: float, radio_audio, mics=None, use_correction_gains=True):
        """
        Generates the radio (car-audio) signal by exploiting the measured  impulse response for a given microphone setup, condition, and microphone index.
        
        Args:
            mic_setup (str): The microphone setup to use.
            window (int): The window condition.
            la (float): The radio audio level.
            radio_audio (numpy.ndarray): The input audio signal, provided by the user.
            radio_audio_fs (int): The sampling frequency of the input audio signal.
            mics (int or list of int, optional): The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.
            use_correction_gains (bool, optional): A boolean indicating whether to use the correction gains. Defaults to True.
        
        Returns:
            numpy.ndarray: The processed audio signal for the specified microphones.
        
        Raises:
            ValueError: If the microphone setup is not available.
            ValueError: If the audio level is negative.
            ValueError: If the window condition is invalid.
            ValueError: If mics is not an integer or a list of integers.
        """
        if mic_setup not in self.mic_setups:
            raise ValueError(f"Microphone setup {mic_setup} is not available.")
        if la < 0:
            raise ValueError(f"Audio level must be positive.")
        if window not in [0, 1, 2, 3]:
            raise ValueError(f"Window condition must be 0, 1, 2 or 3.")
        if not (isinstance(mics, list) and all(isinstance(item, int) for item in mics)) and not isinstance(mics, int) and mics is not None:
            raise ValueError(f"mics must be an integer or a list of integers.")
        
        db_fsa_to_db_a = {
            0: 124.8755,
            1: 124.8381,
            2: 124.7017,
            3: 124.9197,
            4: 124.3212,
            5: 126.4183,
            6: 125.8413,
            7: 124.9133,
            }
             
        radio_ir_condition = f'w{window}'
        radio_ir, _ = self.load_radio_ir(mic_setup, radio_ir_condition)
        radio_ir_reference = radio_ir[:, self.__reference_mic[mic_setup]]

        convolved_radio_reference_signal = np.convolve(radio_audio, radio_ir_reference, mode='full')
        # Apply A-weighting filter
        convolved_radio_reference_signal = self.__A_weighting_filter(convolved_radio_reference_signal, self.fs)
        # Calculate RMS
        convolved_radio_rms = Car.__calculate_rms(convolved_radio_reference_signal)
        # to dB
        convolved_radio_level = 20 * np.log10(convolved_radio_rms)
        level = convolved_radio_level + db_fsa_to_db_a[self.__reference_mic[mic_setup]] 
        # Calculate correction factor
        correction_factor = la - level
        gain = 10 ** (correction_factor / 20)
        if not isinstance(mics, list):
            mics = [mics]
        if mics is None:
            mics = range(radio_ir.shape[1])
        result = []
        for mic in mics:
            convolved_radio_ir = np.convolve(radio_audio, radio_ir[:, mic], mode='full')
            # apply correction gain
            if use_correction_gains:
                mic_gain = gain * self.correction_gains[str(mic)]
                convolved_radio_ir *= mic_gain
            else:
                convolved_radio_ir *= gain
            result.append(convolved_radio_ir)
        result = np.array(result).T
        return result


    def get_ventilation(self, mic_setup: str, window:int, level: int, mics=None, use_correction_gains=True):
        """
        Retrieves and processes the ventilation recording for a given microphone setup, condition, and ventilation level.
        
        Args:
            mic_setup (str): The microphone setup to use.
            window (int): The window condition.
            level (int): The ventilation level (must be 1, 2, or 3).
            mics (int or list of int, optional): The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.
            use_correction_gains (bool, optional): A boolean indicating whether to use the correction gains. Defaults to True.
        
        Returns:
        numpy.ndarray: The processed ventilation signal for the specified microphones.

        Raises:
            ValueError: If the microphone setup is not available.
            ValueError: If the ventilation level is not 1, 2, or 3.
            ValueError: If the window condition is invalid.
            ValueError: If mics is not an integer or a list of integers.
        """
        if mic_setup not in self.mic_setups:
            raise ValueError(f"Microphone setup {mic_setup} is not available.")
        if level not in [1, 2, 3]:
            raise ValueError(f"Ventilation level must be 1, 2 or 3.")
        if window not in [0, 1, 2, 3]:
            raise ValueError(f"Window condition must be 0, 1, 2 or 3.")
        if not (isinstance(mics, list) and all(isinstance(item, int) for item in mics)) and not isinstance(mics, int) and mics is not None:
            raise ValueError(f"mics must be an integer or a list of integers.")
        ventilation_condition = f'v{level}_w{window}'
        ventilation, _ = self.load_ventilation(mic_setup, ventilation_condition)
        # resample to fs
        if not isinstance(mics, list):
            mics = [mics]
        if mics is None:
            mics = range(ventilation.shape[1])
        ventilation = ventilation[:, mics]
        # apply correction gain
        if use_correction_gains:
            gains = [self.correction_gains[str(mic)] for mic in mics]
            ventilation = ventilation * np.array(gains)
        return ventilation  
    

    def get_components(self, mic_setup, location, speed:int, window:int, version:str=None, mics=None, ls=None, dry_speech=None, la=None, radio_audio=None, vent_level=None, use_correction_gains=True): 
        """
        A wrapper function of the get_noise, get_speech, get_radio, and get_ventilation methods.
        Returns a list of components of the mixture in the following order: noise, speech, radio, ventilation.
        Speech, radio, and ventilation are optional.
        
        Args:
            mic_setup (str): The microphone setup to use.
            location (str): The location of the speaker.
            speed (int): The speed condition.
            window (int): The window condition.
            version (str, optional): The version of the noise recording in case there are multiple versions. Defaults to None. Must be "ver1", "ver2", etc or "coarse". 
            mics (int or list of int, optional): The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.
            ls (float, optional): The speech effort level. Defaults to None.
            dry_speech (numpy.ndarray, optional): The input speech signal vector.
            la (float, optional): The reference audio level. Defaults to None.
            radio_audio (numpy.ndarray, optional): The input audio signal vector.
            vent_level (float, optional): The ventilation level. Defaults to None.
            use_correction_gains (bool, optional): A boolean indicating whether to use the correction gains. Defaults to True.
        
        Returns:
            list: A list of NumPy arrays representing the components of the mixture. Order: noise, speech (optional), radio(optional), ventilation(optional).
        
        Raises:
            ValueError: If the microphone setup, location, or condition is not available.
            ValueError: If the speech effort or audio level is negative.
            ValueError: If dry speech  or dry speech sampling frequency is not provided when speech effort level is specified.
            ValueError: If radio audio or radio audio sampling frequency is not provided when reference audio level is specified.
        """
        l = []
        if ls:
            if dry_speech is None:
                raise ValueError("Dry speech must be provided if ls is provided.")
            sp = self.get_speech(mic_setup=mic_setup, location=location, window=window, ls=ls, dry_speech=dry_speech, mics=mics, use_correction_gains=use_correction_gains)
            l.append(sp)
        if la:
            if radio_audio is None:
                raise ValueError("Radio audio must be provided if la is provided.")
            radio_audio = self.get_radio(mic_setup=mic_setup, window=window, la=la, radio_audio=radio_audio, mics=mics, use_correction_gains=use_correction_gains)
            l.append(radio_audio)
        if vent_level:
            vent = self.get_ventilation(mic_setup=mic_setup, window=window, level=vent_level, mics=mics, use_correction_gains=use_correction_gains)
            l.append(vent)
        n = self.get_noise(mic_setup=mic_setup, speed=speed, window=window, version=version, mics=mics, use_correction_gains=use_correction_gains)
        l.append(n)
        
        # s, a, v, n
        out = Car.match_duration(l, self.fs)

        # n, s, a, v
        out = [out[-1]] + out[:-1]

        return out

    def construct_steering_vector(self, freq, theta):
        """
        Calculates the steering vectors for a given frequency and angle for a microphone array configuration.
        The acoustic center is defined as the center of the microphone array. 0 degrees point towards the rear middle passenger,
        so that the driver is positioned at a negative angle and the front passenger at a positive angle.
        
        Args:
            freq (float): The frequency in Hz at which to calculate the steering vectors.
            theta (float): The angle in degrees at which to calculate the steering vectors.
        
        Returns:
            numpy.ndarray: An array of complex steering vectors for each microphone in the array.
        """
        mic_angles = {
            0: np.pi,
            1: 3*np.pi/4,
            2: np.pi/2,
            3: np.pi/4,
            4: 0,
            5: -np.pi/4,
            6: -np.pi/2,
            7: -3*np.pi/4,
        }
        c = 343
        theta = np.deg2rad(theta)
        result = []
        for mic in mic_angles.keys():
            result.append(np.exp(1j * 2 * np.pi * freq / c * np.cos(theta - mic_angles[mic])))
        
        return np.array(result)
