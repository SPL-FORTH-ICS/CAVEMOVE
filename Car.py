# from dataclasses import dataclass, field
from natsort import natsort_keygen
# from source.vad import vad_mean_rms
# from typing import List, Optional, Dict
import scipy.signal as signal
import os
import time
# import re
import librosa
import json
import soundfile as sf
import numpy as np
import waveform_analysis


class Car:
    """
    A class to represent a car and the recordings associated with it.\
    The class provides methods to load and process the recordings.

    Args:
    path (str): The path to the car recordings.
    fs (int): The sampling frequency of the recordings. Defaults to 16000.
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
        # self.__reference_mic = {}
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

            # # Reference_mic
            # ref_file = os.path.join(self.__path, mic_setup, 'reference', 'reference_mic.json')
            # with open(ref_file, 'r') as f:
            #     self.__reference_mic = json.load(f)

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
        """Returns a dictionary of available radio IR conditions per microphone configuration."""
        return self.__radio_irs
    
    @radio_irs.setter
    def radio_irs(self, value):
        """Prevents setting the radio IRs."""
        raise AttributeError('Cannot set radio_irs.')
    
    # @property
    # def __references(self):
    #     """Returns a dictionary of available reference levels for every speaker condition per microphone configuration."""
    #     return self.__references
    
    # @__references.setter
    # def __references(self, value):
    #     """Prevents setting the reference recordings."""
    #     raise AttributeError('Cannot set reference_recordings.')
    
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
        """Returns a dictionary of correction gains."""
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
        
    @classmethod
    def __calculate_rms(cls, x):
        """
        Calculates the root mean square (RMS) mean of the given array.

        This method computes the RMS mean of the input array `x`. The RMS mean is 
        calculated as the square root of the mean of the squares of the elements 
        in `x`.

        Args:
            x (numpy.ndarray): A numpy array for which the RMS mean is to be calculated.

        Returns:
            float: The RMS mean of the input array.
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
                        crossfaded_mic[:, j] = result[:reference_len, :]
                    out.append(crossfaded_mic)
            out.insert(0, x)
            return out
        
        

    # instance methods
    def speaker_locations_angles(self, mic_setup):
        """
        Returns the speaker locations and their corresponding angles for microphone array configurations.
        
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
            raise ValueError(f"Noise condition {condition} is not available.")
        noise_path = os.path.join(self.__path, mic_setup, 'noise', condition + '.wav')
        # s, fs_noise = librosa.load(noise_path, sr=fs, mono=False)
        noise, fs_noise = sf.read(noise_path)
        if fs_noise != self.fs:
            noise = librosa.resample(noise, orig_sr=fs_noise, target_sr=self.fs, axis=0)
            fs_noise = self.fs
        return noise, fs_noise
    
    def load_ir(self, mic_setup: str, condition):
        """
        Loads the impulse response (IR) channels for a given microphone setup and IR condition.
        
        Args:
            mic_setup (str): The microphone setup to load the IR for.
            condition (str): The specific IR condition to load ("speaker position_window condition").
        
        Returns:
            tuple: A tuple containing the IR data as a NumPy array (N_samples x M_channels) and the sampling frequency of IR.
        
        Raises:
            ValueError: If the given IR condition is not available for the given microphone setup.
        """
        if condition not in self.irs[mic_setup]:
            raise ValueError(f"IR condition {condition} is not in Car.irs[condition].")
        ir_path = os.path.join(self.__path, mic_setup, 'IRs', condition + '.wav')
        # ir, fs_ir = librosa.load(ir_path, sr=48000, mono=False)
        ir, fs_ir = sf.read(ir_path)
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
        # ir, fs_ir = librosa.load(ir_path, sr=fs, mono=False)
        ir, fs_ir = sf.read(ir_path) 
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
        # ventilation, fs_ventilation = librosa.load(ventilation_path, sr=fs, mono=False)
        ventilation, fs_ventilation = sf.read(ventilation_path)
        if fs_ventilation != self.fs:
            ventilation = librosa.resample(ventilation, orig_sr=fs_ventilation, target_sr=self.fs, axis=0)
            fs_ventilation = self.fs
        return ventilation, fs_ventilation


    def get_speech(self, mic_setup: str, position: str, condition: str, l_s: float, dry_speech, mics=None, use_correction_gains=True):
        """
        Generates the convolved speech signal with the corresponding impulse response for a given microphone setup, position, and condition.
        
        Args:
            mic_setup (str): The microphone setup to use.
            position (str): The position of the speaker.
            condition (str): The condition of the recording ("speaker position_window condition").
            l_s (float): The speech effort level.
            dry_speech (numpy.ndarray): The input speech signal vector.
            dry_speech_fs (int): The sampling frequency of the input speech signal.
            mics (int or list of int, optional): The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.
            use_correction_gains (bool, optional): A boolean indicating whether to use the correction gains. Defaults to True.
        
        Returns:
            numpy.ndarray: The processed speech signal for the specified microphones.
        
        Raises:
            ValueError: If the microphone setup is not available.
            ValueError: If the position is not available.
            ValueError: If the speech effort is negative.
            ValueError: If the window condition is invalid.
            ValueError: If the microphone index is not an integer or a list of integers.
        """
        if mic_setup not in self.mic_setups:
            raise ValueError(f"Microphone setup {mic_setup} is not available.")
        if position not in self.speaker_locations[mic_setup]:
            raise ValueError(f"Position {position} is not available.")
        if l_s < 0:
            raise ValueError(f"Speech effort must be positive.")
        w_condition = int(condition.split('_')[0][-1])
        if w_condition not in [0, 1, 2, 3]:
            raise ValueError(f"Window condition in condition must be 0, 1, 2 or 3.")
        if not (isinstance(mics, list) and all(isinstance(item, int) for item in mics)) and not isinstance(mics, int) and mics is not None:
            raise ValueError(f"mics must be an integer or a list of integers.")
        ir_condition = f'{position}_w{w_condition}'
        ir, ir_fs = self.load_ir(mic_setup, ir_condition)
        ir_reference = ir[:, self.__reference_mic[mic_setup]]
        # print('ir_reference_level : ', 20 * np.log10(Car.calculate_rms(ir_reference)))
        # print('x : ', 20 * np.log10(Car.calculate_rms(x)))
        
        #########################3
        # ir_ref_path = '/media/andreas/1TB/FORTH/CAVEMOVE/Smart_array_plw1-5.wav'
        # ir_path = '/media/andreas/1TB/FORTH/CAVEMOVE/Smart_array_plw1-1.wav'

        # ir, ir_fs = sf.read(ir_path)
        # ir_reference, _ = sf.read(ir_ref_path)
        ########################
        # plt.plot(ir)
        # plt.title('IR')
        # plt.figure()
        # plt.plot(ir_reference)
        # plt.title('IR - ref')
        # plt.show()
        ###########
        # x_filtered = waveform_analysis.A_weight(x, 48000)
        # x_filtered_level = 20 * np.log10(Car.calculate_rms(x_filtered))
        # ir_filtered = waveform_analysis.A_weight(ir, 48000)
        # ir_filtered_level = 20 * np.log10(Car.calculate_rms(ir_filtered))
        ###########
        convolved_reference_ir = np.convolve(dry_speech, ir_reference, mode='full')
        # print('convolved_reference_ir_level  : ', 20 * np.log10(Car.calculate_rms(convolved_reference_ir)))

        # convolved_reference_ir = convolved_reference_ir
        # Apply A-weighting filter
        # convolved_reference_ir = Car.a_weighting_filter(convolved_reference_ir)
        convolved_reference_ir= waveform_analysis.A_weight(convolved_reference_ir, ir_fs)

        # TODO: Choose if vad is applied or optional
        #####################
        # NO VAD
        # Calculate RMS mean
        convolved_reference_ir_rms = Car.__calculate_rms(convolved_reference_ir)
        # to dB
        convolved_reference_ir_level = 20 * np.log10(convolved_reference_ir_rms)
        # print('convolved_reference_ir_filtered_level  : ', convolved_reference_ir_level)
        
        # convolved_reference_ir_level = 10 * np.log10(convolved_reference_ir_rms)

        # print('no vad:', convolved_reference_ir_level)
        #####################
        # VAD
        # convolved_x_rms = vad_mean_rms(convolved_x_a_filtered[:, 0], fs=fs)
        # print('vad:', convolved_x_rms)
        #####################
        reference = self.__references[mic_setup][ir_condition] + (l_s - 72.5)
        # Calculate correction factor
        correction_factor = reference - convolved_reference_ir_level
        gain = 10 ** (correction_factor / 20)
        # print('Gain:', gain)

        if not isinstance(mics, list):
            mics = [mics]
        if mics is None:
            mics = range(ir.shape[1])
        result = []
        for mic in mics:
            # Apply correction factor to selected microphone
            convolved_x = np.convolve(dry_speech, ir[:, mic], mode='full')
            # print('Convolved x level :', 20 * np.log10(Car.calculate_rms(convolved_x)))
            # apply correction gain
            if use_correction_gains:
                mic_gain = gain * self.correction_gains[str(mic)]
                convolved_x *= mic_gain
            else:
                convolved_x *= gain
            ###############
            # convolved_x_filtered = waveform_analysis.A_weight(convolved_x, ir_fs)
            ###############           
            result.append(convolved_x)
            ###############
            # print('voice dB_fs_a:', 20 * np.log10(Car.calculate_rms(convolved_x_filtered)))
            ###############
        result = np.array(result).T
        return result
    

    def get_noise(self, mic_setup:str, condition:str, mics=None, use_correction_gains=True):
        """
        Retrieves the in-motion noise recording for a given microphone setup, condition, and microphone index.
        
        Args:
            mic_setup (str): The microphone setup to use.
            condition (str): The specific noise condition to load ("speed condition_window condition").
            mics (int or list of int, optional): The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.
            use_correction_gains (bool, optional): A boolean indicating whether to use the correction gains. Defaults to True.
        
        Returns:
            numpy.ndarray: The processed noise signal.
        
        Raises:
            ValueError: If the specified microphone setup is not available.
            ValueError: If the microphone index is not an integer or a list of integers.
        """
        if mic_setup not in self.mic_setups:
            raise ValueError(f"Microphone setup {mic_setup} is not available.")
        if not (isinstance(mics, list) and all(isinstance(item, int) for item in mics)) and not isinstance(mics, int) and mics is not None:
            raise ValueError(f"mics must be an integer or a list of integers.")
        noise, fs_noise = self.load_noise(mic_setup, condition)
        ###############
        # filtered_noise = waveform_analysis.A_weight(noise, fs_noise)
        ###############
        if not isinstance(mics, list):
            mics = [mics]
        if mics is None:
            mics = range(noise.shape[1])
        noise = noise[:, mics] 
        # apply correction gain
        if use_correction_gains:
            gains = [self.correction_gains[str(mic)] for mic in mics]
            noise = noise * np.array(gains)
        ###############
        # print('noise dB_fs_a:', 20 * np.log10(Car.calculate_rms(filtered_noise)))
        ###############
        return noise
    

    def get_radio(self, mic_setup: str, condition: str, l_a: float, radio_audio, mics=None, correction_gains=True):
        """
        Generates the convolved audio signal with the corresponding radio impulse response for a given microphone setup, condition, and microphone index.
        
        Args:
            mic_setup (str): The microphone setup to use.
            condition (str): The specific condition to load ("speed condition_window condition").
            l_a (float): The radio audio level.
            radio_audio (numpy.ndarray): The input audio signal vector.
            radio_audio_fs (int): The sampling frequency of the input audio signal.
            mics (int or list of int, optional): The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.
            correction_gains (bool, optional): A boolean indicating whether to use the correction gains. Defaults to True.
        
        Returns:
            numpy.ndarray: The processed audio signal for the specified microphones.
        
        Raises:
            ValueError: If the microphone setup is not available.
            ValueError: If the audio level is negative.
            ValueError: If the window condition is invalid.
            ValueError: If the microphone index is not an integer or a list of integers.
        """
        if mic_setup not in self.mic_setups:
            raise ValueError(f"Microphone setup {mic_setup} is not available.")
        if l_a < 0:
            raise ValueError(f"Audio level must be positive.")
        w_condition = int(condition.split('_')[0][-1])
        if w_condition not in [0, 1, 2, 3]:
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
             
        radio_ir_condition = f'w{w_condition}'
        radio_ir, radio_ir_fs = self.load_radio_ir(mic_setup, radio_ir_condition)
        radio_ir_reference = radio_ir[:, self.__reference_mic[mic_setup]]
        # radio_ir = radio_ir[:, mic]
        # plt.plot(radio_ir)
        # plt.title('Radio IR')
        # plt.show()
        # convolved_radio_ir = []
        # for i in range(radio_ir.shape[1]):
        #     convolved_radio_ir.append(np.convolve(a, radio_ir[:, i], mode='same'))
        # convolved_radio_ir = np.array(convolved_radio_ir).T
        convolved_radio_reference_ir = np.convolve(radio_audio, radio_ir_reference, mode='full')
        # Apply A-weighting filter
        # convolved_radio_reference_ir = Car.a_weighting_filter(convolved_radio_reference_ir)
        convolved_radio_reference_ir= waveform_analysis.A_weight(convolved_radio_reference_ir, radio_ir_fs)
        # Calculate RMS mean
        convolved_radio_ir_rms = Car.__calculate_rms(convolved_radio_reference_ir)
        # to dB
        convolved_radio_ir_level = 20 * np.log10(convolved_radio_ir_rms)
        level = convolved_radio_ir_level + db_fsa_to_db_a[self.__reference_mic[mic_setup]] 
        # Calculate correction factor
        correction_factor = l_a - level
        gain = 10 ** (correction_factor / 20)
        if not isinstance(mics, list):
            mics = [mics]
        if mics is None:
            mics = range(radio_ir.shape[1])
        result = []
        for mic in mics:
            convolved_radio_ir = np.convolve(radio_audio, radio_ir[:, mic], mode='full')
            # apply correction gain
            if correction_gains:
                mic_gain = gain * self.correction_gains[str(mic)]
                convolved_radio_ir *= mic_gain
            else:
                convolved_radio_ir *= gain
            result.append(convolved_radio_ir)
            # resample to fs
            ###############
            # convolved_x_filtered = waveform_analysis.A_weight(convolved_radio_ir, radio_ir_fs)
            ###############
            ###############
            # print('radio dB_fs_a:', 20 * np.log10(Car.calculate_rms(convolved_x_filtered)))
            ###############
        result = np.array(result).T
        return result


    def get_ventilation(self, mic_setup: str, condition: str, level: int, mics=None, correction_gains=True):
        """
        Retrieves and processes the ventilation recording for a given microphone setup, condition, and ventilation level.
        
        Args:
            mic_setup (str): The microphone setup to use.
            condition (str): The specific condition to load ("speed condition_window condition").
            level (int): The ventilation level (must be 1, 2, or 3).
            mics (int or list of int, optional): The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.
            correction_gains (bool, optional): A boolean indicating whether to use the correction gains. Defaults to True.
        
        Returns:
        numpy.ndarray: The processed ventilation signal for the specified microphones.

        Raises:
            ValueError: If the microphone setup is not available.
            ValueError: If the ventilation level is not 1, 2, or 3.
            ValueError: If the window condition is invalid.
            ValueError: If the microphone index is not an integer or a list of integers.
        """
        if mic_setup not in self.mic_setups:
            raise ValueError(f"Microphone setup {mic_setup} is not available.")
        if level not in [1, 2, 3]:
            raise ValueError(f"Ventilation level must be 1, 2 or 3.")
        w_condition = int(condition.split('_')[0][-1])
        if w_condition not in [0, 1, 2, 3]:
            raise ValueError(f"Window condition must be 0, 1, 2 or 3.")
        if not (isinstance(mics, list) and all(isinstance(item, int) for item in mics)) and not isinstance(mics, int) and mics is not None:
            raise ValueError(f"mics must be an integer or a list of integers.")
        ventilation_condition = f'v{level}_w{w_condition}'
        ventilation, ventilation_fs = self.load_ventilation(mic_setup, ventilation_condition)
        ###############
        # filtered_ventilation = waveform_analysis.A_weight(ventilation, ventilation_fs)
        ###############
        # resample to fs
        if not isinstance(mics, list):
            mics = [mics]
        if mics is None:
            mics = range(ventilation.shape[1])
        ventilation = ventilation[:, mics]
        # apply correction gain
        if correction_gains:
            gains = [self.correction_gains[str(mic)] for mic in mics]
            ventilation = ventilation * np.array(gains)
        ###############
        # print('ventilation dB_fs_a:', 20 * np.log10(Car.calculate_rms(filtered_ventilation)))
        ###############
        return ventilation  
    

    def get_components(self, mic_setup, position, condition, mics, l_s=None, dry_speech=None, l_a=None, radio_audio=None, vent_level=None):
        """
        A wrapper function of the get_noise, get_speech, get_radio, and get_ventilation methods.
        Returns a list of components of the mixture in the following order: noise, speech, radio, ventilation.
        Speech, radio, and ventilation are optional.
        
        Args:
            mic_setup (str): The microphone setup to use.
            position (str): The position of the speaker.
            condition (str): The condition of the recording ("speed condition_window condition").
            mics (int or list of int, optional): The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.
            l_s (float, optional): The speech effort level. Defaults to None.
            dry_speech (numpy.ndarray, optional): The input speech signal vector.
            l_a (float, optional): The reference audio level. Defaults to None.
            radio_audio (numpy.ndarray, optional): The input audio signal vector.
            vent_level (float, optional): The ventilation level. Defaults to None.
        
        Returns:
            list: A list of NumPy arrays representing the components of the mixture. Order: noise, speech (optional), radio(optional), ventilation(optional).
        
        Raises:
            ValueError: If the microphone setup, position, or condition is not available.
            ValueError: If the speech effort or audio level is negative.
            ValueError: If dry speech  or dry speech sampling frequency is not provided when speech effort level is specified.
            ValueError: If radio audio or radio audio sampling frequency is not provided when reference audio level is specified.
        """
        l = []
        if l_s:
            if dry_speech is None:
                raise ValueError("Dry speech must be provided if l_s is provided.")
            # voice, fs_voice = sf.read(voice_path)
            # make mono
            # if dry_speech.ndim > 1:
                # dry_speech = np.mean(dry_speech,axis=1)
            sp = self.get_speech(mic_setup=mic_setup, position=position, condition=condition, l_s=l_s, dry_speech=dry_speech, mics=mics)
            l.append(sp)
        if l_a:
            if radio_audio is None:
                raise ValueError("Radio audio must be provided if l_a is provided.")
            # radio_audio, a_fs = sf.read(radio_path)
            # make mono
            # if radio_audio.ndim > 1:
                # radio_audio = np.mean(radio_audio,axis=1)
            radio_audio = self.get_radio(mic_setup=mic_setup, condition=condition, l_a=l_a, radio_audio=radio_audio, mics=mics)
            l.append(radio_audio)
        if vent_level:
            vent = self.get_ventilation(mic_setup=mic_setup, condition=condition, level=vent_level, mics=mics)
            l.append(vent)
        n = self.get_noise(mic_setup=mic_setup, condition=condition, mics=mics)
        l.append(n)
        
        # s, a, v, n
        out = Car.match_duration(l, self.fs)

        # n, s, a, v
        out = [out[-1]] + out[:-1]

        return out

    def construct_steering_vector(self, freq, theta):
        """
        Calculates the steering vectors for a given frequency and angle for a microphone array configuration.
        The center of the microphone array is the acoustic center. 0 degrees point towards the rear middle passenger,
        so that the driver is positioned at a negative angle and the front passenger at a positive angle.
        
        Args:
            freq (float): The frequency in Hz at which to calculate the steering vectors.
            theta (float): The angle in degrees at which to calculate the steering vectors.
        
        Returns:
            numpy.ndarray: An array of complex steering vectors for each microphone in the array.
        """
        # if mic_setup != 'array':
        #     raise ValueError('Steering vectors are only available for microphone array configurations.')
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
        # TODO: include gains
        theta = np.deg2rad(theta)
        result = []
        for mic in mic_angles.keys():
            result.append(np.exp(1j * 2 * np.pi * freq / c * np.cos(theta - mic_angles[mic])))
        
        return np.array(result)
