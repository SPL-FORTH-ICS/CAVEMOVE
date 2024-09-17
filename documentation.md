# Car module

## *class* Car.Car(path, txt_info, info_dict=None)

Bases: `object`

A class to represent a car and the recordings associated with it.\
The class provides methods to load and process the recordings.

**Args:**\
*path (str):* The path to the car recordings.\
*json_info (bool):* A boolean indicating whether the car information is stored in a json file inside path. Defaults to True.\
*info_dict (dict):* A dictionary containing the car information. Defaults to None. Is *json_info* is True, *info_dict* is ignored.

## Properties

### make
Returns a string containing the make of the car.

### model
Returns a string containing  the model of the car.

### version
Returns a string containing the model’s version of the car.

### year
Returns an integer with the year of the car.


### mic_setups
Returns a list of available microphone configurations.

### irs
Returns a dictionary of available IR conditions per microphone configuration.


### noise_recordings

Returns a dictionary of available noise condition recordings per microphone configuration.

### radio_irs

Returns a dictionary of available radio IR conditions per microphone configuration.

### references

Returns a dictionary of available reference levels for every speaker condition per microphone configuration.

### reference_mic

Returns a dictionary of the reference microphone per microphone configuration.

### ventilation_recordings

Returns a dictionary of available ventilation conditions recordings per microphone configuration.

### speaker_positions

Returns a dictionary of available speaker positions per microphone configuration.



## Methods

### load_noise(mic_setup, condition)

Loads the noise recording channels for a given microphone setup and noise condition.

**Args:**\
 *mic_setup (str):* The microphone setup to load the noise recording for.\
  *condition (str):* The specific noise condition to load (speed condition + window condition).

**Returns:**
*tuple:* A tuple containing the noise data as a NumPy array (N_samples x M_channels) and the sampling frequency of noise recording.

**Raises:**
*ValueError:* If the given noise condition is not available for the given microphone setup.

### load_ir(mic_setup, condition)

Loads the impulse response (IR) channels for a given microphone setup and IR condition.

**Args:**\
 *mic_setup (str):* The microphone setup to load the IR for.\
  *condition (str):* The specific IR condition to load (speaker position + window condition).

**Returns:**
 *tuple:* A tuple containing the IR data as a NumPy array (N_samples x M_channels) and the sampling frequency of IR.

**Raises:**
*ValueError:* If the given IR condition is not available for the given microphone setup.

### load_radio_ir(mic_setup, condition)

Loads the radio impulse response (IR) channels for a given microphone setup and radio condition.

**Args:**\
*mic_setup (str):* The microphone setup to load the IR for.\
*condition (str):* The specific IR condition to load (window condition).

**Returns:**
*tuple:* A tuple containing the IR data as a NumPy array (N_samples x M_channels) and the sampling frequency of radio IR.

**Raises:**\
*ValueError:* If radio IRs are not available.\
*ValueError:* If the given radio IR condition is not available for the given microphone configuration.

### load_ventilation(mic_setup, condition)

Loads the ventilation recording for a given microphone setup and condition.

**Args:**\
*mic_setup (str):* The microphone setup to load the ventilation recording for.\
*condition (str):* The specific ventilation condition to load (ventilation level + window condition).

**Returns:**
*tuple* A tuple containing the ventilation data as a NumPy array (N_samples x M_channels) and the sampling frequency.

**Raises:**
*ValueError:* If the given ventilation condition is not available for the given microphone setup.

### get_speech(mic_setup, position, condition, l_s, dry_speech, dry_speech_fs, mics, fs=None)

Generates the convolved speech signal with the corresponding impulse response for a given microphone setup, position, and condition.

**Args:**\
*mic_setup (str):* The microphone setup to use.\
*position (str):* The position of the speaker.\
*condition (str):* The condition of the recording (speaker position + window condition).\
*l_s (float):* The speech effort level.\
*dry_speech (numpy.ndarray):* The input speech signal.\
*dry_speech_fs (int):* The sampling frequency of the input speech signal.\
*mics (int or list of int, optional):* The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.\
*fs (int, optional):* The target sampling frequency for the output signal. Defaults to None.

**Returns:**
*numpy.ndarray:* The processed speech signal for the specified microphones.

**Raises:**\
*ValueError:* If the microphone setup is not available.\
*ValueError:* If the position is not available.\
*ValueError:* If the speech effort is negative.\
*ValueError:* If the window condition is invalid.\
*ValueError:* If the microphone index is not an integer or a list of integers.
        

### get_noise(mic_setup, condition, mics, fs=None)

Retrieves the noise recording for a given microphone setup, condition, and microphone index.

**Args:**\
*mic_setup (str):* The microphone setup to use.\
  *condition (str):* The specific noise condition to load (speed condition + window condition).\
  *mics (int or list of int, optional):* The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.\
  *fs (int, optional):* The target sampling frequency for the output signal. Defaults to None.

**Returns:**
*numpy.ndarray:* The processed noise signal.

**Raises:**\
*ValueError:* If the specified microphone setup is not available.\
*ValueError:* If the microphone index is not an integer or a list of integers.

### get_radio(mic_setup, condition, l_a, radio_audio, radio_audio_fs, mics=None, fs=None)

Generates the convolved audio signal with the corresponding radio impulse response for a given microphone setup, condition, and microphone index.

**Args:**\
*mic_setup (str):* The microphone setup to use.\
  *condition (str):* The specific condition to load (speed condition + window condition).\
  *l_a (float):* The radio audio level.\
  *radio_audio (numpy.ndarray):* The input audio signal vector.\
  *radio_audio_fs (int):* The sampling frequency of the input audio signal.\
  *mics (int or list of int, optional):* The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.\
  *fs (int, optional):* The target sampling frequency for the output signal. Defaults to None.

**Returns:**
*numpy.ndarray:* The processed audio signal for the specified microphones.

**Raises:**
*ValueError:* If the microphone setup is not available.\
*ValueError:* If the audio level is negative.\
*ValueError:* If the window condition is invalid.\
*ValueError:* If the microphone index is not an integer or a list of integers.


### get_ventilation(mic_setup, condition, level, mics, fs=None)

Retrieves and processes the ventilation recording for a given microphone setup, condition, and ventilation level.
        
**Args:**\
*mic_setup (str):* The microphone setup to use.\
  *condition (str):* The specific condition to load (speed condition + window condition).\
  *level (int):* The ventilation level (must be 1, 2, or 3).\
  *mics (int or list of int, optional):* The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used.\
  *fs (int, optional):* The target sampling frequency for the output signal. Defaults to None.

**Returns:**
*numpy.ndarray:* The processed ventilation signal for the specified microphones.


**Raises:**\
*ValueError:* If the microphone setup is not available.\
*ValueError:* If the ventilation level is not 1, 2, or 3.\
*ValueError:* If the window condition is invalid.\
*ValueError:* If the microphone index is not an integer or a list of integers.


### get_mixture_components(mic_setup, position, condition, mics, fs, voice_path=None, l_s=None, dry_speech=None, dry_speech_fs=None, l_a=None,  radio_audio=None, radio_audio_fs=None, vent_level=None)

A wrapper function of the get_noise, get_speech, get_radio, and get_ventilation methods.
Returns a list of components of the mixture in the following order: noise, speech, radio, ventilation.
Speech, radio, and ventilation are optional.

**Args:**\
*mic_setup (str):* The microphone setup to use.\
*position (str):* The position of the speaker.\
*condition (str):* The condition of the recording (speed condition + window condition).\
*mics (int):* The microphone index to use.\
*fs (int):* The target sampling frequency for the output signal.\
*l_s (float, optional):* The speech effort level. Defaults to None.\
*dry_speech (numpy.ndarray, optional):* The input speech signal vector.\
*dry_speech_fs (int, optional):* The sampling frequency of the input speech signal.\
*l_a (float, optional):* The reference audio level. Defaults to None.\
*radio_audio (numpy.ndarray, optional):* The input audio signal vector.\
*radio_audio_fs (int, optional):* The sampling frequency of the input audio signal.\
*vent_level (float, optional):* The ventilation level. Defaults to None.

**Returns:**
*list:* A list of NumPy arrays representing the components of the mixture. Order: noise, speech (optional), radio(optional), ventilation(optional).
        
**Raises:**\
*ValueError:* If the microphone setup, position, or condition is not available.\
*ValueError:* If the speech effort or audio level is negative.\
*ValueError:* If dry speech  or dry speech sampling frequency is not provided when speech effort level is specified.\
*ValueError:* If radio audio or radio audio sampling frequency is not provided when reference audio level is specified.


### steering_vectors(freq, theta):
Calculates the steering vectors for a given frequency and angle for a microphone array configuration.
        
**Args:**\
*freq (float):* The frequency in Hz at which to calculate the steering vectors.\
*theta (float):* The angle in degrees at which to calculate the steering vectors.
        
**Returns:**
*numpy.ndarray:* An array of complex steering vectors for each microphone in the array.


## Class methods

<!-- ### calculate_rms_mean(x)

Calculates the root mean square (RMS) mean of the given array.

This method computes the RMS mean of the input array x. The RMS mean is 
calculated as the square root of the mean of the squares of the elements 
in x.

**Args:**\
*x (numpy.ndarray):* A numpy array for which the RMS mean is to be calculated.

**Returns:**
*float:* The RMS mean of the input array. -->

### match_duration(n, fs)

Matches the duration of elements in the list n to the duration of the first element.

This method adjusts the duration of each element in the list n to match the duration 
of the first element in the list. If an element is longer than the first element, it is 
truncated. If an element is shorter, it is looped using crossfading to match the duration.

**Args:**\
 *n* (list): A list of numpy arrays where each array represents a signal.\
  *fs* (int): The sampling frequency of the signals.

**Returns:**
 *list:* A list of numpy arrays with matched durations.

Notes:
 - If the list n contains only one element, it is returned as is.
  - The crossfade duration is set to 1 second.
  - The crossfade is achieved using the first quarter of sine and cosine functions.

Example:
```python
  signals = [np.array([1, 2, 3, 4, 5]), np.array([1, 2, 3])]
  fs = 44100
  matched_signals = Car.match_duration(signals, fs)
  ```


