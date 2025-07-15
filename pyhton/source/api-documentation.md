<!-- markdownlint-disable -->

<a href="../Car.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `Car.py`






---

## <kbd>class</kbd> `Car`
A class to represent a car and the recordings associated with it.    The class provides methods to load and process the recordings. 



**Args:**
- <b>`path`</b> (str):  The path to the folder with the recordings for the particular car.
- <b>`fs`</b> (int):  The sampling frequency of the recordings. Default is 16000 Hz.
- <b>`json_info`</b> (bool):   A boolean indicating whether the car information is stored in a json file inside path. Defaults to True.
- <b>`info_dict`</b> (dict):  A dictionary containing the car information. Defaults to None. Is *json_info* is True, *info_dict* is ignored.

<a href="../Car.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `__init__`

```python
__init__(path, fs=16000, json_info=True, info_dict=None)
```






---

#### <kbd>property</kbd> correction_gains

Returns a dictionary with the correction gains of all microphones. 

---

#### <kbd>property</kbd> fs

Returns the sampling frequency. 

---

#### <kbd>property</kbd> irs

Returns a dictionary of available IR conditions per microphone configuration. 

---

#### <kbd>property</kbd> make

Returns a string containing the make of the car. 

---

#### <kbd>property</kbd> mic_setups

Returns a list of available microphone configurations. 

---

#### <kbd>property</kbd> model

Returns a string containing  the model of the car. 

---

#### <kbd>property</kbd> noise_recordings

Returns a dictionary of available noise condition recordings per microphone configuration. 

---

#### <kbd>property</kbd> radio_irs

Returns a dictionary of available car audio IR conditions per microphone configuration. 

---

#### <kbd>property</kbd> speaker_locations

Returns a dictionary of available speaker locations per microphone configuration. 

---

#### <kbd>property</kbd> ventilation_recordings

Returns a dictionary of available ventilation conditions recordings per microphone configuration. 

---

#### <kbd>property</kbd> version

Returns a string containing the model's version of the car. 

---

#### <kbd>property</kbd> year

Returns an integer with the year of the car. 



---

<a href="../Car.py#L834"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `construct_steering_vector`

```python
construct_steering_vector(freq, theta)
```

Calculates the steering vectors for a given frequency and angle for a microphone array configuration. The acoustic center is defined as the center of the microphone array. 0 degrees point towards the rear middle passenger, so that the driver is positioned at a negative angle and the front passenger at a positive angle. 



**Args:**
 
 - <b>`freq`</b> (float):  The frequency in Hz at which to calculate the steering vectors. 
 - <b>`theta`</b> (float):  The angle in degrees at which to calculate the steering vectors. 



**Returns:**
 
 - <b>`numpy.ndarray`</b>:  An array of complex steering vectors for each microphone in the array. 

---

<a href="../Car.py#L780"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_components`

```python
get_components(
    mic_setup,
    location,
    speed: int,
    window: int,
    version: str = None,
    mics=None,
    ls=None,
    dry_speech=None,
    la=None,
    radio_audio=None,
    vent_level=None,
    use_correction_gains=True
)
```

A wrapper function of the get_noise, get_speech, get_radio, and get_ventilation methods. Returns a list of components of the mixture in the following order: noise, speech, radio, ventilation. Speech, radio, and ventilation are optional. 



**Args:**
 
 - <b>`mic_setup`</b> (str):  The microphone setup to use. 
 - <b>`location`</b> (str):  The location of the speaker. 
 - <b>`speed`</b> (int):  The speed condition. 
 - <b>`window`</b> (int):  The window condition. 
 - <b>`version`</b> (str, optional):  The version of the noise recording in case there are multiple versions. Defaults to None. Must be "ver1", "ver2", etc or "coarse".  
 - <b>`mics`</b> (int or list of int, optional):  The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used. 
 - <b>`ls`</b> (float, optional):  The speech effort level. Defaults to None. 
 - <b>`dry_speech`</b> (numpy.ndarray, optional):  The input speech signal vector. 
 - <b>`la`</b> (float, optional):  The reference audio level. Defaults to None. 
 - <b>`radio_audio`</b> (numpy.ndarray, optional):  The input audio signal vector. 
 - <b>`vent_level`</b> (float, optional):  The ventilation level. Defaults to None. 
 - <b>`use_correction_gains`</b> (bool, optional):  A boolean indicating whether to use the correction gains. Defaults to True. 



**Returns:**
 
 - <b>`list`</b>:  A list of NumPy arrays representing the components of the mixture. Order: noise, speech (optional), radio(optional), ventilation(optional). 



**Raises:**
 
 - <b>`ValueError`</b>:  If the microphone setup, location, or condition is not available. 
 - <b>`ValueError`</b>:  If the speech effort or audio level is negative. 
 - <b>`ValueError`</b>:  If dry speech  or dry speech sampling frequency is not provided when speech effort level is specified. 
 - <b>`ValueError`</b>:  If radio audio or radio audio sampling frequency is not provided when reference audio level is specified. 

---


<a href="../Car.py#L619"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_noise`

```python
get_noise(
    mic_setup: str,
    speed: int,
    window: int,
    version: str = None,
    mics=None,
    use_correction_gains=True
)
```

Retrieves the in-motion noise recording for a given microphone setup, condition, and microphone index. 



**Args:**
 
 - <b>`mic_setup`</b> (str):  The microphone setup to use. 
 - <b>`speed`</b> (int):  The speed condition. 
 - <b>`window`</b> (int):  The window condition. 
 - <b>`version`</b> (str, optional):  The version of the noise recording in case there are multiple versions. Defaults to None. Must be "ver1", "ver2", etc or "coarse".  
 - <b>`mics`</b> (int or list of int, optional):  The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used. 
 - <b>`use_correction_gains`</b> (bool, optional):  A boolean indicating whether to use the correction gains. Defaults to True. 



**Returns:**
 
 - <b>`numpy.ndarray`</b>:  The processed noise signal. 



**Raises:**
 
 - <b>`ValueError`</b>:  If the specified microphone setup is not available. 
 - <b>`ValueError`</b>:  If the microphone index is not an integer or a list of integers. 

---

<a href="../Car.py#L662"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_radio`

```python
get_radio(
    mic_setup: str,
    window: int,
    la: float,
    radio_audio,
    mics=None,
    use_correction_gains=True
)
```

Generates the radio (car-audio) signal by exploiting the measured  impulse response for a given microphone setup, condition, and microphone index. 



**Args:**
 
 - <b>`mic_setup`</b> (str):  The microphone setup to use. 
 - <b>`window`</b> (int):  The window condition. 
 - <b>`la`</b> (float):  The radio audio level. 
 - <b>`radio_audio`</b> (numpy.ndarray):  The input audio signal, provided by the user. 
 - <b>`mics`</b> (int or list of int, optional):  The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used. 
 - <b>`use_correction_gains`</b> (bool, optional):  A boolean indicating whether to use the correction gains. Defaults to True. 



**Returns:**
 
 - <b>`numpy.ndarray`</b>:  The processed audio signal for the specified microphones. 



**Raises:**
 
 - <b>`ValueError`</b>:  If the microphone setup is not available. 
 - <b>`ValueError`</b>:  If the audio level is negative. 
 - <b>`ValueError`</b>:  If the window condition is invalid. 
 - <b>`ValueError`</b>:  If the microphone index is not an integer or a list of integers. 

---

<a href="../Car.py#L549"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_speech`

```python
get_speech(
    mic_setup: str,
    location: str,
    window: int,
    ls: float,
    dry_speech,
    mics=None,
    use_correction_gains=True
)
```

Generates the convolved speech signal with the corresponding impulse response for a given microphone setup, location, and condition. 



**Args:**
 
 - <b>`mic_setup`</b> (str):  The microphone setup to use. 
 - <b>`location`</b> (str):  The location of the speaker. 
 - <b>`window`</b> (int):  The window condition. 
 - <b>`ls`</b> (float):  The speech effort level. 
 - <b>`dry_speech`</b> (numpy.ndarray):  The input speech signal vector. 
 - <b>`mics`</b> (int or list of int, optional):  The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used. 
 - <b>`use_correction_gains`</b> (bool, optional):  A boolean indicating whether to use the correction gains. Defaults to True. 



**Returns:**
 
 - <b>`numpy.ndarray`</b>:  The processed speech signal for the specified microphones. 



**Raises:**
 
 - <b>`ValueError`</b>:  If the microphone setup is not available. 
 - <b>`ValueError`</b>:  If the location is not available. 
 - <b>`ValueError`</b>:  If the speech effort is negative. 
 - <b>`ValueError`</b>:  If the window condition is invalid. 
 - <b>`ValueError`</b>:  If mics is not an integer or a list of integers. 

---

<a href="../Car.py#L737"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `get_ventilation`

```python
get_ventilation(
    mic_setup: str,
    level: int,
    window: int,
    version:str=None
    mics=None,
    use_correction_gains=True
)
```

Retrieves and processes the ventilation recording for a given microphone setup, condition, and ventilation level. 



**Args:**
 
 - <b>`mic_setup`</b> (str):  The microphone setup to use. 
 - <b>`level`</b> (int):  The ventilation level (must be 1, 2, or 3). 
 - <b>`window`</b> (int):  The window condition. 
 - <b>`version` </b> (str, optional): The version of the ventilation recording in case there are multiple versions. Defaults to None. Must be "ver1", "ver2". 
 - <b>`mics`</b> (int or list of int, optional):  The microphone index or a list of microphone indices to use. Defaults to None. If mics is None, all microphones are used. 
 - <b>`use_correction_gains`</b> (bool, optional):  A boolean indicating whether to use the correction gains. Defaults to True. 



**Returns:**
 numpy.ndarray: The processed ventilation signal for the specified microphones. 



**Raises:**
 
 - <b>`ValueError`</b>:  If the microphone setup is not available. 
 - <b>`ValueError`</b>:  If the ventilation level is not 1, 2, or 3. 
 - <b>`ValueError`</b>:  If the window condition is invalid. 
 - <b>`ValueError`</b>:  If the microphone index is not an integer or a list of integers. 

---


<a href="../Car.py#L472"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `load_ir`

```python
load_ir(mic_setup: str, condition)
```

Loads the impulse response (IR) channels for a given microphone setup and IR condition. 



**Args:**
 
 - <b>`mic_setup`</b> (str):  The microphone setup to load the IR for. 
 - <b>`condition`</b> (str):  The specific IR condition to load ("'speaker location'_w'window condition'"). 



**Returns:**
 
 - <b>`tuple`</b>:  A tuple containing the IR data as a NumPy array (N_samples x M_channels) and the sampling frequency of IR. 



**Raises:**
 
 - <b>`ValueError`</b>:  If the given IR condition is not available for the given microphone setup. 

---

<a href="../Car.py#L445"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `load_noise`

```python
load_noise(mic_setup: str, condition)
```

Loads the noise recording channels for a given microphone setup and noise condition. 



**Args:**
 
 - <b>`mic_setup`</b> (str):  The microphone setup to load the noise recording for. 
 - <b>`condition`</b> (str):  The specific noise condition to load ("s'speed condition'_w'window condition'"). 



**Returns:**
 
 - <b>`tuple`</b>:  A tuple containing the noise data as a NumPy array (N_samples x M_channels) and the sampling frequency of noise recording. 



**Raises:**
 
 - <b>`ValueError`</b>:  If the given noise condition is not available for the given microphone setup. 

---

<a href="../Car.py#L496"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `load_radio_ir`

```python
load_radio_ir(mic_setup: str, condition)
```

Loads the radio impulse response (IR) channels for a given microphone setup and radio condition. 



**Args:**
 
 - <b>`mic_setup`</b> (str):  The microphone setup to load the IR for. 
 - <b>`condition`</b> (str):  The specific IR condition to load ("window condition"). 



**Returns:**
 
 - <b>`tuple`</b>:  A tuple containing the IR data as a NumPy array (N_samples x M_channels) and the sampling frequency of radio IR. 



**Raises:**
 
 - <b>`ValueError`</b>:  If radio IRs are not available. 
 - <b>`ValueError`</b>:  If the given radio IR condition is not available for the given microphone configuration. 

---

<a href="../Car.py#L524"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `load_ventilation`

```python
load_ventilation(mic_setup: str, condition)
```

Loads the ventilation recording for a given microphone setup and condition. 



**Args:**
 
 - <b>`mic_setup`</b> (str):  The microphone setup to load the ventilation recording for. 
 - <b>`condition`</b> (str):  The specific ventilation condition to load ("v'ventilation level'_w'window condition'"). 



**Returns:**
 
 - <b>`tuple`</b>:  A tuple containing the ventilation data as a NumPy array (N_samples x M_channels) and the sampling frequency. 



**Raises:**
 
 - <b>`ValueError`</b>:  If the given ventilation condition is not available for the given microphone setup. 

---

<a href="../Car.py#L295"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `match_duration`

```python
match_duration(n: list, fs)
```

Matches the duration of elements in the list `n` to the duration of the first element. 

This method adjusts the duration of each element in the list `n` to match the duration  of the first element in the list. If an element is longer than the first element, it is  truncated. If an element is shorter, it is looped using crossfading to match the duration. 



**Args:**
 
 - <b>`n`</b> (list):  A list of numpy arrays where each array represents a signal. 
 - <b>`fs`</b> (int):  The sampling frequency of the signals. 



**Returns:**
 
 - <b>`list`</b>:  A list of numpy arrays with matched durations. 



**Notes:**

> - If the list `n` contains only one element, it is returned as is.
> - Crossfading is used to loop shorter elements. The crossfade duration is set to 1 second.
> - The crossfade is achieved using the first quarter of sine and cosine functions. 

**Example:**
``` 
signals = [np.array([1, 2, 3, 4, 5]), np.array([1, 2, 3])]
fs = 16000
matched_signals = Car.match_duration(signals, fs)
```


---

<a href="../Car.py#L407"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>function</kbd> `speaker_locations_angles`

```python
speaker_locations_angles(mic_setup)
```

Returns the speaker locations and their corresponding angles with respect to the center of the microphone array. 



**Args:**
 
 - <b>`mic_setup`</b> (str):  The microphone setup to use. 



**Returns:**
 
 - <b>`dict or None`</b>:  A dictionary with speaker locations as keys and their corresponding angles as values.  Returns None if the microphone setup is 'distributed'. 



**Raises:**
 
 - <b>`ValueError`</b>:  If the make and model combination is not recognized. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
