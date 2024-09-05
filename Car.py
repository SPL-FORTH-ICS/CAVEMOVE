# from dataclasses import dataclass, field
from natsort import natsort_keygen
from vad import vad_mean_rms
# from typing import List, Optional, Dict
import scipy.signal as signal
import os
import time
# import re
import librosa
import json
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import waveform_analysis


class Car:
    def __init__(self, path, txt_info, info_dict = None):
        self.__path = path
        self.__txt_info = txt_info
        if self.__txt_info:
            # TODO: Ignore rest of args and read from txt
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
            wav_list = os.listdir(os.path.join(self.__path, mic_setup, 'radio_IRs'))
            self.__radio_irs[mic_setup] = sorted([wav[:-4] for wav in wav_list], key=natsort_key)

            # Ventilation
            wav_list = os.listdir(os.path.join(self.__path, mic_setup, 'ventilation'))
            self.__ventilation[mic_setup] = sorted([wav[:-4] for wav in wav_list], key=natsort_key)

            # References
            ref_file = os.path.join(self.__path, mic_setup, 'reference', 'reference.json')
            with open(ref_file, 'r') as f:
                self.__references[mic_setup] = json.load(f)

    def __repr__(self):
        return f'Car(path={self.__path!r}, txt_info=False, info_dict={self.__in_dict!r})'
        
        
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
    
    @property
    def references(self):
        """Returns a dictionary of available reference levels for every speaker condition per microphone configuration."""
        return self.__references
    
    @references.setter
    def references(self, value):
        """Prevents setting the reference recordings."""
        raise AttributeError('Cannot set reference_recordings.')
    
    @property
    def reference_mic(self):
        """Returns a dictionary of the reference microphone per microphone configuration."""
        reference_mics = {
            'AlphaRomeo': {'array': None, 'distributed': 2},
            'hondaCRV': {'array': 4, 'distributed': 2},
            'Smartfor2': {'array': 4, 'distributed': 0},
            'Volkswagen': {'array': 4, 'distributed': 0},
        }
        return reference_mics[self.make + self.model]
    
    @reference_mic.setter
    def reference_mic(self, value):
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
    def speaker_positions(self):
        """Returns a dictionary of available speaker positions per microphone configuration."""
        natsort_key = natsort_keygen(key=lambda y: y.lower())
        positions = {}
        for mic_setup in self.mic_setups:
            positions[mic_setup] = sorted(list(set([s.split('w')[0] for s in self.irs[mic_setup]])), key=natsort_key)
        return positions
    
    @speaker_positions.setter
    def speaker_positions(self, value):
        """Prevents setting the speaker positions."""
        raise AttributeError('Cannot set speaker_positions.')  
    
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
        

    # class methods
    # @classmethod
    ## not working properly
    # def a_weighting_filter(cls, x):
    #     '''
    #     Apply A-weighting filter to the input signals.
    #     '''
    #     filter_coefficients = [
    #     {"b" : [0.96525096525, -1.34730163086, 0.38205066561], "a" : [1.0, -1.34730722798, 0.34905752979]},
    #     {"b" : [0.94696969696, -1.89393939393, 0.94696969696], "a" : [1.0, -1.89387049481, 0.89515976917]},
    #     {"b" : [0.64666542810, -0.38362237137, -0.26304305672], "a" : [1.0, -1.34730722798, 0.34905752979]},
    #     ]
    #     out = np.zeros_like(x)
    #     for i in range(x.shape[1]):
    #         out[:, i] = signal.lfilter(filter_coefficients[0]["b"], filter_coefficients[0]["a"], x[:, i])
    #         out[:, i] = signal.lfilter(filter_coefficients[1]["b"], filter_coefficients[1]["a"], out[:, i])
    #         out[:, i] = signal.lfilter(filter_coefficients[2]["b"], filter_coefficients[2]["a"], out[:, i])   
    #     return out
    

    @classmethod
    def calculate_rms_mean(cls, x):
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
        
        def create_sine_cosine_windows(duration):
            '''Create the first quarter of sine and cosine functions for crossfading. 
            Duration must be 4*crossfade_samples.
            '''
            t = np.arange(duration) / fs
            frequency = 1 / duration
            sine = np.sin(2 * np.pi * frequency * t)[:int(len(t)/4)]
            cos = np.cos(2 * np.pi * frequency * t)[:int(len(t)/4)]
            return sine, cos
        
        x = n.pop(0)
        for i, element in enumerate(n):
            if len(element) > len(x):
                n[i] = element[:len(x)]
            elif len(element) < len(x):
                crossfade_samples = int(fs) # Number of samples for 1 second crossfade
        
                # Create sine and cosine windows for crossfading. 
                # We want the first quarter of each function, 
                # so the length should be 4*crossfade_samples.
                sine, cos = create_sine_cosine_windows(4*crossfade_samples)

                start = element[0:crossfade_samples]
                middle = element[crossfade_samples:len(element)-crossfade_samples]
                end = element[len(element)-crossfade_samples:]
                cf = start * cos + end * sine

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
        

    # instance methods
    def load_noise(self, mic_setup: str, condition):
        """
        Loads the noise recording for a given microphone setup and noise condition.

        Args:
            mic_setup (str): The microphone setup to load the noise recording for.
            condition (str): The specific noise condition to load (speed condition + window condition).

        Returns:
            tuple: A tuple containing the noise data as a NumPy array and the sampling frequency of noise recording.

        Raises:
            ValueError: If the given noise condition is not available for the given microphone setup.
        """
        if condition not in self.noise_recordings[mic_setup]:
            raise ValueError(f"Noise condition {condition} is not available.")
        noise_path = os.path.join(self.__path, mic_setup, 'noise', condition + '.wav')
        # s, fs_noise = librosa.load(noise_path, sr=fs, mono=False)
        noise, fs_noise = sf.read(noise_path)
        noise = noise.T
        return noise, fs_noise
    
    
    def load_ir(self, mic_setup: str, condition):
        """
        Loads the impulse response (IR) for a given microphone setup and IR condition.
        
        Args:
            mic_setup (str): The microphone setup to load the IR for.
            condition (str): The specific IR condition to load (speaker position + window condition).
        
        Returns:
            tuple: A tuple containing the IR data as a NumPy array and the sampling frequency of IR.
        
        Raises:
            ValueError: If the given IR condition is not available for the given microphone setup.
        """
        if condition not in self.irs[mic_setup]:
            raise ValueError(f"IR condition {condition} is not in Car.irs[condition].")
        ir_path = os.path.join(self.__path, mic_setup, 'IRs', condition + '.wav')
        # ir, fs_ir = librosa.load(ir_path, sr=48000, mono=False)
        ir, fs_ir = sf.read(ir_path)
        ir = ir.T
        return ir, fs_ir
    
    def load_radio_ir(self, mic_setup: str, condition):
        """
        Loads the radio impulse response (IR) for a given microphone setup and radio condition.
        
        Args:
            mic_setup (str): The microphone setup to load the IR for.
            condition (str): The specific IR condition to load (window condition).
        
        Returns:
            tuple: A tuple containing the IR data as a NumPy array and the sampling frequency of radio IR.
        
        Raises:
            ValueError: If the given radio IR condition is not available for the given microphone setup.
        """
        if condition not in self.radio_irs[mic_setup]:
            raise ValueError(f"Radio IR condition {condition} is not in Car.radio_irs[condition].")
        ir_path = os.path.join(self.__path, mic_setup, 'radio_IRs', condition + '.wav')
        # ir, fs_ir = librosa.load(ir_path, sr=fs, mono=False)
        ir, fs_ir = sf.read(ir_path)    
        ir = ir.T
        return ir, fs_ir
    

    def load_ventilation(self, mic_setup: str, condition):
        """
        Loads the ventilation recording for a given microphone setup and condition.
        
        Args:
            mic_setup (str): The microphone setup to load the ventilation recording for.
            condition (str): The specific ventilation condition to load (ventilation level + window condition).
        
        Returns:
            tuple: A tuple containing the ventilation data as a NumPy array and the sampling frequency.
        
        Raises:
            ValueError: If the given ventilation condition is not available for the given microphone setup.
        """
        if condition not in self.ventilation_recordings[mic_setup]:
            raise ValueError(f"Ventilation condition {condition} is not in Car.ventilation_recordings[condition].")
        ventilation_path = os.path.join(self.__path, mic_setup, 'ventilation', condition + '.wav')
        # ventilation, fs_ventilation = librosa.load(ventilation_path, sr=fs, mono=False)
        ventilation, fs_ventilation = sf.read(ventilation_path)
        ventilation = ventilation.T
        return ventilation, fs_ventilation


    def get_speech(self, mic_setup: str, position: str, condition: str, l_s: float, x, x_fs, mic: int, fs=None):
        """
        Generates the convolved speech signal with the corresponding impulse response for a given microphone setup, position, and condition.
        
        Args:
            mic_setup (str): The microphone setup to use.
            position (str): The position of the speaker.
            condition (str): The condition of the recording (speaker position + window condition).
            l_s (float): The speech effort level.
            x (numpy.ndarray): The input speech signal.
            x_fs (int): The sampling frequency of the input speech signal.
            mic (int): The microphone index to use.
            fs (int, optional): The target sampling frequency for the output signal. Defaults to None.
        
        Returns:
            numpy.ndarray: The processed speech signal.
        
        Raises:
            ValueError: If the microphone setup, position, or window condition is not available, or if the speech effort is negative.
        """
        if mic_setup not in self.mic_setups:
            raise ValueError(f"Microphone setup {mic_setup} is not available.")
        if position not in self.speaker_positions[mic_setup]:
            raise ValueError(f"Position {position} is not available.")
        if l_s < 0:
            raise ValueError(f"Speech effort must be positive.")
        w_condition = int(condition.split('_')[0][-1])
        if w_condition not in [0, 1, 2, 3]:
            raise ValueError(f"Window condition must be 0, 1, 2 or 3.")
        if fs is not None and fs != x_fs:
            x = librosa.resample(x, orig_sr=x_fs, target_sr=fs)
        ir_condition = f'{position}w{w_condition}'
        ir, ir_fs = self.load_ir(mic_setup, ir_condition)
        ir_reference = ir[self.reference_mic[mic_setup], :]
        print('ir_reference_level : ', 20 * np.log10(Car.calculate_rms_mean(ir_reference)))
        print('x : ', 20 * np.log10(Car.calculate_rms_mean(x)))
        
        ir = ir[mic, :]
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
        # x_filtered_level = 20 * np.log10(Car.calculate_rms_mean(x_filtered))
        # ir_filtered = waveform_analysis.A_weight(ir, 48000)
        # ir_filtered_level = 20 * np.log10(Car.calculate_rms_mean(ir_filtered))
        ###########
        convolved_reference_ir = np.convolve(x, ir_reference, mode='full')
        print('convolved_reference_ir_level  : ', 20 * np.log10(Car.calculate_rms_mean(convolved_reference_ir)))

        # convolved_reference_ir = convolved_reference_ir
        # Apply A-weighting filter
        # convolved_reference_ir = Car.a_weighting_filter(convolved_reference_ir)
        convolved_reference_ir= waveform_analysis.A_weight(convolved_reference_ir, ir_fs)

        # TODO: Choose if vad is applied or optional
        #####################
        # NO VAD
        # Calculate RMS mean
        convolved_reference_ir_rms = Car.calculate_rms_mean(convolved_reference_ir)
        # to dB
        convolved_reference_ir_level = 20 * np.log10(convolved_reference_ir_rms)
        print('convolved_reference_ir_filtered_level  : ', convolved_reference_ir_level)
        
        # convolved_reference_ir_level = 10 * np.log10(convolved_reference_ir_rms)

        # print('no vad:', convolved_reference_ir_level)
        #####################
        # VAD
        # convolved_x_rms = vad_mean_rms(convolved_x_a_filtered[:, 0], fs=fs)
        # print('vad:', convolved_x_rms)
        #####################
        reference = self.references[mic_setup][ir_condition] + (l_s - 72.5)
        # Calculate correction factor
        correction_factor = reference - convolved_reference_ir_level
        gain = 10 ** (correction_factor / 20)
        print('Gain:', gain)
        # Apply correction factor to selected microphone
        convolved_x = np.convolve(x, ir, mode='full')
        print('Convolved x level :', 20 * np.log10(Car.calculate_rms_mean(convolved_x)))
        convolved_x *= gain
        ###############
        convolved_x_filtered = waveform_analysis.A_weight(convolved_x, ir_fs)
        ###############
        # resample to fs
        if fs is not None and fs != ir_fs:
            convolved_x = librosa.resample(convolved_x, orig_sr=ir_fs, target_sr=fs)
        ###############
        print('voice dB_fs_a:', 20 * np.log10(Car.calculate_rms_mean(convolved_x_filtered)))
        ###############
        return convolved_x
    

    def get_noise(self, mic_setup:str, condition:str, mic:int, fs=None):
        """
        Retrieves the noise recording for a given microphone setup, condition, and microphone index.
        
        Args:
            mic_setup (str): The microphone setup to use.
            condition (str): The specific noise condition to load (speed condition + window condition).
            mic (int): The index of the microphone to use.
            fs (int, optional): The target sampling frequency for the output signal. Defaults to None.
        
        Returns:
            numpy.ndarray: The processed noise signal.
        
        Raises:
            ValueError: If the specified microphone setup is not available.
        """
        if mic_setup not in self.mic_setups:
            raise ValueError(f"Microphone setup {mic_setup} is not available.")
        noise, fs_noise = self.load_noise(mic_setup, condition)
        noise = noise[mic, :] #, None] # ,None to keep the shape (n_samples, 1) instead of (n_samples,)
        ###############
        filtered_noise = waveform_analysis.A_weight(noise, fs_noise)
        ###############
        # resample to fs
        if fs is not None and fs != fs_noise:
            noise = librosa.resample(noise, orig_sr=fs_noise, target_sr=fs)
        ###############
        print('noise dB_fs_a:', 20 * np.log10(Car.calculate_rms_mean(filtered_noise)))
        ###############
        return noise
    

    def get_audio(self, mic_setup: str, condition: str, l_r: float, a, a_fs, mic: int, fs=None):
        """
        Generates the convolved audio signal with the corresponding radio impulse response for a given microphone setup, condition, and microphone index.
        
        Args:
            mic_setup (str): The microphone setup to use.
            condition (str): The specific condition to load (speed condition + window condition).
            l_r (float): The radio audio level.
            a (numpy.ndarray): The input audio signal.
            a_fs (int): The sampling frequency of the input audio signal.
            mic (int): The index of the microphone to use.
            fs (int, optional): The target sampling frequency for the output signal. Defaults to None.
        
        Returns:
            numpy.ndarray: The processed audio signal.
        
        Raises:
            ValueError: If the microphone setup is not available, the audio level is negative, or the window condition is invalid.
        """
        if mic_setup not in self.mic_setups:
            raise ValueError(f"Microphone setup {mic_setup} is not available.")
        if l_r < 0:
            raise ValueError(f"Audio level must be positive.")
        w_condition = int(condition.split('_')[0][-1])
        if w_condition not in [0, 1, 2, 3]:
            raise ValueError(f"Window condition must be 0, 1, 2 or 3.")
        # if a_fs != 48000:
        #     a = librosa.resample(a, orig_sr=a_fs, target_sr=48000)
        
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
        radio_ir_reference = radio_ir[self.reference_mic[mic_setup], :]
        radio_ir = radio_ir[mic, :]#, None] # ,None to keep the shape (n_samples, 1) instead of (n_samples,)
        # plt.plot(radio_ir)
        # plt.title('Radio IR')
        # plt.show()
        # convolved_radio_ir = []
        # for i in range(radio_ir.shape[1]):
        #     convolved_radio_ir.append(np.convolve(a, radio_ir[:, i], mode='same'))
        # convolved_radio_ir = np.array(convolved_radio_ir).T
        convolved_radio_reference_ir = np.convolve(a, radio_ir_reference, mode='full')
        # Apply A-weighting filter
        # convolved_radio_reference_ir = Car.a_weighting_filter(convolved_radio_reference_ir)
        convolved_radio_reference_ir= waveform_analysis.A_weight(convolved_radio_reference_ir, radio_ir_fs)
        # Calculate RMS mean
        convolved_radio_ir_rms = Car.calculate_rms_mean(convolved_radio_reference_ir)
        # to dB
        convolved_radio_ir_level = 20 * np.log10(convolved_radio_ir_rms)
        level = convolved_radio_ir_level + db_fsa_to_db_a[self.reference_mic[mic_setup]] 
        # Calculate correction factor
        correction_factor = l_r - level
        gain = 10 ** (correction_factor / 20)

        convolved_radio_ir = np.convolve(a, radio_ir, mode='full')
        convolved_radio_ir *= gain
        # resample to fs
        ###############
        convolved_x_filtered = waveform_analysis.A_weight(convolved_radio_ir, radio_ir_fs)
        ###############
        if fs is not None and fs != radio_ir_fs:
            convolved_radio_ir = librosa.resample(convolved_radio_ir, orig_sr=radio_ir_fs, target_sr=fs)
        ###############
        print('radio dB_fs_a:', 20 * np.log10(Car.calculate_rms_mean(convolved_x_filtered)))
        ###############
        return convolved_radio_ir


    def get_ventilation(self, mic_setup: str, condition: str, level: int, mic: int, fs=None):
        # TODO: check if it works ok
        if mic_setup not in self.mic_setups:
            raise ValueError(f"Microphone setup {mic_setup} is not available.")
        if level not in [1, 2, 3]:
            raise ValueError(f"Ventilation level must be 1, 2 or 3.")
        w_condition = int(condition.split('_')[0][-1])
        if w_condition not in [0, 1, 2, 3]:
            raise ValueError(f"Window condition must be 0, 1, 2 or 3.")
        ventilation_condition = f'v{level}w{w_condition}'
        ventilation, ventilation_fs = self.load_ventilation(mic_setup, ventilation_condition)
        ventilation = ventilation[mic, :]
        ###############
        filtered_ventilation = waveform_analysis.A_weight(ventilation, ventilation_fs)
        ###############
        # resample to fs
        if fs is not None and fs != ventilation_fs:
            ventilation = librosa.resample(ventilation, orig_sr=ventilation_fs, target_sr=fs)
        ###############
        print('ventilation dB_fs_a:', 20 * np.log10(Car.calculate_rms_mean(filtered_ventilation)))
        ###############
        return ventilation  
    

    def get_mixture_components(self, mic_setup, position, condition, mic, fs, voice_path=None, l_s=None, radio_path=None, l_r=None, vent_level=None):
        """
        Returns a list of components of the mixture in the following order: speech, radio, ventilation, noise.
        Speech, radio, and ventilation are optional.
        
        Args:
            mic_setup (str): The microphone setup to use.
            position (str): The position of the speaker.
            condition (str): The condition of the recording (speed condition + window condition).
            mic (int): The microphone index to use.
            fs (int): The target sampling frequency for the output signal.
            voice_path (str, optional): The file path to the voice recording. Defaults to None.
            l_s (float, optional): The speech effort level. Defaults to None.
            radio_path (str, optional): The file path to the radio recording. Defaults to None.
            l_r (float, optional): The reference audio level. Defaults to None.
            vent_level (float, optional): The ventilation level. Defaults to None.
        
        Returns:
            list: A list of NumPy arrays representing the components of the mixture.
        
        Raises:
            ValueError: If the microphone setup, position, or condition is not available, or if the speech effort or audio level is negative.
        """
        l = []
        if l_s:
            voice, fs_voice = sf.read(voice_path)
            # make mono
            if np.dim(voice)>1:
                voice = np.mean(voice,axis=1)
            s = self.get_speech(mic_setup=mic_setup, position=position, condition=condition, l_s=l_s, x=voice, x_fs=fs_voice, mic=mic, fs=fs)
            l.append(s)
        if l_r:
            radio_audio, fs_radio = sf.read(radio_path)
            # make mono
            if np.dim(radio_audio)>1:
                radio_audio = np.mean(radio_audio,axis=1)
            a = self.get_audio(mic_setup=mic_setup, condition=condition, l_r=l_r, a=radio_audio, a_fs=fs_radio, mic=mic, fs=fs)
            l.append(a)
        if vent_level:
            v = self.get_ventilation(mic_setup=mic_setup, condition=condition, level=vent_level, mic=mic, fs=fs)
            l.append(v)
        n = self.get_noise(mic_setup=mic_setup, condition=condition, mic=mic, fs=fs)
        l.append(n)
        
        out = Car.match_duration(l, fs)
        # s, a, v, n
        return out

