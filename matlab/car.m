classdef car % full version 16kHz
    properties(Access = private)
        setup_check % this variable is an auxiliary variable
        window_check % this variable is an auxiliary variable
        dBFS_A % this is related to the calibration
        dBA % this is related to the calibration
        dBFS_A_to_dBA
        mic_reference_list % mic reference
        current_car % current_car
        path % cavemove path
        speech_calibration % 70 dBA pink noise (talkbox) High Speech Effort
    end
    properties
        correction_lin % Returns a table (1x8) with the correction gains of all microphones. (linear gains).
        fs % Returns the sampling frequency.
        irs % Returns a struck with all the available IRs per microphone configuration.
        radio_irs % Returns a struck with all the available radio IRs per microphone configuration.
        noise_recordings % Returns a struck with all the available noise recordings per microphone configuration.
        ventilation_recordings % Returns a struck with all the available ventilation conditions recordings per microphone configuration.
        mic_setups % Returns all the available microphones configurations.
        speaker_locations % Returns a struck with all the available speaker locations per microphone configuration.
        make % Returns the make of the car.
        model % Returns the model of the car.
        year % Returns the year of construction of the car.
    end
    methods
        function obj = car(varargin)

            %
            %car
            %
            %   A class to represent a car and the recordings associated with it.
            %   The class provides methods to load and process the recordings.
            %
            %   Input:
            %       path (char)   - The path to the folder with the recordings for the particular car.
            %       fs (char)     - The sampling frequency of the recordings. Default is 16000 Hz.
            %
            %   Example:
            %       my_car = car(path=car_path, fs=sampling_rate);

            p = inputParser;


            addParameter(p,'path','null')
            addParameter(p,'fs',16000)

            parse(p,varargin{:})

            obj.path = p.Results.path;
            obj.fs = p.Results.fs;


            % - - - - %
            load(['.' filesep 'source' filesep 'info_cavemove.mat']); % load cavemove info
            % - - - - %

            obj.speech_calibration = 70; % 70 dBA High Speech Effort

            obj.setup_check = infofull.setups;
            obj.window_check = infofull.windows;
            obj.mic_reference_list = infofull.mic_reference;

            % load correction gains

            obj.correction_lin = infofull.correction_lin; % load correction gains
            obj.correction_lin = obj.correction_lin(1:8,1); % load correction gains

            % calibration
            obj.dBFS_A = infofull.dBFS_A;
            obj.dBA = infofull.dBA;
            obj.dBFS_A_to_dBA = infofull.dBFS_A_to_dBA;

            % check path

            check_path = exist([obj.path],'dir');
            if check_path == 7
            else
                ME = MException('myComponent:inputError','This path "%s" is incorrect.',obj.path);
                throw(ME)
            end

            % creating name of current_car

            load([ obj.path 'info.mat']);
            current_car = info_car(2);
            current_car = cellstr(current_car);
            current_car = current_car{1,1};
            current_car = current_car(14:length(current_car)-2);

            model = info_car(3);
            model = cellstr(model);
            model = model{1,1};
            model = model(15:length(model)-2);

            obj.current_car = ([current_car '_' model]);
            obj.make = current_car;
            obj.model = model;

            year = info_car(5);
            year = cellstr(year);
            year = year{1,1};
            obj.year = year(13:length(year)-1);

            %% mic setups

            mic_setups_scan = dir([obj.path '*']); % in search of mic setups
            for z=1:length(mic_setups_scan)
                mic_setups_scan_aux = mic_setups_scan(z).name;
                if mic_setups_scan_aux == "array"
                    mic_setups_scan_results(:,z) = 1;
                elseif mic_setups_scan_aux == "distributed"
                    mic_setups_scan_results(:,z) = 2;
                else
                    mic_setups_scan_results(:,z) = 0;
                end
            end

            if sum(mic_setups_scan_results)==1
                mic_setups_scan_results_list = ["array"];
            elseif sum(mic_setups_scan_results)==2
                mic_setups_scan_results_list = ["distributed"];
            elseif sum(mic_setups_scan_results)==3
                mic_setups_scan_results_list = ["array","distributed"];
            end

            if obj.current_car == "Hyundai_i30"
                mic_setups_scan_results_list = ["hybrid","array","distributed"];
            end

            obj.mic_setups = mic_setups_scan_results_list;

            %% irs

            irs_distributed = dir([obj.path 'distributed' filesep 'IRs' filesep '*.wav']);
            for z=1:length(irs_distributed)
                irs_distributed_aux02 = irs_distributed(z).name;
                irs_distributed_aux02 = irs_distributed_aux02(1:end-4);
                irs_distributed_aux{z} = irs_distributed_aux02;
            end


            try
                irs.distributed = irs_distributed_aux';
                obj.irs = irs;
            catch
            end


            irs_array = dir([obj.path 'array' filesep 'IRs' filesep '*.wav']);
            for z=1:length(irs_array)
                irs_array_aux02 = irs_array(z).name;
                irs_array_aux02 = irs_array_aux02(1:end-4);
                irs_array_aux{z} = irs_array_aux02;
            end

            try
                irs.array = irs_array_aux';
                obj.irs = irs;
            catch
            end


            irs_hybrid = dir([obj.path 'hybrid' filesep 'IRs' filesep '*.wav']);
            for z=1:length(irs_hybrid)
                irs_hybrid_aux02 = irs_hybrid(z).name;
                irs_hybrid_aux02 = irs_hybrid_aux02(1:end-4);
                irs_hybrid_aux{z} = irs_hybrid_aux02;
            end

            try
                irs.hybrid = irs_hybrid_aux';
                irs.array = irs.hybrid;
                irs.distributed = irs.hybrid;
                obj.irs = irs;
            catch
            end

            %% speaker locations

            speaker_locations_distributed = dir([obj.path 'distributed' filesep 'IRs' filesep '*w0.wav']);
            for z=1:length(speaker_locations_distributed)
                speaker_locations_distributed_aux02 = speaker_locations_distributed(z).name;
                speaker_locations_distributed_aux02 = speaker_locations_distributed_aux02(1:end-7);
                speaker_locations_distributed_aux{z} = speaker_locations_distributed_aux02;
            end

            try
                speaker_locations.distributed = speaker_locations_distributed_aux';
                obj.speaker_locations = speaker_locations;
            catch
            end

            speaker_locations_array = dir([obj.path 'array' filesep 'IRs' filesep '*w0.wav']);
            for z=1:length(speaker_locations_array)
                speaker_locations_array_aux02 = speaker_locations_array(z).name;
                speaker_locations_array_aux02 = speaker_locations_array_aux02(1:end-7);
                speaker_locations_array_aux{z} = speaker_locations_array_aux02;
            end

            try
                speaker_locations.array = speaker_locations_array_aux';
                obj.speaker_locations = speaker_locations;
            catch
            end


            speaker_locations_hybrid = dir([obj.path 'hybrid' filesep 'IRs' filesep '*w0.wav']);
            for z=1:length(speaker_locations_hybrid)
                speaker_locations_hybrid_aux02 = speaker_locations_hybrid(z).name;
                speaker_locations_hybrid_aux02 = speaker_locations_hybrid_aux02(1:end-7);
                speaker_locations_hybrid_aux{z} = speaker_locations_hybrid_aux02;
            end

            try
                speaker_locations.hybrid = speaker_locations_hybrid_aux';
                speaker_locations.array = speaker_locations.hybrid;
                speaker_locations.distributed = speaker_locations.hybrid;
                obj.speaker_locations = speaker_locations;
            catch
            end

            %% radio irs

            radio_irs_distributed = dir([obj.path 'distributed' filesep 'radio_IRs' filesep '*.wav']);
            for z=1:length(radio_irs_distributed)
                radio_irs_distributed_aux02 = radio_irs_distributed(z).name;
                radio_irs_distributed_aux02 = radio_irs_distributed_aux02(1:end-4);
                radio_irs_distributed_aux{z} = radio_irs_distributed_aux02;
            end

            try
                radio_irs.distributed = radio_irs_distributed_aux';
                obj.radio_irs = radio_irs;
            catch
            end

            radio_irs_array = dir([obj.path 'array' filesep 'radio_IRs' filesep '*.wav']);
            for z=1:length(radio_irs_array)
                radio_irs_array_aux02 = radio_irs_array(z).name;
                radio_irs_array_aux02 = radio_irs_array_aux02(1:end-4);
                radio_irs_array_aux{z} = radio_irs_array_aux02;
            end

            try
                radio_irs.array = radio_irs_array_aux';
                obj.radio_irs = radio_irs;
            catch
            end


            radio_irs_hybrid = dir([obj.path 'hybrid' filesep 'radio_IRs' filesep '*.wav']);
            for z=1:length(radio_irs_hybrid)
                radio_irs_hybrid_aux02 = radio_irs_hybrid(z).name;
                radio_irs_hybrid_aux02 = radio_irs_hybrid_aux02(1:end-4);
                radio_irs_hybrid_aux{z} = radio_irs_hybrid_aux02;
            end

            try
                radio_irs.hybrid = radio_irs_hybrid_aux';
                radio_irs.array = radio_irs.hybrid;
                radio_irs.distributed = radio_irs.hybrid;
                obj.radio_irs = radio_irs;
            catch
            end
            %% noise recordings

            noise_recordings_distributed = dir([obj.path 'distributed' filesep 'noise' filesep '*.wav']);
            for z=1:length(noise_recordings_distributed)
                noise_recordings_distributed_aux02 = noise_recordings_distributed(z).name;
                noise_recordings_distributed_aux02 = noise_recordings_distributed_aux02(1:end-4);
                noise_recordings_distributed_aux{z} = noise_recordings_distributed_aux02;
            end

            try
                noise_recordings.distributed = noise_recordings_distributed_aux';
                obj.noise_recordings = noise_recordings;
            catch
            end

            noise_recordings_array = dir([obj.path 'array' filesep 'noise' filesep '*.wav']);
            for z=1:length(noise_recordings_array)
                noise_recordings_array_aux02 = noise_recordings_array(z).name;
                noise_recordings_array_aux02 = noise_recordings_array_aux02(1:end-4);
                noise_recordings_array_aux{z} = noise_recordings_array_aux02;
            end

            try
                noise_recordings.array = noise_recordings_array_aux';
                obj.noise_recordings = noise_recordings;
            catch
            end


            noise_recordings_hybrid = dir([obj.path 'hybrid' filesep 'noise' filesep '*.wav']);
            for z=1:length(noise_recordings_hybrid)
                noise_recordings_hybrid_aux02 = noise_recordings_hybrid(z).name;
                noise_recordings_hybrid_aux02 = noise_recordings_hybrid_aux02(1:end-4);
                noise_recordings_hybrid_aux{z} = noise_recordings_hybrid_aux02;
            end

            try
                noise_recordings.hybrid = noise_recordings_hybrid_aux';
                noise_recordings.array = noise_recordings.hybrid;
                noise_recordings.distributed = noise_recordings.hybrid;
                obj.noise_recordings = noise_recordings;
            catch
            end
            %% ventilation recordings

            ventilation_recordings_distributed = dir([obj.path 'distributed' filesep 'ventilation' filesep '*.wav']);
            for z=1:length(ventilation_recordings_distributed)
                ventilation_recordings_distributed_aux02 = ventilation_recordings_distributed(z).name;
                ventilation_recordings_distributed_aux02 = ventilation_recordings_distributed_aux02(1:end-4);
                ventilation_recordings_distributed_aux{z} = ventilation_recordings_distributed_aux02;
            end

            try
                ventilation_recordings.distributed = ventilation_recordings_distributed_aux';
                obj.ventilation_recordings = ventilation_recordings;
            catch
            end

            ventilation_recordings_array = dir([obj.path 'array' filesep 'ventilation' filesep '*.wav']);
            for z=1:length(ventilation_recordings_array)
                ventilation_recordings_array_aux02 = ventilation_recordings_array(z).name;
                ventilation_recordings_array_aux02 = ventilation_recordings_array_aux02(1:end-4);
                ventilation_recordings_array_aux{z} = ventilation_recordings_array_aux02;
            end

            try
                ventilation_recordings.array = ventilation_recordings_array_aux';
                obj.ventilation_recordings = ventilation_recordings;
            catch
            end


            ventilation_recordings_hybrid = dir([obj.path 'hybrid' filesep 'ventilation' filesep '*.wav']);
            for z=1:length(ventilation_recordings_hybrid)
                ventilation_recordings_hybrid_aux02 = ventilation_recordings_hybrid(z).name;
                ventilation_recordings_hybrid_aux02 = ventilation_recordings_hybrid_aux02(1:end-4);
                ventilation_recordings_hybrid_aux{z} = ventilation_recordings_hybrid_aux02;
            end

            try
                ventilation_recordings.hybrid = ventilation_recordings_hybrid_aux';
                ventilation_recordings.array = ventilation_recordings.hybrid;
                ventilation_recordings.distributed = ventilation_recordings.hybrid;
                obj.ventilation_recordings = ventilation_recordings;
            catch
            end

        end
        function ir = load_ir(obj,varargin)

            %
            %
            %load_ir Loading impulse responses
            %
            %   Loads the impulse response (IR) channels for a given microphone setup and IR condition.
            %
            %   Input:
            %       mic_setup (char)   - The desired microphone setup to load the IR for.
            %       condition (char)   - The specific IR condition to load ("'speaker location'_w'window condition'").
            %   Output:
            %       ir (vector)   - Matrix NxM, containing the IR data
            %                       N = the number of samples, M=number of
            %                       microphones.
            %
            %   Example:
            %       my_car = car(path=car_path, fs=sampling_rate);
            %       irs = my_car.load_ir("condition",'d50_w1',"mic_setup",'array');

            p = inputParser;


            addParameter(p,'mic_setup','null')
            addParameter(p,'condition','null')

            parse(p,varargin{:})

            mic_setup = p.Results.mic_setup;
            condition = p.Results.condition;

            % check mic_setup

            searchname = ([obj.current_car '_' mic_setup]);
            selectedrow = strcmp(obj.setup_check, searchname);
            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The name of mic_setup "%s" is incorrect.',mic_setup);
                throw(ME)
            end

            if obj.current_car == "Hyundai_i30"
                [mic_setup,mic_setup_imag,mics_imag] = hyundai_aux(obj,mic_setup);
            end

            % check location & wav

            wav_list = dir([obj.path mic_setup '' filesep 'IRs' filesep '*.wav']);
            for z=1:length(wav_list)
                wav_list_aux{z,1} = wav_list(z).name;
            end

            ir_name_user = ([condition '.wav']);
            selectedrow = strcmp(wav_list_aux,ir_name_user);

            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The condition "%s" is incorrect.',condition);
                throw(ME)
            end

            ir_name = ([obj.path mic_setup '' filesep 'IRs' filesep '' condition '.wav']);
            [ir, Fs_ir] = audioread(ir_name); %% load impulse response

            % resample to fs

            if Fs_ir ~= obj.fs
                [P,Q] = rat(obj.fs/Fs_ir);
                ir = resample(ir,P,Q);
            end

            if obj.current_car == "Hyundai_i30"
                ir = hyundai_aux2(obj,ir,mic_setup_imag,mics_imag);
            end

        end
        function radio_ir = load_radio_ir(obj,varargin)

            %
            %load_radio_ir Loading radio impulse responses
            %
            %   Loads the radio impulse response (IR) channels for a given
            %   microphone setup and radio condition.
            %
            %   Input:
            %       mic_setup (char)   - The desired microphone setup to load the IR for.
            %       condition (char)   - The specific IR condition to load ("window condition").
            %   Output:
            %       radio_ir (vector)   - Matrix NxM, containing the radio IR data
            %                       N = the number of samples, M=number of
            %                       microphones.
            %   Example:
            %       my_car = car(path=car_path, fs=sampling_rate);
            %       radio_irs = my_car.load_radio_ir("condition",'w1',"mic_setup",'array');

            p = inputParser;


            addParameter(p,'mic_setup','null')
            addParameter(p,'condition','null')

            parse(p,varargin{:})

            mic_setup = p.Results.mic_setup;
            condition = p.Results.condition;

            % check mic_setup

            searchname = ([obj.current_car '_' mic_setup]);
            selectedrow = strcmp(obj.setup_check, searchname);
            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The name of mic_setup "%s" is incorrect.',mic_setup);
                throw(ME)
            end

            if obj.current_car == "Hyundai_i30"
                [mic_setup,mic_setup_imag,mics_imag] = hyundai_aux(obj,mic_setup);
            end

            % check wav and radio

            wav_list = dir([obj.path mic_setup '' filesep 'radio_IRs' filesep '*.wav']);
            for z=1:length(wav_list)
                wav_list_aux{z,1} = wav_list(z).name;
            end

            radio_ir_name_user = ([condition '.wav']);
            selectedrow = strcmp(wav_list_aux,radio_ir_name_user);

            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The condition "%s" is incorrect.',condition);
                throw(ME)
            end

            radio_ir_name = ([obj.path mic_setup '' filesep 'radio_IRs' filesep '' condition '.wav']);
            [radio_ir, Fs_radio_ir] = audioread(radio_ir_name); %% load impulse response

            % resample to fs

            if Fs_radio_ir ~= obj.fs
                [P,Q] = rat(obj.fs/Fs_radio_ir);
                radio_ir = resample(radio_ir,P,Q);
            end

            if obj.current_car == "Hyundai_i30"
                radio_ir = hyundai_aux2(obj,radio_ir,mic_setup_imag,mics_imag);
            end

        end
        function noise = load_noise(obj,varargin)

            %
            %load_noise Loading noise recordings
            %   Loads the noise recording channels for a given microphone setup and noise condition.
            %
            %   Input:
            %       mic_setup (char)   - The desired microphone setup to load the IR for.
            %       condition (char)   - The specific IR condition to load ("'speaker location'_w'window condition'").
            %   Output:
            %       ir (vector)   - Matrix NxM, containing the noise data
            %                       N = the number of samples, M=number of
            %                       microphones.
            %
            %   Example:
            %       my_car = car(path=car_path, fs=sampling_rate);
            %       noise = my_car.load_noise("condition",'s90_w1_ver1',"mic_setup",'array');

            p = inputParser;


            addParameter(p,'mic_setup','null')
            addParameter(p,'condition','null')

            parse(p,varargin{:})

            mic_setup = p.Results.mic_setup;
            condition = p.Results.condition;

            % check mic_setup

            searchname = ([obj.current_car '_' mic_setup]);
            selectedrow = strcmp(obj.setup_check, searchname);
            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The name of mic_setup "%s" is incorrect.',mic_setup);
                throw(ME)
            end


            if obj.current_car == "Hyundai_i30"
                [mic_setup,mic_setup_imag,mics_imag] = hyundai_aux(obj,mic_setup);
            end

            %check speed, version and speed

            wav_list = dir([obj.path mic_setup '' filesep 'noise' filesep '*.wav']);
            for z=1:length(wav_list)
                wav_list_aux{z,1} = wav_list(z).name;
            end

            noise_name_user = ([condition '.wav']);
            selectedrow = strcmp(wav_list_aux,noise_name_user);

            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The condition "%s" is incorrect.',condition);
                throw(ME)
            end

            noise_name = ([obj.path mic_setup '' filesep 'noise' filesep '' condition '.wav']);
            [noise,Fs_noise] = audioread(noise_name); %% load noise

            if Fs_noise ~= obj.fs
                [P,Q] = rat(obj.fs/Fs_noise);
                noise = resample(noise,P,Q);
            end

            if obj.current_car == "Hyundai_i30"
                noise = hyundai_aux2(obj,noise,mic_setup_imag,mics_imag);
            end

        end
        function ventilation = load_ventilation(obj,varargin)

            %
            %load_ventilation Loading ventilation recordings
            %
            %   Loads the ventilation recording for a given microphone
            %   setup and condition.            
            %   Input:
            %       mic_setup (char)   - The desired microphone setup to load the IR for.
            %       condition (char)   - The specific ventilation condition to load ("v'ventilation level'_w'window condition'").
            %   Output:
            %       ventilation(vector)   - Matrix NxM, containing the ventilation data
            %                               N = the number of samples, M=number of
            %                               microphones.
            %   Example:
            %       my_car = car(path=car_path, fs=sampling_rate);
            %       ventilation = my_car.load_ventilation("condition",'v1_w0',"mic_setup",'array');

            p = inputParser;


            addParameter(p,'mic_setup','null')
            addParameter(p,'condition','null')

            parse(p,varargin{:})

            mic_setup = p.Results.mic_setup;
            condition = p.Results.condition;

            % check mic_setup

            searchname = ([obj.current_car '_' mic_setup]);
            selectedrow = strcmp(obj.setup_check, searchname);
            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The name of mic_setup "%s" is incorrect.',mic_setup);
                throw(ME)
            end


            if obj.current_car == "Hyundai_i30"
                [mic_setup,mic_setup_imag,mics_imag] = hyundai_aux(obj,mic_setup);
            end

            % check ventilation

            wav_list = dir([obj.path mic_setup '' filesep 'ventilation' filesep '*.wav']);
            for z=1:length(wav_list)
                wav_list_aux{z,1} = wav_list(z).name;
            end

            ventilation_name_user = ([condition '.wav']);
            selectedrow = strcmp(wav_list_aux,ventilation_name_user);

            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The condition "%s" is incorrect.',condition);
                throw(ME)
            end

            ventilation_name = ([obj.path mic_setup '' filesep 'ventilation' filesep '' condition '.wav']);
            [ventilation, Fs_ventilation] = audioread(ventilation_name); %% load ventilation

            if Fs_ventilation ~= obj.fs
                [P,Q] = rat(obj.fs/Fs_ventilation);
                ventilation = resample(ventilation,P,Q);
            end


            if obj.current_car == "Hyundai_i30"
                ventilation = hyundai_aux2(obj,ventilation,mic_setup_imag,mics_imag);
            end

        end
        function [S] = get_speech(obj,varargin)

            %
            %get_speech Creating speech component (y=dry_speech*h_passenger)
            %
            %   Generates the convolved speech signal with the corresponding impulse response for a given
            %   microphone setup, location, and condition.
            %
            %   Input:
            %       mic_setup (char)   - The microphonesconfiguration to use.
            %       location (char)   - The location of speaker inside the car.
            %       window (double)   - The window condition.
            %       ls (double or char)   - The speech effort level.
            %       dry_speech (double)   - The dry speech signal in mono.
            %       mics (double or char, optional)   -  The microphone index or indices to use (Default=nan, all availabe microphones are used.).
            %       use_correction_gains (bool, optional)   -  A boolean indicating whether to use the correction gains (Default=true).
            %   Output:
            %       S (vector)   - Vector NxM, The processed speech signal.
            %                      N = the number of samples, M = the number of channels.
            %   Example:
            %       my_car = car(path=car_path, fs=sampling_rate);
            %       S = my_car.get_speech("dry_speech",dry_voice,"ls",'High',"mics",5, ...
            %       "location",'d50',"mic_setup",'array',"use_correction_gains",true,"window",1);


            p = inputParser;


            addParameter(p,'mic_setup','null')
            addParameter(p,'location','null')
            addParameter(p,'window','null')
            addParameter(p,'ls','null')
            addParameter(p,'dry_speech','null')
            addParameter(p,'mics',nan)
            addParameter(p,'use_correction_gains',true)

            parse(p,varargin{:})

            mic_setup = p.Results.mic_setup;
            location = p.Results.location;
            window = p.Results.window;
            ls = p.Results.ls;
            dry_speech = p.Results.dry_speech;
            mics = p.Results.mics;
            use_correction_gains = p.Results.use_correction_gains;

            % check mic_setup

            searchname = ([obj.current_car '_' mic_setup]);
            selectedrow = strcmp(obj.setup_check, searchname);
            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The name of mic_setup "%s" is incorrect.',mic_setup);
                throw(ME)
            end


            if obj.current_car == "Hyundai_i30"
                [mic_setup,mic_setup_imag] = hyundai_aux(obj,mic_setup);
            end

            % check window

            searchname = ([obj.current_car '_' mic_setup '_w' num2str(window)]);
            selectedrow = strcmp(obj.window_check, searchname);
            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The value of the variable "window" is incorrect.');
                throw(ME)
            end

            try
                if isnan(mics)
                    mics = 'None';
                end
            catch
            end

            % check mics

            if obj.current_car == "Hyundai_i30"
                [mics] = hyundai_aux3(obj,mics,mic_setup_imag);
            else
                if isnumeric(mics)
                    for m=1:length(mics)
                        if mics(m) >= 1 && mics(m) <= 8
                        else
                            ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                            throw(ME)
                        end
                    end
                else
                    if mics == "None"
                        mics = [1,2,3,4,5,6,7,8];
                    else
                        ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                        throw(ME)
                    end
                end
            end

            % check location (ir) & wav

            wav_list = dir([obj.path mic_setup '' filesep 'IRs' filesep '*.wav']);
            for z=1:length(wav_list)
                wav_list_aux{z,1} = wav_list(z).name;
            end

            ir_name_user = ([location '_w' num2str(window) '.wav']);
            selectedrow = strcmp(wav_list_aux,ir_name_user);

            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The value of the variable "location" is incorrect.');
                throw(ME)
            end

            % mic reference

            searchname = ([obj.current_car '_' mic_setup]);
            selectedrow = strcmp(obj.setup_check, searchname);
            aux_pointer = find(selectedrow,1); % mic_reference
            mic_reference_search = obj.mic_reference_list; % mic_reference
            mic_reference = mic_reference_search(aux_pointer,1); % mic_reference

            % check level ref

            load(['.' filesep 'source' filesep 'references.mat']); % load references levels
            searchname = ([location 'w' num2str(window) 'pink70mic' num2str(mic_reference) '.wav']);
            selectedrow = strcmp(references16KHzdatasetfull.([obj.current_car '_' mic_setup]), searchname);

            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','There is not this reference level.');
                throw(ME)
            end

            S = []; % vector of speech

            ir = load_ir(obj,"mic_setup",mic_setup,"condition",([location '_w' num2str(window)]));

            speech = dry_speech;

            for k=1:length(mics) %% l = this program will run l times. The loop is related to the quantity of microphones which choices for user.
                mic_in = mics(1,k); %% the k table is a table which shows what mic will export.

                ir_reference = ir(:,mic_reference);

                convoluted_signal = conv(speech,ir(:,mic_in)); %% convolution (dry speech * impulse response)
                convoluted_signal_reference = conv(speech,ir_reference); %% convolution (dry speech * impulse response)

                % dba meter
                [level_convoluted] = dBFS_A_meter(obj,convoluted_signal_reference); %% level_convoluted

                % level_references
                [level_reference] = levels_reference(obj,mic_setup,location,window,mic_reference);

                % scaling

                if  isnumeric(ls)
                    dl_aux  = (ls - obj.speech_calibration);
                    dl = (level_reference + dl_aux) - level_convoluted;
                    gain = 10^(dl/20);
                    convoluted_signal_scaled = convoluted_signal * gain;
                elseif ls == "High"
                    dl_aux  = (70 - obj.speech_calibration);
                    dl = (level_reference + dl_aux) - level_convoluted;
                    gain = 10^(dl/20);
                    convoluted_signal_scaled = convoluted_signal * gain;
                elseif ls == "Normal"
                    dl_aux  = (60 - obj.speech_calibration);
                    dl = (level_reference + dl_aux) - level_convoluted;
                    gain = 10^(dl/20);
                    convoluted_signal_scaled = convoluted_signal * gain;
                else
                    ME = MException('myComponent:inputError','The value of the variable "ls" is incorrect.');
                    throw(ME)
                end

                if use_correction_gains
                    convoluted_signal_scaled = convoluted_signal_scaled * obj.correction_lin(mic_in); %% gain_section (correction gains)
                end

                S = [S convoluted_signal_scaled];

            end
        end
        function [N] = get_noise(obj,varargin)

            %
            %get_noise Loading noise recordings
            %   Retrieves the in-motion noise recording for a given microphone setup, condition, and microphone index.
            %
            %   Input:
            %       mic_setup (char)   - The microphonesconfiguration to use.
            %       speed (double)   - The speed condition.
            %       window (double)   - The window condition.
            %       version (char, optional)   - The version of the noise recording in case there are multiple versions. Defaults to None. Must be "ver1", "ver2", etc or "coarse" (Default=nan).
            %       mics (double or char, optional)   - The microphone index or indices to use (Default=nan, all availabe microphones are used).
            %       use_correction_gains (bool, optional)   -  A boolean indicating whether to use the correction gains (Default=true).
            %   Output
            %       N (vector)   - Vector NxM, The processed noise signal.
            %                      N = the number of samples, M = the number of channels.
            %   Example:
            %       my_car = car(path=car_path, fs=sampling_rate);
            %       N = my_car.get_noise("mic_setup",'array',"speed",100,"window",1, ...
            %       "use_correction_gains",true,"mics",5);


            p = inputParser;


            addParameter(p,'mic_setup','null')
            addParameter(p,'speed','null')
            addParameter(p,'window','null')
            addParameter(p,'version',nan)
            addParameter(p,'mics',nan)
            addParameter(p,'use_correction_gains',true)

            parse(p,varargin{:})

            mic_setup = p.Results.mic_setup;
            speed = p.Results.speed;
            window = p.Results.window;
            version = p.Results.version;
            mics = p.Results.mics;
            use_correction_gains = p.Results.use_correction_gains;

            % check mic_setup

            searchname = ([obj.current_car '_' mic_setup]);
            selectedrow = strcmp(obj.setup_check, searchname);
            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The name of mic_setup "%s" is incorrect.',mic_setup);
                throw(ME)
            end

            if obj.current_car == "Hyundai_i30"
                [mic_setup,mic_setup_imag] = hyundai_aux(obj,mic_setup);
            end

            % check window

            searchname = ([obj.current_car '_' mic_setup '_w' num2str(window)]);
            selectedrow = strcmp(obj.window_check, searchname);
            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The value of the variable "window" is incorrect.');
                throw(ME)
            end

            try
                if isnan(mics)
                    mics = 'None';
                end
            catch
            end

            % check mics

            if obj.current_car == "Hyundai_i30"
                [mics] = hyundai_aux3(obj,mics,mic_setup_imag);
            else
                if isnumeric(mics)
                    for m=1:length(mics)
                        if mics(m) >= 1 && mics(m) <= 8
                        else
                            ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                            throw(ME)
                        end
                    end
                else
                    if mics == "None"
                        mics = [1,2,3,4,5,6,7,8];
                    else
                        ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                        throw(ME)
                    end
                end
            end

            try
                if isnan(version)
                    version = 'None';
                end
            catch
            end

            %check speed and version

            if ~isnumeric(version) && isnumeric(speed)
                if version == "None"
                    wav_list = dir([obj.path mic_setup '' filesep 'noise' filesep '*.wav']);
                    for z=1:length(wav_list)
                        wav_list_aux{z,1} = wav_list(z).name;
                    end

                    noise_name_user = ([ 's' num2str(speed) '_w' num2str(window) '.wav']);
                    condition = ([ 's' num2str(speed) '_w' num2str(window)]);
                    selectedrow = strcmp(wav_list_aux,noise_name_user);

                    if sum(selectedrow) == 0
                        noise_name_user = ([ 's' num2str(speed) '_w' num2str(window) '_ver1.wav']);
                        condition = ([ 's' num2str(speed) '_w' num2str(window) '_ver1']);
                        selectedrow = strcmp(wav_list_aux,noise_name_user);
                        if sum(selectedrow) > 0
                        else
                            ME = MException('myComponent:inputError','The value of the variable "speed" is incorrect.');
                            throw(ME)
                        end
                    end
                end

                if version == "ver1"
                    wav_list = dir([obj.path mic_setup '' filesep 'noise' filesep '*.wav']);
                    for z=1:length(wav_list)
                        wav_list_aux{z,1} = wav_list(z).name;
                    end

                    noise_name_user = ([ 's' num2str(speed) '_w' num2str(window) '.wav']);
                    condition = ([ 's' num2str(speed) '_w' num2str(window)]);
                    selectedrow = strcmp(wav_list_aux,noise_name_user);

                    if sum(selectedrow) == 0
                        noise_name_user = ([ 's' num2str(speed) '_w' num2str(window) '_ver1.wav']);
                        condition = ([ 's' num2str(speed) '_w' num2str(window) '_ver1']);
                        selectedrow = strcmp(wav_list_aux,noise_name_user);
                        if sum(selectedrow) > 0
                        else
                            ME = MException('myComponent:inputError','The value of the variable "speed" is incorrect.');
                            throw(ME)
                        end
                    end

                elseif version ~= "None"
                    wav_list = dir([obj.path mic_setup '' filesep 'noise' filesep '*.wav']);
                    for z=1:length(wav_list)
                        wav_list_aux{z,1} = wav_list(z).name;
                    end

                    noise_name_user = ([ 's' num2str(speed) '_w' num2str(window) '_' version '.wav']);
                    condition = ([ 's' num2str(speed) '_w' num2str(window) '_' version]);
                    selectedrow = strcmp(wav_list_aux,noise_name_user);

                    if sum(selectedrow) > 0
                    else
                        ME = MException('myComponent:inputError','The value of the variable "speed" is incorrect.');
                        throw(ME)
                    end
                end
            else
                ME = MException('myComponent:inputError','The value of the variable "speed" is incorrect.');
                throw(ME)
            end

            N = []; % vector noise

            [noise] =  load_noise(obj,"mic_setup",mic_setup,"condition",condition);

            if (use_correction_gains)
                for j=1:8
                    noise(:,j) = noise(:,j) * obj.correction_lin(j);
                end
            else
            end

            for k=1:length(mics) %% l = this program will run l times. The loop is related to the quantity of microphones which choices for user.
                mic_in = mics(1,k); %% the k table is a table which shows what mic will export.
                N = [N noise(:,mic_in)];
            end

        end
        function [A] = get_radio(obj,varargin)


            %
            %get_radio Creating radio_component (y=dry_radio*h_radio)
            %   Generates the radio (car-audio) signal by exploiting the measured  impulse response for a given
            %   microphone setup, condition, and microphone index.
            %
            %   Input:
            %       mic_setup (char)   - The configuration of microphones.
            %       window (double)   - The window condition.
            %       la (double)   - The radio audio level.
            %       radio_audio (double)   - The radio audio signal in mono (Default=nan).
            %       mics (double or char, optional)   - The microphone or microphones, which is chosen by the user.
            %       use_correction_gains (bool, optional)   -  A boolean indicating whether to use the correction gains (Default=true).
            %   Output:
            %       A (vector)   - Vector NxM, The processed radio signal.
            %                      N = the number of samples, M = the number of channels.
            %   Example:
            %       my_car = car(path=car_path, fs=sampling_rate);
            %       A = my_car.get_radio("la",70,"mics",5,"radio_audio",radio_tune, ...
            %       "mic_setup",'array',"use_correction_gains",true,"window",1);



            p = inputParser;


            addParameter(p,'mic_setup','null')
            addParameter(p,'window','null')
            addParameter(p,'la','null')
            addParameter(p,'radio_audio','null')
            addParameter(p,'mics',nan)
            addParameter(p,'use_correction_gains',true)

            parse(p,varargin{:})

            mic_setup = p.Results.mic_setup;
            window = p.Results.window;
            la = p.Results.la;
            radio_audio = p.Results.radio_audio;
            mics = p.Results.mics;
            use_correction_gains = p.Results.use_correction_gains;


            % check mic_setup

            searchname = ([obj.current_car '_' mic_setup]);
            selectedrow = strcmp(obj.setup_check, searchname);
            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The name of mic_setup "%s" is incorrect.',mic_setup);
                throw(ME)
            end

            if obj.current_car == "Hyundai_i30"
                [mic_setup,mic_setup_imag] = hyundai_aux(obj,mic_setup);
            end

            % check window

            searchname = ([obj.current_car '_' mic_setup '_w' num2str(window)]);
            selectedrow = strcmp(obj.window_check, searchname);
            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The value of the variable "window" is incorrect.');
                throw(ME)
            end

            try
                if isnan(mics)
                    mics = 'None';
                end
            catch
            end

            % check mics

            if obj.current_car == "Hyundai_i30"
                [mics] = hyundai_aux3(obj,mics,mic_setup_imag);
            else
                if isnumeric(mics)
                    for m=1:length(mics)
                        if mics(m) >= 1 && mics(m) <= 8
                        else
                            ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                            throw(ME)
                        end
                    end
                else
                    if mics == "None"
                        mics = [1,2,3,4,5,6,7,8];
                    else
                        ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                        throw(ME)
                    end
                end
            end

            % check wav and radio

            try

                wav_list = dir([obj.path mic_setup '' filesep 'radio_IRs' filesep '*.wav']);
                for z=1:length(wav_list)
                    wav_list_aux{z,1} = wav_list(z).name;
                end

                radio_ir_name_user = (['w' num2str(window) '.wav']);
                selectedrow = strcmp(wav_list_aux,radio_ir_name_user);

                if sum(selectedrow) > 0
                else
                    ME = MException('myComponent:inputError','There is not this "radio" condition.');
                    throw(ME)
                end
            catch
                ME = MException('myComponent:inputError','There is not this "radio" condition.');
                throw(ME)
            end


            % mic reference

            searchname = ([obj.current_car '_' mic_setup]);
            selectedrow = strcmp(obj.setup_check, searchname);
            aux_pointer = find(selectedrow,1); % mic_reference
            mic_reference_search = obj.mic_reference_list; % mic_reference
            mic_reference = mic_reference_search(aux_pointer,1); % mic_reference

            A = []; % vector of audio program

            [radio_ir] = load_radio_ir(obj,"mic_setup",mic_setup,"condition",(['w' num2str(window)]));

            radio_media_sample = radio_audio;

            for k=1:length(mics) %% l = this program will run l times. The loop is related to the quantity of microphones which choices for user.
                mic_in = mics(1,k); %% the k table is a table which shows what mic will export.

                radio_ir_reference = radio_ir(:,mic_reference);


                convoluted_radio = conv(radio_media_sample,radio_ir(:,mic_in)); %% convolution (dry speech * impulse response)
                convoluted_radio_reference = conv(radio_media_sample,radio_ir_reference); %% convolution (dry speech * impulse response)


                convoluted_radio_reference_cut = convoluted_radio_reference;

                if isnumeric(la)
                    [la_in_dbfs,level_convoluted_radio] = set_radio_volume(obj,mic_reference,la,convoluted_radio_reference_cut);
                    dl = la_in_dbfs - level_convoluted_radio;
                    gain = 10^(dl/20);
                    convoluted_radio_scaled = convoluted_radio * gain;
                else
                    ME = MException('myComponent:inputError','The value of the variable "la" is incorrect.');
                    throw(ME)
                end

                if use_correction_gains
                    convoluted_radio_scaled = convoluted_radio_scaled * obj.correction_lin(mic_in); %% gain_section (correction gains)
                end

                A = [A convoluted_radio_scaled];
            end
        end
        function [V] = get_ventilation(obj,varargin)

            %
            %get_ventilation Loading ventilation recordings
            %   Retrieves and processes the ventilation recording for a given
            %   microphone setup, condition, and ventilation level.
            %
            %   Input:
            %       mic_setup (char)   - The microphonesconfiguration to use.
            %       window (double)   - The window condition.
            %       level (double)   - The ventilation level.
            %       version (char, optional)   - The version of the ventilation recording in case there are multiple versions. Defaults to None. Must be "ver1", "ver2", etc (Default=nan).
            %       mics (double or char, optional)   -  The microphone index or indices to use (Default=nan, all availabe microphones are used.).
            %       use_correction_gains (bool, optional)   -  A boolean indicating whether to use the correction gains (Default=true).
            %   Output:
            %       V (vector)   - Vector NxM, The processed ventilation signal for the specified microphones.
            %                      N = the number of samples, M = the number of channels.
            %   Example:
            %       my_car = car(path=car_path, fs=sampling_rate);
            %       V = my_car.get_ventilation("mic_setup",'array',"level",3, ...
            %       "window",0,"use_correction_gains",true,"mics",5);




            p = inputParser;


            addParameter(p,'mic_setup','null')
            addParameter(p,'window','null')
            addParameter(p,'level','null')
            addParameter(p,'version',nan)
            addParameter(p,'mics',nan)
            addParameter(p,'use_correction_gains',true)

            parse(p,varargin{:})

            mic_setup = p.Results.mic_setup;
            window = p.Results.window;
            level = p.Results.level;
            version = p.Results.version;
            mics = p.Results.mics;
            use_correction_gains = p.Results.use_correction_gains;


            % check mic_setup

            searchname = ([obj.current_car '_' mic_setup]);
            selectedrow = strcmp(obj.setup_check, searchname);
            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The name of mic_setup "%s" is incorrect.',mic_setup);
                throw(ME)
            end

            if obj.current_car == "Hyundai_i30"
                [mic_setup,mic_setup_imag] = hyundai_aux(obj,mic_setup);
            end

            % check window

            searchname = ([obj.current_car '_' mic_setup '_w' num2str(window)]);
            selectedrow = strcmp(obj.window_check, searchname);
            if sum(selectedrow) > 0
            else
                ME = MException('myComponent:inputError','The value of the variable "window" is incorrect.');
                throw(ME)
            end

            try
                if isnan(mics)
                    mics = 'None';
                end
            catch
            end

            % check mics

            if obj.current_car == "Hyundai_i30"
                [mics] = hyundai_aux3(obj,mics,mic_setup_imag);
            else
                if isnumeric(mics)
                    for m=1:length(mics)
                        if mics(m) >= 1 && mics(m) <= 8
                        else
                            ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                            throw(ME)
                        end
                    end
                else
                    if mics == "None"
                        mics = [1,2,3,4,5,6,7,8];
                    else
                        ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                        throw(ME)
                    end
                end
            end

            try
                if isnan(version)
                    version = 'None';
                end
            catch
            end

            % check ventilation

            if ~isnumeric(version) && isnumeric(level)
                if version == "None"
                    wav_list = dir([obj.path mic_setup '' filesep 'ventilation' filesep '*.wav']);
                    for z=1:length(wav_list)
                        wav_list_aux{z,1} = wav_list(z).name;
                    end

                    ventilation_name_user = ([ 'v' num2str(level) '_w' num2str(window) '.wav']);
                    condition = ([ 'v' num2str(level) '_w' num2str(window)]);
                    selectedrow = strcmp(wav_list_aux,ventilation_name_user);

                    if sum(selectedrow) == 0
                        ventilation_name_user = ([ 'v' num2str(level) '_w' num2str(window) '_ver1.wav']);
                        condition = ([ 'v' num2str(level) '_w' num2str(window) '_ver1']);
                        selectedrow = strcmp(wav_list_aux,ventilation_name_user);
                        if sum(selectedrow) > 0
                        else
                            ME = MException('myComponent:inputError','The value of the variable "level" is incorrect.');
                            throw(ME)
                        end
                    end
                end

                if version == "ver1"
                    wav_list = dir([obj.path mic_setup '' filesep 'ventilation' filesep '*.wav']);
                    for z=1:length(wav_list)
                        wav_list_aux{z,1} = wav_list(z).name;
                    end

                    ventilation_name_user = ([ 'v' num2str(level) '_w' num2str(window) '.wav']);
                    condition = ([ 'v' num2str(level) '_w' num2str(window)]);
                    selectedrow = strcmp(wav_list_aux,ventilation_name_user);

                    if sum(selectedrow) == 0
                        ventilation_name_user = ([ 'v' num2str(level) '_w' num2str(window) '_ver1.wav']);
                        condition = ([ 'v' num2str(level) '_w' num2str(window) '_ver1']);
                        selectedrow = strcmp(wav_list_aux,ventilation_name_user);
                        if sum(selectedrow) > 0
                        else
                            ME = MException('myComponent:inputError','The value of the variable "level" is incorrect.');
                            throw(ME)
                        end
                    end

                elseif version ~= "None"
                    wav_list = dir([obj.path mic_setup '' filesep 'ventilation' filesep '*.wav']);
                    for z=1:length(wav_list)
                        wav_list_aux{z,1} = wav_list(z).name;
                    end

                    ventilation_name_user = ([ 'v' num2str(level) '_w' num2str(window) '_' version '.wav']);
                    condition = ([ 'v' num2str(level) '_w' num2str(window) '_' version]);
                    selectedrow = strcmp(wav_list_aux,ventilation_name_user);

                    if sum(selectedrow) > 0
                    else
                        ME = MException('myComponent:inputError','The value of the variable "level" is incorrect.');
                        throw(ME)
                    end
                end
            else
                ME = MException('myComponent:inputError','The value of the variable "level" is incorrect.');
                throw(ME)
            end

            V = []; % vector of ventilation

            [ventilation] = load_ventilation(obj,"mic_setup",mic_setup,"condition",condition);

            if (use_correction_gains)
                for j=1:8
                    ventilation(:,j) = ventilation(:,j) * obj.correction_lin(j);
                end
            else
            end

            for k=1:length(mics) %% l = this program will run l times. The loop is related to the quantity of microphones which choices for user.
                mic_in = mics(1,k); %% the k table is a table which shows what mic will export.
                V = [V ventilation(:,mic_in)];
            end
        end
        function [components] = get_components(obj,varargin)



            %get_components
            %   A wrapper function of the get_noise, get_speech, get_radio, and get_ventilation methods.
            %   Returns a matrix of components of the mixture in the following order: noise, speech, radio, ventilation.
            %   Speech, radio, and ventilation are optional.
            %
            %   Input:
            %       mic_setup (char)   - The microphonesconfiguration to use.
            %       location (char)   - The location of speaker inside the car.
            %       speed (double)   - The speed condition.
            %       window (double)   - The window condition.
            %       version (char, optional)   - The version of the noise recording in case there are multiple versions. Defaults to None. Must be "ver1", "ver2", etc or "coarse" (Default=nan).
            %       mics (double or char, optional)   -  The microphone index or indices to use (Default=nan, all availabe microphones are used.).
            %       ls (double or char, optional)   - The speech effort level (Default=nan).
            %       dry_speech (double, optional)   - The dry speech signal in mono (Default=nan).
            %       la (double, optional)   - The radio audio level (Default=nan).
            %       radio_audio (double, optional)   - The radio audio signal in mono (Default=nan).
            %       vent_level (double, optional)   - The ventilation level (Default=nan).
            %       use_correction_gains (bool, optional)   -  A boolean indicating whether to use the correction gains (Default=true).
            %   Output:
            %       components (matrix)   - Components (NxMxZ, N = the number of samples, M = the number of channels, Z = 4
            %       [speech component, noise component, radio component, ventilation component]).
            %   Example:
            %       my_car = car(path=car_path, fs=sampling_rate);
            %       [components] = my_car.get_components( ...
            %       "dry_speech",dry_voice,"la",70,"ls",'High',"mics",5, ...
            %       "location",'d50',"radio_audio",radio_tune, ...
            %       "mic_setup",'array',"speed",100,"window",1);
            %       noise_sample= components(:,:,1);
            %       speech_sample= components(:,:,2);
            %       radio_sample= components(:,:,3);
            %       ventilation_sample= components(:,:,4);


            p = inputParser;


            addParameter(p,'mic_setup','null')
            addParameter(p,'location','null')
            addParameter(p,'speed','null')
            addParameter(p,'window','null')
            addParameter(p,'version',nan)
            addParameter(p,'mics',nan)
            addParameter(p,'ls',nan)
            addParameter(p,'dry_speech',nan)
            addParameter(p,'la',nan)
            addParameter(p,'radio_audio',nan)
            addParameter(p,'vent_level',nan)
            addParameter(p,'use_correction_gains',true)

            parse(p,varargin{:})

            mic_setup = p.Results.mic_setup;
            location = p.Results.location;
            speed = p.Results.speed;
            window = p.Results.window;
            version = p.Results.version;
            mics = p.Results.mics;
            ls = p.Results.ls;
            dry_speech = p.Results.dry_speech;
            la = p.Results.la;
            radio_audio = p.Results.radio_audio;
            vent_level = p.Results.vent_level;
            use_correction_gains = p.Results.use_correction_gains;

            %% get_speech_switch

            try
                if isnan(dry_speech)
                    get_speech_switch = false;
                    ls=nan;
                else
                    get_speech_switch = true;
                end
            catch
                get_speech_switch = true;
            end

            try
                if isnan(ls)
                    get_speech_switch = false;
                    dry_speech=nan;
                else
                    get_speech_switch = true;
                end
            catch
                get_speech_switch = true;
            end

            %% get_radio_switch

            try
                if isnan(radio_audio)
                    get_radio_switch = false;
                    la=nan;
                else
                    get_radio_switch = true;
                end
            catch
                get_radio_switch = true;
            end
            try
                if isnan(la)
                    get_radio_switch = false;
                    radio_audio=nan;
                else
                    get_radio_switch = true;
                end
            catch
                get_radio_switch = true;
            end

            %% get_ventilation_switch

            try
                if isnan(vent_level)
                    get_ventilation_switch = false;
                else
                    get_ventilation_switch = true;
                end
            catch
                get_ventilation_switch = true;
            end

            %% scenerios

            if get_speech_switch && get_radio_switch && get_ventilation_switch % speech master
                S = get_speech(obj,"mic_setup",mic_setup,"location",location,"window",window,"mics",mics,"ls",ls,"dry_speech",dry_speech,"use_correction_gains",use_correction_gains);
                N = get_noise(obj,"mic_setup",mic_setup,"speed",speed,"window",window,"version",version,"mics",mics,"use_correction_gains",use_correction_gains);
                A = get_radio(obj,"mic_setup",mic_setup,"window",window,"mics",mics,"la",la,"radio_audio",radio_audio,"use_correction_gains",use_correction_gains);
                V = get_ventilation(obj,"mic_setup",mic_setup,"window",window,"level",vent_level,"mics",mics,"use_correction_gains",use_correction_gains);
                [S_new,N_new,A_new,V_new] = match_duration(obj,S,N,A,V); % S is the master.
            elseif get_speech_switch && get_radio_switch % speech master
                S = get_speech(obj,"mic_setup",mic_setup,"location",location,"window",window,"mics",mics,"ls",ls,"dry_speech",dry_speech,"use_correction_gains",use_correction_gains);
                N = get_noise(obj,"mic_setup",mic_setup,"speed",speed,"window",window,"version",version,"mics",mics,"use_correction_gains",use_correction_gains);
                A = get_radio(obj,"mic_setup",mic_setup,"window",window,"mics",mics,"la",la,"radio_audio",radio_audio,"use_correction_gains",use_correction_gains);
                V_new = zeros(size(S));
                [S_new,N_new,A_new] = match_duration(obj,S,N,A); % S is the master.
            elseif get_speech_switch && get_ventilation_switch % speech master
                S = get_speech(obj,"mic_setup",mic_setup,"location",location,"window",window,"mics",mics,"ls",ls,"dry_speech",dry_speech,"use_correction_gains",use_correction_gains);
                N = get_noise(obj,"mic_setup",mic_setup,"speed",speed,"window",window,"version",version,"mics",mics,"use_correction_gains",use_correction_gains);
                A_new = zeros(size(S));
                V = get_ventilation(obj,"mic_setup",mic_setup,"window",window,"level",vent_level,"mics",mics,"use_correction_gains",use_correction_gains);
                [S_new,N_new,V_new] = match_duration(obj,S,N,V); % S is the master.
            elseif get_speech_switch% speech master
                S = get_speech(obj,"mic_setup",mic_setup,"location",location,"window",window,"mics",mics,"ls",ls,"dry_speech",dry_speech,"use_correction_gains",use_correction_gains);
                N = get_noise(obj,"mic_setup",mic_setup,"speed",speed,"window",window,"version",version,"mics",mics,"use_correction_gains",use_correction_gains);
                A_new = zeros(size(S));
                V_new = zeros(size(S));
                [S_new,N_new] = match_duration(obj,S,N); % S is the master.
            elseif get_radio_switch && get_ventilation_switch % radio master
                N = get_noise(obj,"mic_setup",mic_setup,"speed",speed,"window",window,"version",version,"mics",mics,"use_correction_gains",use_correction_gains);
                A = get_radio(obj,"mic_setup",mic_setup,"window",window,"mics",mics,"la",la,"radio_audio",radio_audio,"use_correction_gains",use_correction_gains);
                V = get_ventilation(obj,"mic_setup",mic_setup,"window",window,"level",vent_level,"mics",mics,"use_correction_gains",use_correction_gains);
                S_new = zeros(size(A));
                [A_new,V_new,N_new] = match_duration(obj,A,V,N); % A is the master.
            elseif get_radio_switch % radio master
                N = get_noise(obj,"mic_setup",mic_setup,"speed",speed,"window",window,"version",version,"mics",mics,"use_correction_gains",use_correction_gains);
                A = get_radio(obj,"mic_setup",mic_setup,"window",window,"mics",mics,"la",la,"radio_audio",radio_audio,"use_correction_gains",use_correction_gains);
                V_new = zeros(size(A));
                S_new = zeros(size(A));
                [A_new,N_new] = match_duration(obj,A,N); % A is the master.
            elseif get_ventilation_switch % ventilation master
                N = get_noise(obj,"mic_setup",mic_setup,"speed",speed,"window",window,"version",version,"mics",mics,"use_correction_gains",use_correction_gains);
                V = get_ventilation(obj,"mic_setup",mic_setup,"window",window,"level",vent_level,"mics",mics,"use_correction_gains",use_correction_gains);
                S_new = zeros(size(V));
                A_new = zeros(size(V));
                [V_new,N_new] = match_duration(obj,V,N); % V is the master.
            else
                N_new = get_noise(obj,"mic_setup",mic_setup,"speed",speed,"window",window,"version",version,"mics",mics,"use_correction_gains",use_correction_gains);
                S_new = zeros(size(N_new));
                A_new = zeros(size(N_new));
                V_new = zeros(size(N_new));
            end

            components(:,:,1)=N_new;
            components(:,:,2)=S_new;
            components(:,:,3)=A_new;
            components(:,:,4)=V_new;
        end
        function steering_vector = construct_steering_vector(obj,varargin)

            %
            %construct_steering_vector Constucting steering vector
            %   Calculates the steering vectors for a given frequency and angle, theta,  for a microphone array configuration.
            %   The acoustic center is defined as the center of the microphone array. 0 degrees point towards the rear middle passenger,
            %   so that the driver is positioned at a negative angle and the front passenger at a positive angle.
            %
            %   Input:
            %       freq (double)   -  The frequency in Hz at which to calculate the steering vectors.
            %       theta (double)   - The angle in degrees at which to calculate the steering vectors.
            %   Output:
            %       steering_vector (complex double)   - An array of complex steering vectors for each microphone in the array.
            %   Example:
            %       my_car = car(path=car_path, fs=sampling_rate);
            %       sv = my_car.construct_steering_vector("freq",8000, "theta",-28)


            p = inputParser;

            addParameter(p,'freq','null')
            addParameter(p,'theta','null')

            parse(p,varargin{:})

            freq = p.Results.freq;
            theta = p.Results.theta;

            try

                theta= deg2rad(theta);
                c=343;

                if obj.current_car ~= "Hyundai_i30"

                    mic_angels = [pi,3*pi/4,pi/2,pi/4,0,-pi/4,-pi/2,-3*pi/4];

                    for mic=1:8
                        result(mic) = exp(1j*2*pi*freq/c*cos(theta-mic_angels(mic)));
                    end

                    steering_vector = result;

                else

                    mic_angels = [-pi,pi/2,0,-pi/2];

                    for mic=1:4
                        result(mic) = exp(1j*2*pi*freq/c*cos(theta-mic_angels(mic)));
                    end

                    steering_vector = result;

                end

            catch
                ME = MException('myComponent:inputError','The arguments are not correct. The freq must be positive number. Theta must be real number.');
                throw(ME)
            end

        end
        function angles = speaker_locations_angles(obj,varargin)

            %speaker_locations_angles
            %   Returns the speaker locations and their corresponding
            %   angles with respect to the center of the microphone array.
            %
            %   Input:
            %       mic_setup (char)   - The desired microphone setup to use. .
            %   Output:
            %       angles (Struct with 2 fields)   - The angles in degrees.
            %   Example:
            %       my_car = car(path=car_path, fs=sampling_rate);
            %       my_car.speaker_locations_angles("mic_setup",'array')

            p = inputParser;

            addParameter(p,'mic_setup','array')

            parse(p,varargin{:})

            mic_setup = p.Results.mic_setup;

            if mic_setup == "array"

                if obj.current_car == "Smart_forfour"

                    Smart_forfour_angles.location = ["d","pf","prl","prm","prr","prm10l","prm10r"];
                    Smart_forfour_angles.degrees = [-25,25,-13,0,13,-4,4];
                    angles = Smart_forfour_angles;

                elseif obj.current_car == "Volkswagen_Golf"

                    Volkswagen_Golf_angles.location = ["d50","pf60","pf80","prl","prm","prr"];
                    Volkswagen_Golf_angles.degrees = [-28,26,18,-12,0,-12];
                    angles = Volkswagen_Golf_angles;
                elseif obj.current_car == "Honda_CRV"

                    Honda_CRV_angles.location = ["d55","d63","pf","prl","prm","prr"];
                    Honda_CRV_angles.degrees = [-26,-24,26,-12,0,-12];
                    angles = Honda_CRV_angles;
                elseif obj.current_car == "Hyundai_i30"

                    Hyundai_i30_angles.location = ["d52","pf","prl","prm","prr"];
                    Hyundai_i30_angles.degrees = [-25,27,-13,0,-13];
                    angles = Hyundai_i30_angles;
                else

                    ME = MException('myComponent:inputError','There is no "array" configuration in this car ("%s").',obj.current_car);
                    throw(ME)
                end

            else
                ME = MException('myComponent:inputError','The function "speaker_locations_angles" is only executed when the mic_setup configuration is "array".');
                throw(ME)
            end
        end
        function [signal_A_new,signal_B_new,signal_C_new,signal_D_new] = match_duration(obj,signal_A,signal_B,signal_C,signal_D)


            %match_duration
            %   Matches the duration of all input signals to the duration of the first signal.
            %
            %   This method adjusts the duration of each input signal to match the duration of the first input signal. If a signal is longer than the first input signal, it is truncated. If an it is shorter, it is looped using crossfading to match the duration.
            %
            %   Input:
            %       signal_A (double)   - The master signal.
            %       signal_B (double)   - The signal b.
            %       signal_C (double, optional)   - The signal c.
            %       signal_D (double, optional)   - The signal d.
            %   Output:
            %       signal_A_new (vector)   - Vector NxM, N = the number of samples, M = the number of channels.
            %       signal_B_new (vector)   - Vector NxM, N = length(signal_A), M = the number of channels.
            %       signal_C_new (vector)   - Vector NxM, N = length(signal_A), M = the number of channels.
            %       signal_D_new (vector)   - Vector NxM, N = length(signal_A), M = the number of channels.
            %   Example:
            %       my_car = car(path=car_path, fs=sampling_rate);
            %       [S_new,N_new,A_new,V_new] = my_car.match_duration(S,N,A,V);

            z = nargin;

            signal_A_new = [];
            signal_B_new = [];
            signal_C_new = [];
            signal_D_new = [];

            signal_A_length = length(signal_A); % master
            [~,s2] = size(signal_A); %NumChannels

            if z == 2
                for k=1:s2

                    signal_A_mono = signal_A(:,k);

                    signal_A_new_mono = signal_A_mono;

                    signal_A_new = [signal_A_new signal_A_new_mono];
                    signal_B_new = NaN;
                    signal_C_new = NaN;
                    signal_D_new = NaN;
                end
            elseif z == 3
                for k=1:s2

                    signal_A_mono = signal_A(:,k);
                    signal_B_mono = signal_B(:,k);

                    signal_A_new_mono = signal_A_mono;
                    signal_B_new_mono = set_duration_crossfade(obj,signal_B_mono,signal_A_length);

                    signal_A_new = [signal_A_new signal_A_new_mono];
                    signal_B_new = [signal_B_new signal_B_new_mono];
                    signal_C_new = NaN;
                    signal_D_new = NaN;
                end
            elseif z == 4
                for k=1:s2

                    signal_A_mono = signal_A(:,k);
                    signal_B_mono = signal_B(:,k);
                    signal_C_mono = signal_C(:,k);

                    signal_A_new_mono = signal_A_mono;
                    signal_B_new_mono = set_duration_crossfade(obj,signal_B_mono,signal_A_length);
                    signal_C_new_mono = set_duration_crossfade(obj,signal_C_mono,signal_A_length);

                    signal_A_new = [signal_A_new signal_A_new_mono];
                    signal_B_new = [signal_B_new signal_B_new_mono];
                    signal_C_new = [signal_C_new signal_C_new_mono];
                    signal_D_new = NaN;
                end
            elseif z == 5
                for k=1:s2

                    signal_A_mono = signal_A(:,k);
                    signal_B_mono = signal_B(:,k);
                    signal_C_mono = signal_C(:,k);
                    signal_D_mono = signal_D(:,k);

                    signal_A_new_mono = signal_A_mono;
                    signal_B_new_mono = set_duration_crossfade(obj,signal_B_mono,signal_A_length);
                    signal_C_new_mono = set_duration_crossfade(obj,signal_C_mono,signal_A_length);
                    signal_D_new_mono = set_duration_crossfade(obj,signal_D_mono,signal_A_length);

                    signal_A_new = [signal_A_new signal_A_new_mono];
                    signal_B_new = [signal_B_new signal_B_new_mono];
                    signal_C_new = [signal_C_new signal_C_new_mono];
                    signal_D_new = [signal_D_new signal_D_new_mono];
                end
            else
            end
        end
    end
    methods (Access = private)
        function [level_convoluted] = dBFS_A_meter(obj,convoluted_signal_reference)

            AWeighting = weightingFilter('A-weighting',obj.fs);
            aSOSFilter = getFilter(AWeighting);
            aFiltered_convoluted_signal = aSOSFilter(convoluted_signal_reference);
            aFiltered_convoluted_signal_length = length(aFiltered_convoluted_signal);
            level_convoluted = 10*(log10(norm(aFiltered_convoluted_signal)^2/aFiltered_convoluted_signal_length));

        end
        function [level_reference] = levels_reference(obj,mic_setup,location,window,mic_reference)

            load(['.' filesep 'source' filesep 'references.mat']); % load references levels

            searchname = ([location 'w' num2str(window) 'pink70mic' num2str(mic_reference) '.wav']);
            selectedrow = strcmp(references16KHzdatasetfull.([obj.current_car '_' mic_setup]), searchname);
            pointer = find(selectedrow,1);
            level_reference_search = references16KHzdatasetfull.([obj.current_car '_' mic_setup '_level']);
            level_reference = level_reference_search(pointer,1);
            level_reference = level_reference - 2.5; %% You must subtract 2.5 dB due to the different sound  level between the samples "pink70" and "speech 70".

        end
        function [la_in_dbfs,level_convoluted_radio] = set_radio_volume(obj,mic_reference,la,convoluted_radio_reference_cut)

            AWeighting = weightingFilter('A-weighting',obj.fs);
            aSOSFilter = getFilter(AWeighting);
            aFiltered_convoluted_radio_signal = aSOSFilter(convoluted_radio_reference_cut);
            aFiltered_convoluted_radio_signal_length = length(aFiltered_convoluted_radio_signal);
            level_convoluted_radio = 10*(log10(norm(aFiltered_convoluted_radio_signal)^2/aFiltered_convoluted_radio_signal_length));

            la_in_dbfs = la - obj.dBFS_A_to_dBA(mic_reference);

        end
        function [secondary_signal_cut] = set_duration_crossfade(obj,secondary_signal,signal_A_length)

            secondary_signal_length = length(secondary_signal);

            if secondary_signal_length > signal_A_length
                secondary_signal_cut = secondary_signal(1:signal_A_length,1);
            elseif secondary_signal_length == signal_A_length
                secondary_signal_cut = secondary_signal(1:signal_A_length,1);
            elseif secondary_signal_length < signal_A_length

                sec = 1; % the duration of crossfade

                secondary_signal_start = secondary_signal(1:(obj.fs*sec));


                x = 0:(pi/2)/(obj.fs*sec):pi/2;
                y = sin(x);
                y = y(1:(obj.fs*sec));
                y = y'; % fade in curve (pi/2)
                z = flip(y); % fade out curve


                secondary_signal_cut = zeros(signal_A_length,1); % creating signal with duration = signal_A_length

                fade_in_signal = secondary_signal(1:(obj.fs*sec)) .* y;
                fade_out_signal = secondary_signal(length(secondary_signal)-(obj.fs*sec)+1:end) .* z;
                cross_fade_signal = fade_in_signal + fade_out_signal;
                body_signal = secondary_signal((obj.fs*sec)+1:(length(secondary_signal)-(obj.fs*sec))); % body singal (fs+1 up to end-fs)


                aux_signal = zeros(length(cross_fade_signal)+length(body_signal),1); % aux signal

                aux_signal(1:(obj.fs*sec)) = cross_fade_signal;
                % from 1 up to fs has crossfade
                aux_signal((obj.fs*sec)+1:end) = body_signal;
                % The "body_signal" is a signal which was created from fs+1 sample of the signal up to last sample of the signal

                loop_time = ceil(signal_A_length/length(aux_signal));

                aux_signal_extented = repmat(aux_signal,loop_time,1);
                aux_signal_extented = aux_signal_extented(1:length(secondary_signal_cut));


                release = length(aux_signal_extented) - signal_A_length;

                secondary_signal_cut = aux_signal_extented(1:(length(secondary_signal_cut)-release));
                secondary_signal_cut(1:obj.fs*sec) = secondary_signal_start; % The start of signal has not crossfade
            end
        end
        function [mic_setup,mic_setup_imag,mics_imag] = hyundai_aux(obj,mic_setup_real)
            mic_setup_imag = mic_setup_real;
            mic_setup = 'hybrid';
            if mic_setup_imag == "array"
                mics_imag = [1,2,3,4];
            elseif mic_setup_imag == "distributed"
                mics_imag = [3,5,6,7,8];
            elseif mic_setup_imag == "hybrid"
                mics_imag = [1,2,3,4,5,6,7,8];
            end
        end
        function [singalIN] = hyundai_aux2(obj,singalIN,mic_setup_imag,mics_imag)
            if mic_setup_imag == "array"
                for i=1:length(mics_imag)
                    singalIN_post(:,i) = singalIN(:,mics_imag(i));
                end
                singalIN=singalIN_post;
            elseif mic_setup_imag == "distributed"
                for i=1:length(mics_imag)
                    singalIN_post(:,i) = singalIN(:,mics_imag(i));
                end
                singalIN=singalIN_post;
            end
        end
        function [mics] = hyundai_aux3(obj,mics,mic_setup)
            if mic_setup == "hybrid"
                if isnumeric(mics)
                    for m=1:length(mics)
                        if mics(m) >= 1 && mics(m) <= 8
                        else
                            ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                            throw(ME)
                        end
                    end
                else
                    if mics == "None"
                        mics = [1,2,3,4,5,6,7,8];
                    else
                        ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                        throw(ME)
                    end
                end
            elseif mic_setup == "array"
                if isnumeric(mics)
                    for m=1:length(mics)
                        if mics(m) >= 1 && mics(m) <= 4
                        else
                            ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                            throw(ME)
                        end
                    end
                else
                    if mics == "None"
                        mics = [1,2,3,4];
                    else
                        ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                        throw(ME)
                    end
                end
            elseif mic_setup == "distributed"
                if isnumeric(mics)
                    for m=1:length(mics)
                        if mics(m) >= 2 && mics(m) <= 5
                            mics(m) = mics(m) + 3;
                        elseif mics(m) == 1
                            mics(m) = 3;
                        else
                            ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                            throw(ME)
                        end
                    end
                else
                    if mics == "None"
                        mics = [3,5,6,7,8];
                    else
                        ME = MException('myComponent:inputError','The value of the variable "mics" is incorrect.');
                        throw(ME)
                    end
                end
            end
        end
    end
end