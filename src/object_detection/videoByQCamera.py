'''
Final file containing finalized code from diff test files
'''
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtMultimedia as qtmm
from . import custom_test_vid_revised
import sys
import os
import cv2
import numpy as np
import threading
import time

class video(qtc.QObject):

    lock = qtc.QReadWriteLock()
    error = qtc.pyqtSignal(str)
    getFrame = qtc.pyqtSignal(np.ndarray)
    currentFramePos = qtc.pyqtSignal(int)
    currentTimePos = qtc.pyqtSignal(int)
    frameCount = qtc.pyqtSignal(int)
    FPSSignal = qtc.pyqtSignal(int)
    videoEnded = qtc.pyqtSignal()
    getRecorderFrame = qtc.pyqtSignal(np.ndarray)
    stopRecordingSignal = qtc.pyqtSignal(bool)
    startRecordingSignal = qtc.pyqtSignal()
    requestDelete = qtc.pyqtSignal()
    rawVideoRecordingStarted = qtc.pyqtSignal(bool)

    def __init__(self):
        
        super().__init__(parent = None)
        
        

        self.frame = None
        self.isCamera = False
        self.isImageFlag = False
        self.first = True
        self.firstFileSaveFlag = True
        self.cameraSetFlag = False  # indicates whether self.camera variable has been set
        self.urlSetFlag = False   # indicates whether self.url has been set. Useful to avoid error when, due to multi threading, self.url is called before being set.
        self.pauseRecording = True
        self.saveFlag = False
        self.emitCount = 0
        self.url = None
        self.previousSingleFileFlag = False  # initial value is False so as to prevent it from entering initial conditions
        self.forceStopFlag = False
        self.stopProcessingFlag = False
        self.recordingInProgressFlag = False
        
        #self.rawVideoRecordingFlag = False

    def getCamerasList(self):
        # returns the cameras
        self.cameras = qtmm.QCameraInfo.availableCameras()
        return self.cameras

    @qtc.pyqtSlot(str)
    def setCamera(self,camera):
        # convert it into pyqt slot
        for x in self.getCamerasList():
            if x.description() == camera:
                self.camera = qtmm.QCamera(x)
                self.camera.setParent(self)  # check if it has positive effect or negative
                print(id(self.camera))
                self.cameraSetFlag = True
                return
        print("CANNOT FIND THE CAMERA!!!")
    
    @qtc.pyqtSlot()
    def start(self):

        if not self.cameraSetFlag:
            self.error.emit("No camera has been set")
            return
        print(id(self.camera))
        print("a",self.camera.viewfinderSettings().pixelFormat(),self.camera.supportedViewfinderFrameRateRanges())
        #self.camera.viewfinderSettings().setPixelFormat(qtmm.QVideoFrame.Format_RGB24)
        self.probe = qtmm.QVideoProbe(parent = self)
        support = self.probe.setSource(self.camera)
        if not support:
            print("support",support)
            support = self.probe.setSource(qtmm.QMediaRecorder(self.camera))
            if not support:
                # use qabstract shit
                pass
        self.probe.videoFrameProbed.connect(self.setFrame)
       
        self.camera.start()

        x = self.camera.viewfinderSettings()
        self.fps = int(x.maximumFrameRate())
        self.height = x.resolution().height()
        self.width = x.resolution().width()
        self.startTime = time.time()
        self.FPSSignal.emit(int(self.fps))
        print("a",self.camera.supportedViewfinderPixelFormats(),self.camera.supportedViewfinderFrameRateRanges()[0].maximumFrameRate,x.minimumFrameRate(),x.maximumFrameRate(),x.resolution())
        #xyz
        print("a",self.camera.viewfinderSettings().pixelFormat())
        if qtmm.QVideoFrame.Format_YUYV in self.camera.supportedViewfinderPixelFormats():
            x.setPixelFormat(qtmm.QVideoFrame.Format_YUYV)
            print("pixel format set to format_yuyv!")
        else:
            print("pixel format format_yuyv! not found!!!")
        print("a",self.camera.viewfinderSettings().pixelFormat())
        #self.camera.setViewfinderSettings(x)
        #print("a",self.camera.viewfinderSettings().pixelFormat())
        self.isCamera = True

    def stopCamera(self):
        if self.isCamera == False:
            return
        
        self.camera.stop()
        self.probe.videoFrameProbed.disconnect()
        
    def frameRate(self):
        # TODO this method is not in use remove it
        print("in frameRate")

        if self.isCamera or (self.fps is not None):
            return self.fps
        else:
            return "Unspecified"
    
    def frameSize(self):
        return self.width,self.height
            
    def setUrl(self,url,isImageFlag = False):
        self.url = url
        self.isImageFlag = isImageFlag
        print(self.url)
        

    def startByURL(self):

        if self.url is None:
            self.error.emit("No file path has been set")
            return
        #print("a",self.camera.viewfinderSettings().pixelFormat())
        #self.camera.viewfinderSettings().setPixelFormat(qtmm.QVideoFrame.Format_RGB24)
        if not self.isImageFlag:
            writeLocker = qtc.QWriteLocker(self.lock)
            self.cap = cv2.VideoCapture(self.url)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            writeLocker.unlock()
            print(self.cap.get(cv2.CAP_PROP_POS_AVI_RATIO),self.cap.get(cv2.CAP_PROP_FRAME_COUNT),self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            print("fps",self.fps)
            self.FPSSignal.emit(int(self.fps))
            self.emitFrameCount()
            print("c")
            self.isCamera = False
            self.cameraSetFlag = True
            self.startTimer = 0
            self.readFromCap()
        else:
            writeLocker = qtc.QWriteLocker(self.lock)
            self.frame = cv2.imread(self.url)
            print("aaa")
            self.getFrame.emit(self.frame)
            writeLocker.unlock()
            print("emitted image's frame")
        ##timer = qtc.QTimer()
        ##timer.singleShot(500,self.readFromCap)    # to simulate the first signal to get the detection going. The timer is needed because the function call to readFromCap emits signal but at that time, the signal is not connected to the inter class
        
        #timer.timeout.connect(self.saveFrame)
        #self.readFromCap()
        #print("a",self.camera.supportedViewfinderPixelFormats())
        #x = self.camera.viewfinderSettings()
        #x.setPixelFormat(qtmm.QVideoFrame.Format_Jpeg)
        #self.camera.setViewfinderSettings(x)
        #print("a",self.camera.viewfinderSettings().pixelFormat())
    
    @qtc.pyqtSlot(int)
    def setFrameNumber(self,fNum):
        print("self.cap.get(cv2.CAP_PROP_POS_FRAMES)",self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        writeLocker = qtc.QWriteLocker(self.lock)
        _ = self.cap.set(cv2.CAP_PROP_POS_FRAMES,fNum)
        writeLocker.unlock()
        print("fNum",_,self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def emitFrameCount(self):
        readLocker = qtc.QReadLocker(self.lock)
        self.frameCount.emit(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)))
        readLocker.unlock()

    def emitCurrentPos(self,time = None):
        if time == None:
            readLocker = qtc.QReadLocker(self.lock)
            self.currentFramePos.emit(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
            readLocker.unlock()
        else:
            self.currentTimePos.emit(int(time))

    def initTimer(self):
        print("timer started")
        self.urlTimer = qtc.QTimer()
        self.urlTimer.setInterval(1000/self.fps)
        self.urlTimer.timeout.connect(self.readFromCap)
        self.urlTimer.setTimerType(qtc.Qt.PreciseTimer)
        self.urlTimer.start()
        
        # if the obj exists
        try:
            self.recall()
            print("a3")
        except AttributeError:
            print("error")
    
    @qtc.pyqtSlot(bool)
    def startStopTimer(self,flag):
        # Starts and stops the urlTimer. This function is used to play pause the video played by url
        if flag:
            self.urlTimer.start()
        else:
            self.urlTimer.stop()
            print("urlTimer stopped")

    def readFromCap(self):
        writeLocker = qtc.QWriteLocker(self.lock)
        _, frame = self.cap.read()
        writeLocker.unlock()
        if _:
            self.setFrame(frame)
            #print(frame.shape)
            #cv2.imshow("xyz",frame)
        else:
            print("ENDED")
            self.videoEnded.emit()
            self.setFrameNumber(0)
            #self.urlTimer.stop()
            #self.cap.release()
    
    @qtc.pyqtSlot()
    def emitFrame(self):
        # this function would not be used by url system
        self.emitCount += 1
        print("vid self.emitCount",self.emitCount)
        if self.isCamera:
            writeLocker = qtc.QWriteLocker(self.lock)
            if self.saveFlag and not(self.pauseRecording) and type(self.frame) is not qtmm.QVideoFrame:   # emit the already converted frame
                self.getFrame.emit(self.frame)
                print("no convertyuv")
                return
            elif type(self.frame) is np.ndarray:
                self.getFrame.emit(self.frame)
                print("no convertyuv inspite of saving off due to the thread latency/queue artifact")
                return
            elif self.frame.map(qtmm.QAbstractVideoBuffer.ReadOnly):
                print("yes convertyuv",type(self.frame),type(self.frame) is np.ndarray,type(self.frame) == np.ndarray)
                
                if not self.frame.isMapped():
                    print("self.frame is None !!!!!!!!!!!!!","vid self.emitCount",self.emitCount)
                    count = 0
                    while not self.frame.isMapped():
                        self.frame.map(qtmm.QAbstractVideoBuffer.ReadOnly)
                        if count == 50:
                            print(50)   # TODO raise error here
                            return
                        count += 1
                    print("count",count)

                    #return

                frame = self.convertYUV(self.frame)
                self.frame.unmap()  # changed
                self.getFrame.emit(frame)    # changed
                self.convertedFrame = frame
            else:
                print("frame map failed!")
            writeLocker.unlock()
            self.emitCurrentPos(time.time()-self.startTime)
            #print("time.time()-self.startTime",time.time()-self.startTime)
            
        else:
            print("how did it got here")
            if not self.first and self.startTimer == 0:
                self.startTimer = 1
            if self.startTimer == 1:
                self.startTimer = 2
                self.initTimer()
                #self.readFromCap()
            print("emit")
            self.getFrame.emit(self.frame)
            self.emitCurrentPos()

    def setFrame(self,x):
        #print("type",type(x))
        #if self.pause:
        #    return
        if (self.cameraSetFlag or self.urlSetFlag )and self.saveFlag and not(self.pauseRecording): # if camera
            writeLocker = qtc.QWriteLocker(self.lock)
            if self.isCamera and x.map(qtmm.QAbstractVideoBuffer.ReadOnly):
                # if frame coming from camera, then convert it
                t1 = time.time()
                frame = self.convertYUV(x)
                print("time diff for convertYUV",time.time()-t1)
                x.unmap()
                #writeLocker = qtc.QWriteLocker(self.lock)
                self.frame = frame
                self.convertedFrame = frame
                #writeLocker.unlock()
                #t1 = time.time()
                #self.addFrameToRecorder(self.frame)
                #self.getRecorderFrame.emit(self.frame)
                #print("time to add frame to recorder",time.time()-t1)
            else:
                # if frame coming from opencv capture, then assign as it is.
                print("oopsie1")
                #writeLocker = qtc.QWriteLocker(self.lock)
                self.frame = x
                self.convertedFrame = x
                #writeLocker.unlock()
            self.getRecorderFrame.emit(self.frame)
            writeLocker.unlock()
            print("recorder frame emitted")
        else:
            print("oopsie2",threading.get_ident())
            writeLocker = qtc.QWriteLocker(self.lock)
            self.frame = x
            self.convertedFrame = x
            writeLocker.unlock()
        if self.first:
            print("self.first",self.first)
            
            #self.urlTimer.pau
            #self.emitFrame(np.array([""]))    # give a push to the system first time.
            self.emitFrame()
            self.first=False

        elif self.startTimer == 0:
            self.startTimer = 1
        #if self.rawVideoRecordingFlag:
            #t1 = time.time()
            #self.addFrameToRecorder(self.frame)
            #self.getRecorderFrame.emit(self.frame)
            #print("time to add frame to recorder",time.time()-t1)

            
    @qtc.pyqtSlot()
    def stop(self):
        if self.isCamera:
            #self.probe.setSource(
            try:
                self.probe.deleteLater()
            except:
                print("TRIED TO DELETE THE PROBE OBJ!!!!!!!")
            print("xyzze")

        elif not self.isImageFlag:
                self.urlTimer.stop()
                self.cap.release()
            
        with qtc.QReadLocker(self.lock):
            print("self.recordingInProgressFlag",self.recordingInProgressFlag)
            if not self.recordingInProgressFlag:
                self.requestDelete.emit()


    def setFilePath(self,filePath):
        self.filePath = filePath
        print("filepath",filePath)

    def detectionVideoRecordingHandler(self,flag,singleFileFlag,path):
        # locker not implemented in this function as it wont be used
        if flag:
            if self.previousSingleFileFlag and not singleFileFlag:
                print("self.recorder_thread.isFinished()",self.recorder_thread.isFinished())
                self.recorder_thread.quit()
                print("self.recorder_thread.isFinished()",self.recorder_thread.isFinished())

            elif self.previousSingleFileFlag and singleFileFlag:
                self.getRecorderFrame.connect(self.recorderObj.addFrameToRecorder)
                self.startRecordingSignal.emit()
                self.saveFlag = True
                self.pauseRecording = False
                return

            print("recording started")
            self.saveFlag = True
            self.pauseRecording = False
            self.singleFileFlag = singleFileFlag
            self.previousSingleFileFlag = singleFileFlag
            self.setFilePath(path)
            #self.startRawVideoRecording()
            self.recorderObj = cameraRecorder(path,self.fps,self.width,self.height,self.singleFileFlag)
            self.recorderObj.startRawVideoRecording()
            self.recorder_thread = qtc.QThread(parent= self)
            self.recorderObj.moveToThread(self.recorder_thread)
            self.recorder_thread.start()
            self.temp = self.getRecorderFrame.connect(self.recorderObj.addFrameToRecorder)
            #self.getRecorderFrame.connect(lambda x: print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"))
            self.stopRecordingSignal.connect(self.recorderObj.stopRecording)
            self.startRecordingSignal.connect(self.recorderObj.startRawVideoRecording)
        else:
            print("recording stopped")
            self.stopRecording()

    def rawVideoRecordingHandler(self,flag,singleFileFlag,path,forceStopFlag):
        if flag:
            if self.previousSingleFileFlag and not singleFileFlag:
                print("self.recorder_thread.isFinished()",self.recorder_thread.isFinished())
                #self.recorder_thread.quit()
                self.forceStopFlag = True
                self.stopRecording()
                print("self.recorder_thread.isFinished()",self.recorder_thread.isFinished())

            elif self.previousSingleFileFlag and singleFileFlag:
                self.getRecorderFrame.connect(self.recorderObj.addFrameToRecorder)
                self.startRecordingSignal.emit()
                self.saveFlag = True
                self.pauseRecording = False
                return

            print("recording started")
            self.saveFlag = True
            self.pauseRecording = False
            with qtc.QWriteLocker(self.lock):
                self.recordingInProgressFlag = True
            self.singleFileFlag = singleFileFlag
            self.previousSingleFileFlag = singleFileFlag
            self.setFilePath(path)
            #self.startRawVideoRecording()
            self.recorderObj = cameraRecorder(path,self.fps,self.width,self.height,self.singleFileFlag)
            #self.recorderObj.setParent(self)
            #self.recorderObj.startRawVideoRecording()
            self.recorder_thread = qtc.QThread(parent = self)
            self.recorderObj.moveToThread(self.recorder_thread)
            self.recorder_thread.start()
            self.temp = self.getRecorderFrame.connect(self.recorderObj.addFrameToRecorder)
            #self.getRecorderFrame.connect(lambda x: print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"))
            self.stopRecordingSignal.connect(self.recorderObj.stopRecording)
            self.recorderObj.recordingStarted.connect(self.rawVideoRecordingStarted)
            self.startRecordingSignal.connect(self.recorderObj.startRawVideoRecording)
            self.startRecordingSignal.emit()
            self.recorderObj.requestDelete.connect(self.killRecorderThread)
        else:
            print("forceStopFlag",forceStopFlag)
            if forceStopFlag:
                self.forceStopFlag = forceStopFlag
                self.stopRecording()
            else:
                if singleFileFlag:
                    self.forceStopFlag = False
                    self.stopRecording()
                else:
                    self.forceStopFlag = True
                    self.stopRecording()
                self.previousSingleFileFlag = singleFileFlag
                    
                print("recording stopped")
                
    @qtc.pyqtSlot()
    def stopVideoProcessing(self):
        
        self.stopProcessingFlag = True

    def startRawVideoRecording(self):
        # filePath is already checked before being passed here.
        '''self.recorder = qtmm.QMediaRecorder(self.camera)
        self.settings = self.recorder.videoSettings()
        self.settings.setQuality(qtmm.QMultimedia.VeryHighQuality)
        self.recorder.setVideoSettings(self.settings)
        self.recorder.setOutputLocation(filePath)
        self.recorder.record()'''
        print("self.singleFileFlag",self.singleFileFlag)
        if self.filePath is None:
            self.error.emit("No path set for recording!")
            return
        #fourcc = cv2.VideoWriter_fourcc(*'FFV1')    # TODO: change codec depending on type of video quality (give option in settings)
        if self.firstFileSaveFlag:
            #self.recorder = cv2.VideoWriter(self.filePath,fourcc,int(self.fps),(int(self.width),int(self.height)))
            self.firstFileSaveFlag = False
        else:
            if not self.singleFileFlag:
                #self.recorder = cv2.VideoWriter(self.filePath,fourcc,int(self.fps),(int(self.width),int(self.height)))
                pass
        self.pauseRecording = False
        self.saveFlag = True
        if self.isCamera:
            #self.probe.videoFrameProbed.connect(self.addFrameToRecorder)
            pass

        else:
            try:
                self.urlTimer.timeout.connect(self.addFrameToRecorderURLSlot)
                temp = self.recorder.isOpened()
                print("a1",temp)
                #if not temp:
                    #print(self.recorder.open(self.filePath,fourcc,int(self.fps),(int(self.width),int(self.height))),int(self.fps),(int(self.width),int(self.height)))
            except AttributeError:
                self.recall = self.startRawVideoRecording
                print("a2")

    def addFrameToRecorder(self,frame):
        # locker not implemented in this function as it won't be used
        print("recording cont..")
        if self.saveFlag and not(self.pauseRecording):
            '''if self.isCamera and self.frame.map(qtmm.QAbstractVideoBuffer.ReadOnly):
                frame = self.convertYUV()
                self.frame.unmap()

                self.recorder.write(frame)'''
            #print(type(self.frame))
            self.recorder.write(self.frame)

    def stopRecording(self):
        self.saveFlag = False
        self.pauseRecording = True
        print("i am here to stop the recording!")
        '''if self.isCamera:
            #self.probe.videoFrameProbed.disconnect(self.addFrameToRecorder)
            self.getRecorderFrame.disconnect(self.recorderObj.addFrameToRecorder)
            self.stopRecordingSignal.emit()
            #pass
        else:
            self.urlTimer.timeout.disconnect(self.addFrameToRecorderURLSlot)'''
        #if not self.isCamera:
        #    self.urlTimer.timeout.disconnect(self.addFrameToRecorderURLSlot)
        
        #x = self.getRecorderFrame.disconnect(self.recorderObj.addFrameToRecorder)
        print(type(self.temp),type(self.getRecorderFrame),self.receivers(self.getRecorderFrame))#dir(qtc.QMetaMethod))#self.isSignalConnected(self.getRecorderFrame))
        
        #tmp = qtc.QObject()
        #tmp.disconnect(self.temp)
        #print("x",x)
        if self.receivers(self.getRecorderFrame)>0:
            x = self.getRecorderFrame.disconnect()
            #self.temp.disconnect()
            print("x",x,self.receivers(self.getRecorderFrame))
        #readLocker = qtc.QReadLocker(self.lock)  # to prevent self.forceStopFlag being changed while emitted
        self.stopRecordingSignal.emit(self.forceStopFlag)
        #readLocker.unlock()
        
        '''if not self.singleFileFlag:
            #self.getRecorderFrame.disconnect(self.recorderObj.addFrameToRecorder)
            #self.stopRecordingSignal.emit()
            # more needs to be done here
            print("a self.recorder_thread.isFinished()",self.recorder_thread.isFinished())
            self.recorder_thread.quit()
            print("a self.recorder_thread.isFinished()",self.recorder_thread.isFinished())
            
            #self.recorder.release'''
        print("stopped")
    
    def killRecorderThread(self):
        print("self.recorder_thread.isFinished()",self.recorder_thread.isFinished())
        self.recorder_thread.quit()
        print("self.recorder_thread.wait(3000)",self.recorder_thread.wait(3000))
        print("self.recorder_thread.isFinished()",self.recorder_thread.isFinished())
        self.recorder_thread.deleteLater()
        self.recorderObj.deleteLater()
        if self.stopProcessingFlag:
            self.requestDelete.emit()
        else:
            with qtc.QWriteLocker(self.lock):
                self.recordingInProgressFlag = False
    
    def addFrameToRecorderURLSlot(self):
        self.addFrameToRecorder(self.frame)

    @qtc.pyqtSlot()
    def pauseRVidRecording(self):
        self.pauseRecording = True
    
    @qtc.pyqtSlot()
    def resumeRVidRecording(self):
        self.pauseRecording = False

    '''def startDbGenr(self,dbPath,prefix,delay = None,maxImgCount = ):
        self.dbGenrFlag = True
        self.dbPath = dbPath
        self.prefix = prefix
        self.timer = qtc.QTimer()
        self.timer.setInterval(delay)
        self.timer.timeout.connect(self.saveFrame)
        #self.count = self.checkCount(self.dbPath,self.prefix)
        self.maxImgCount = maxImgCount
        self.count = 0
        self.timer.start()
    
    def saveFrame(self):

        if self.dbGenrFlag:
            
            if self.isCamera and self.frame.map(qtmm.QAbstractVideoBuffer.ReadOnly):
                #print(self.frame.pixelFormat(),self.frame.planeCount(),self.frame.bytesPerLine(1),self.frame.mappedBytes())
                print("saveFrame")
                ''''''img = qtg.QImage(self.frame.bits(),self.frame.size().width(),self.frame.size().height(),self.frame.bytesPerLine(),self.frame.imageFormatFromPixelFormat(self.frame.pixelFormat()))
                width = img.width()
                height = img.height()
                print(width,height,self.frame.size().width(),self.frame.size().height(),self.frame.bytesPerLine(),self.frame.imageFormatFromPixelFormat(self.frame.pixelFormat()))
                img = img.convertToFormat(4)
                width = img.width()
                height = img.height()
                print(width,height)
                ptr = img.bits()
                ptr.setsize(img.sizeInBytes())
                arr = np.array(ptr).reshape(height, width, 4)''''''
                x = self.convertYUV(self.frame)
                #cv2.imwrite("D:\db\sam"+str(self.count)+'.png',x)
                cv2.imwrite(os.path.join(self.dbPath,self.prefix+str(self.count)+'.png'),x)
                self.frame.unmap()
                self.count += 1
                #convertedFrame.dtype()    # so that the programs ends, even with error
            elif not self.isCamera:
                cv2.imwrite("D:\db\sam"+str(self.count)+'.png',self.frame)
                #convertedFrame.dtype()    # so that the programs ends, even with error
                self.count += 1
            
            if self.count >= maxImgCount:
                self.timer.stop()
                self.timer.deleteLater()'''
    
    def convertYUV(self,img):
        print("type(img)",type(img),type(img.bits()),img.bits(),img.isMapped(),img.isValid(),img.isReadable())
        if type(img) is not qtmm.QVideoFrame:
            print("ALERT! type(img) is",type(img))
            return None
        #readLocker = qtc.QReadLocker(self.lock)
        #if img.pixelFormat() == qtmm.QVideoFrame.Format_Jpeg:
            '''x = qtmm.QVideoFrame.imageFormatFromPixelFormat(img.pixelFormat())
            print("the frame format is JPEG",x)
            img = qtg.QImage( img.bits(),
             img.width(),
             img.height(),
             img.bytesPerLine(),
             x)
            
            img = img.convertToFormat(qtg.QImage.Format_BGR888)

            ptr = img.constBits()
            depth = img.depth()
            print("depth",depth,img.byteCount(),img.format())

            ptr.setsize(img.byteCount())
            frame = np.ndarray(shape = (self.height,self.width,3),buffer = ptr,dtype  = np.uint8)
            print("frame.shape",frame.shape)'''

        #    ptr = img.bits()
            

        #    return frame
        print("img.width(),img.height()",img.width(),img.height())
        print("plane count",img.planeCount())
        ptr = img.bits()
        if ptr == None:
            print("ptr is None")
            return np.zeros((480,640,3),dtype=np.uint8)
        print("ptr size",ptr.getsize())
        print("bytes per line",img.bytesPerLine())
        
        convertedFrame = np.frombuffer(ptr,dtype=np.uint8)
        #readLocker.unlock()
        #print("img.bits()",img.bits())
        #print("convertYUV")
        print(convertedFrame.shape)
        
        convertedFrame = convertedFrame.reshape((self.height,self.width,2))
        print(convertedFrame.shape,type(convertedFrame),convertedFrame.dtype)
        x = np.empty((480,640,3),dtype=np.uint8)
        cv2.cvtColor(np.array(convertedFrame),cv2.COLOR_YUV2BGR_YUYV,x)
        #cv2.convertScaleAbs(x, x, 5)
        #print(x.shape,x.dtype,convertedFrame[300][200],convertedFrame[300][201],x[300][200])
        print(x.shape,x.dtype)
        #cv2.imwrite(os.path.join(self.dbPath,self.prefix + str(self.count)+'.png'),convertedFrame)
        #cv2.imwrite("D:\db\sample"+str(self.count)+'.png',convertedFrame)
        #cv2.imshow("xyz",x)
        #cv2.waitKey(0)
        return x

class dbGenr(qtc.QObject):
    
    requestDelete = qtc.pyqtSignal()
    getFrame = qtc.pyqtSignal()
    error = qtc.pyqtSignal(str)

    #def startDbGenr(self,dbPath,prefix,delay = None,maxImgCount = ):
    def __init__(self,dbPath = None,prefix = None,delay = None,maxImgCount = None):
        super().__init__()
        if dbPath == None or prefix == None or delay == None or maxImgCount == None:
            self.dbGenrFlag = False
        else:
            self.dbGenrFlag = True
            self.dbPath = dbPath
            self.prefix = prefix
            self.timer = qtc.QTimer()
            self.timer.setInterval(delay)
            self.timer.timeout.connect(self.getFrame)
            #self.count = self.checkCount(self.dbPath,self.prefix)
            self.maxImgCount = maxImgCount
            self.timer.start()
        self.count = 0

    @qtc.pyqtSlot(np.ndarray)
    @qtc.pyqtSlot(np.ndarray,str,str)
    def saveFrame(self, frame, dbPath = None, prefix = None):
        
        if not self.dbGenrFlag :
            cv2.imwrite(os.path.join(dbPath,prefix+str(self.count)+'.png'),frame)    
        else:    
            cv2.imwrite(os.path.join(self.dbPath,self.prefix+str(self.count)+'.png'),frame)

            if self.count >= self.maxImgCount:
                '''self.timer.stop()
                self.timer.deleteLater()
                self.requestDelete.emit()'''
                self.stop()
        
        self.count += 1
        
    def stop(self):

        self.timer.stop()
        self.timer.deleteLater()
        self.requestDelete.emit()

class cameraRecorder(qtc.QObject):

    requestDelete = qtc.pyqtSignal()
    recordingStarted = qtc.pyqtSignal(bool)

    def __init__(self, path,fps,width,height,singleFileFlag,objNum = 0):
        super().__init__()
        self.filePath = path
        self.fps = fps
        self.width = width
        self.height = height
        self.firstFileSaveFlag = True
        #self.singleFileFlag = True
        self.singleFileFlag = singleFileFlag
        self.isCamera = True
        self.pp = 0
        self.objNum = objNum
        print("apple"*10)

    def startRawVideoRecording(self):
        # filePath is already checked before being passed here.
        '''self.recorder = qtmm.QMediaRecorder(self.camera)
        self.settings = self.recorder.videoSettings()
        self.settings.setQuality(qtmm.QMultimedia.VeryHighQuality)
        self.recorder.setVideoSettings(self.settings)
        self.recorder.setOutputLocation(filePath)
        self.recorder.record()'''
        print("self.singleFileFlag",self.singleFileFlag)
        if self.filePath is None:
            #self.error.emit("No path set for recording!")
            print("ERROR")
            return
        #fourcc = cv2.VideoWriter_fourcc(*'FFV1')    # TODO: change codec depending on type of video quality (give option in settings)
        fourcc = cv2.VideoWriter_fourcc(*'H264')    # TODO: change codec depending on type of video quality (give option in settings)
        if self.firstFileSaveFlag: # this flag helps us to check if the frames to be added to single file-- if yes then to avoid creating another recorder object.
            self.recorder = cv2.VideoWriter(self.filePath,fourcc,int(self.fps),(int(self.width),int(self.height)),True)
            self.firstFileSaveFlag = False
        else:
            if not self.singleFileFlag:
                self.recorder = cv2.VideoWriter(self.filePath,fourcc,int(self.fps),(int(self.width),int(self.height)),True)
        self.pauseRecording = False
        self.saveFlag = True
        self.recordingStarted.emit(True)
        '''if self.isCamera:
            #self.probe.videoFrameProbed.connect(self.addFrameToRecorder)
            pass

        else:
            try:
                #self.urlTimer.timeout.connect(self.addFrameToRecorderURLSlot)
                temp = self.recorder.isOpened()
                print("a1",temp)
                if not temp:
                    print(self.recorder.open(self.filePath,fourcc,int(self.fps),(int(self.width),int(self.height))),int(self.fps),(int(self.width),int(self.height)))
            except AttributeError:
                self.recall = self.startRawVideoRecording
                print("a2")'''

    @qtc.pyqtSlot(np.ndarray)
    def addFrameToRecorder(self,frame):
        
        print("recording cont..",frame.shape,self.pp,threading.get_ident())
        if self.saveFlag and not(self.pauseRecording):
            '''if self.isCamera and self.frame.map(qtmm.QAbstractVideoBuffer.ReadOnly):
                frame = self.convertYUV()
                self.frame.unmap()

                self.recorder.write(frame)'''
            #print(type(self.frame))
            #f = cv2.resize(frame,(int(self.width),int(self.height)))
            #f = cv2.resize(frame,(570,760))
            #self.recorder.write(frame)
            self.recorder.write(frame)
            #cv2.imwrite("D:/tmpImg2.png",frame)
            print("Video Write successfull",self.recorder.isOpened(),frame[300][300])#,f.shape)
        self.pp += 1

    @qtc.pyqtSlot(bool)
    def stopRecording(self,forceStopFlag):
        self.saveFlag = False
        self.pauseRecording = True
        if self.isCamera:
            #self.probe.videoFrameProbed.disconnect(self.addFrameToRecorder)
            pass
        else:
            #self.urlTimer.timeout.disconnect(self.addFrameToRecorderURLSlot)
            pass
        #if not self.singleFileFlag or forceStopFlag:
        if forceStopFlag:
            print("force stop!")
            self.recorder.release()
            self.requestDelete.emit()
            print("self.recorder.isOpened()",self.recorder.isOpened())
            del self.recorder
        print("stopped",forceStopFlag)
        self.recordingStarted.emit(False)

        #TODO delete all the object in thread when singleFileFlag is False


class cameraMonitor(qtc.QObject):

    cameraLost = qtc.pyqtSignal()
    def __init__(self,camera):
        super().__init__()
        self._camera = camera
    
    def check(self):
        while(True):
            if qtc.QThread.currentThread().isInterruptionRequested():
                return
            cameras = qtmm.QCameraInfo.availableCameras()
            #print(cameras)
            found = False
            for camera in cameras:
                if camera == self._camera:
                    found = True
            if not found:
                self.cameraLost.emit()
                return

class interfacer(qtc.QObject):
    # this class encompases the module with Qt which enables detection on the model (custom_test_vid_revised)

    detectionComplete = qtc.pyqtSignal([],[np.ndarray,list])
    error = qtc.pyqtSignal(str)
    inferenceTime = qtc.pyqtSignal(str)

    def __init__(self,w = None, h= None):
        super().__init__()
        self.width = w
        self.height = h
        if self.width != None:
            self.detection = custom_test_vid_revised.detection(self.width,self.height)
        else:
            self.detection = custom_test_vid_revised.detection()
        #self.detection.load_model()
        self.firstRun = True
        self.count = 0
        self.halfModelLoaded = False

    def setSize(self,w,h):
        # convert to pyqt slot
        self.width = w
        self.height = h

    def loadModel(self):
        t1 = time.time()
        if self.width != None and self.height != None:
            if not self.halfModelLoaded:
                self.detection.load_model()
            self.detection.load_model_2()
            self.firstRun = False
        else:
            self.detection.load_model()

        print("TIME FOR LOADING MODEL: ",time.time()-t1,self.firstRun)

    @qtc.pyqtSlot(np.ndarray)
    def detect(self,frame):
        a = 1
        print(a)
        if frame is None:
            self.error.emit("Frame is empty")
            return
        if self.firstRun:
            self.setSize(frame.shape[1],frame.shape[0])
            t1 = time.time()
            if not self.halfModelLoaded:
                self.detection.load_model()
            self.detection.load_model_2()
            self.firstRun = False
            print("TIME FOR LOADING MODEL",time.time()-t1,self.firstRun)
        elif frame.shape[1] != self.width or frame.shape[0] != self.height:
            self.setSize(frame.shape[1],frame.shape[0])
            self.detection.load_model_2(flag = False)
        t1 = time.time()
        outputFrame,l = self.detection.detect(frame)
        #x = self.detection.detect(frame)
        #print(x)
        #outputFrame = frame
        print(a+1)
        #self.emitSignal(outputFrame)
        self.count+=1
        print("inter self.count",self.count)
        self.detectionComplete[np.ndarray,list].emit(outputFrame,l)
        self.detectionComplete.emit()
        self.inferenceTime.emit("{:.2f}s".format(time.time()-t1))
        #self.detectionComplete.emit()
        print(a+2)
        

    def emitSignal(self,outputFrame):
        #return
        self.detectionComplete.emit(outputFrame)
        print(4)
    
def show(frame):
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",frame.shape)
    cv2.imshow("xyz",frame)

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)

    v = video()
    inter = interfacer()
    #print("sigs",inter.detectionComplete.types())
    #image = self.detection.detect(image)
    print("hola")
    #cam = qtmm.QCamera(v.getCamerasList()[0])
    #v.setCamera(cam)
    #v.start()
    v.setUrl("D:/assignments/fyp/WL.mp4")
    v.startByURL()
    #timer = qtc.QTimer()
    #timer.singleShot(10000,v.stopRecording)
    #timer.timeout.connect(self.saveFrame)
    #self.count = self.checkCount(self.dbPath,self.prefix)
    #timer.start()
    
    video_thread = qtc.QThread()
    v.moveToThread(video_thread)
    #ss.finished.connect(video_thread.quit)
    video_thread.start()

    inter_thread = qtc.QThread()
    inter.moveToThread(inter_thread)
    #ss.finished.connect(video_thread.quit)
    inter_thread.start()
    
    inter.detectionComplete.connect(v.emitFrame)

    v.getFrame.connect(inter.detect)
    inter.detectionComplete[np.ndarray,list].connect(show)
    #v.ge
    ##v.startRawVideoRecording(r"D:\testing.avi")
    #v.setUrl("D:/assignments/fyp/WL.mp4")
    #v.setUrl(r"D:\testing.avi")
    #v.startByURL()
    print("xyxz")
    #v.startDbGenr(8000,"","apple")
    sys.exit(app.exec_())