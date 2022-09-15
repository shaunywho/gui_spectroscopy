from PyQt5.QtWidgets import QApplication

from models import Camera, DAQ
from views import StartWindow

camera = Camera(1)
camera.initialise()
daq = DAQ()

app = QApplication([])
start_window = StartWindow(camera,daq)
start_window.show()
app.exit(app.exec_())
camera.close_camera()
daq.close_daq()