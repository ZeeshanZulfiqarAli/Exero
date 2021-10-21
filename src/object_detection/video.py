import sys
from os import path

import numpy as np
from custom_test_vid_revised import detection
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import cv2

class video(QtCore.QObject):
    image_data = QtCore.pyqtSignal(np.ndarray)

    def __init__(self,path,parent=None):
        super().__init__(parent)
        self.camera = cv2.VideoCapture(path)
        self.frame = None
        self.saveFlag = False
        self.fps = self.camera.get(cv2.CAP_PROP_FPS)
        self.width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.pause = False
        self.stop = False
        self.counter = 0
        print("fps ",self.fps,self.width,self.height)

    def run(self):

        #while True:
        _, frame = self.camera.read()
        self.frame = frame

        if self.saveFlag and not(self.pause):
            self.out.write(self.frame)

        #if self.camera.isOpened() is False:
        #    break


    def save(self,savePath):

        self.saveFlag = True
        self.savePath = savePath
        fourcc = cv2.VideoWriter_fourcc(*'FFV1')    # add backup format option too, or check on startup if this installed.
        self.out = cv2.VideoWriter(self.savePath,fourcc,int(self.fps),(int(self.width),int(self.height)))
        print(type(self.fps),self.width,self.height)

    # make it a slot 
    def getImage(self):
        print("a")
        self.run()
        self.image_data.emit(self.frame)
    
    def pauseSave(self):
        self.pause = True
        

    def resumeSave(self):
        self.pause = False
        

    def stopSave(self):
        # overwrite existing file because same file name
        # add a check that this doesn't happen!
        self.saveFlag = False
        

class FaceDetectionWidget(QtWidgets.QWidget):
    getImage = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QtGui.QImage()
        self.timer = QtCore.QBasicTimer()
        #self._red = (0, 0, 255)
        #self._width = 2
        #self._min_size = (30, 30)
    
    def start_recording(self,delay):

        self.timer.start(delay, self)
    
    def timerEvent(self, event):
        if (event.timerId() != self.timer.timerId()):
            return
        self.getImage.emit()
            

    def detect_faces(self, image: np.ndarray):
        # haarclassifiers work better in black and white
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_image = cv2.equalizeHist(gray_image)

        faces = self.classifier.detectMultiScale(gray_image, scaleFactor=1.3, minNeighbors=4, flags=cv2.CASCADE_SCALE_IMAGE, minSize=self._min_size)

        return faces

    def image_data_slot(self, image_data):
        #faces = self.detect_faces(image_data)
        #for (x, y, w, h) in faces:
        #        cv2.rectangle(image_data, (x, y), (x+w, y+h), self._red, self._width)

        self.image = self.get_qimage(image_data)
        if self.image.size() != self.size():
            self.setFixedSize(self.image.size())

        self.update()

    def get_qimage(self, image: np.ndarray):
        height, width, colors = image.shape
        bytesPerLine = 3 * width
        QImage = QtGui.QImage

        image = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)

        image = image.rgbSwapped()
        return image

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QtGui.QImage()

class MainWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        #fp = haarcascade_filepath
        self.record_video = video(r"D:\assignments\fyp\WL.mp4")
        #self.detection = detection(self.record_video.width,self.record_video.height)
        #self.detection.load_model()
        self.face_detection_widget = FaceDetectionWidget()

        # TODO: set video port
        #self.record_video = video(r"D:\TensorFlow\workspace\fyp_ssd_inception_v2_14556+25000epochs_rmsProp_dropout90_autoaugment_lr0.004_step2000_decayRate95\output.avi")
        
        self.run_button = QtWidgets.QPushButton('Start')
        self.save_button = QtWidgets.QPushButton('Save')
        self.pause_button = QtWidgets.QPushButton('pause')
        self.resume_button = QtWidgets.QPushButton('resume')
        self.stop_button = QtWidgets.QPushButton('Stop')

        # Connect the image data signal and slot together
        image_data_slot = self.face_detection_widget.image_data_slot
        self.face_detection_widget.getImage.connect(self.record_video.getImage)
        #self.record_video.image_data.connect(image_data_slot)
        self.record_video.image_data.connect(self.someName)
        # connect the run button to the start recording slot
        delay = 1000/self.record_video.fps
        print("delay",delay)
        self.run_button.clicked.connect(self.record_video.run)
        self.run_button.clicked.connect(lambda: self.face_detection_widget.start_recording(delay))
        self.save_button.clicked.connect(lambda: self.record_video.save(r"D:\Sample.avi"))
        self.stop_button.clicked.connect(self.record_video.stopSave)
        #self.stop_button.clicked.connect(self.detection.close)
        self.pause_button.clicked.connect(self.record_video.pauseSave)
        self.resume_button.clicked.connect(self.record_video.resumeSave)

        # Create and set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.face_detection_widget)
        layout.addWidget(self.run_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.resume_button)
        

        self.setLayout(layout)

    def someName(self,image):
        #image = self.detection.detect(image)
        self.face_detection_widget.image_data_slot(image)

def main():
    app = QtWidgets.QApplication(sys.argv)

    main_window = QtWidgets.QMainWindow()
    main_widget = MainWidget()
    main_window.setCentralWidget(main_widget)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()