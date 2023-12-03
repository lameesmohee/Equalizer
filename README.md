# Equalizer

## Table of Contents

- [Runing Project](#running-project)
- [Description](#description)
- [Features](#features)
- [Project Demo](#project-demo)

  ## Running the Project

1. **Prerequisites**:
   - Python (version 3.1.2)
   - PyQt5 (version 5.15.9)

2. **Installation**:
   To install the required dependencies, run the following command:
   ```bash
   pip install PyQt5

## Project Description

A Signal Equalizer Desktop Application is a software tool designed to manipulate and enhance audio signals. Users can open audio files and adjust the magnitude of specific frequency components using intuitive sliders.

## Features

- #### Mode Selection:
  The application offers four distinct modes - Uniform Range, Musical Instruments, Animal Sounds, and ECG Abnormalities. Users can switch between these modes 
  through an option menu or a combobox.
- #### Slider Control:
  - Uniform Range Mode: Ten sliders corresponding to ten equal frequency ranges of the input signal. Each slider controls the magnitude of its assigned frequency 
    range.
  - Musical Instruments Mode: Sliders controlling the magnitude of specific musical instruments in the input music signal, composed of at least four different 
    instruments.
  - Animal Sounds Mode: Sliders controlling the magnitude of specific animal sounds in a mixture of at least four animal sounds.
  - ECG Abnormalities Mode: Sliders controlling the magnitude of arrhythmia components in ECG signals, with four collected signals (one normal, three with specific 
    arrhythmias).
- #### Multiplication/Smoothing Windows:
   Users can choose from four windows (Rectangle, Hamming, Hanning, Gaussian) for applying a multiplication/smoothing window to the frequency range multiplied by 
   the corresponding slider value. Users can customize window parameters through the UI.
- #### Signal Visualization:
  - Cine Viewer: Allows signals to run in time with linked viewers for synchronous display.
  - Spectrograms: Visual representation of input and output signals, reflecting changes in real-time based on equalizer adjustments.:
- #### Real-Time Processing:
  Performs sampling and recovery in real-time without the need for manual updates or refreshes. 
- #### Responsive UI:
  Allows the application to be resized without compromising the user interface.

## Project Demo

## Screenshots


## Made by:

| Name                           | Section | BN  |
| ------------------------------ | ------- | --- |
| [Lama Zakaria Hassan Diab](https://github.com/lamalozo)              | 2 | 6  |
| [Lamees Mohamed Mohee Eldeen](https://github.com/lameesmohee)        | 2 | 7 |
| [Salema Abdeltawab](https://github.com/SalmaAbeltawab)        | 1 | 29 |

- Course Name : Digital Signal Processing .

## Submitted to:

- Prof. Tamer Basha & Eng. Abdullah Darwish

All rights reserved © 2023 to Team 9 - Systems & Biomedical Engineering, Cairo University (Class 2025)
