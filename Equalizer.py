import math
import os
import matplotlib

matplotlib.use('Qt5Agg')
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from os import path
import sys
import wave
import time
import numpy as np
import librosa
import soundfile as sf
from scipy.fft import ifft
from scipy.fftpack import fft, fftfreq
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
plt.style.use('ggplot')
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from qtawesome import icon
from scipy import signal
from scipy.misc import electrocardiogram
import pandas as pd
import scipy as sc
from scipy.io import wavfile
from datetime import datetime
from scipy.fft import fftshift
import wfdb
import pandas as pd


MainUI, _ = loadUiType(path.join(path.dirname(__file__), 'equalizer.ui'))


class MainApp(QMainWindow, MainUI):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.no_of_frames = 0
        self.counter_window = 0
        self.frequencies = []
        self.i = 0
        self.uesd_window = False
        self.first_adjusted = False
        self.y_min_time = None
        self.y_max_time = None
        self.Reset = False
        self.changed_data = False
        self.Windowing = False
        self.scenes = []
        self.amplitudes = []
        self.figures = [] # 0 -> original 1-> modified 2-> freqency
        self.axes = []
        self.play_animation = True
        self.lines = [None] * 4
        self.amps_down = {}
        self.ecg_mode = False
        self.amps_up = {}
        self.amps_up = {
            "owl": [],
            "frog": [],
            "canary": [],
            "grasshoppers": [],
            "xylophone": [],
            "drums": [],
            "piano": [],
            'flute': [],
            "AF": [],
            "VT": [],
            "APC": [],
            '1': [],
            '2': [],
            '3': [],
            '4': [],
            '5': [],
            '6': [],
            '7': [],
            '8': [],
            '9': [],
            '10': []

        }
        self.amps_down = {
            "owl": [],
            "frog": [],
            "canary": [],
            "grasshoppers": [],
            "xylophone": [],
            "drums": [],
            "piano": [],
            'flute': [],
            "AF": [],
            "VT": [],
            "APC": [],
            '1': [],
            '2': [],
            '3': [],
            '4': [],
            '5': [],
            '6': [],
            '7': [],
            '8': [],
            '9': [],
            '10': []

        }

        self.rs = None
        self.setupUi(self)
        self.setWindowTitle("Equalizer")
        self.uniform_sliders_list = [self.uni_slider1, self.uni_slider2, self.uni_slider3, self.uni_slider4,
                                     self.uni_slider5, self.uni_slider6, self.uni_slider7, self.uni_slider8,
                                     self.uni_slider9, self.uni_slider10]
        self.graphs = {
            0: self.graphicsView_original,
            1: self.graphicsView_modified,
            2: self.graphicsView_windowing

        }

        
        self.music_sliders_list = [self.music_slider1, self.music_slider2, self.music_slider3, self.music_slider4]

        self.animal_sliders_list = [self.animal_slider1, self.animal_slider2, self.animal_slider3, self.animal_slider4]

        self.all_sliders_list = [self.uni_slider1, self.uni_slider2, self.uni_slider3, self.uni_slider4,
                                 self.uni_slider5, self.uni_slider6, self.uni_slider7, self.uni_slider8,
                                 self.uni_slider9, self.uni_slider10, self.music_slider1, self.music_slider2,
                                 self.music_slider3, self.music_slider4, self.animal_slider1, self.animal_slider2,
                                 self.animal_slider3, self.animal_slider4, self.ecg_slider0,self.ecg_slider_VT,self.ecg_slider_AF]
        
        self.uni_labels_list = [self.uni_freq1, self.uni_freq2, self.uni_freq3, self.uni_freq4, self.uni_freq5,
                                self.uni_freq6, self.uni_freq7, self.uni_freq8, self.uni_freq9, self.uni_freq10]
        for label in self.uni_labels_list:
            label.hide()

        self.animal_labels_list = [self.owl_label, self.frog_label, self.grasshoppers_label, self.canary_label]

        self.music_labels_list = [self.xylophone_label, self.drums_label, self.piano_label, self.flute_label]

        for slider in self.all_sliders_list:
            # slider.setMinimum(0)
            # slider.setMaximum(2)  
            # slider.setValue(1)  
            # slider.setMinimum(0)
            # slider.setMaximum(20)  # Cover a range where each step represents 0.5 (0 to 20)
            # slider.setValue(10)  
            slider.setMinimum(0)
            slider.setMaximum(8)  # Multiply by 100
            slider.setValue(4)    # Set default value to 100
            slider.setSingleStep(1) 
             

        self.amp_uniform_list = [self.amp_uni1, self.amp_uni2, self.amp_uni3, self.amp_uni4, self.amp_uni5,
                                  self.amp_uni6, self.amp_uni7, self.amp_uni8, self.amp_uni9, self.amp_uni10]
        
        self.amp_animal_list = [self.amp_animal1, self.amp_animal2, self.amp_animal3, self.amp_animal4]

        self.amp_music_list = [self.amp_music1, self.amp_music2, self.amp_music3, self.amp_music4]

        self.all_amp_list = [self.amp_uni1, self.amp_uni2, self.amp_uni3, self.amp_uni4, self.amp_uni5,
                                  self.amp_uni6, self.amp_uni7, self.amp_uni8, self.amp_uni9, self.amp_uni10,
                                  self.amp_animal1, self.amp_animal2, self.amp_animal3, self.amp_animal4,
                                  self.amp_music1, self.amp_music2, self.amp_music3, self.amp_music4,
                                    self.amp_ecg, self.amp_ecg_VT, self.amp_ecg_AF ]
        
        for label in self.all_amp_list:
            label.setStyleSheet("background-color: transparent;")

        self.audio_player_components = [self.original_audio_label, self.original_frame, self.play_pause_audio_button,
                                         self.audio_progress, self.modified_audio_label, self.modified_frame,
                                         self.audio_progress_2, self.play_pause_audio_button_2]
        self.ecg_components = [self.ecg_slider0, self.ecg_slider_VT, self.ecg_slider_AF, self.AF_label,
                              self.VT_label, self.APC_label, self.amp_ecg_VT, self.amp_ecg, self.amp_ecg_AF]

        self.mode_index = 0
        self.Delay_interval = 200
        self.pause = False
        self.times_of_modified = 0
        self.x_fig_original = []
        self.x_fig_modified = []
        self.y_fig_original = []
        self.y_fig_modified = []
        self.check_ended_animation_1 = False
        self.modified_signal = False
        self.modified_signal_after_inverse = []
        self.line = None
        self.ani_2 = None
        self.ani_1 = None
        # self.ani_11 = None
        self.specific_row = 0
        self.specific_row_2 = 0
        self.index = 0
        self.data_original = None
        self.sampling_rate = 0
        self.n_samples = 0
        self.type_data = 0
        self.Counter_file = 0
        self.path_original_data = None
        self.selected_rectangle =None
        self.selected = False
        self.windows ={
            'Hamming':self.hamming,
            "Hanning":self.hanning,
            "Rectagular":self.rectangular,
            "Gaussian":self.gaussian

        }
        self.data_of_window = []
        # 0-> animal mode 1-> music mode 2-> ecg 3-> uniform
        self.list_of_modes = [{
            "owl": np.array([650, 950, -650, -950]),
            "frog": np.array([950, 1900, -950, -1900]),
            "canary": np.array([3000, 5500, -3000, -5500]),
            "grasshoppers": np.array([6000, 20000, -6000, -20000])
        },
            {
                "drums": np.array([0, 1000, 0, -1000]),
                'piano': np.array([1000, 2300, -1000, -2300]),
                "xylophone": np.array([2000, 3000, -2000, -3000]),
                'flute': np.array([3400, 25000, -3400, -25000])
            },
            {'AF': np.array([25, 250, -25, -250]),
             'APC':np.array([7, 13, -7, -13]),
             "VT":np.array([1, 5, -1, -5])
             },

            {
                "1": np.array([0, 2000, 0, -2000]),
                "2": np.array([2000, 4000, -2000, -4000]),
                "3": np.array([4000, 6000, -4000, -6000]),
                "4": np.array([6000, 8000, -6000, -8000]),
                "5": np.array([8000, 10000, -8000, -10000]),
                "6": np.array([10000, 12000, -10000, -12000]),
                "7": np.array([12000, 14000, -12000, -14000]),
                "8": np.array([14000, 16000, -14000, -16000]),
                "9": np.array([16000, 18000, -16000, -18000]),
                "10": np.array([18000, 20000, -18000, -20000])
            }]

        self.create_figures()
        self.create_scene()
        self.ecg_slider0.hide()
        self.show_sliders()
        self.no_of_points = 1000
        self.media_player = QMediaPlayer()
        self.media_player_modified_signal = QMediaPlayer()
        self.handle_buttons()

        self.styles()
        self.players = {1: [self.media_player, self.graph_btn_play, self.play_pause_audio_button],
                        2: [self.media_player_modified_signal, self.play_pause_audio_button_2]}

    def handle_buttons(self):
        self.mode_options.currentIndexChanged.connect(self.show_sliders)

        self.actionUpload.triggered.connect(self.add_audio)

        self.play_pause_audio_button.clicked.connect(lambda: self.play_pause_audio(self.play_pause_audio_button))
        self.play_pause_audio_button_2.clicked.connect(lambda: self.play_pause_audio(self.play_pause_audio_button_2))

        self.media_player.positionChanged.connect(
            lambda: self.set_audio_position(self.media_player, self.audio_progress))
        self.media_player_modified_signal.positionChanged.connect(
            lambda: self.set_audio_position(self.media_player_modified_signal, self.audio_progress_2))

        self.graphicsView_original.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.graphicsView_original.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.graphicsView_windowing.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.graphicsView_windowing.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.graphicsView_modified.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.graphicsView_modified.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.graphicsView_Spectro_original.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.graphicsView_Spectro_original.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.graphicsView_spectro_modified.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.graphicsView_spectro_modified.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.animal_slider1.valueChanged.connect(lambda: self.band_width('owl', self.animal_slider1.value()/4.0, label = self.amp_animal1))

        self.animal_slider2.valueChanged.connect(lambda: self.band_width('frog', self.animal_slider2.value()/4.0, label = self.amp_animal2))

        self.animal_slider3.valueChanged.connect(lambda: self.band_width('grasshoppers', self.animal_slider3.value()/4, label = self.amp_animal3))
        self.animal_slider4.valueChanged.connect(lambda: self.band_width('canary', self.animal_slider4.value()/4.0, label = self.amp_animal4))

        self.music_slider1.valueChanged.connect(lambda: self.band_width('xylophone', self.music_slider1.value()/4.0,label = self.amp_music1))

        self.music_slider2.valueChanged.connect(lambda: self.band_width('drums', self.music_slider2.value()/4.0, label = self.amp_music2))
        self.music_slider3.valueChanged.connect(lambda: self.band_width('piano', self.music_slider3.value()/4.0, label = self.amp_music3))

        self.music_slider4.valueChanged.connect(lambda: self.band_width('flute', self.music_slider4.value()/4.0, label = self.amp_music4))

        self.ecg_slider0.valueChanged.connect(lambda: self.band_width('APC', self.ecg_slider0.value()/4.0, label = self.amp_ecg,fs=360))
        self.ecg_slider_VT.valueChanged.connect(lambda: self.band_width('VT', self.ecg_slider_VT.value()/4.0, label = self.amp_ecg_VT,fs=360))
        self.ecg_slider_AF.valueChanged.connect(lambda: self.band_width('AF', self.ecg_slider_AF.value()/4.0, label = self.amp_ecg_AF,fs=360))

        self.ecg_slider0.valueChanged.connect(self.arrhythima)
        self.graph_btn_play.clicked.connect(self.toggle_channel_animation)

        self.speed_down_btn.clicked.connect(self.decrease_speed)

        self.pan_btn.clicked.connect(self.pan)

        self.speed_up_btn.clicked.connect(self.increase_speed)

        self.zoom_in_btn.clicked.connect(self.Zoom_in)

        self.zoom_out_btn.clicked.connect(self.Zoom_out)
        self.backward.clicked.connect(self.backward_changes)
        # self.zoom_out_btn.clicked.connect(self.selection)
        self.reset_btn.clicked.connect(self.reset)
        self.Timer = QTimer(self)
        self.graphicsView_windowing.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.graphicsView_windowing.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.check_spectro.stateChanged.connect(self.check_spectro_state_changed)
        self.uni_slider1.valueChanged.connect(lambda: self.band_width('1', self.uni_slider1.value()/4.0, label = self.amp_uni1))

        self.uni_slider2.valueChanged.connect(lambda: self.band_width('2', self.uni_slider2.value()/4.0, label = self.amp_uni2))

        self.uni_slider3.valueChanged.connect(lambda: self.band_width('3', self.uni_slider3.value()/4.0, label = self.amp_uni3))

        self.uni_slider4.valueChanged.connect(lambda: self.band_width('4', self.uni_slider4.value()/4.0, label = self.amp_uni4))

        self.uni_slider5.valueChanged.connect(lambda: self.band_width('5', self.uni_slider5.value()/4.0, label = self.amp_uni5))

        self.uni_slider6.valueChanged.connect(lambda: self.band_width('6', self.uni_slider6.value()/4.0, label = self.amp_uni6))

        self.uni_slider7.valueChanged.connect(lambda: self.band_width('7', self.uni_slider7.value()/4.0, label = self.amp_uni7))

        self.uni_slider8.valueChanged.connect(lambda: self.band_width('8', self.uni_slider8.value()/4.0, label = self.amp_uni8))

        self.uni_slider9.valueChanged.connect(lambda: self.band_width('9', self.uni_slider9.value()/4.0, label = self.amp_uni9))

        self.uni_slider10.valueChanged.connect(lambda: self.band_width('10', self.uni_slider10.value()/4.0, label = self.amp_uni10))

        self.comboBox_windowing.currentTextChanged.connect(self.check_type_window)
        self.comboBox_windowing.currentTextChanged.connect(self.on_combobox_changed)
        self.enter_window.clicked.connect(self.get_window_size)
        self.graphicsView_windowing.setMouseTracking(True)
        # self.graphicsView_windowing.mousePressEvent = self.selection
        self.figures[2].canvas.mpl_connect('button_press_event', self.selection)

        # self.selection()
    def styles(self):
        zoom_in_icon = icon("ei.zoom-in", color='black')
        zoom_out_icon = icon("ei.zoom-out", color="black")
        self.zoom_in_btn.setIcon(zoom_in_icon)
        self.zoom_out_btn.setIcon(zoom_out_icon)
        speed_up_icon = icon("ph.trend-up-bold", color="black")
        speed_down_icon = icon("ph.trend-down-bold", color="black")
        self.speed_up_btn.setIcon(speed_up_icon)
        self.speed_down_btn.setIcon(speed_down_icon)
        pan_icon = icon("fa5s.hand-paper", color="black")
        self.pan_btn.setIcon(pan_icon)
        reset_icon = icon("msc.debug-restart", color="black")
        self.reset_btn.setIcon(reset_icon)
        back_icon = icon('ri.arrow-go-back-fill', color="black")
        self.backward.setIcon(back_icon)
        
        self.std_label.hide()
        self.std_input.hide()
        self.enter_window.hide()

    def on_combobox_changed(self, index):
        current_window = self.check_type_window()
        if current_window == "No Window":
            self.reset()
        else:
            if current_window == "Gaussian":
                self.std_label.show()
                self.std_input.show()
                self.enter_window.show()
                self.enter_window.move(500, 130)
            else:
                self.enter_window.hide()
                self.std_label.hide()
                self.std_input.hide()
                self.windowing(current_window)

    def get_window_size(self):
        current_window = self.check_type_window()
        print(len(self.std_input.text()))
        if len(self.std_input.text()) > 1:
            std = float(self.std_input.text())
        else:
            std = 0

        print(f"std:{std}")

        self.windowing(current_window, std)

    def play_pause_audio(self, button_name):
        # Toggling the Play and Pause for the audio
        if button_name == self.play_pause_audio_button:
            if self.play_pause_audio_button.text() == "►":
                self.play_pause_audio_button.setText('❚❚')
                self.media_player.play()
            else:
                self.play_pause_audio_button.setText('►')
                self.media_player.pause()
        else:
            if self.play_pause_audio_button_2.text() == "►":
                self.play_pause_audio_button_2.setText('❚❚')
                self.media_player_modified_signal.play()
            else:
                self.play_pause_audio_button_2.setText('►')
                self.media_player_modified_signal.pause()

    def set_audio_position(self, media_name, audio_progress):
        # Connecting the media player to the progress slider
        if audio_progress.maximum() != (media_name.duration()):
            audio_progress.setMaximum(media_name.duration())
        audio_progress.setValue(media_name.position())

    def set_audio(self, file_path, player): ## comment
        self.players[player][0].setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        self.players[player][0].play()
        self.players[3-player][0].pause()
        self.players[player][1].setText("❚❚")
        self.players[3-player][1].setText('►')

        return

    def create_figures(self):
        for __ in range(0,3):
            figure = Figure(figsize=(650 / 80, 250 / 80), dpi=80)
            ax = figure.add_subplot(111)
            self.figures.append(figure)
            self.axes.append(ax)
        self.figures[2] = Figure(figsize=(480 / 80, 300 / 80), dpi=80)
        ax = self.figures[2].add_subplot(111)
        self.axes[2] = ax
    def create_scene(self):
        for __ in range (0,3):
            scene = QtWidgets.QGraphicsScene()
            self.scenes.append(scene)

    def add_audio(self):
        # Reading the audio
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", os.path.expanduser("~"),
                                                        "Audio Files (*.mp3 *.wav)")
        if self.file_path:

            self.delete()
            self.times_of_modified += 1
            if self.mode != 2:
                self.x_fig_original = []
                self.time = []
                self.Read_signal(file_path=self.file_path)
                self.set_audio(file_path=self.file_path, player=1)
            else:
                self.ecg(self.file_path)
                # self.ecg_record(self.file_path)

    def Write_modified_signal(self, modified_signal):
        directory_path, file_name = os.path.split(self.file_path)
        file_name_without_extension, file_extension = os.path.splitext(file_name)


        self.Counter_file += 1
        modified_file_name = f"{file_name_without_extension}_modified_{self.Counter_file}.wav"

        file_path = os.path.join(directory_path, modified_file_name)


        try:
            with sf.SoundFile(file_path, 'w', format='wav', samplerate=self.sampling_rate, channels=1) as file:
                # Write the modified signal to the file
                file.write(modified_signal)
                print("The Data is stored")

        except Exception as e:
            print(f"Error: {e}")
        print("Modified file written to:", file_path)

        if not self.changed_data:
            self.modified_signal = True
            self.set_audio(file_path=file_path, player=2)

        else:
            self.set_audio(file_path=file_path, player=1)
        QCoreApplication.processEvents()
        self.Read_signal(file_path)

    def load_data(self, file_path, sr=44100):
        data, self.sampling_rate = librosa.load(file_path, sr=sr)
        # self.data_signal = data
        print(f"sampling_rate:{self.sampling_rate}")
        end_time = librosa.get_duration(y=data, sr=self.sampling_rate)
        self.time = np.linspace(0, end_time, len(data))
        return data

    def Read_signal(self, file_path, sr=44100):
        data = self.load_data(file_path, sr)

        if self.play_animation:
            if len(self.modified_signal_after_inverse) > 1:
                print(f"fileeeeeeeee:{file_path}")
                # QCoreApplication.processEvents()
                print(f"modify:{min(self.data_original), max(self.data_original)}")

                self.plot(1, [], [], 'r', min(self.data_original), max(self.data_original))

            else:

                self.data_original = data
                if not self.changed_data:  # to stop creation of animation when i make windowing
                    self.axes[0].cla()
                    self.path_original_data = file_path
                    self.no_of_frames = int(np.floor(len(data)) / 1000)
                    print("ALLLLO")
                    print(f"org:{min(self.data_original), max(self.data_original)}")
                    self.plot(0, [], [], 'b', min(self.data_original), max(self.data_original))
                    self.y_min_time, self.y_max_time = self.axes[0].get_ylim()
                    self.create_frequency_spectrum(self.data_original)
                    self.ani_1 = FuncAnimation(self.figures[0], self.animate_figures_origin,
                                               interval=self.Delay_interval,
                                               frames=self.no_of_frames, repeat=False,
                                               fargs=(len(self.data_original), self.data_original), blit=False)

            self.plot_spectrogram(self.sampling_rate)

    def plot(self,figure_index, data_x, data_y, color, y_min, y_max):
        self.axes[figure_index].set_position([0.1, 0.3, 0.75, 0.65])
        # print(f"xx:{x_min}")
        self.axes[figure_index].set_ylim(y_min, y_max)

        self.lines[figure_index], = self.axes[figure_index].plot(data_x,data_y,color=color)

        canvas = FigureCanvasQTAgg(self.figures[figure_index])
        self.graphs[figure_index].setScene(self.scenes[figure_index])
        self.scenes[figure_index].addWidget(canvas)

    def create_frequency_spectrum(self, signal, sigma=0, sr=44100):## coment
        if not self.changed_data:
            print("TTTTTTTT")
            self.axes[2].clear()
            # self.changed_data = False
        else:
            self.axes[2].clear()
            if self.counter_window > 2:
                self.windowing(self.window_name)

            self.plot_windowing(sigma)

        # frequencies_bin, amplitudes, signal = self.Fourier_Transform(signal, sr)
        self.frequencies, self.amplitudes, self.modified_signal_list = self.Fourier_Transform(signal, sr)
        if len(self.modified_signal_after_inverse) < 1 and not self.Windowing:
            print("HALLO")
            self.y_min, self.y_max = min(self.amplitudes), max(self.amplitudes)
            self.x_min, self.x_max = min(self.frequencies), max(self.frequencies)

        self.plot(2,self.frequencies,self.amplitudes,'g',self.y_min,self.y_max)
        return

    def plot_spectrogram(self, sampling_rate):
        self.fig_spectrogram_original = plt.figure(figsize=(500 / 80, 250 / 80), dpi=80)
        f, t, Sxx = signal.spectrogram(self.data_original, sampling_rate, scaling='spectrum')
        print(f"f:{Sxx}")
        plt.pcolormesh(t, f, np.log10(Sxx))
        plt.ylabel('f [Hz]')
        plt.xlabel('t [sec]')
        # plt.ylim(0,20)
        print(f"before scene:{self.graphicsView_original.scene()}")
        scene5 = QtWidgets.QGraphicsScene(self)
        canvas_3 = FigureCanvasQTAgg(self.fig_spectrogram_original)
        self.graphicsView_Spectro_original.setScene(scene5)
        print(f"After scene:{self.graphicsView_Spectro_original.scene()}")
        scene5.addWidget(canvas_3)
        if len(self.modified_signal_after_inverse) > 1:
            print("kkkk")
            self.fig_spectrogram_modified = plt.figure(figsize=(500 / 80, 250 / 80), dpi=80)
            f_modified, t_modified, Sxx_modified = signal.spectrogram(self.modified_signal_after_inverse, sampling_rate,
                                                                      scaling='spectrum')
            plt.pcolormesh(t_modified, f_modified, np.log10(Sxx_modified))
            plt.ylabel('f [Hz]')
            plt.xlabel('t [sec]')
            scene2 = QtWidgets.QGraphicsScene(self)
            canvas_4 = FigureCanvasQTAgg(self.fig_spectrogram_modified)
            self.graphicsView_spectro_modified.setScene(scene2)
            scene2.addWidget(canvas_4)

    def declaretion_mode(self, mode_name):
        return self.list_of_modes[mode_name]


    def animate_figures_origin(self, i, length_data, data):
        # print(f"i:{i}")
        # QCoreApplication.processEvents()
        self.i = i
        if self.modified_signal or self.Windowing or self.Reset:
            print("lamaaa")
            self.ani_1.pause()
            if self.Reset:
                print("Reset")
                self.Reset = False

            self.no_of_frames = int(np.floor(length_data) / 1000)
            self.modified_signal = False
            if i > 0:
                self.ani_1 = FuncAnimation(self.figures[0], self.animate_figures_origin, interval=self.Delay_interval,
                                           frames=self.no_of_frames, repeat=False, fargs=(length_data, data), blit=False)


            self.specific_row = 0
            self.y_fig_original = []
            self.x_fig_original = []

            print("lllll")

            if len(self.modified_signal_after_inverse) > 1:
                self.axes[1].cla()
                print(f"x_fig_length:{len(self.x_fig_modified)}")

                if len(self.x_fig_modified) > 1:
                    self.ani_2.pause()
                self.y_fig_modified = []
                self.x_fig_modified = []
                print(f"x_fig_length:{len(self.x_fig_modified)}")

                print("bbbbb")
                QCoreApplication.processEvents()
                self.ani_2 = FuncAnimation(self.figures[1], self.animate_figures_modified, interval=self.Delay_interval,
                                           frames=self.no_of_frames, repeat=False, fargs=(
                        len(self.modified_signal_after_inverse), self.modified_signal_after_inverse), blit=False)


                print("lkkkk")
            self.Windowing = False


        self.specific_row += self.no_of_points
        if self.specific_row <= length_data - 1:

            self.check_ended_animation_1 = False
            data_array = np.array(data)
            time_array = np.array(self.time)
            # Slice the arrays
            data_sliced = data_array[:self.specific_row]
            time_sliced = time_array[:self.specific_row]
            print(f"length of data:{len(data_array)}")
            self.y_fig_original, self.x_fig_original = data_sliced.tolist(), time_sliced.tolist()
            self.lines[0].set_data(self.x_fig_original, self.y_fig_original)
            if self.specific_row > 1000:
                self.axes[0].set_xlim(self.time[self.specific_row - 1000], self.time[self.specific_row])
        else:
            self.check_ended_animation_1 = True

        return self.lines[0],

    def animate_figures_modified(self, i, length_data, data):
        print(f"i_2:{i}")
        print(f"spec:{self.specific_row},{length_data}")
        if self.specific_row <= length_data - 1:
            data_array = np.array(data)
            time_array = np.array(self.time)
            # Slice the arrays
            data_sliced = data_array[:self.specific_row]
            time_sliced = time_array[:self.specific_row]
            print(f"data:{len(data_sliced),len(time_sliced)}")
            self.y_fig_modified, self.x_fig_modified = data_sliced.tolist(), time_sliced.tolist()
            self.lines[1].set_data(self.x_fig_modified , self.y_fig_modified)

            if self.specific_row > 1000:
                self.axes[1].set_xlim(self.time[self.specific_row - 1000], self.time[self.specific_row])

        return self.lines[1],



    def band_width(self, name, amp, label, fs=44100):
        label.setText(str(amp))
        data_bands = self.declaretion_mode(self.mode)
        band_width_bin = data_bands[name]
        amp = float(amp)
        if amp == 0.0:
            amp = 0.001
        modified_amp = self.adjust_sliders(amp, name)
        self.assign_amp(amp, name)

        print(f"amp:{amp}")
        print(f"band:{band_width_bin}")
        print(f"index:{name}")
        self.Modify_frequency(band_width_bin, modified_amp, fs)

    def adjust_sliders(self,modified_amp,mode):
        amp = 1
        if len(self.amps_down[mode]) > 0:
            for item in self.amps_down[mode]:
                print(f"before amp:{item}")
                amp *= 1.0/ item
                print(f"amppp:{amp}")
                print(f"amp2:{float(amp * modified_amp)}")
            self.amps_down[mode] = []
            return float(amp * modified_amp)
        elif  len(self.amps_up[mode]) > 0:
            for item in self.amps_up[mode]:
                amp *= 1.0/ item
            self.amps_up[mode] = []

            return float(amp * modified_amp)
        else:
            return modified_amp

    def assign_amp(self,amp,mode):
        if amp < 1.0:
            self.amps_down[mode].append(amp)
        else:
            self.amps_up[mode].append(amp)

    def Modify_frequency(self, band_width, modified_amp, fs=44100):
        print(f"amp:{modified_amp}")
        self.modified_signal = True
        # self.times_of_modified += 1
        if len(self.modified_signal_after_inverse) > 1:
            data = self.modified_signal_after_inverse
        else:

            data = self.data_original


        # print(f"freq:{max(frequencies)}")
        band_index_pos = np.logical_and(self.frequencies >= band_width[0], self.frequencies <= band_width[1])
        band_index_negv = np.logical_and(self.frequencies >= band_width[3], self.frequencies <= band_width[2])

        self.modified_signal_list[band_index_pos] = modified_amp * self.modified_signal_list[band_index_pos]
        self.modified_signal_list[band_index_negv] = modified_amp * self.modified_signal_list[band_index_negv]

        self.modified_signal_after_inverse = ifft(self.modified_signal_list)
        print(f"modify_data:{self.modified_signal_after_inverse}")
        self.modified_signal_after_inverse = np.array(self.modified_signal_after_inverse.real)

        self.create_frequency_spectrum(self.modified_signal_after_inverse)
        QCoreApplication.processEvents()
        if self.mode == 2:
            self.arrhythima()
        else:
            self.Write_modified_signal(self.modified_signal_after_inverse)



    def Fourier_Transform(self, data, sr=44100):
        signal = fft(data)
        print(f"fs:{sr}")
        frequencies_bin = fftfreq(len(signal), 1 / sr)
        amplitudies = np.abs(signal)
        return frequencies_bin, amplitudies, signal




    def plot_windowing(self,sigma): ## comment
        print("arrived")
        # self.ax_frequecies.clear()
        QCoreApplication.processEvents()
        data_pos,data_negv,frequencies, amplitudes = self.append_data_band()
        for item_data, amp_band in zip(self.frequencies, amplitudes):
            # print(f"len_window:{len(window)},len_data:{len(item)}")
            # print(f"item:{item}")
            # window = self.padding(window_data, len(item))
            print("yyyyyyyyy")
            window_size = len(item_data)
            # QCoreApplication.processEvents()

            window = self.windows[self.window_name](window_size, sigma)
            # QCoreApplication.processEvents()
            # print(f"len_window:{len(window)},len_data:{len(item)}")
            # self.axes[2].plot(item_data, 500 * window, color='r')
            self.plot(2,item_data,max(amp_band)*window,'r',self.y_min,self.y_max)
            self.figures[2].canvas.draw()

        return


    def show_sliders(self): ## comment
        self.mode_index = self.mode_options.currentIndex()
        if self.mode_index == 0:
            for uni_slider in self.uniform_sliders_list:
                uni_slider.show()
            for label in self.amp_uniform_list:
                label.show()
            for uni_label in self.uni_labels_list:
                uni_label.show()
            for music_slider in self.music_sliders_list:
                music_slider.hide()
            for label in self.amp_music_list:
                label.hide()
            for animal_slider in self.animal_sliders_list:
                animal_slider.hide()
            for animal_label in self.animal_labels_list:
                animal_label.hide()
            for label in self.amp_animal_list:
                label.hide()
            for music_label in self.music_labels_list:
                music_label.hide()
            for component in self.audio_player_components:
                component.show()
            for component in self.ecg_components:
                component.hide()
            self.mode = 3

        if self.mode_index == 1:
            for music_slider in self.music_sliders_list:
                music_slider.show()
            for music_label in self.music_labels_list:
                music_label.show()
            for label in self.amp_music_list:
                label.show()
            for uni_slider in self.uniform_sliders_list:
                uni_slider.hide()
            for label in self.amp_uniform_list:
                label.hide()
            for uni_label in self.uni_labels_list:
                uni_label.hide()
            for animal_slider in self.animal_sliders_list:
                animal_slider.hide()
            for animal_label in self.animal_labels_list:
                animal_label.hide()
            for label in self.amp_animal_list:
                label.hide()
            for component in self.ecg_components:
                component.hide()
            for component in self.audio_player_components:
                component.show()
            self.mode = 1

        if self.mode_index == 2:
            for slider in self.animal_sliders_list:
                slider.show()
            for animal_label in self.animal_labels_list:
                animal_label.show()
            for label in self.amp_animal_list:
                label.show()
            for uni_slider in self.uniform_sliders_list:
                uni_slider.hide()
            for label in self.amp_uniform_list:
                label.hide()
            for uni_label in self.uni_labels_list:
                uni_label.hide()
            for music_slider in self.music_sliders_list:
                music_slider.hide()
            for label in self.amp_music_list:
                label.hide()
            for music_label in self.music_labels_list:
                music_label.hide()
            for component in self.ecg_components:
                component.hide()
            for component in self.audio_player_components:
                component.show()
            self.mode = 0

        if self.mode_index == 3:
            for component in self.ecg_components:
                component.show()
            for component in self.audio_player_components:
                component.hide()
            for uni_slider in self.uniform_sliders_list:
                uni_slider.hide()
            for uni_label in self.uni_labels_list:
                uni_label.hide()
            for label in self.amp_uniform_list:
                label.hide()
            for music_slider in self.music_sliders_list:
                music_slider.hide()
            for label in self.amp_music_list:
                label.hide()
            for label in self.amp_animal_list:
                label.hide()
            for animal_slider in self.animal_sliders_list:
                animal_slider.hide()
            for animal_label in self.animal_labels_list:
                animal_label.hide()
            for music_label in self.music_labels_list:
                music_label.hide()
            self.mode = 2
            # self.ecg()

    def arrhythima(self):
        self.axes[1].cla()
        fs = 360
        self.plot_spectrogram(fs)
        self.plot(1, self.time, self.modified_signal_after_inverse, 'r', min(self.data_original)
                  , max(self.data_original))
        # sf.write(r"C:\Users\lama zakaria\Desktop\Equalizer\APC_New.wav",self.modified_signal_after_inverse,samplerate=fs,subtype='FLOAT')
        self.create_frequency_spectrum(self.modified_signal_after_inverse, 360)


    def ecg(self, file_path):
        data = self.load_data(file_path, 360)
        self.data_original = data
        fs = 360
        self.create_frequency_spectrum(self.data_original, 360)
        self.axes[0].cla()
        self.plot_spectrogram(fs)
        self.plot(0, self.time, self.data_original, 'b', min(self.data_original)
                  , max(self.data_original))

    def delete(self):
        if self.times_of_modified >= 1:
            print("file is deleted")
            print(f"frames:{self.no_of_frames,self.i}")
            if self.i < self.no_of_frames - 1:
                self.ani_1.pause()
            self.no_of_points = 1000
            self.uesd_window = False
            self.changed_data = False
            self.set_audio(file_path=None, player=1)
            self.set_audio(file_path=None, player=2)
            self.graphs[0].scene().clear()
            self.graphs[2].scene().clear()
            self.times_of_modified = 0
            if len(self.modified_signal_after_inverse) > 1:
                self.modified_signal_after_inverse = []
                if self.i < self.no_of_frames - 1:
                    self.ani_2.pause()

                self.graphs[1].scene().clear()

    def Zoom_out(self):
        y_min, y_max = self.axes[0].get_ylim()
        y_min -= 0.01
        y_max += 0.01
        self.draw(y_min, y_max)

    def Zoom_in(self):
        y_min, y_max = self.axes[0].get_ylim()
        y_min += 0.01
        y_max -= 0.01
        self.draw(y_min, y_max)

    def draw(self, y_min, y_max):
        self.axes[0].set_ylim(y_min, y_max)
        self.axes[1].set_ylim(y_min, y_max)
        # canvas refers to the area where the figure and its subplots are drawn
        self.figures[0].canvas.draw()
        self.figures[1].canvas.draw()

    def toggle_channel_animation(self):  # to play /stop animation
        if self.graph_btn_play.text() == "►":
            self.play_animation = True
            print(f"animation is played")
            self.graph_btn_play.setText("❚❚")
            self.ani_1.event_source.start()
            # if len(self.modified_signal_after_inverse) > 1:
            #     print("Nakusa")
            #     self.ani_2.event_source.start()
            shortcut1 = QShortcut(QKeySequence('Ctrl+P'), self)
            shortcut1.activated.connect(self.graph_btn_play.click)
        else:
            self.play_animation = False
            self.graph_btn_play.setText("►")
            self.ani_1.event_source.stop()
            print(f"animation is paused")
            # if len(self.modified_signal_after_inverse) > 1:
            #     self.ani_1.event_source.stop()
            #     self.ani_2.event_source.stop()
            shortcut1 = QShortcut(QKeySequence('Ctrl+P'), self)
            shortcut1.activated.connect(self.graph_btn_play.click)

    def pan(self):
        self.figures[0].canvas.mpl_connect('button_press_event', self.buttonZemaphore)
        self.figures[0].canvas.mpl_connect('button_release_event', self.buttonZemaphore)
        self.figures[0].canvas.mpl_connect('motion_notify_event', self.pan_fun)

    def buttonZemaphore(self, event):
        # changing the flags for panning
        if (event.name == 'button_press_event') and (event.button.numerator == 1):
            # left-mouse button press: activate pan
            self.oldxy = [event.xdata, event.ydata]
            self.panningflag = 1
        elif (event.name == 'button_release_event') and (event.button.numerator == 1):
            # left-mouse button release: deactivate pan
            self.panningflag = 0

    def pan_fun(self, event):
        # drag-panning the axis
        # This function has to be efficient, as it is polled often.
        if (self.panningflag == 1) and (event.inaxes is not None):
            self.pan_ch1 = True
            # do pan
            self.axes[0] = event.inaxes  # set the axis to work on
            x, y = event.xdata, event.ydata
            print(self.oldxy[0], self.oldxy[1])
            print(f"x,y:{x, y}")
            print(f"limits:{self.axes[0].get_xlim()}")
            x_min, x_max = self.axes[0].get_xlim() + self.oldxy[0] - x
            y_min, y_max = self.axes[0].get_ylim() + self.oldxy[1] - y
            if x_min >= self.time[3] and x_max <= self.time[self.specific_row]:
                self.axes[0].set_xlim(self.axes[0].get_xlim() + self.oldxy[0] - x)
                self.axes[1].set_xlim(self.axes[0].get_xlim() + self.oldxy[0] - x)  # set new axes limits
            if y_min >= self.y_min_time and y_max <= self.y_max_time:
                self.axes[0].set_ylim(self.axes[0].get_ylim() + self.oldxy[1] - y)
                # set new axes limits
                self.axes[1].set_ylim(self.axes[0].get_ylim() + self.oldxy[1] - y)

            self.axes[1].figure.canvas.draw()
            self.axes[0].figure.canvas.draw()  # force re-draw

    def increase_speed(self):  # to increase speed
        if self.Delay_interval is None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setInformativeText("Please Upload A Signal")
            msg.show()
            msg.exec_()
        else:
            self.pause = True
            self.no_of_points += 1000

    def decrease_speed(self):  # decrease speed
        if self.Delay_interval is None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setInformativeText("Please Upload A Signal")
            msg.show()
            msg.exec_()
        else:
            self.no_of_points -= 1000
            if self.no_of_points == 0:
                self.no_of_points = 1000
            self.pause = True

    def reset(self):
        self.Reset = True
        self.changed_data = False
        self.uesd_window = False
        # self.times_of_modified = 0
        if len(self.modified_signal_after_inverse) > 1:
            self.ani_2.pause()
            self.graphs[1].scene().clear()
            self.set_audio(file_path=None, player=2)
        self.modified_signal_after_inverse = []
        self.graphs[2].scene().clear()
        self.set_audio(file_path=self.path_original_data, player=1)
        self.Read_signal(self.path_original_data)
        # audio_progress.setValue(0)

    def draw_rectangular_selection(self,eclick,erelease):
        # if self.selected:
        #     self.selected_rectangle.remove()
        #     self.selected = False
        #
        #
        # x1, y1 = eclick.xdata, eclick.ydata
        # x2, y2 = erelease.xdata, erelease.ydata
        # self.selected_rectangle = plt.Rectangle(
        #     (min(x1, x2), min(y1, y2)),
        #     np.abs(x1 - x2),
        #     np.abs(y1 - y2),
        #     color='r',
        #     fill=False
        # )
        # self.ax_frequecies.add_patch(self.selected_rectangle)
        extent = self.rs.extents
        self.axes[2].set_xlim(extent[0], extent[1])
        self.selected = True


    def selection(self,event):
        if self.rs is None:
            # Create RectangleSelector if it doesn't exist
            self.rs = RectangleSelector(
                self.axes[2],
                self.draw_rectangular_selection,
                button=[1],
                minspanx=5,
                minspany=5,
                spancoords="data"
            )
            print("RectangleSelector created")
        else:
            print("RectangleSelector already exists")

        self.figures[2].canvas.draw()

        # self.draw_rectangular_selection()
        print(self.rs)
    def backward_changes(self):
        self.axes[2].set_xlim(self.x_min, self.x_max)

        self.figures[2].canvas.draw()

    def check_type_window(self):
        window_name = self.comboBox_windowing.currentText()
        return window_name


    def append_data_band(self):
        self.uesd_window = True
        data_band = self.declaretion_mode(self.mode)
        data_bands_negv, data_bands_pos, self.frequencies, self.amplitudes = [], [], [], []
        for item, value in data_band.items():
            self.uesd_window = True
            data_band_neqv, data_band_pos, frequency, amplitude = self.get_data_band(value)
            print(f"data_band:{data_band_pos}")
            self.frequencies.append(frequency)
            self.amplitudes.append(amplitude)
            data_bands_negv.append(data_band_neqv)
            data_bands_pos.append(data_band_pos)
        return data_bands_negv, data_bands_pos, self.frequencies,self.amplitudes
    def get_information_data(self):
        if len(self.modified_signal_after_inverse) > 1:
            return len(self.modified_signal_after_inverse), self.modified_signal_after_inverse
        else:
            return len(self.data_original), self.data_original

    def hamming(self,window_size,sigma):
        window = np.hamming(window_size)
        return window
    def hanning(self,window_size,sigma):
        window = np.hanning(window_size)
        return window
    def rectangular(self,window_size,sigma):
        window = np.ones(window_size)
        return window
    def gaussian(self,window_size,sigma):
        window = signal.windows.gaussian(window_size, std=sigma)
        return window

    def windowing(self, window_name,sigma=0.1): ## comment
        self.Windowing = True
        self.changed_data = True
        self.window_name = window_name
        self.counter_window +=1

        if self.window_name == "No Window":
            self.changed_data = False
            self.counter_window  = 0

        print("arrived1")
        # data_band = self.declaretion_mode(self.mode)
        data_bands_negv, data_bands_pos, self.frequencies, amplitudes = self.append_data_band()
        # for item, value in data_band.items():
        #     self.uesd_window = True
        #     data_band_neqv, data_band_pos, frequency, amplitude = self.get_data_band(value)
        #     print(f"data_band:{data_band_pos}")
        #     self.frequencies.append(frequency)
        #     self.amplitudes.append(amplitude)
        #     data_bands_negv.append(data_band_neqv)
        #     data_bands_pos.append(data_band_pos)

        print("arrived2")
        window_result = self.split_window_to_bands(window_name,sigma,data_bands_pos, data_bands_negv)
        print("arrived7")
        print(window_result)
        data_after_windowing = ifft(window_result)
        data_after_windowing = np.array(data_after_windowing.real)
        self.Write_modified_signal(data_after_windowing)
        self.axes[2].cla()
        if self.counter_window < 2:
            self.create_frequency_spectrum(data_after_windowing, sigma)

        QCoreApplication.processEvents()
        # self.plot_windowing(window_name, sigma, frequencies)

        print("arrived5")

    def padding(self, window, padding_size):
        window = np.concatenate([window, np.zeros(padding_size - len(window))])
        return window



    def padding_ones(self,padding_data,padding_size):
        padding_data = np.concatenate([padding_data,np.ones(padding_size)])
        return padding_data

    def split_window_to_bands(self, window_name, sigma,data_bands_pos, data_bands_negv):
        data_pos_after_multiplication = []
        data_negv_after_multiplication = []


        for data_pos, data_negv in zip(data_bands_pos, data_bands_negv):
            window_size = len(data_pos)
            window = self.windows[window_name](window_size, sigma)
            self.data_of_window.append(window)
            print(f"pos:{len(data_pos)},negv:{len(data_negv)}")
            data_pos_after_multiplication.append(data_pos * window)
            data_negv_after_multiplication.append(data_negv * window)
        print(f"conv:{data_pos_after_multiplication}")
        data_after_multiplication = np.concatenate([np.concatenate(data_pos_after_multiplication),
                                                 np.concatenate(data_negv_after_multiplication)
                                                 ])

        return data_after_multiplication

    def get_data_band(self, bands):
        data_length, data = self.get_information_data()
        # frequencies, amplitudes, data = self.Fourier_Transform(data)
        print(f"band:{bands}")
        band_index_pos = np.logical_and(self.frequencies >= bands[0], self.frequencies <= bands[1])
        band_index_negv = np.logical_and(self.frequencies >= bands[3], self.frequencies <= bands[2])
        print(f"ddd:{data[band_index_pos]}")
        return data[band_index_negv], data[band_index_pos], self.frequencies[band_index_pos],self.amplitudes[band_index_pos]



def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
    