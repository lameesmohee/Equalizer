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
import matplotlib.pyplot as plt
plt.style.use('ggplot')

from matplotlib.animation  import FuncAnimation
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
        self.mode_index = 0
        self.fig_original = plt.figure(figsize=(1500 / 80, 345 / 80), dpi=80)
        self.fig_modified = plt.figure(figsize=(1500 / 80, 345 / 80), dpi=80)
        self.x_fig_original = []
        self.x_fig_modified = []
        self.y_fig_original = []
        self.y_fig_modified = []
        self.line = None
        self.specific_row = 0


        self.ecg_slider.hide()
        self.show_sliders()
        self.media_player = QMediaPlayer()
        self.handle_buttons()

    def handle_buttons(self):
        self.mode_options.currentIndexChanged.connect(self.show_sliders)
        self.actionUpload.triggered.connect(self.add_audio)
        self.play_pause_audio_button.clicked.connect(self.play_pause_audio)
        self.media_player.positionChanged.connect(self.set_audio_position)
        self.Timer = QTimer(self)

    def play_pause_audio(self):
        # Toggling the Play and Pause for the audio
        if self.play_pause_audio_button.text() == "►":
            self.play_pause_audio_button.setText('❚❚')
            self.ani_1.event_source.start()
            self.media_player.play()
        else:
            self.play_pause_audio_button.setText('►')
            self.ani_1.event_source.stop()
            self.media_player.pause()

    def set_audio_position(self, position):
        print(f"pos:{position}")
        # Connecting the media player to the progress slider
        if self.audio_progress.maximum() != self.media_player.duration():
            self.audio_progress.setMaximum(self.media_player.duration())
        self.audio_progress.setValue(position)

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


    def Read_signal(self,file_path):
        data = wave.open(file_path,mode='rb')
        data_signal = data.readframes(-1)
        type_data = data.getsampwidth() * 8
        print(f"type:{type_data}")
        n_samples = data.getnframes()
        print(f"n_samples:{n_samples,data.getnchannels()}")
        length_data = n_samples
        data_signal = np.frombuffer(data_signal,dtype="int"+str(type_data))
        sampling_rate = data.getframerate()
        self.Plot(data_signal,sampling_rate,length_data)

    def animate_fig_original(self,i,length_data,data):
        print(f"leng:{length_data}")
        self.specific_row += 100
        if self.media_player.state() == QMediaPlayer.StoppedState:
            self.media_player.play()
        if self.specific_row <= length_data:
            print(f"data:{self.data[self.specific_row]}")

            print(f".specific_row:{self.specific_row}")

            self.y_fig_original, self.x_fig_original = zip(*[(item_y, item_x) for item_y, item_x in
                                                             zip(self.data[0:self.specific_row],
                                                                 self.time[0:self.specific_row])])

            # self.y_fig_original.append(self.data[self.specific_row])
            # self.x_fig_original.append(self.time[self.specific_row])
            self.ax_original.set_xlim(0, self.time[self.specific_row])

            self.line.set_data(self.x_fig_original, self.y_fig_original)
            end = time.time()
            print(f"runtime:{(end - self.start) * 1000}")

            return self.line,
        else:
            return
    def Plot(self,data,sampling_rate,length_data):

        no_of_points = length_data
        self.data = data[0::2]
        print(self.data[:10])
        print(f"len:{min(self.data),max(self.data)}")
        end_time = int(np.floor(no_of_points/sampling_rate))
        # no_of_frames =int(np.floor(length_data/8000)-2)
        no_of_frames = int(np.floor(length_data/100))
        # no_of_frames = length_data
        print(f"endtime:{end_time,sampling_rate,len(self.data)}")
        # Delay_interval = (1/sampling_rate)* 1000
        Delay_interval = int(5000/no_of_frames)
        print(Delay_interval)
        self.time = np.linspace(0,end_time,no_of_points)
        self.ax_original = self.fig_original.add_subplot(111)
        self.ax_original.set_xlim(0,end_time)
        self.ax_original.set_ylim(min(self.data),max(self.data))


        self.line, = self.ax_original.plot([],[],color='b')
        # self.Timer.timeout.connect(self.animate_fig_original)
        # self.Timer.start(Delay_interval)
        self.start = time.time()
        self.ani_1 = FuncAnimation(self.fig_original,self.animate_fig_original,interval=Delay_interval,frames=no_of_frames
                                   ,repeat=False,fargs=(length_data,self.data))

        # self.ax_original.plot(self.time,self.data)
        scene = QtWidgets.QGraphicsScene(self)
        canvas_1 = FigureCanvasQTAgg(self.fig_original)
        self.graphicsView_original.setScene(scene)
        scene.addWidget(canvas_1)

































    def show_sliders(self):
        self.mode_index = self.mode_options.currentIndex()
        if self.mode_index == 0:
            for uni_slider in self.uniform_sliders_list:
                uni_slider.show()
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
            for animal_slider in self.animal_sliders_list:
                animal_slider.hide()
            self.ecg_slider.hide()

        if self.mode_index == 2:
            for slider in self.animal_sliders_list:
                slider.show()
            for uni_slider in self.uniform_sliders_list:
                uni_slider.hide()
            for music_slider in self.music_sliders_list:
                music_slider.hide()
            self.ecg_slider.hide()

        if self.mode_index == 3:
            self.ecg_slider.show()
            for uni_slider in self.uniform_sliders_list:
                uni_slider.hide()
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