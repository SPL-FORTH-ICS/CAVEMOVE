<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!-- [![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url] -->



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href=https://github.com/SPL-FORTH-ICS/CAVEMOVE>
    <img src="source/images/cavemoveLogoJune2024.png" alt="Logo" >
  </a>

  <h3 align="center">CAVEMOVE</h3>

  <p align="center">
    <!-- <br />
    <a href="https://github.com/othneildrew/Best-README-Template"><strong>Explore the docs »</strong></a>
    <br /> -->
    Acoustic data collection for speech enabled technologies in moving vehicles.
    <br />
    <a href="https://github.com/SPL-FORTH-ICS/CAVEMOVE/blob/main/documentation.md">Documentation</a>
    ·
    <a href="https://github.com/SPL-FORTH-ICS/CAVEMOVE/blob/main/CAVEMOVE_demo.ipynb">View Demo</a>
    ·
    <a href="https://github.com/SPL-FORTH-ICS/CAVEMOVE/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/SPL-FORTH-ICS/CAVEMOVE/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#quick-start">Quick Start</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Project dercription here

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

* [![Next][Next.js]][Next-url]
* [![React][React.js]][React-url]
* [![Vue][Vue.js]][Vue-url]
* [![Angular][Angular.io]][Angular-url]
* [![Svelte][Svelte.dev]][Svelte-url]
* [![Laravel][Laravel.com]][Laravel-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![JQuery][JQuery.com]][JQuery-url]
* [![Python][https://www.python.org/]][python-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p> -->



<!-- GETTING STARTED -->
## Getting Started
### Prerequisites

* A ```python 3.11``` enviroment .

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/SPL-FORTH-ICS/CAVEMOVE
   ```
2. Download CAVEMOVE dataset from  lllliiiiiiiiiinkkkkkk
    ```sh

    ```

3. Install dependancies
   ```sh
   pip install -r requirements.txt
   ```

4. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin github_username/repo_name
   git remote -v # confirm the changes
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- QUICKSTART -->
## Quick Start

```python
from Car import Car
import os

dataset_path = 'path/to/cavemove/dataset'
car_namea = ['Volkswagen_Golf', 'AlfaRomeo_146', 'AlfaRomeo_146']
car_path = os.path.join(dataset_path, car_names[0])

my_car = Car(path=car_path)

# You can use get_mixture_components to get only noise recording. Function returns a list containing only of the noise recording
components = my_car.get_mixture_components(mic_setup='array', position='d', condition='s50_w0', mics=[0, 2], fs=16000)

# by providing l_s, dry_speech and dry_speech_fs the function returns a list containing noise and speech component.
voice_path = 'path/to/dry/speech'
dry_voice, fs_dry_voice = librosa.load(voice_path, sr=16000)

components = my_car.get_mixture_components(mic_setup='array', position='d', condition='s50_w0', mics=[0, 2], fs=16000, l_s=60, dry_speech=dry_voice, dry_speech_fs=fs_dry_voice)

# by providing l_a, radio_audio and radio_audio_fs the function returns list containing noise and radio components.
radio_path = 'path/to/radio/song'
radio_tune, fs_radio_tune = librosa.load(radio_path, sr=16000)

components = my_car.get_mixture_components(mic_setup='array', position='d', condition='s50_w0', mics=[0, 2], fs=16000,l_a=50, radio_audio=radio_tune, radio_audio_fs=fs_radio_tune)

# by providing vent_level the function returns list containing noise and ventilation components.
components = my_car.get_mixture_components(mic_setup='array', position='d', condition='s50_w0', mics=[0, 2], fs=16000, vent_level=1)

# finally, get_mixture components can return all the above combinations or all of the components by providing te correspodins arguments
components = my_car.get_mixture_components(mic_setup='array', position='d', condition='s50_w0', mics=[0, 2], fs=16000, l_s=60, dry_speech=dry_voice, dry_speech_fs=fs_dry_voice, l_a=50, radio_audio=radio_tune, radio_audio_fs=fs_radio_tune, vent_level=1)


```

_For more examples, please refer to the [Documentation](https://github.com/SPL-FORTH-ICS/CAVEMOVE/documentation.md) or to the [CAVEMOVE demo](https://github.com/SPL-FORTH-ICS/CAVEMOVE/CAVEMOVE_demo.ipynb)._

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- DOCUMENTATION -->
## Documentation
For extensive documentation refer to [documentation.md](https://github.com/SPL-FORTH-ICS/CAVEMOVE/documentation.md) file.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
<!-- ROADMAP -->
<!-- ## Roadmap

- [x] Add Changelog
- [x] Add back to top links
- [ ] Add Additional Templates w/ Examples
- [ ] Add "components" document to easily copy & paste sections of the readme
- [ ] Multi-language Support
    - [ ] Chinese
    - [ ] Spanish

See the [open issues](https://github.com/SPL-FORTH-ICS/CAVEMOVE/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p> -->



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Top contributors:

<a href="https://github.com/SPL-FORTH-ICS/CAVEMOVE/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=SPL-FORTH-ICS/CAVEMOVE" />
</a>

Made with [contrib.rocks](https://contrib.rocks).
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Nikolaos Stefanakis - nstefana@ics.forth.gr

Project Link: [https://github.com/SPL-FORTH-ICS/CAVEMOVE/](https://github.com/SPL-FORTH-ICS/CAVEMOVE/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)

<p align="right">(<a href="#readme-top">back to top</a>)</p> -->



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
<!-- [contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 

[pyhton-url]: https://www.python.org/ -->

