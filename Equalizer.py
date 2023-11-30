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
from scipy.fftpack import fft,fftfreq
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
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


MainUI, _ = loadUiType(path.join(path.dirname(__file__), 'equalizer.ui'))


class MainApp(QMainWindow, MainUI):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Equalizer")
        self.uniform_sliders_list = [self.uni_slider1, self.uni_slider2, self.uni_slider3, self.uni_slider4,
                                     self.uni_slider5, self.uni_slider6, self.uni_slider7, self.uni_slider8,
                                     self.uni_slider9, self.uni_slider10]
        self.music_sliders_list = [self.music_slider1, self.music_slider2, self.music_slider3, self.music_slider4]
        self.animal_sliders_list = [self.animal_slider1, self.animal_slider2, self.animal_slider3, self.animal_slider4]
        self.all_sliders_list = [self.uni_slider1, self.uni_slider2, self.uni_slider3, self.uni_slider4,
                                 self.uni_slider5, self.uni_slider6, self.uni_slider7, self.uni_slider8,
                                 self.uni_slider9, self.uni_slider10, self.music_slider1, self.music_slider2,
                                 self.music_slider3, self.music_slider4, self.animal_slider1, self.animal_slider2,
                                 self.animal_slider3, self.animal_slider4, self.ecg_slider]
        self.uni_labels_list = [self.uni_freq1, self.uni_freq2, self.uni_freq3, self.uni_freq4, self.uni_freq5,
                                self.uni_freq6, self.uni_freq7, self.uni_freq8, self.uni_freq9, self.uni_freq10]
        self.animal_labels_list = [self.owl_label, self.frog_label, self.grasshoppers_label, self.canary_label]
        self.mode_index = 0
        self.fig_original = plt.figure(figsize=(650 / 80, 450 / 80), dpi=80)
        self.fig_modified = plt.figure(figsize=(650 / 80, 450 / 80), dpi=80)
        self.fig_spectrogram_original = plt.figure(figsize=(630 / 80, 350 / 80), dpi=80)
        self.ax_original = self.fig_original.add_subplot(111)
        self.ax_modified = self.fig_modified.add_subplot(111)
        self.fig_frequecies = plt.figure(figsize=(650 / 80, 450 / 80), dpi=80)
        self.ax_modified.set_position([0.1, 0.3, 0.75, 0.65])
        self.ax_original.set_position([0.1, 0.3, 0.75, 0.65])
        self.ax_frequecies = self.fig_frequecies.add_subplot(111)
        self.ax_frequecies.set_position([0.1, 0.24, 0.75, 0.65])
        self.x_fig_original = []
        self.x_fig_modified = []
        self.y_fig_original = []
        self.y_fig_modified = []
        self.Delay_interval = 200
        self.pause = False
        self.check_ended_animation_1 =False
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
        self.ecg_slider.hide()
        self.show_sliders()
        self.no_of_points = 1000
        self.media_player = QMediaPlayer()
        self.media_player_modified_signal = QMediaPlayer()
        self.handle_buttons()
        self.styles()

    def handle_buttons(self):
        self.mode_options.currentIndexChanged.connect(self.show_sliders)
        QCoreApplication.processEvents()
        self.actionUpload.triggered.connect(self.add_audio)
        QCoreApplication.processEvents()
        self.play_pause_audio_button.clicked.connect(lambda: self.play_pause_audio(self.play_pause_audio_button))
        self.play_pause_audio_button_2.clicked.connect(lambda: self.play_pause_audio(self.play_pause_audio_button_2))
        QCoreApplication.processEvents()
        self.media_player.positionChanged.connect(lambda: self.set_audio_position(self.media_player,self.audio_progress))
        self.media_player_modified_signal.positionChanged.connect(lambda: self.set_audio_position(self.media_player_modified_signal,self.audio_progress_2))
        QCoreApplication.processEvents()
        self.graphicsView_original.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        QCoreApplication.processEvents()
        self.graphicsView_original.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        QCoreApplication.processEvents()
        self.animal_slider1.setMaximum(5)
        QCoreApplication.processEvents()
        self.animal_slider1.setMinimum(0)
        QCoreApplication.processEvents()
        self.animal_slider1.valueChanged.connect(lambda: self.band_width('owl'))
        self.animal_slider2.valueChanged.connect(lambda: self.band_width('frog'))
        self.animal_slider3.valueChanged.connect(lambda: self.band_width('grasshoppers'))
        self.animal_slider4.valueChanged.connect(lambda: self.band_width('canary'))
        QCoreApplication.processEvents()
        self.ecg_slider.valueChanged.connect(self.arrhythima)
        self.graph_btn_play.clicked.connect(self.toggle_channel_animation)
        QCoreApplication.processEvents()
        self.speed_down_btn.clicked.connect(self.decrease_speed)
        QCoreApplication.processEvents()
        self.pan_btn.clicked.connect(self.pan)
        QCoreApplication.processEvents()
        self.speed_up_btn.clicked.connect(self.increase_speed)
        QCoreApplication.processEvents()
        self.zoom_in_btn.clicked.connect(self.Zoom_in)
        QCoreApplication.processEvents()
        self.zoom_out_btn.clicked.connect(self.Zoom_out)
        self.reset_btn.clicked.connect( self.reset)
        self.Timer = QTimer(self)
        self.graphicsView_windowing.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        QCoreApplication.processEvents()
        self.graphicsView_windowing.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.check_spectro.stateChanged.connect(self.check_spectro_state_changed)
        self.uni_slider1.valueChanged.connect(lambda: self.band_width('1'))
        QCoreApplication.processEvents()
        self.uni_slider2.valueChanged.connect(lambda: self.band_width('2'))
        QCoreApplication.processEvents()
        self.uni_slider3.valueChanged.connect(lambda: self.band_width('3'))
        QCoreApplication.processEvents()
        self.uni_slider4.valueChanged.connect(lambda: self.band_width('4'))
        QCoreApplication.processEvents()
        self.uni_slider5.valueChanged.connect(lambda: self.band_width('5'))
        QCoreApplication.processEvents()
        self.uni_slider6.valueChanged.connect(lambda: self.band_width('6'))
        QCoreApplication.processEvents()
        self.uni_slider7.valueChanged.connect(lambda: self.band_width('7'))
        QCoreApplication.processEvents()
        self.uni_slider8.valueChanged.connect(lambda: self.band_width('8'))
        QCoreApplication.processEvents()
        self.uni_slider9.valueChanged.connect(lambda: self.band_width('9'))
        QCoreApplication.processEvents()
        self.uni_slider10.valueChanged.connect(lambda: self.band_width('10'))
        QCoreApplication.processEvents()
        self.comboBox_windowing.currentTextChanged.connect(self.check_type_window)

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

    def add_audio(self):
        # Reading the audio
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", os.path.expanduser("~"),
                                                   "Audio Files (*.mp3 *.wav)")
        if self.file_path:
            self.x_fig_original = []
            self.time = []
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.file_path)))
            self.Read_signal(file_path=self.file_path)
            self.media_player.play()
            self.graph_btn_play.setText("❚❚")
            self.play_pause_audio_button.setText('❚❚')

    def Write_modified_signal(self, modified_signal):
        directory_path, file_name = os.path.split(self.file_path)
        file_name_without_extension, file_extension = os.path.splitext(file_name)
        # Create the full file path for the modified file

        self.Counter_file +=1
        modified_file_name = f"{file_name_without_extension}_modified_{self.Counter_file}.wav"

        # Create the full file path for the modified file
        file_path = os.path.join(directory_path, modified_file_name)

        # Write the modified signal to the new file
        try:
            # wavfile.write(file_path,self.sampling_rate,modified_signal.astype("int16"))
            # print("The Data is stored")
            with sf.SoundFile(file_path, 'w', format='wav', samplerate=self.sampling_rate, channels=1) as file:
                # Write the modified signal to the file
                file.write(modified_signal)
                print("The Data is stored")

        # Code that may cause the issue

        except Exception as e:
            print(f"Error: {e}")
        print("Modified file written to:", file_path)
        # Continue with the rest of your code
        self.modified_signal = True
        self.media_player_modified_signal.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        QCoreApplication.processEvents()
        self.media_player_modified_signal.play()
        QCoreApplication.processEvents()
        self.play_pause_audio_button_2.setText('❚❚')
        QCoreApplication.processEvents()
        self.play_pause_audio_button.setText('►')
        QCoreApplication.processEvents()
        self.media_player.pause()
        QCoreApplication.processEvents()
        self.Read_signal(file_path)

    def Read_signal(self, file_path):
        self.data_original, self.sampling_rate = librosa.load(file_path, sr=44100)
        self.data_signal = self.data_original
        print(f"sampling_rate:{self.sampling_rate}")
        end_time = librosa.get_duration(y=self.data_original, sr=self.sampling_rate)
        print(f"end_time:{end_time}")
        if  len(self.modified_signal_after_inverse) > 1:
            print(f"fileeeeeeeee:{file_path}")
            QCoreApplication.processEvents()
            self.scene2 = QtWidgets.QGraphicsScene()
            canvas = FigureCanvasQTAgg(self.fig_modified)
            self.graphicsView_modified.setScene(self.scene2)
            self.scene2.addWidget(canvas)
            # if self.check_ended_animation_1:
            #     self.specific_row = 0
            #     print(f"check:{self.check_ended_animation_1}")
            #     self.data_original = self.data_signal
            #     self.Plot(self.data_signal, self.sampling_rate, end_time, self.ax_original, self.animate_fig_original)
        else:
            self.data_original = self.data_signal
            self.Plot(self.data_signal, self.sampling_rate, end_time, self.ax_original, self.animate_fig_original)

    def check_spectro_state_changed(self, state):
        if state == 2:  # 2 corresponds to checked state
            self.plot_spectrogram(self.data_signal, self.sampling_rate)
        else:
            self.Plot(self.data_signal, self.sampling_rate, self.length_data, self.ax_original, self.animate_fig_original)

    def plot_spectrogram(self, original_audio, sampling_rate):
        f, t, Sxx = signal.spectrogram(original_audio, sampling_rate, scaling='spectrum')
        plt.pcolormesh(t, f, np.log10(Sxx))
        plt.ylabel('f [Hz]')
        plt.xlabel('t [sec]')
        scene = QtWidgets.QGraphicsScene(self)
        canvas_3 = FigureCanvasQTAgg(self.fig_spectrogram_original)
        self.graphicsView_original.setScene(scene)
        scene.addWidget(canvas_3)

    def animate_fig_original(self, i, length_data, data):
        print(f"i:{i}")
        if self.modified_signal:
            print("lamaaa")
            self.ani_1.event_source.stop()
            # self.ani_11.event_source.stop()
            # print("animation is stopped")
            no_of_frames = int(np.floor(length_data) / 1000)
            self.modified_signal = False
            if i > 0: # we can not stop animation if it does not start 
                self.ani_1 = FuncAnimation(self.fig_original, self.animate_fig_original, interval=self.Delay_interval,
                                           frames=no_of_frames, repeat=False, fargs=(length_data, data), blit=False)

            QCoreApplication.processEvents()
            self.specific_row = 0
            self.y_fig_original = []
            self.x_fig_original = []
            self.y_fig_modified = []
            self.x_fig_modified = []

            print(f"x_fig_length:{len(self.x_fig_modified)}")
            # if len(self.x_fig_modified) > 1:
            #     self.y_fig_modified = []
            #     self.x_fig_modified = []

            self.ax_frequecies.clear()
            print("lllll")
            self.line2, = self.ax_modified.plot([], [], color='r')
            QCoreApplication.processEvents()
            self.Plot_frequency_spectrum(self.modified_signal_after_inverse)
            self.ax_modified.set_ylim(min(self.modified_signal_after_inverse), max(self.modified_signal_after_inverse))
            QCoreApplication.processEvents()
            print("bbbbb")
            self.ani_2 = FuncAnimation(self.fig_modified, self.animate_fig_modified, interval=self.Delay_interval,
                                       frames=no_of_frames, repeat=False, fargs=(len(self.modified_signal_after_inverse), self.modified_signal_after_inverse), blit=False)
            print("lkkkk")
            QCoreApplication.processEvents()

        self.specific_row += self.no_of_points
        if self.specific_row <= length_data - 1:
            self.check_ended_animation_1 = False
            # print(f"no of points{self.no_of_points,self.specific_row}")
            # print(f"data:{data[self.specific_row]}")
            # print(f".specific_row:{self.specific_row}")
            data_array = np.array(data)
            time_array = np.array(self.time)
            # Slice the arrays
            data_sliced = data_array[:self.specific_row]
            time_sliced = time_array[:self.specific_row]
            self.y_fig_original, self.x_fig_original = data_sliced.tolist(), time_sliced.tolist()
            self.line1.set_data(self.x_fig_original, self.y_fig_original)
            if self.specific_row > 1000:
                self.ax_original.set_xlim(self.time[self.specific_row - 1000], self.time[self.specific_row])
        else:
            self.check_ended_animation_1 = True

        return self.line1,

    def animate_fig_modified(self, i, length_data, data):
        print("Hate ")
        if self.specific_row <= length_data - 1:
            # print(f"data:{data[self.specific_row]}")
            # print(f".specific_row_2:{self.specific_row}")
            data_array = np.array(data)
            time_array = np.array(self.time)
            # print("animation 2 is started")

            # Slice the arrays
            data_sliced = data_array[:self.specific_row]
            time_sliced = time_array[:self.specific_row]
            self.y_fig_modified, self.x_fig_modified = data_sliced.tolist(), time_sliced.tolist()
            # self.ax_modified.clear()
            # self.ax_modified.plot(self.x_fig_modified, self.y_fig_modified)
            self.line2.set_data(self.x_fig_modified, self.y_fig_modified)

            # print(f"runtime:{(end - self.start) * 1000}")
            if self.specific_row > 1000:
                # self.index += 1200
                self.ax_modified.set_xlim(self.time[self.specific_row - 1000], self.time[self.specific_row])

        return self.line2,

    def Plot(self, data, sampling_rate, end_time, axes, animation_func):
        no_of_frames = int(np.floor(len(data)) / 1000)
        print(f"lenght:{len(data)}")
        # print(Delay_interval)
        self.time = np.linspace(0, end_time, len(data))
        QCoreApplication.processEvents()
        if len(self.modified_signal_after_inverse) > 1:
            print("hallllo")
            QCoreApplication.processEvents()
            self.scene2= QtWidgets.QGraphicsScene()
            canvas = FigureCanvasQTAgg(self.fig_modified)
            self.graphicsView_modified.setScene(self.scene2)
            self.scene2.addWidget(canvas)
        else:
            axes.set_ylim(min(data), max(data))
            QCoreApplication.processEvents()
            self.line1, = self.ax_original.plot([], [], color='b')
            self.Plot_frequency_spectrum(data)
            self.ani_1 = FuncAnimation(self.fig_original, animation_func, interval=self.Delay_interval,
                                       frames=no_of_frames, repeat=False, fargs=(len(data), data), blit=False)

            self.scene = QtWidgets.QGraphicsScene()
            canvas_1 = FigureCanvasQTAgg(self.fig_original)
            QCoreApplication.processEvents()
            self.graphicsView_original.setScene(self.scene)
            self.scene.addWidget(canvas_1)

    def band_width(self, name):
        band_width = []
        if name == "owl":
            band_width_bin = np.array([650, 950, -650, -950])
            amp = int(self.animal_slider1.value())
        if name == "frog":
            band_width_bin = np.array([950,1900, -950, -1900])
            amp = int(self.animal_slider2.value())
        if name == "grasshoppers":
            band_width_bin = np.array([6000, 30000, -6000, -30000])
            amp = int(self.animal_slider3.value())
        if name == "canary":
            band_width_bin = np.array([3000, 5500, -3000, -5500])
            amp = int(self.animal_slider4.value())

        
            # Animals mode
            # band_width_bin = np.array([650, 950, -650, -950])  # owl
            # band_width_bin = np.array([950,1900, -950, -1900]) # frog
            # band_width_bin = np.array([6000, 30000, -6000, -30000])  # grasshoppers
            # band_width_bin = np.array([3000, 5500, -3000, -5500])  # canary
            # band_width_bin = np.array([0, 1200, 0, -1200])  # xylphone
            # band_width_bin = np.array([0, 800, 0, -800]) # xylphone

            # band_width_bin = np.array([0, 1000, 0, -800])  # guitar
            # band_width_bin = np.array([500, 2700,-500, -2700])  # flute
            # band_width_bin = np.array([500, 2700,-500, -2700])  # flute
            # amp = int(self.animal_slider1.value())

            print(f"amp:{amp}")

        if name == "1":
            band_width_hz = [0, 500, 0, -500]
            amp = int(self.uni_slider1.value())

        if name == "2":
            band_width_hz = [500, 1000, -500, -1000]
            amp = int(self.uni_slider2.value())
        if name == "3":
            band_width_hz = [1000, 1500, -1000, -1500]
            amp = int(self.uni_slider3.value())
        if name == "4":
            band_width_hz = [1500, 2000, -1500, -2000]
            amp = int(self.uni_slider4.value())
        if name == "5":
            band_width_hz = [2000, 2500, -2000, -2500]
            amp = int(self.uni_slider5.value())
        if name == "6":
            band_width_hz = [2000, 2500, -2000, -2500]
            amp = int(self.uni_slider6.value())
        if name == "7":
            band_width_hz = [3000, 3500, -3000, -3500]
            amp = int(self.uni_slider7.value())
        if name == "8":
            bband_width_hz = [3500, 4000, -3500, -4000]
            amp = int(self.uni_slider8.value())
        if name == "9":
            band_width_hz = [4000, 4500, -4000, -4500]
            amp = int(self.uni_slider9.value())
        if name == "10":
            band_width_hz = [4500, 5000, -4500, -5000]
            amp = int(self.uni_slider10.value())

        print(f"length of data :{len(self.data_original)}")
        # band_width_bin = (band_width_hz * 124416) / self.sampling_rate
        # band_width_bin = (band_width_hz * 903723) / self.sampling_rate
        # band_width_bin = (band_width_hz * 617472) / self.sampling_rate
        # band_width_bin = (band_width_hz * 330750) / self.sampling_rate
        print(f"band:{band_width_bin}")
        print(f"index:{name}")
        self.Modify_frequency(band_width_bin, amp)

    def Modify_frequency(self, band_width, modified_amp):
        print(f"amp:{modified_amp}")
        self.modified_signal = True
        # w = np.hanning(self.n_samples)
        # windowed_signal = self.data_original * w
        # modified_signal = self.data_original.copy() ## can write on array
        if len(self.modified_signal_after_inverse) > 1:
            data = self.modified_signal_after_inverse
        else:
            data = self.data_original

        frequencies, amplitudes, modified_signal_list = self.Fourier_Transform(data)
        print(f"freq:{max(frequencies)}")
        band_index_pos = np.logical_and(frequencies >= band_width[0], frequencies <= band_width[1])
        band_index_negv = np.logical_and(frequencies >= band_width[3], frequencies <= band_width[2])

        modified_signal_list[band_index_pos] = 0 * modified_signal_list[band_index_pos]
        modified_signal_list[band_index_negv] = 0 * modified_signal_list[band_index_negv]

        self.modified_signal_after_inverse = ifft(modified_signal_list)
        print(f"modify_data:{self.modified_signal_after_inverse}")
        # new_data = np.array(modified_signal_after.real)
        # print(new_data)
        self.modified_signal_after_inverse = np.array(self.modified_signal_after_inverse.real)
        # self.modified_signal_after_inverse = np.array(np.abs(self.modified_signal_after_inverse))
        self.Write_modified_signal(self.modified_signal_after_inverse)
    
    def arrhythima(self):
        ecg = electrocardiogram()
        fs = 360
        time = np.arange(ecg.size) / fs
        # time = np.linespace(0,)
        rfrequency, amplitude, modified_signal_list = self.Fourier_Transform(ecg, fs)
        # self.Plot_frequency_spectrum(ecg, 360)
        # fft_file = sc.fft.rfft(ecg)
        # amplitude = np.abs(fft_file)
        phase = np.angle(modified_signal_list)
        # rfrequency = sc.fft.rfftfreq(len(ecg), 1/fs)
        value = 0
        band_index_pos = np.where((rfrequency >= 1) & (rfrequency < 5))
        band_index_neg = np.where((rfrequency >= -5) & (rfrequency < -1))
        for i in band_index_pos:
           amplitude[i] = value * amplitude[i]
        for i in band_index_neg:
            amplitude[i] = value * amplitude[i]
        # phase = np.angle(modified_signal_list)
        modified_signal_list = np.multiply(amplitude, np.exp(1j*phase))
        modified_signal_after_inverse = ifft(modified_signal_list)
        # df = pd.DataFrame({'time': time, 'amplitude': ecg,
        #                 'modified_amplitude': modified_signal_after_inverse})
        # rows_until_45sec = df.loc[df['time'] <= float(45)]
        # rows_until_51sec = df.loc[df['time'] <= float(51)]
        # df = df.loc[len(rows_until_45sec):len(rows_until_51sec)]
        self.Plot_frequency_spectrum(modified_signal_after_inverse,360)
        self.arr_scene = QtWidgets.QGraphicsScene()
        canvas_1 = FigureCanvasQTAgg(self.fig_original)
        QCoreApplication.processEvents()
        self.graphicsView_original.setScene(self.arr_scene)
        self.arr_scene.addWidget(canvas_1)
        self.ax_original.set_xlim(45, 51)
        self.ax_original.set_ylim(-2, 3.5)
        self.ax_original.plot(time, ecg, color='g')

        self.arr_scene_modified = QtWidgets.QGraphicsScene()
        canvas_2 = FigureCanvasQTAgg(self.fig_modified)
        QCoreApplication.processEvents()
        self.graphicsView_modified.setScene(self.arr_scene_modified)
        self.arr_scene_modified.addWidget(canvas_2)
        self.ax_modified.set_xlim(45, 51)
        self.ax_modified.set_ylim(-2, 3.5)
        self.ax_modified.plot(time, modified_signal_after_inverse, color='r')

        
    def Fourier_Transform(self, data, sr = 44100):
        signal = fft(data)
        print(f"fs:{sr}")
        frequencies_bin = fftfreq(len(signal), 1/sr)
        amplitudies = np.abs(signal)
        return frequencies_bin, amplitudies, signal

    def plot_windowing(self,window_data,amplitudes_in_db):
        print("arrived")
        print(f'amplitudes:{amplitudes_in_db}')
        self.ax_frequecies.plot(amplitudes_in_db, color='r')
        return

    def Plot_frequency_spectrum(self, signal,sr=44100):
        frequencies_bin, amplitudes, signal = self.Fourier_Transform(signal,sr)
        # dbs= 20 * np.log10((np.abs(amplitudes))**2)
        # dbs = librosa.amplitude_to_db(amplitudes)
        dbs = amplitudes
        # frequencies_hz = (frequencies_bin * self.sampling_rate) / 124416
        # frequencies_hz = (frequencies_bin * self.sampling_rate) / 903723
        self.scene3 = QtWidgets.QGraphicsScene()
        canvas3 = FigureCanvasQTAgg(self.fig_frequecies)
        self.graphicsView_windowing.setScene(self.scene3)
        self.scene3.addWidget(canvas3)
        if len(self.modified_signal_after_inverse) < 1:
            print("HALLO")
            self.y_min, self.y_max = min(dbs),max(dbs)
        self.ax_frequecies.set_ylim(self.y_min, self.y_max)
        self.ax_frequecies.plot(frequencies_bin, dbs, color='g')
        return

    def show_sliders(self):
        self.mode_index = self.mode_options.currentIndex()
        if self.mode_index == 0:
            for uni_slider in self.uniform_sliders_list:
                uni_slider.show()
            for uni_label in self.uni_labels_list:
                uni_label.show()
            for music_slider in self.music_sliders_list:
                music_slider.hide()
            for animal_slider in self.animal_sliders_list:
                animal_slider.hide()
            for animal_label in self.animal_labels_list:
                animal_label.hide()
            self.ecg_slider.hide()

        if self.mode_index == 1:
            for music_slider in self.music_sliders_list:
                music_slider.show()
            for uni_slider in self.uniform_sliders_list:
                uni_slider.hide()
            for uni_label in self.uni_labels_list:
                uni_label.hide()
            for animal_slider in self.animal_sliders_list:
                animal_slider.hide()
            for animal_label in self.animal_labels_list:
                animal_label.hide()
            self.ecg_slider.hide()

        if self.mode_index == 2:
            for slider in self.animal_sliders_list:
                slider.show()
            for animal_label in self.animal_labels_list:
                animal_label.show()
            for uni_slider in self.uniform_sliders_list:
                uni_slider.hide()
            for uni_label in self.uni_labels_list:
                uni_label.hide()
            for music_slider in self.music_sliders_list:
                music_slider.hide()
            self.ecg_slider.hide()

        if self.mode_index == 3:
            self.ecg_slider.show()
            for uni_slider in self.uniform_sliders_list:
                uni_slider.hide()
            for uni_label in self.uni_labels_list:
                uni_label.show()
            for music_slider in self.music_sliders_list:
                music_slider.hide()
            for animal_slider in self.animal_sliders_list:
                animal_slider.hide()
            for animal_label in self.animal_labels_list:
                animal_label.hide()

    def Zoom_out(self):
        y_min, y_max = self.ax_original.get_ylim()
        y_min -= 0.05
        y_max += 0.05
        self.draw(y_min, y_max)

    def Zoom_in(self):
        y_min, y_max = self.ax_original.get_ylim()
        y_min += 0.05
        y_max -= 0.05
        self.draw(y_min, y_max)

    def draw(self, y_min, y_max):
        self.ax_original.set_ylim(y_min, y_max)
        self.ax_modified.set_ylim(y_min, y_max)
        # canvas refers to the area where the figure and its subplots are drawn
        self.fig_original.canvas.draw()
        self.fig_modified.canvas.draw()

    def toggle_channel_animation(self):  # to play /stop animation
        if self.graph_btn_play.text() == "►":
            self.play_animation = True

            print(f"animation is played")
            self.graph_btn_play.setText("❚❚")
            self.ani_1.event_source.start()
            if len(self.modified_signal_after_inverse) > 1:
                self.ani_2.event_source.start()
            shortcut1 = QShortcut(QKeySequence('Ctrl+P'), self)
            shortcut1.activated.connect(self.graph_btn_play.click)
        else:
            self.play_animation = False
            self.graph_btn_play.setText("►")
            self.ani_1.event_source.stop()
            print(f"animation is paused")
            if len(self.modified_signal_after_inverse) > 1:
                self.ani_1.event_source.stop()
                self.ani_2.event_source.stop()
            shortcut1 = QShortcut(QKeySequence('Ctrl+P'), self)
            shortcut1.activated.connect(self.graph_btn_play.click)

    def pan(self):
        self.fig_original.canvas.mpl_connect('button_press_event', self.buttonZemaphore)
        self.fig_original.canvas.mpl_connect('button_release_event', self.buttonZemaphore)
        self.fig_original.canvas.mpl_connect('motion_notify_event', self.pan_fun)

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
            self.ax_original = event.inaxes  # set the axis to work on
            x, y = event.xdata, event.ydata
            print(self.oldxy[0], self.oldxy[1])
            print(f"x,y:{x, y}")
            print(f"limits:{self.ax_original.get_xlim()}")
            x_min, x_max = self.ax_original.get_xlim() + self.oldxy[0] - x
            y_min, y_max = self.ax_original.get_ylim() + self.oldxy[1] - y
            if x_min >= self.time[3] and x_max <= self.time[self.specific_row]:
                self.ax_original.set_xlim(self.ax_original.get_xlim() + self.oldxy[0] - x)
                self.ax_modified.set_xlim(self.ax_original.get_xlim() + self.oldxy[0] - x)  # set new axes limits
            if y_min >= -1 and y_max <= 1:
                self.ax_original.set_ylim(self.ax_original.get_ylim() + self.oldxy[1] - y)
                # set new axes limits
                self.ax_modified.set_ylim(self.ax_original.get_ylim() + self.oldxy[1] - y)

            self.ax_modified.figure.canvas.draw()
            self.ax_original.figure.canvas.draw()   # force re-draw

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
        pass

    def check_type_window(self):
        window_name = self.comboBox_windowing.currentText()
        self.windowing(window_name, window_size=60)


    def get_information_data(self):
        if len(self.modified_signal_after_inverse) > 1:
            return len(self.modified_signal_after_inverse), self.modified_signal_after_inverse
        else:
            return len(self.data_original), self.data_original

    def windowing(self,window_name,window_size,sigma=0.1):
        self.Windowing =True
        padding_size, data = self.get_information_data()
        if window_name == "Hamming":
            window = np.hamming(window_size)
        if window_name == "Hanning":
            window = np.hanning(window_size)
        if window_name == "Rectagular":
            window = np.ones(window_size)
        if window_name == "Gaussian":
            window =signal.windows.gaussian(window_size, std=sigma)

        print("arrived1")

        window_after_padding = np.concatenate([window, np.zeros(padding_size - window_size)])

        frequencies, amplitudes, window_transform = self.Fourier_Transform(window_after_padding,1)
        amplitudes = np.abs(fftshift(window_transform / abs(window_transform ).max())) #fftshift => Shift the zero-frequency component to the center of the spectrum
        self.plot_windowing(window_after_padding,amplitudes)
        print("arrived2")
        data_length,data = self.get_information_data()
        frequencies, amplitudes, data = self.Fourier_Transform(data)
        print("arrived5")
        data_after_windowing = self.convolution(window_transform, data)
        self.data_original = data_after_windowing


    def convolution(self, window_transform, modified_data):
        print("arrived6")
        # print(window_transform)
        # print(modified_data)
        try:
            window_result = np.convolve(window_transform, modified_data, mode='full')
            print(window_result)
            print("arrived3")
            print(window_result)
            data_after_windowing = ifft(window_result)
        except Exception as e:
            print("An error occurred:", e)
            data_after_windowing = None

        print("arrived4")
        # return data_after_windowing

def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()