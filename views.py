import numpy as np

from datetime import datetime
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QApplication, QSlider, QLabel, QGridLayout, QFormLayout, QSpinBox
from pyqtgraph import ImageView, PlotWidget, plot


class StartWindow(QMainWindow):
    def __init__(self, camera = None, daq = None):
        super().__init__()
        self.camera = camera
        self.daq = daq
        self.central_widget = QWidget()
        self.button_start = QPushButton('Start DAQ', self.central_widget)
        self.button_save = QPushButton('Save DAQ', self.central_widget)
        self.button_save.setCheckable(True)
        self.button_save.setStyleSheet("QPushButton:checked {color: white; background-color: green;}")
        self.button_start.setCheckable(True)
        self.button_start.setStyleSheet("QPushButton:checked {color: white; background-color: green;}")
        self.graphwidget = PlotWidget()


        self.feedlabel = QLabel(self.central_widget)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0,128)
        self.main_layout = QGridLayout(self.central_widget)
        self.configuration_layout = QFormLayout()
        self.number_of_samples = QSpinBox()
        self.sampling_rate = QSpinBox()
        self.delay = QSpinBox()
        self.number_of_samples.setRange(0,1000000)
        self.sampling_rate.setRange(0,1000000)
        self.delay.setRange(-1000000,1000000)
        self.number_of_samples.setValue(1000)
        self.sampling_rate.setValue(200)
        self.delay.setValue(0)
        self.configuration_layout.addRow(QLabel("Number of Samples"), self.number_of_samples)
        self.configuration_layout.addRow(QLabel("Sampling Rate (Hz)"), self.sampling_rate)
        self.configuration_layout.addRow(QLabel("Delay (No of Samples)"), self.delay)
        self.layout = QVBoxLayout(self.central_widget)
        self.button_layout = QHBoxLayout(self.central_widget)
        self.button_layout.addWidget(self.button_start)
        self.button_layout.addWidget(self.button_save)
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.feedlabel)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.graphwidget)

        self.main_layout.addLayout(self.layout,1,2)
        self.main_layout.addLayout(self.configuration_layout,1,1)
        self.setCentralWidget(self.central_widget)

        self.button_start.clicked.connect(self.start_daq)
        self.button_save.clicked.connect(self.save_data)
        self.slider.valueChanged.connect(self.update_brightness)
        self.daq_thread = DAQThread(self.daq)
        self.plot_curve = self.graphwidget.plot(range(1000))
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_image)
        self.daq_thread.signal.connect(self.update_graph)
        self.update_timer.start()


    def start_daq(self):
        if self.button_start.isChecked():
            self.daq_thread.set_config(self.number_of_samples.value(),self.sampling_rate.value(),self.delay.value())
            self.daq_thread.set_save_time()
            self.daq_thread.start()
        else:
            self.daq_thread.stop()


    def save_data(self):
        if self.button_save.isChecked():
            self.daq_thread.set_save_time()
            self.daq_thread.ifSave = True
        else:
            self.daq_thread.ifSave = False

        

    def update_image(self):
        frame = self.camera.get_frame()
        qimage =QImage(frame.data,frame.shape[1],frame.shape[0],QImage.Format_RGB888)
        self.feedlabel.setPixmap(QPixmap.fromImage(qimage))

    def update_graph(self):
        self.plot_curve.setData(self.daq.time,self.daq.data)

    
    def read_brightness(self):
        print(self.camera.get_brightness())
    def update_brightness(self, value):
        self.camera.set_brightness(value)



class DAQThread(QThread):
    signal = pyqtSignal(object)
    def __init__(self,daq):
        super().__init__()
        self.daq = daq
        self.delay = 100
        self.data = np.zeros(self.daq.number_of_samples)
        self.ThreadActive = False
        self.ifSave = False
        self.save_time = datetime.now()
    
    def set_config(self,number_of_samples, sampling_rate, delay):
        self.daq.number_of_samples = number_of_samples
        self.daq.sampling_rate = sampling_rate
        self.daq.sampling_time = number_of_samples/sampling_rate
        self.daq.delay = delay
    
    def run(self):
        self.ThreadActive = True
        self.daq.start_measurement()
        while self.ThreadActive:
            data = self.daq.read_data()
            self.signal.emit(data)
            if self.ifSave:
                self.save()

    def set_save_time(self):
        self.save_time = datetime.now()
    
    def save(self):
        save_time = self.save_time.strftime('%Y%m%d%H%M%S')
        self.daq.save_data(save_time)

    def stop(self):
        self.ThreadActive = False
        self.daq.stop_measurement()




if __name__ == '__main__':
    app = QApplication([])
    window = StartWindow()
    window.show()
    app.exit(app.exec_())