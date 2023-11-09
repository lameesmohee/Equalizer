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
from scipy.signal import hamming
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
        self.mode_index = 0
        self.fig_original = plt.figure(figsize=(1200 / 80, 290 / 80), dpi=80)
        self.fig_modified = plt.figure(figsize=(1200 / 80, 290 / 80), dpi=80)
        self.fig_frequecies = plt.figure(figsize=(1200 / 80, 290 / 80), dpi=80)
        self.x_fig_original = []
        self.x_fig_modified = []
        self.y_fig_original = []
        self.y_fig_modified = []
        self.modified_signal = False
        self.line = None
        # self.line2 = None
        self.ani_2 = None
        self.ani_1 = None
        self.specific_row = 0
        self.index = 0
        self.data_original = None
        self.sampling_rate = 0
        self.n_samples = 0
        self.type_data = 0
        self.ecg_slider.hide()
        self.show_sliders()
        self.media_player = QMediaPlayer()
        self.media_player_modified_signal = QMediaPlayer()
        self.handle_buttons()

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
        self.animal_slider1.valueChanged.connect(lambda: self.band_width('elephant'))
        QCoreApplication.processEvents()
        self.Timer = QTimer(self)

    def play_pause_audio(self,button_name):
        # Toggling the Play and Pause for the audio
        if button_name == self.play_pause_audio_button                                           :
            if self.play_pause_audio_button.text() == "►":
                self.play_pause_audio_button.setText('❚❚')
                self.ani_1.event_source.start()
                self.media_player.play()
            else:
                self.play_pause_audio_button.setText('►')
                self.ani_1.event_source.stop()
                self.media_player.pause()

        else:
            if self.play_pause_audio_button_2.text() == "►":
                self.play_pause_audio_button_2.setText('❚❚')
                self.ani_2.event_source.start()
                self.media_player_modified_signal.play()
            else:
                self.play_pause_audio_button_2.setText('►')
                self.ani_2.event_source.stop()
                self.media_player_modified_signal.pause()




    def set_audio_position(self,media_name,audio_progress):
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
            self.play_pause_audio_button.setText('❚❚')

    def Write_modified_signal(self,modified_signal):
        # "C:\Users\lama zakaria\Desktop\Equalizer\animalsSounds.wav"
        directory_path = os.path.dirname(self.file_path)
        file_path = str(self.file_path)
        print(f"file:{file_path}")
        file_path = file_path.split('/')[-1].split('.')[0] + "modified.wav"
        file_path = directory_path + '/' +file_path
        print(f"file:{file_path}")
        data = wave.open(file_path, mode='wb')
        fs = self.sampling_rate
        data.setnchannels(1)
        data.setsampwidth(self.type_data)
        data.setframerate(fs)
        data.setnframes(self.n_samples)
        data.writeframes(modified_signal)

        data.close()
        self.modified_signal = True
        self.media_player_modified_signal.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        self.media_player_modified_signal.play()
        self.play_pause_audio_button_2.setText('❚❚')
        self.play_pause_audio_button.setText('►')
        self.media_player.pause()


        self.Read_signal(file_path)



    def Read_signal(self, file_path):

        data = wave.open(file_path, mode='rb')

        data_signal = data.readframes(-1)

        self.type_data = data.getsampwidth()
        print(f"type:{self.type_data}")
        self.n_samples = data.getnframes()
        print(f"n_samples:{self.n_samples,data.getnchannels()}")
        length_data = self.n_samples
        data_signal = np.frombuffer(data_signal, dtype="int"+str(self.type_data*8))
        self.sampling_rate = data.getframerate()
        if self.modified_signal:
            print(f"fileeeeeeeee:{file_path}")
            self.ax_modified = self.fig_modified.add_subplot(111)
            self.Plot(data_signal, self.sampling_rate, length_data, self.ax_modified,self.animate_fig_modified)
        else:
            self.data_original =  data_signal
            self.ax_original = self.fig_original.add_subplot(111)
            self.Plot(data_signal, self.sampling_rate, length_data, self.ax_original,self.animate_fig_original)




    def animate_fig_original(self, i, length_data, data):
        if self.modified_signal:
            self.ani_1.event_source.stop()
            no_of_frames = int(np.floor(length_data) / 1000)
            self.ani_1 = FuncAnimation(self.fig_original, self.animate_fig_original, interval=0,
                                       frames=no_of_frames, repeat=False, fargs=(length_data, data))
            self.specific_row = 0
            self.y_fig_original = []
            self.x_fig_original =[]
            # self.modified_signal = False

        # print(f"leng:{length_data}")
        self.specific_row += 1000


        # if self.media_player.state() == QMediaPlayer.StoppedState :
        #     self.media_player.play()
        if self.specific_row <= length_data-1:
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
                self.ax_original.set_xlim(self.time[self.specific_row - 1990], self.time[self.specific_row])
            return self.line1,
        else:
            return


    def animate_fig_modified(self, i, length_data, data):
        print(f"leng:{length_data}")
        # self.specific_row += 1000
        self.modified_signal = False
        if self.specific_row <= length_data-1:
            # print(f"data:{data[self.specific_row]}")
            # print(f".specific_row:{self.specific_row}")
            data_array = np.array(data)
            time_array = np.array(self.time)

            # Slice the arrays
            data_sliced = data_array[:self.specific_row]
            time_sliced = time_array[:self.specific_row]
            self.y_fig_modified, self.x_fig_modified = data_sliced.tolist(), time_sliced.tolist()

            self.line2.set_data(self.x_fig_modified, self.y_fig_modified)

            # print(f"runtime:{(end - self.start) * 1000}")
            if self.specific_row > 1000:
                # self.index += 1200
                self.ax_modified.set_xlim(self.time[self.specific_row - 1990], self.time[self.specific_row])
            return self.line2,
        else:
            return


    def Plot(self, data, sampling_rate, length_data,axes,animation_func):
        no_of_points = length_data
        # self.data = data
        # print(self.data[:10])
        print(f"len:{min(data),max(data)}")
        end_time = int(np.floor(no_of_points/sampling_rate))
        # no_of_frames =int(np.floor(length_data/8000)-2)
        no_of_frames = int(np.floor(length_data)/1000)
        # no_of_frames = length_data
        print(f"endtime:{end_time,sampling_rate,len(data)}")
        # Delay_interval = (1/sampling_rate)* 1000
        Delay_interval = 0
        # print(Delay_interval)
        self.time = np.linspace(0, end_time, no_of_points)
        axes.set_position([0.05, 0.24, 0.75, 0.65])
        axes.set_xlim(0, self.time[1000])
        axes.set_ylim(min(data), max(data))

        scene = QtWidgets.QGraphicsScene()
        QCoreApplication.processEvents()
        if self.modified_signal:
            print("hallllo")
            # self.ax_modified.set_position([0.05, 0.24, 0.75, 0.65])
            # self.ax_modified.set_xlim(0, self.time[1000])
            # self.ax_modified.set_ylim(min(data), max(data))

            self.line2, = self.ax_modified.plot([], [], color='r')

            self.ani_2 = FuncAnimation( self.fig_modified, animation_func, interval=Delay_interval,
                                       frames=no_of_frames, repeat=False, fargs=(length_data, data))
            QCoreApplication.processEvents()


            # scene2= QtWidgets.QGraphicsScene()
            canvas = FigureCanvasQTAgg(self.fig_modified)
            self.graphicsView_modified.setScene(scene)
            scene.addWidget(canvas)


        else:

            QCoreApplication.processEvents()
            self.line1, = self.ax_original.plot([], [], color='b')
            self.ani_1 = FuncAnimation( self.fig_original, animation_func, interval=Delay_interval,
                                       frames=no_of_frames, repeat=False, fargs=(length_data, data))


            canvas_1 = FigureCanvasQTAgg(self.fig_original)
            QCoreApplication.processEvents()
            self.graphicsView_original.setScene(scene)
            scene.addWidget(canvas_1)



    def band_width(self,name):
        band_width = []
        if name == "elephant":
            band_width =[-1000,1000]
            amp = int(self.animal_slider1.value())
            print(f"amp:{amp}")
            self.Modify_frequency(band_width,amp)





    def Modify_frequency(self,band_width,modified_amp):
        print(f"amp:{modified_amp}")
        self.modified_signal =True
        # w = np.hanning(self.n_samples)
        # windowed_signal = self.data_original * w
        # modified_signal = self.data_original.copy() ## can write on array

        frequencies, amplitudes, modified_signal = self.Fourier_Transform(self.data_original)
        print(f"freq:{frequencies[19999]}")
        band_index = np.logical_and(frequencies >= band_width[0], frequencies <= band_width[1])

        modified_signal[band_index] = 0.5 * modified_signal[band_index]

        modified_signal_after = ifft(modified_signal)
        print(f"modify_data:{modified_signal_after}")
        new_data = np.array(modified_signal_after, dtype="int16")




        self.Write_modified_signal(new_data)


    def Fourier_Transform(self,data):
        signal = fft(data)
        frequencies = fftfreq(len(signal), 1/self.sampling_rate)
        amplitudies = np.abs(signal)/len(signal)
        return frequencies, amplitudies, signal


    def Plot_frequency_spectrum(self,signal):
        frequencies, amplitudes ,signal = self.Fourier_Transform(signal)
        self.ax_frequecies = self.fig_frequecies.add_subplot(111)
        self.ax_original.set_position([0.05, 0.24, 0.75, 0.65])
        self.ax_frequecies.plot(frequencies,amplitudes,color='b')






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
            self.ecg_slider.hide()

        if self.mode_index == 2:
            for slider in self.animal_sliders_list:
                slider.show()
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


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()