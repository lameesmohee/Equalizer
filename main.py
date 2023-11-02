import math
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from os import path
import sys
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
        self.ecg_slider.hide()
        self.show_sliders()
        self.media_player = QMediaPlayer()
        self.handle_buttons()

    def handle_buttons(self):
        self.mode_options.currentIndexChanged.connect(self.show_sliders)
        self.actionUpload.triggered.connect(self.add_audio)
        self.play_pause_audio_button.clicked.connect(self.play_pause_audio)
        self.media_player.positionChanged.connect(self.set_audio_position)

    def play_pause_audio(self):
        # Toggling the Play and Pause for the audio
        if self.play_pause_audio_button.text() == "►":
            self.play_pause_audio_button.setText('❚❚')
            self.media_player.play()
        else:
            self.play_pause_audio_button.setText('►')
            self.media_player.pause()

    def set_audio_position(self, position):
        # Connecting the media player to the progress slider
        if self.audio_progress.maximum() != self.media_player.duration():
            self.audio_progress.setMaximum(self.media_player.duration())
        self.audio_progress.setValue(position)

    def add_audio(self):
        # Reading the audio
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", os.path.expanduser("~"),
                                                   "Audio Files (*.mp3 *.wav)")
        if self.file_path:
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.file_path)))
            self.media_player.play()
            self.play_pause_audio_button.setText('❚❚')

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