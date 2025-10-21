dataset_path = 'D:\16kHz';
car_names = ["Volkswagen_Golf", "AlfaRomeo_146", "Smart_forfour"];
car_path = ([dataset_path '\' car_names{1} '\']);
radio_path = 'Music_mono_16KHz.wav';
voice_path = 'Speech_mono_16KHz.wav';

sampling_rate = 16000;  % open access data is provided at 16kHz sampling rate
my_mic_setup = 'array';
my_location = 'd50';
my_speed = 50;
my_window = 1;
my_Ls = 70;
my_La = 60;
my_mics = [1, 2, 3, 4, 5, 6, 7, 8];
my_vent_level = 1;
my_car = car("path", car_path, "fs", sampling_rate);

%% Get noise component
n = my_car.get_noise("mic_setup", my_mic_setup, "speed", my_speed, "window", my_window, "mics", my_mics);

%% Get speech component
[dry_voice, fs_dry_voice] = audioread(voice_path);
s = my_car.get_speech("mic_setup", my_mic_setup, "location", my_location, ...
                      "window", my_window, "ls", my_Ls, "dry_speech", dry_voice, "mics", my_mics);
%% Get radio component
[radio_tune, fs_radio] = audioread(radio_path);
a = my_car.get_radio("mic_setup",my_mic_setup, "window", my_window, ...
                     "la", my_La, "radio_audio" ,radio_tune, "mics", my_mics);

%% Get ventilation noise component
v = my_car.get_ventilation("mic_setup", my_mic_setup, "window", my_window, "level" ,my_vent_level, "mics", my_mics);

%% Match duration of components to speech duration
[s_new, a_new, v_new, n_new] = my_car.match_duration(s, a, v, n);

%%  add components to produce a mix
mix = s_new + a_new + v_new + n_new;


%% Finally, get_components can return all the above components or cominations of those, in matched duration.by providing te correspodins arguments. See Documentation for more info
components = my_car.get_components("mic_setup", my_mic_setup, "location", my_location, "speed", my_speed, ...
                                   "window", my_window, "mics", my_mics, "ls", my_Ls, "dry_speech", dry_voice, ...
                                   "la", my_La, "radio_audio", radio_tune, "vent_level", 1);

%% export selected microphone channel as a wav file
audiowrite('mix.wav', mix(:,1), my_car.fs)