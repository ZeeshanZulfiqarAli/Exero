from . import resources
import sys
import os
import time
from . import settings
import threading
from .bookmark import bookmark
from .marqueeLabel import marqueeLabel
from .clickLabel import clickLabel
from .bookmarkWidget import bookmarkWidget
from .slider import customSlider
from .test2 import Switch
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from .object_detection import videoByQCamera
import numpy as np
import time
import cv2
import copy
import collections

#os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
#if hasattr(qtc.Qt, 'AA_UseHighDpiPixmaps'):
#    qtw.QApplication.setAttribute(qtc.Qt.AA_UseHighDpiPixmaps, True)
#    print("yes attr")

class MainWindow(qtw.QMainWindow):
    
    loadModel = qtc.pyqtSignal()
    startByURLSignal = qtc.pyqtSignal()
    startByCamSignal = qtc.pyqtSignal()
    setCam = qtc.pyqtSignal(str)
    stopVideoProcessing = qtc.pyqtSignal()
    startRawVideoRecordingSignal = qtc.pyqtSignal(bool,bool,str,bool)
    detectionVideoRecordingFrame = qtc.pyqtSignal(np.ndarray)
    stopDetectionVideoRecording = qtc.pyqtSignal(bool)
    dbGenrFrame = qtc.pyqtSignal(np.ndarray)
    stopDbGenr = qtc.pyqtSignal()
    singleFrame = qtc.pyqtSignal(np.ndarray,str,str)
    startStopTimerSignal = qtc.pyqtSignal(bool)
    pauseRVidRecForLiveVidSignal = qtc.pyqtSignal()
    resumeRVidRecForLiveVidSignal = qtc.pyqtSignal()
    playAlarm = qtc.pyqtSignal()
    lock = qtc.QReadWriteLock()
    
    def __init__(self):
        super().__init__()
        # Main UI code goes here
        global app
        screen = app.primaryScreen()
        print(screen.size(),screen.geometry())
        #print(screen.devicePixelRatio,app.devicePixelRatio)
        print(screen.logicalDotsPerInch(),screen.physicalDotsPerInch())
        print(screen.manufacturer(),screen.model())

        self.objs = dict()
        self.settings = settings.getObj()

        self.inter = videoByQCamera.interfacer()
        self.inter_thread = qtc.QThread(parent = self)
        self.inter.moveToThread(self.inter_thread)
        self.inter_thread.start()
        self.loadModel.connect(self.inter.loadModel)
        self.loadModel.emit()

        self.widthScale = screen.size().width() / 1920
        self.heightScale = screen.size().height() / 1080
        print(self.widthScale,self.heightScale)
        self.allowRecording = False
        self.detectionVideoRecordingFlag = False
        self.previousDetectionVideoRecordingSingleFileFlag = False
        self.rawVideoRecordingFlag = False
        self.previousRawVideoRecordingFlag = False   # Not being used currently
        self.frame = None
        self.dbGenrFlag = False
        self.isStopped = True
        self.fps = None
        self.refs = list()   # list to hold references to the widgets in bookmark view
        self.polypFoundFlag = False
        self.finalConvertedFrame = None   # used for detection video recording
        self.detectionFlag = None    # tells which type of source is used for detection
        self.newBookmarkAddedFlag = True    # shows if new bookmark added. Used to avoid reading data from scratch everytime show bookmark btn is clicked.
        self.dequeLength = self.settings.value("dequeLength",4,int)
        self.polypDetectedDeque = collections.deque(self.dequeLength*[False], self.dequeLength)
        self.playAlarmflag = True

        self.bookmarkObj = bookmark()
        self.capFrameObj = videoByQCamera.dbGenr()
        self.capFrameThread = qtc.QThread(parent = self)
        self.capFrameObj.moveToThread(self.capFrameThread)
        self.singleFrame.connect(self.capFrameObj.saveFrame)
        #self.dbGenrObj.getFrame.connect(self.emitDbGenrFrame)
        self.capFrameObj.requestDelete.connect(self.killCapFrameThread)
        self.capFrameThread.start()

        #self.widthScale = 1366 / 1920
        #self.heightScale = 768 / 1080
        #print(self.widthScale,self.heightScale)
        stylesheet = '''
        #qwid2{
            background-color: #FAFAFA;
            border: 0px solid red;
        }
        QMainWindow {
            background-color: #000000;
        }
        a{
            background-color: rgb(200,20,80);
        }
        '''
        stsheet2 = f'''
        #SPWid,#SPWid1 {{
            background-color: #FAFAFA;
        }}
        #a {{
            background-color: rgb(200,20,80);
        }}
        QLabel {{
            font-family: Segoe UI;
            font-size: 10pt;
            color: #525856;            
        }}
        #details,#tLbl,#ctbLbl,#bkmrkLbl,#settingsLbl,#aboutLbl,#helpLbl {{
            font-family: Segoe UI;
            font-size: 22pt;
            color: #525856;
            font-weight: 200;
        }}
        #orLbl{{
            font-size: 16pt;
            font-weight: 200;
        }}

        #addBkmrkNotifLbl{{
            font-family: Segoe UI;
            font-size: 8pt;
            
        }}
        #dropdown {{
            
            min-width:{(365.45*self.widthScale)+0.5}px;

        }}


        #dropdown::down-arrow{{
            
        }}
        QLineEdit , QComboBox, QComboBox QAbstractItemView{{
            font-family: Segoe UI;
            font-size: 8pt;
            color: #525856;
            border: {(1.4*self.widthScale)}px solid #707070;
            height: {(28.125*self.heightScale)+0.5}px;
        }}
        QPushButton,#dropdown::drop-down{{
            height: {(42.1875*self.heightScale)+0.5}px;
            background-color: #F4F4F4;
            border-style: solid;
            border-color: #707070;
            border-width: {(1.4*self.widthScale)+0.5}px;
            border-radius: {int((21*self.widthScale)+0.5)}px;
            font-family: Segoe UI;
            font-size: 10pt;
            color: #424242;
        }}
        QPushButton:hover,#dropdown::drop-down{{
            background-color: #F8F8F8;
        }}
        QPushButton:pressed,#dropdown::drop-down{{
            background-color: #FFFFFF;
        }}
        #dropdown::drop-down {{
            subcontrol-origin: margin;
            subcontrol-position: top right;
            height: {(28.125*self.heightScale)+0.5}px;
            width: {(28.1*self.widthScale)+0.5}px;
        }}
        #sidePanelBtn{{
            background-color: #CCCCCC;
            border: 0px solid #666666;
        }}
        #sidePanelBtn:hover{{
            background-color: #d9d9d9;
        }}
        QMenuBar{{
            padding-left: {(14*self.widthScale)+0.5}px;
            font-family: Segoe UI;
            
        }}
        #settingLWidget,#l1,#l2,#bWidget,#shortcutLbl,#helpLWidget,#vsoLbl,#dmLbl,#sysCorrOptLbl,#bkmrkLbl2,#videoLbl,#btnHolderWidget{{
            
            padding-left: {(8.4*self.widthScale)+0.5}px;
            background-color: #FAFAFA;
            
        }}
        #l2{{
            border-top: 0px solid blue;
            
        }}
        #subTitleLbl,#settingsSubTitleLbl,#camLbl{{
            font-size: 14pt;
        }}
        #helpScroll{{
            border: None;
        }}
        '''
        '''
        #LSpace{{
            background-color: rgb(200,0,0);
        }}
        #PLA{{
            border: 0px solid white;
            background-color: rgb(0,0,200);
            background-origin: content;
            background-clip: content;
            background-position: left;
            subcontrol-origin: content;
            subcontrol-position: left;
            margin: 0px;
            padding: 0px;
            spacing:0;
        }}
        #tLbl,#ctbLbl{{
            border: 0px solid orange;
            left: 0px;
            background-color: rgb(0,200,200);
            background-origin: content;
            background-clip: content;
            background-position: left;
            subcontrol-origin: content;
            subcontrol-position: left;
            padding: 0px;
            margin: 0;
            spacing:0;
        }}
        '''
        
        self.bboxColor = qtg.QColor(self.settings.value("boxColor","#FFFFFF",str))
        # Set window related properties
        self.setStyleSheet(stsheet2)
        self.setWindowTitle("Exero")

        # todo: add shortcut
        '''# set Menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        optionMenu = menubar.addMenu("Options")
        helpMenu = menubar.addMenu("Help")

        self.openFileAction = fileMenu.addAction("Open...",self.openFile)
        #fileMenu.addAction("Save...",)
        #recentFilesMenu = qtw.QMenu("Recent Files...",self)
        #recentFilesMenu.setDisabled(True)
        #fileMenu.addMenu(recentFilesMenu)
        self.closeFileAction = fileMenu.addAction("Close File",self.closeVideoImage)
        fileMenu.addAction("Settings",self.show_settings)#Keyboard Shortcuts  dict
        fileMenu.addAction("Exit")

        self.playPauseAction = optionMenu.addAction("Play/Pause",self.playPauseBtn.click)
        #optionMenu.addAction("Pause Video")
        #optionMenu.addAction("Start Detection")
        #optionMenu.addAction("Stop Detection")
        optionMenu.addAction("Start/Stop Raw Video Recording",self.rVidRecToggle.toggle)
        optionMenu.addAction("Start/Stop Detection Video Recording",self.rVidRecToggle.toggle)
        optionMenu.addAction("Capture Frame",self.capFrameBtn.click)
        optionMenu.addAction("Add Bookmark",self.addBkmrkIconLbl.click)
        optionMenu.addAction("View Bookmarks",self.viewBkmrkBtn.click)
        optionMenu.addAction("Dataset Generation",self.dsGenrToggle.toggle)#check box





        helpMenu.addAction("Help",self.showHelp)
        helpMenu.addAction("About",self.showAbout)'''



        # Making label which will not be displayed to fix the font-weight problem
        self.extraLabel = qtw.QLabel("invisible")
        self.extraLabel.setFixedWidth(0)

        # Set logo
        self.final_logo = qtg.QPixmap(':/icons/final_fyp_logo2.svg')#.scaledToWidth(100,qtc.Qt.SmoothTransformation)
        self.setWindowIcon(qtg.QIcon(self.final_logo.scaledToWidth((70.278*self.widthScale)+0.5,qtc.Qt.SmoothTransformation))) # 50
        
        # Set base layout with a widget
        self.baseWidget = qtw.QWidget(self)
        self.baseLayout = qtw.QHBoxLayout()
        self.baseWidget.setLayout(self.baseLayout)
        self.setCentralWidget(self.baseWidget)
        self.baseLayout.addWidget(self.extraLabel)
        #print(self.baseLayout.spacing())
        # Set Spacing to 0. Allows child widgets to stick together
        self.baseLayout.setSpacing(0)
        self.baseLayout.setContentsMargins(0,0,0,0)
        #print(self.baseLayout.spacing())
        
        self.SPLay = qtw.QVBoxLayout()
        self.SPWidget = qtw.QWidget()
        self.SPWidget.setLayout(self.SPLay)
        self.baseLayout.addWidget(self.SPWidget)
        self.SPWidget.setFixedWidth((491.95 * self.widthScale)+0.5)  #350
        self.SPLay.setSpacing(0)
        self.SPLay.setContentsMargins(0,0,0,0)
        self.SPWidget.setObjectName("SPWid")

        # Side Panel layout
        #self.SPLay1= qtw.QVBoxLayout()
        self.SPLay1 = qtw.QGridLayout()
        self.SPWidget1 = qtw.QWidget()
        self.SPWidget1.setLayout(self.SPLay1)
        self.SPLay.addWidget(self.SPWidget1)


        # Bookmark panel layout
        self.SPLay2 = qtw.QGridLayout()
        self.SPWidget2 = qtw.QWidget()
        self.SPWidget2.setLayout(self.SPLay2)
        self.SPLay.addWidget(self.SPWidget2)
        self.bkmrkLbl = qtw.QLabel("Bookmarks")
        self.bkmrkLbl.setObjectName("bkmrkLbl")
        self.bkmrkLbl.setContentsMargins((14 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5, (14 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5)  # 10,20,10,20  # args: left top right bottom
        self.scroll = qtw.QScrollArea()
        #self.scroll.setFixedSize((210.9375*self.widthScale)+0.5,(140.556*self.heightScale)+0.5)  # 150,100
        #self.scroll.setFixedSize((400*self.widthScale)+0.5,(140.556*self.heightScale)+0.5)
        self.scroll.setSizePolicy(qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Expanding)
        self.bkmrkDisplay = qtw.QWidget()
        self.bkmrkDisplayLayout = qtw.QGridLayout()
        self.bkmrkDisplay.setLayout(self.bkmrkDisplayLayout)
        
        '''px = 0
        py = -1
        for x in range(5):
            btn = qtw.QPushButton(str(x))
            btn.setFixedSize((70.278*self.widthScale)+0.5,(70.3125*self.heightScale)+0.5) #50,50
            if py==1:
                px += 1
                py = 0
            else:
                py += 1
            self.bkmrkDisplayLayout.addWidget(btn,px,py)'''
        #self.scroll.setWidget(self.bkmrkDisplay)
        self.backBtn = qtw.QPushButton("Back")
        self.backBtn.setFixedSize((281.11 * self.widthScale)+0.5,(42.19 * self.heightScale)+0.5)
        self.backBtn.setGraphicsEffect(qtw.QGraphicsDropShadowEffect(blurRadius=(8.4*self.widthScale)+0.5, xOffset=0, yOffset=(4.21*self.heightScale)+0.5, color=qtg.QColor(201,201,201,204)))
        self.backBtnSpace = qtw.QWidget()
        self.backBtnSpace.setFixedHeight((14 * self.heightScale)+0.5) #(10)
        self.space4 = qtw.QWidget()
        self.space4.setSizePolicy(qtw.QSizePolicy.Preferred,qtw.QSizePolicy.Preferred)

        self.SPLay2.addWidget(self.bkmrkLbl,0,0)
        #self.SPLay2.addWidget(self.scroll,1,0)
        self.SPLay2.addWidget(self.space4,2,0)
        self.SPLay2.addWidget(self.backBtn,3,0,qtc.Qt.AlignHCenter)
        self.SPLay2.addWidget(self.backBtnSpace,4,0,qtc.Qt.AlignHCenter)
        
        #self.SPWidget2.setFixedHeight(0)
        self.SPWidget2.setVisible(False)

        # Side Panel Collapse button
        ##self.collapse = qtg.QPixmap(r"D:\zeeshan work\fyp gui\Exero\exero\collapse.svg")
        ##self.expand = qtg.QPixmap(r"D:\zeeshan work\fyp gui\Exero\exero\expand.svg")
        self.collapse = qtg.QPixmap(":/icons/collapse.svg")
        self.expand = qtg.QPixmap(":/icons/expand.svg")

        self.btn = qtw.QPushButton()
        self.btn.setFixedWidth((30.9 * self.widthScale)+0.5) # 22
        self.btn.setObjectName("sidePanelBtn")
        self.btn.setIcon(qtg.QIcon(self.collapse))
        #self.btn.set
        

        # Side Panel Internal Widgets
        self.detLbl = qtw.QLabel("Details")
        self.detLbl.setObjectName("details")
        self.detLbl.setContentsMargins((14 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5, (14 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5)  # 10,20,10,20  # args: left top right bottom
        #print("margin ",self.detLbl.margin())
        self.modeLbl = qtw.QLabel("Mode")
        self.modeLbl.setContentsMargins((14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5, (14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5) #(10,2, 10,2)
        self.modeLbl.setToolTip("Current mode of function. Can be live, recorded video or static picture.")
        #self.modeVal = qtw.QLabel("-")
        #self.modeVal = qtw.QLabel("This is one heck of a long text -- ")
        self.modeVal = marqueeLabel(parent= self.SPWidget)
        #self.modeVal.setText("This is one heck of a long text This is one heck of a long text")
        self.modeVal = qtw.QLabel("-")
        #self.modeVal.setFixedWidth(192)
        self.modeVal.setMinimumWidth((182.7 * self.widthScale)+0.5) #130
        
        #print("self.modeVal", self.modeVal.geometry(),self.rect(),self.width())
        self.FPSLbl = qtw.QLabel("FPS")
        self.FPSLbl.setContentsMargins((14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5, (14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5) #(10,2, 10,2)
        self.FPSLbl.setToolTip("Frames being generated per Second")
        #self.FPSVal = qtw.QLabel("-")
        self.FPSVal = marqueeLabel(parent= self.SPWidget)
        self.FPSVal.setText("-")
        self.infLbl = qtw.QLabel("Inference time per frame")
        self.infLbl.setContentsMargins((14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5, (14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5) #(10,2, 10,2)
        self.infLbl.setToolTip("Time algorithm takes to process a frame")
        self.infVal = qtw.QLabel("-")
        self.infVal.setMaximumWidth((182.7 * self.widthScale)+0.5)
        print("self.infVal.contentsMargins()",self.infVal.contentsMargins())
        self.infVal.setContentsMargins((10 * self.widthScale)+0.5,0,0,0)
        self.modeVal.setContentsMargins((10 * self.widthScale)+0.5,0,0,0)
        #self.infVal = marqueeLabel(parent= self.SPWidget)
        #self.infVal.setText("-")
        self.lastDetectLbl = qtw.QLabel("Time since last detection")
        self.lastDetectLbl.setContentsMargins((14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5, (14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5) #(10,2, 10,2)
        self.lastDetectLbl.setToolTip("Time since last detection was made. This is relative to the accuracy threshold a the time, thus changing threshold would have no effect on previous positive detection.")
        #self.lastDetectVal = qtw.QLabel("-")
        self.lastDetectVal = marqueeLabel(parent= self.SPWidget)
        self.lastDetectVal.setText("-")
        self.rPathLbl = qtw.QLabel("Video recording path")
        self.rPathLbl.setContentsMargins((14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5, (14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5) #(10,2, 10,2)
        self.rPathLbl.setToolTip("Path where recording is saved")
        #self.rPathVal = qtw.QLabel("-")
        self.rPathVal = marqueeLabel(parent= self.SPWidget)
        self.rPathVal.setText("-")
        #self.rPathVal.setText("apple banana mango")
        self.rPathVal.setToolTip(self.rPathVal.text())
        self.rVidRecLbl = qtw.QLabel("Live raw video recording")
        self.rVidRecLbl.setContentsMargins((14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5, (14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5) #(10,2, 10,2)
        self.rVidRecToggle = Switch(widthScale = self.widthScale, heightScale = self.heightScale)
        self.folder = qtg.QPixmap(':/icons/icons8-folder.svg').scaledToWidth((22.489*self.widthScale)+0.5,qtc.Qt.SmoothTransformation) #16
        #self.rFolderIconLbl = qtw.QLabel()
        self.rFolderIconLbl = clickLabel()
        self.rFolderIconLbl.setPixmap(self.folder)
        self.rFolderIconLbl.setToolTip("Select video recording destination")
        self.rFolderIconLbl.clicked.connect(lambda: self.saveFile("rVRDir"))
        self.rFolderIconLbl.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.rFolderIconLbl.setFixedWidth(self.folder.width())
        self.dVidRecLbl = qtw.QLabel("Live detection video recording")
        self.dVidRecLbl.setContentsMargins((14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5, (14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5) #(10,2, 10,2)
        self.dVidRecToggle = Switch(widthScale = self.widthScale, heightScale = self.heightScale)
        self.dFolderIconLbl = clickLabel()
        self.dFolderIconLbl.setPixmap(self.folder)
        self.dFolderIconLbl.setToolTip("Select video recording destination")
        self.dFolderIconLbl.clicked.connect(lambda: self.saveFile("dVRDir"))
        self.dFolderIconLbl.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.dFolderIconLbl.setFixedWidth(self.folder.width())
        #print("folder",self.folder.width())
        self.dsGenrLbl = qtw.QLabel("Dataset generation")
        self.dsGenrLbl.setContentsMargins((14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5, (14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5) #(10,2, 10,2)
        self.dsGenrToggle = Switch(widthScale = self.widthScale, heightScale = self.heightScale)
        self.dsFolderIconLbl = clickLabel()
        self.dsFolderIconLbl.setPixmap(self.folder)
        self.dsFolderIconLbl.setToolTip("Select dataset destination directory")
        self.dsFolderIconLbl.clicked.connect(lambda: self.saveFile("dbGenrDir"))
        self.dsFolderIconLbl.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.dsFolderIconLbl.setFixedWidth(self.folder.width())
        #print("self.dsFolderIconLbl.width()",self.dsFolderIconLbl.width())
        self.addBkmrkLbl = qtw.QLabel("Add Bookmark")
        self.addBkmrkLbl.setContentsMargins((14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5, (14 * self.widthScale)+0.5,0) #(10,2, 10,0)
        self.bkmrkTitle = qtw.QLineEdit("",self,placeholderText='Bookmark title (optional)')
        self.bkmrkTitle.setContentsMargins((14 * self.widthScale)+0.5,0, (14 * self.widthScale)+0.5,0) #(10,0,10,0)
        self.addBkmrkIconLbl = clickLabel()
        self.bookmark_add = qtg.QPixmap(':/icons/bookmark_add.svg').scaledToWidth((25.3*self.widthScale)+0.5,qtc.Qt.SmoothTransformation) #18
        self.addBkmrkIconLbl.setPixmap(self.bookmark_add)
        #self.addBkmrkNotifLbl = qtw.QLabel("Bookmark saved")
        self.addBkmrkNotifLbl = qtw.QLabel("")
        self.addBkmrkNotifLbl.setContentsMargins((21.08 * self.widthScale)+0.5,0, (14 * self.widthScale)+0.5,(2.8125 * self.heightScale)+0.5) #(15,0, 10,2)
        self.addBkmrkNotifLbl.setObjectName("addBkmrkNotifLbl")
        self.space = qtw.QWidget()
        self.space.setSizePolicy(qtw.QSizePolicy.Preferred,qtw.QSizePolicy.Expanding)

        self.viewBkmrkBtn = qtw.QPushButton("View bookmarks")
        self.viewBkmrkBtn.setFixedSize((281.11 * self.widthScale)+0.5,(42.19 * self.heightScale)+0.5) #(200,30)
        self.crtSysBtn = qtw.QPushButton("Correct system")
        self.crtSysBtn.setFixedSize((281.11 * self.widthScale)+0.5,(42.19 * self.heightScale)+0.5) #(200,30)
        self.capFrameBtn = qtw.QPushButton("Capture frame")
        self.capFrameBtn.setFixedSize((281.11 * self.widthScale)+0.5,(42.19 * self.heightScale)+0.5) #(200,30)
        self.space2 = qtw.QWidget()
        self.space2.setSizePolicy(qtw.QSizePolicy.Preferred,qtw.QSizePolicy.Maximum)
        self.space2.sizeHint = lambda : qtc.QSize((281.11 * self.widthScale)+0.5,(42.19 * self.heightScale)+0.5) #(200,30)
        #self.pauseBtn = qtw.QPushButton("Pause")
        #self.pauseBtn.setFixedSize((281.11 * self.widthScale)+0.5,(42.19 * self.heightScale)+0.5) #(200,30)
        #self.pauseBtn.setContentsMargins(0,0,20,0)
        self.btnSpace1 = qtw.QWidget()
        #self.btnSpace1.setFixedHeight((10 * self.heightScale)+0.5) #(10)
        self.btnSpace2 = qtw.QWidget()
        #self.btnSpace2.setFixedHeight((10 * self.heightScale)+0.5) #(10)
        self.btnSpace1.setSizePolicy(qtw.QSizePolicy.Maximum,qtw.QSizePolicy.Maximum)
        self.btnSpace2.setSizePolicy(qtw.QSizePolicy.Maximum,qtw.QSizePolicy.Maximum)
        self.btnSpace1.sizeHint = lambda : qtc.QSize((281.11 * self.widthScale)+0.5,(20 * self.heightScale)+0.5) #(200,30)
        self.btnSpace2.sizeHint = lambda : qtc.QSize((281.11 * self.widthScale)+0.5,(20 * self.heightScale)+0.5) #(200,30)

        #print("self.pauseBtn.contentsMargins",self.pauseBtn.contentsMargins())
        #self.dsGenrLbl.setAlignment
        
        
        self.capFrameBtn.clicked.connect(self.emitSingleFrame)
        self.crtSysBtn.clicked.connect(self.correctSystemHandler)

        # adding widgets to side panel
        self.SPLay1.addWidget(self.detLbl,0,0)
        self.SPLay1.addWidget(self.modeLbl,1,0)
        self.SPLay1.addWidget(self.modeVal,1,1,1,2)
        self.SPLay1.addWidget(self.FPSLbl,2,0)
        self.SPLay1.addWidget(self.FPSVal,2,1,1,2)
        self.SPLay1.addWidget(self.infLbl,3,0)
        self.SPLay1.addWidget(self.infVal,3,1,1,2)
        self.SPLay1.addWidget(self.lastDetectLbl,4,0)
        self.SPLay1.addWidget(self.lastDetectVal,4,1,1,2)
        self.SPLay1.addWidget(self.rPathLbl,5,0)
        self.SPLay1.addWidget(self.rPathVal,5,1,1,2)
        self.SPLay1.addWidget(self.rVidRecLbl,6,0)
        self.SPLay1.addWidget(self.rVidRecToggle,6,1)
        self.SPLay1.addWidget(self.rFolderIconLbl,6,2)
        self.SPLay1.addWidget(self.dVidRecLbl,7,0)
        self.SPLay1.addWidget(self.dVidRecToggle,7,1)
        self.SPLay1.addWidget(self.dFolderIconLbl,7,2)
        self.SPLay1.addWidget(self.dsGenrLbl,8,0)
        self.SPLay1.addWidget(self.dsGenrToggle,8,1)
        self.SPLay1.addWidget(self.dsFolderIconLbl,8,2)
        self.SPLay1.addWidget(self.addBkmrkLbl,9,0)
        self.SPLay1.addWidget(self.bkmrkTitle,10,0,1,2)
        self.SPLay1.addWidget(self.addBkmrkIconLbl,10,2)
        self.SPLay1.addWidget(self.addBkmrkNotifLbl,11,0)
        self.SPLay1.addWidget(self.space,12,0,1,3)
        self.SPLay1.addWidget(self.viewBkmrkBtn,13,0,1,3,qtc.Qt.AlignHCenter)
        self.SPLay1.addWidget(self.btnSpace1,14,0,1,3,qtc.Qt.AlignHCenter)
        self.SPLay1.addWidget(self.crtSysBtn,15,0,1,3,qtc.Qt.AlignHCenter)
        self.SPLay1.addWidget(self.btnSpace2,16,0,1,3,qtc.Qt.AlignHCenter)
        self.SPLay1.addWidget(self.capFrameBtn,17,0,1,3,qtc.Qt.AlignHCenter)
        self.SPLay1.addWidget(self.space2,18,0,1,3)
        #self.SPLay1.addWidget(self.pauseBtn,17,0,1,3,qtc.Qt.AlignHCenter)
        #self.SPLay1.addWidget(self.pauseBtnSpace,18,0,1,3,qtc.Qt.AlignHCenter)

        # Adding effects
        self.viewBkmrkBtn.setGraphicsEffect(qtw.QGraphicsDropShadowEffect(blurRadius=(8.4*self.widthScale)+0.5, xOffset=0, yOffset=(4.21*self.heightScale)+0.5, color=qtg.QColor(201,201,201,204))) #blurRadius=6, xOffset=0, yOffset=3,
        self.crtSysBtn.setGraphicsEffect(qtw.QGraphicsDropShadowEffect(blurRadius=(8.4*self.widthScale)+0.5, xOffset=0, yOffset=(4.21*self.heightScale)+0.5, color=qtg.QColor(201,201,201,204)))
        self.capFrameBtn.setGraphicsEffect(qtw.QGraphicsDropShadowEffect(blurRadius=(8.4*self.widthScale)+0.5, xOffset=0, yOffset=(4.21*self.heightScale)+0.5, color=qtg.QColor(201,201,201,204)))
        #self.pauseBtn.setGraphicsEffect(qtw.QGraphicsDropShadowEffect(blurRadius=(8.4*self.widthScale)+0.5, xOffset=0, yOffset=(4.21*self.heightScale)+0.5, color=qtg.QColor(201,201,201,204)))

        # Center panel widgets
        #self.fLbl = qtw.QLabel("<span style=\"color: #525856; font-family: segoe ui; font-size:22pt; font-weight:200;\">Start detection on <span style=\"color: #D60404;\">live</span> video</span>")
        self.fLbl = clickLabel(text = "<span style=\"color: #525856; font-family: segoe ui; font-size:22pt; font-weight:200;\">Start detection on <span style=\"color: #D60404;\">live</span> video</span>")
        #self.fLbl = qtw.QLabel("Start detection on live video")
        self.fLbl.setObjectName("fLbl")
        self.fLbl.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.fLbl.clicked.connect(self.handleLiveVideo)
        self.orLbl = qtw.QLabel("Or")
        self.orLbl.setObjectName("orLbl")
        self.tLbl = qtw.QLabel("Drag and drop pre-recorded video/image or ")
        self.tLbl.setObjectName("tLbl")
        self.ctbLbl = clickLabel(text = "click to browse", enterStyleSheet="#ctbLbl{text-decoration: underline;}", leaveStyleSheet="#ctbLbl{text-decoration: none;}")
        self.ctbLbl.setObjectName("ctbLbl")
        self.ctbLbl.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.ctbLbl.clicked.connect(self.openFile)

        self.placeholderWidget = qtw.QWidget()
        self.placeholderLayout = qtw.QHBoxLayout()
        #self.placeholderLayout = qtw.QGridLayout()
        self.placeholderWidget.setLayout(self.placeholderLayout)
        self.placeholderWidget.setObjectName("PLA")
        #self.SPLay1.addWidget(label)
        #self.SPLay1.addWidget(btn2)
        self.flag = True
        self.SPWidget1.setObjectName("SPWid1")
        
        #self.aw = qtw.QWidget()
        self.a = qtw.QVBoxLayout()
        self.aw = qtw.QWidget()
        self.aw.setLayout(self.a)
        #print(self.a.spacing())
        self.a.setSpacing(0)
        #print(self.a.spacing())
        self.baseLayout.addWidget(self.aw)
        #self.rLayout.addWidget(self.aw)
        self.a.setObjectName("a")

        self.a.addWidget(self.btn)

        self.rWidget = qtw.QWidget()
        self.rLayout = qtw.QHBoxLayout()
        self.rWidget.setLayout(self.rLayout)
        self.baseLayout.addWidget(self.rWidget)
        self.rLayout.setSpacing(0)
        self.rWidget.setContentsMargins(0,0,0,0)

        self.lSpace = qtw.QWidget()
        #self.baseLayout.addWidget(self.lSpace)
        self.rLayout.addWidget(self.lSpace)
        #self.lSpace.sizeHint = lambda: qtc.QSize((351.39*self.widthScale)+0.5,(351.56*self.heightScale)+0.5)#(250,250)
        #self.lSpace.setSizePolicy(qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Expanding)

        self.lSpace.sizeHint = lambda: qtc.QSize((28.11 * self.widthScale)+0.5,(351.56*self.heightScale)+0.5)#(250,250)
        self.lSpace.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)
        self.lSpace.setObjectName("LSpace")
        #self.space3.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Fixed)
        #self.a.addWidget(qtw.QLabel("helllllooo"))
        #print("lSpace",self.lSpace.sizePolicy().horizontalPolicy())
        self.cWidget = qtw.QWidget()
        self.cLayout = qtw.QVBoxLayout()
        self.cWidget.setLayout(self.cLayout)
        #self.baseLayout.addWidget(self.cWidget)
        self.rLayout.addWidget(self.cWidget)
        self.cSpaceT = qtw.QWidget()
        self.cSpaceB = qtw.QWidget()
        self.cLayout.addWidget(self.cSpaceT)
        self.cLayout.addWidget(self.fLbl)
        self.cLayout.addWidget(self.orLbl)
        #self.cLayout.addWidget(self.ctbLbl)
        self.cLayout.addWidget(self.placeholderWidget)
        self.cLayout.addWidget(self.cSpaceB)
        self.cLayout.setSpacing(0)
        self.cWidget.setContentsMargins(0,0,0,0)
        self.cSpaceT.setSizePolicy(qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Expanding)
        self.cSpaceB.setSizePolicy(qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Expanding)
        self.fLbl.setContentsMargins(0, 0, 0, 0) #(20,0,0,0) LTRB
        self.orLbl.setContentsMargins(0, (35.16 * self.heightScale)+0.5, 0, (35.16 * self.heightScale)+0.5) #(20,25,0,25)
        self.tLbl.setContentsMargins(0,0,0,0)
        #self.fLbl.contentsRect
        self.fLbl.setMargin(0)
        self.fLbl.setIndent(0)
        self.fLbl.setFixedWidth((515.84*self.widthScale)+0.5) #367  # added 28 to the 515 as the text was being clipped. 28 as its been left margin
        #print()
        #print("self.fLbl",self.fLbl.contentsRect(),self.fLbl.contentsMargins())
        self.placeholderWidget.setContentsMargins(0,0,0,0)#(10,0,0,0)
        self.placeholderLayout.setSpacing(0)
        self.placeholderLayout.setContentsMargins(0,0,0,0)
        
        #print("spacing",self.placeholderWidget.contentsMargins().left(),self.placeholderLayout.spacing(),self.placeholderLayout.contentsMargins().left(),self.placeholderLayout.horizontalSpacing(),self.placeholderLayout.originCorner())
        self.placeholderLayout.addWidget(self.tLbl)
        self.placeholderLayout.addWidget(self.ctbLbl)
        self.fLbl.setVisible(True)
        #print(self.placeholderWidget.contentsRect(),self.placeholderWidget.rect(),self.placeholderWidget.pos(),self.placeholderWidget.geometry(),self.placeholderWidget.frameGeometry(),self.placeholderWidget.contentsMargins().left(),self.orLbl.contentsRect(),self.orLbl.height())
        #print("                           ",self.fLbl.isVisible(),self.fLbl.width())
        #self.ctbLbl.setStyleSheet("#ctbLbl{text-decoration: underline;}")
        #print(self.SPWidget1.height(),self.SPWidget1.maximumHeight,self.SPWidget1.minimumHeight)
        #print("ss ",self.ctbLbl.styleSheet())

        self.rSpace = qtw.QWidget()
        #self.baseLayout.addWidget(self.rSpace)
        self.rLayout.addWidget(self.rSpace)
        self.rSpace.sizeHint = lambda: qtc.QSize((351.39*self.widthScale)+0.5,(351.56*self.heightScale)+0.5)#(250,250)
        self.rSpace.setSizePolicy(qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Expanding)
        #line_edit = qtw.QLineEdit("default value",self)
        #self.a.addWidget(line_edit)
        self.a.setContentsMargins(0,0,0,0)
        #self.SPWidget1.resizeEvent()
        #btn.setFixedHeight(self.SPWidget1.height())
        self.btn.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.MinimumExpanding)
        #print("rSpace",self.rSpace.sizePolicy().horizontalPolicy())
        #self.baseLayout.addWidget(self.qwid2)
        #self.baseLayout.addWidget(self.aw)
        
        #grid_layout.addWidget(btn,0,1)
        #grid_layout.addWidget(self.qwid2,0,0)
        #grid_layout.setHorizontalSpacing
        #grid_layout.setHorizontalSpacing(0)
        #grid_layout.addWidget(btn2,1,0)
        self.btn.clicked.connect(self.onBtnClick)
        self.viewBkmrkBtn.clicked.connect(self.showBkmrks)
        self.backBtn.clicked.connect(self.showDetails)
        #self._SPWidget1Height = self.SPWidget1.height()
        #btn.clicked.connect(btn2.setFixedWidth(0))
        # End main UI code)
        # TEST

        '''self.cWidget.setAcceptDrops(True)
        self.cWidget.dragEnterEvent = self.customDragEnterEvent
        self.cWidget.dropEvent = self.customDropEvent
        self.lSpace.setAcceptDrops(True)
        self.lSpace.dragEnterEvent = self.customDragEnterEvent
        self.lSpace.dropEvent = self.customDropEvent
        self.rSpace.setAcceptDrops(True)
        self.rSpace.dragEnterEvent = self.customDragEnterEvent
        self.rSpace.dropEvent = self.customDropEvent'''
        self.rWidget.setAcceptDrops(True)
        self.rWidget.dragEnterEvent = self.customDragEnterEvent
        self.rWidget.dropEvent = self.customDropEvent
        # TEST
        
        ##self.wav_file = r"D:\zeeshan work\fyp gui\Exero\exero\bell.wav"
        self.wav_file = ":/audio/bell.wav"
        #self.player = qtmm.QSoundEffect()
        #self.player.setSource(qtc.QUrl.fromLocalFile(self.wav_file))
        #self.pauseBtn.clicked.connect(self.player.play)
        
        self.chkVar = 0
        #self.player = qtmm.QMediaPlayer(flags = qtmm.QMediaPlayer.LowLatency)
        #self.player.setAudioRole(qtmm.QAudio.GameRole)
        #self.player.setMedia(qtmm.QMediaContent(qtc.QUrl.fromLocalFile(self.wav_file)))
        self.player = qtmm.QSound(self.wav_file)
        #self.playAlarm.connect(self.player.play)
        #self.player.loadedChanged.connect(lambda : print("loaded changeddd",self.player.status()))

        self.vidWidget = qtw.QWidget()
        self.vidLayout = qtw.QGridLayout()
        self.vidWidget.setLayout(self.vidLayout)
        self.baseLayout.addWidget(self.vidWidget)
        self.vidLayout.setSpacing(0)
        self.vidWidget.setContentsMargins(0,0,0,0)
        self.vidWidget.setVisible(False)

        self.vidLSpace = qtw.QWidget()
        self.vidRSpace = qtw.QWidget()
        self.vidTSpace = qtw.QWidget()
        self.vidTTwoSpace = qtw.QWidget()
        self.vidBSpace = qtw.QWidget()

        self.vidLSpace.setObjectName("vidLSpace")
        self.vidRSpace.setObjectName("vidRSpace")
        self.vidTSpace.setObjectName("vidTSpace")
        self.vidBSpace.setObjectName("vidBSpace")

        #self.vidLSpace.setStyleSheet("QWidget{ background-color: yellow; }")
        #self.vidRSpace.setStyleSheet("QWidget{ background-color: blue; }")
        #self.vidBSpace.setStyleSheet("QWidget{ background-color: green; }")
        #self.vidTSpace.setStyleSheet("QWidget{ background-color: red; }")

        self.vidLSpace.setSizePolicy(qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Expanding)
        self.vidRSpace.setSizePolicy(qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Expanding)
        #self.vidTSpace.setSizePolicy(qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Expanding)
        self.vidTTwoSpace.setSizePolicy(qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Expanding)
        self.vidBSpace.setSizePolicy(qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Expanding)

        '''self.vidLayout.addWidget(self.vidLSpace,0,0,4,1)
        self.vidLayout.addWidget(self.vidTSpace,0,1,2,2)
        self.vidLayout.addWidget(self.vidRSpace,2,2,2,1)
        self.vidLayout.addWidget(self.vidBSpace,3,1,1,1)'''
        self.vidLayout.addWidget(self.vidLSpace,0,0,4,1)
        self.vidLayout.addWidget(self.vidTTwoSpace,1,1,1,2)
        self.vidLayout.addWidget(self.vidTSpace,0,1,1,2)
        self.vidLayout.addWidget(self.vidRSpace,2,2,2,1)
        self.vidLayout.addWidget(self.vidBSpace,3,1,1,1)

        self.vidLbl = qtw.QLabel()
        #self.vidLayout.addWidget(self.lbl,0,0)
        self.vidLayout.addWidget(self.vidLbl,2,1,1,1)

        #self.closeVidLbl = clickLabel("X", modifyStyleSheet = False)
        self.closeVidLbl = clickLabel(text = "<span>&#x2715;</span>")
        self.closeVidLbl.setObjectName("closeVidLbl")
        self.closeVidLbl.setToolTip("Close Current Video")
        self.closeVidLbl.clicked.connect(self.closeVideoImage)

        #self.closeVidLbl.setStyleSheet("#closeVidLbl{font-size: 16pt;}")
        
        self.oldCloseVidLblEnterEvent = self.closeVidLbl.enterEvent
        self.oldCloseVidLblLeaveEvent = self.closeVidLbl.leaveEvent
        self.closeVidLbl.enterEvent = self.customEnterEvent
        self.closeVidLbl.leaveEvent = self.customLeaveEvent

        self.vidLayout.addWidget(self.closeVidLbl,0,3,1,1)

        self.closeVidSpace = qtw.QWidget()
        self.vidBSpace.setSizePolicy(qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Expanding)
        self.vidLayout.addWidget(self.closeVidSpace,1,3,3,1)
        #self.closeVidSpace.setStyleSheet("QWidget{ background-color: pink; }")

        self.vidBottomBar = qtw.QWidget()
        self.vidBottomBarLayout = qtw.QGridLayout()
        self.vidBottomBar.setLayout(self.vidBottomBarLayout)
        self.vidBottomBar.setObjectName("vidBottomBar")

        #self.vidSlider = qtw.QSlider(parent = self,minimum=0, maximum = 1000, orientation=qtc.Qt.Horizontal)
        
        '''self.vidSlider.setStyleSheet(\
        "QSlider::groove:horizontal {\
        border: 1px solid #999999;\
        height: 8px; \
        background-color: blue;\
        margin: -4px 0;\
        }QSlider::handle:horizontal {\
        background-color: red;\
        border: 1px solid #5c5c5c;\
        border-radius: 0px;\
        border-color: black;\
        height: 8px;\
        width: 6px;\
        margin: -8px 2; \
        }\
        QSlider::sub-page:horizontal {\
        background: yellow;\
        }")        border: 1px solid #bbb;
        border-radius: 4px;        background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
            stop: 0 #66e, stop: 1 #bbf);
        background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
            stop: 0 #bbf, stop: 1 #55f);'''
        self.vidQSS = '''
        QSlider{
            min-height: 52px;
            max-height: 52px;
            min-width: 100px;
            max-width: 200px;
        }
        QSlider::groove:horizontal {
        background: #A0CEE4;
        height: 20px;
        }

        QSlider::sub-page:horizontal {
        background: #A0CEE4;
        
        height: 20px;
        
        }

        QSlider::add-page:horizontal {
        background: #fff;
        
        height: 20px;
        
        }

        QSlider::handle:horizontal {
        
        background: #3B9EC6;
        height: 20px;
        width: 5px;
        margin-top: -2px;
        margin-bottom: -2px;
        
        }

        QSlider::sub-page:horizontal:disabled {
        background: #bbb;
        border-color: #999;
        }

        QSlider::add-page:horizontal:disabled {
        background: #eee;
        border-color: #999;
        }

        QSlider::handle:horizontal:disabled {
        background: #eee;
        border: 1px solid #aaa;
        border-radius: 4px;
        }
        
        '''
        self.vidSliderHoverQSS = f'''
        QSlider{{{{
            min-height: {(52* self.heightScale)+0.5}px;
            max-height: {(52* self.heightScale)+0.5}px;
        }}}}
        QSlider::groove:horizontal {{{{
        background: #A0CEE4;
        height: {(20* self.heightScale)+0.5}px;
        }}}}

        QSlider::sub-page:horizontal {{{{
        background: #A0CEE4;
        
        height: {(20* self.heightScale)+0.5}px;
        
        }}}}

        QSlider::add-page:horizontal {{{{
        background: #fff;
        
        height: {(20* self.heightScale)+0.5}px;
        
        }}}}

        QSlider::handle:horizontal {{{{
        
        background: #3B9EC6;
        height: {(20* self.heightScale)+0.5}px;
        width: {{}}px;
        margin-top: {{}}px;
        margin-bottom: {{}}px;
        
        }}}}

        QSlider::sub-page:horizontal:disabled {{{{
        background: #bbb;
        border-color: #999;
        }}}}

        QSlider::add-page:horizontal:disabled {{{{
        background: #eee;
        border-color: #999;
        }}}}

        QSlider::handle:horizontal:disabled {{{{
        background: #eee;
        border: {(1* self.widthScale)+0.5}px solid #aaa;
        border-radius: {(4* self.widthScale)+0.5}px;
        }}}}
        
        '''
        self.vidSlider = customSlider(parent = self,minimum=0, maximum = 1000, orientation=qtc.Qt.Horizontal,animationStartValue = qtc.QSize((5 * self.widthScale)+0.5,(-2 * self.heightScale)+0.5),animationEndValue = qtc.QSize((20 * self.widthScale)+0.5,(-10 * self.heightScale)+0.5),QSS = self.vidSliderHoverQSS,animationDuration = 250)
        #self.vidSlider.setStyleSheet(self.vidQSS)
        #self.vidSlider.setObjectName("vidSlider")
        #self.old = self.vidSlider.event
        #self.vidSlider.event = self.vidSliderMouseMoveEvent
        #self.vidSlider.mouseMoveEvent = self.vidSliderMouseMoveEvent

        '''self.old1 = self.vidSlider.enterEvent
        self.vidSlider.enterEvent = self.vidSliderEnterEvent
        self.old2 = self.vidSlider.leaveEvent
        self.vidSlider.leaveEvent = self.vidSliderLeaveEvent
        #self.vidSlider.setMouseTracking(True)
        self.vidSlider.apple = self.vidSliderAnimate'''
        self.currentTimeLbl = qtw.QLabel("00:00")
        self.totalTimeLbl = qtw.QLabel("00:00")
        self.isPlayFlag = True
        self.playPauseBtn = qtw.QPushButton()
        self.playIcon = qtg.QIcon()#'icons8-play-96.png'
        ##self.playIcon.addPixmap(qtg.QPixmap('D:/zeeshan work/fyp gui/Exero/exero/playIcon.svg'), qtg.QIcon.Normal)
        self.playIcon.addPixmap(qtg.QPixmap(':/icons/playIcon.svg'), qtg.QIcon.Normal)
        self.pauseIcon = qtg.QIcon()#'icons8-play-96.png'
        ##self.pauseIcon.addPixmap(qtg.QPixmap('D:/zeeshan work/fyp gui/Exero/exero/pauseIcon.svg'), qtg.QIcon.Normal)
        self.pauseIcon.addPixmap(qtg.QPixmap(':/icons/pauseIcon.svg'), qtg.QIcon.Normal)

        #self.playPauseBtn.setIcon(self.playIcon)
        self.playPauseBtn.setIcon(self.pauseIcon)

        self.playPauseBtn.clicked.connect(self.playPauseBtnClickHandler)
        
        self.vidBottomBarLblSpacer = qtw.QWidget()
        self.vidBottomBarLblSpacer.setSizePolicy(qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Fixed)
        self.totalTimeLbl.setSizePolicy(qtw.QSizePolicy.Maximum,qtw.QSizePolicy.Maximum)
        self.totalTimeLbl.setContentsMargins(0,0,0,0)
        self.totalTimeLbl.setAlignment(qtc.Qt.AlignLeft)

        #self.totalTimeLbl.setGraphicsEffect(qtw.QGraphicsDropShadowEffect(blurRadius=(6*self.widthScale)+0.5, xOffset=0, yOffset=0, color=qtg.QColor(255,0,0,255)))
        #print(self.totalTimeLbl.size(),self.totalTimeLbl.geometry(),self.totalTimeLbl.getContentsMargins(),self.totalTimeLbl.frameGeometry(),self.totalTimeLbl.frameRect())
        #self.totalTimeLbl.setFixedWidth(50)
        
        self.vidBottomBarLayout.addWidget(self.vidSlider,0,0,1,11)
        self.vidBottomBarLayout.addWidget(self.currentTimeLbl,1,0)
        self.vidBottomBarLayout.addWidget(self.totalTimeLbl,1,10)
        self.vidBottomBarLayout.addWidget(self.playPauseBtn,1,5)
        self.vidBottomBarLayout.addWidget(self.vidBottomBarLblSpacer,1,1,1,10)

        self.vidBottomBarLayout.setSpacing(0)
        self.vidBottomBarLayout.setContentsMargins(0,0,0,0)
        self.vidLayout.addWidget(self.vidBottomBar,4,0,1,3)
        self.vidWidget.setVisible(False)
        self.rWidget.setVisible(True)
        #print(self.vidSlider.singleStep(),self.vidSlider.pageStep(),self.vidSlider.tickInterval())
        self.vidSlider.setSingleStep(100)
        #self.rVidRecToggle.toggled.connect(lambda x: print(self.rVidRecToggle.isChecked(),x))  for testing purpose only

        # bookmark functionality
        self.addBkmrkIconLbl.clicked.connect(self.addBookmark)

        # Menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        optionMenu = menubar.addMenu("Options")
        helpMenu = menubar.addMenu("Help")

        self.openFileAction = fileMenu.addAction("Open...",self.openFile)
        #fileMenu.addAction("Save...",)
        #recentFilesMenu = qtw.QMenu("Recent Files...",self)
        #recentFilesMenu.setDisabled(True)
        #fileMenu.addMenu(recentFilesMenu)
        self.closeFileAction = fileMenu.addAction("Close File",self.closeVideoImage)
        fileMenu.addAction("Settings",self.show_settings)#Keyboard Shortcuts  dict
        fileMenu.addAction("Exit",self.exitRoutine)

        self.playPauseAction = optionMenu.addAction("Play/Pause",self.playPauseBtn.click)
        #optionMenu.addAction("Pause Video")
        #optionMenu.addAction("Start Detection")
        #optionMenu.addAction("Stop Detection")
        optionMenu.addAction("Start/Stop Raw Video Recording",self.rVidRecToggle.toggle)
        optionMenu.addAction("Start/Stop Detection Video Recording",self.rVidRecToggle.toggle)
        optionMenu.addAction("Capture Frame",self.capFrameBtn.click)
        optionMenu.addAction("Add Bookmark",self.addBkmrkIconLbl.click)
        optionMenu.addAction("View Bookmarks",self.viewBkmrkBtn.click)
        optionMenu.addAction("Dataset Generation",self.dsGenrToggle.toggle)#check box

        helpMenu.addAction("Help",self.showHelp)
        helpMenu.addAction("About",self.showAbout)
        self.detectionStarted(False)
        self.show()

    def addBookmark(self):

        if self.detectionFlag == None:
            self.addBkmrkNotifLbl.setText("<span style=\"color: #D60404;\">Start detection first</span>")
        elif self.detectionFlag == 0:
            # detection by live video
            if self.detectionVideoRecordingFlag or self.rawVideoRecordingFlag:
                # if detection video recording happening or raw video recording happening, then proceed.
                #if self.detectionVideoRecordingFlag and self.rawVideoRecordingFlag:
                    # check if both types of recording happening
                    
                if self.detectionVideoRecordingFlag:
                    #time.time()
                    path = self.detectionVideoRecordingPath[:-4]+".txt"
                    frameCount = int((time.time() - self.detectionVideoRecordingStartTime) * self.actualFPS)
                    frameShape = str(list(self.finalConvertedFrame.shape))
                    frameData = str(list(self.finalConvertedFrame.ravel()))    # TODO add mutex lock to prevent crashes
                    if self.bkmrkTitle.text() == "":
                        self.bookmarkObj.write(path,frameCount,"Untitled",frameShape,frameData)
                    else:
                        self.bookmarkObj.write(path,frameCount,self.bkmrkTitle.text(),frameShape,frameData)

                if self.rawVideoRecordingFlag:
                    path = self.rPathVal.text()[:-4]+".txt"
                    frameCount = int((time.time() - self.rawVideoRecordingStartTime) * self.fps)
                    # TODO make a function and put the frame converted code(in display frame) in it and use it here, so that we convert the pixmap with bbox drawn to ndarray and save it here.
                    frameShape = str(list(self.frame.shape))
                    frameData = str(list(self.frame.ravel()))    # TODO add mutex lock to revent crashes
                    if self.bkmrkTitle.text() == "":
                        self.bookmarkObj.write(path,frameCount,"Untitled",frameShape,frameData)
                    else:
                        self.bookmarkObj.write(path,frameCount,self.bkmrkTitle.text(),frameShape,frameData)
                self.bkmrkTitle.setText("")
                self.addBkmrkNotifLbl.setText("<span style=\"color: #8FB0FE;\">Bookmark successfully added</span>")
                self.newBookmarkAddedFlag = True

            else:
                self.addBkmrkNotifLbl.setText("<span style=\"color: #D60404;\">Start detection first</span>")
            
        elif self.detectionFlag == 1:
            # detection by video
            frameShape = str(list(self.frame.shape))
            frameData = str(list(self.frame.ravel()))
            if self.bkmrkTitle.text() == "":
                #self.addBkmrkNotifLbl.setText("No title")
                # self.vidSlider.value() contains video position in terms of frames, so we convert it to seconds
                self.bookmarkObj.write(self.filename[:-4]+".txt",self.vidSlider.value(),"Untitled",frameShape,frameData)
            else:
                self.bookmarkObj.write(self.filename[:-4]+".txt",self.vidSlider.value(),self.bkmrkTitle.text(),frameShape,frameData)
                self.bkmrkTitle.setText("")
            self.addBkmrkNotifLbl.setText("<span style=\"color: #8FB0FE;\">Bookmark successfully added</span>")
            self.newBookmarkAddedFlag = True
        elif self.detectionFlag == 2:
            # detection by image
            self.addBkmrkNotifLbl.setText("<span style=\"color: #D60404;\">Start detection on video first</span>")
        timer = qtc.QTimer()
        timer.singleShot(2000,lambda: self.addBkmrkNotifLbl.setText(""))

    @qtc.pyqtSlot(bool)
    def setRawVideoRecordingStartTime(self,flag):
        self.rawVideoRecordingStartTime = time.time()

    @qtc.pyqtSlot(int)
    def setFPS(self,fps):
        self.fps = fps
        self.FPSVal.setText(str(self.fps))

    #@qtc.pyqtSlot(float)
    @qtc.pyqtSlot(int)
    def setCurrentTime(self,num):

        if self.detectionFlag == 1:        
            if self.fps != None:
                totalSecs = num//self.fps
                mins = totalSecs//60
                secs = totalSecs%60
                self.currentTimeLbl.setText(str(mins)+":"+str(secs))
        elif self.detectionFlag == 0:
            mins = num//60
            secs = num%60
            self.currentTimeLbl.setText(str(mins)+":"+str(secs))
            print(num)

    #@qtc.pyqtSlot(float)
    @qtc.pyqtSlot(int)
    def setTotalTime(self,num):
    
        if self.detectionFlag == 1:
            if self.fps != None:
                totalSecs = num//self.fps
                mins = totalSecs//60
                secs = totalSecs%60
                self.totalTimeLbl.setText(str(mins)+":"+str(secs))
        elif self.detectionFlag == 0:
            mins = num//60
            secs = num%60
            self.totalTimeLbl.setText(str(mins)+":"+str(secs))
        

    def customEnterEvent(self,ev):
        self.closeVidLbl.setGraphicsEffect(qtw.QGraphicsDropShadowEffect(blurRadius=(6*self.widthScale)+0.5, xOffset=0, yOffset=0, color=qtg.QColor(255,0,0)))
        #self.closeVidLbl.setStyleSheet("#closeVidLbl{font-size: 16pt; color: #FF5C56; font-weight: 100;}")
        #self.closeVidLbl.setText("<span style=\"color: #FF5C56;\">&#x2715;</span>")
        return self.oldCloseVidLblEnterEvent(ev)

    def customLeaveEvent(self,ev):
        self.closeVidLbl.setGraphicsEffect(qtw.QGraphicsDropShadowEffect(blurRadius=0, xOffset=0, yOffset=0, color=qtg.QColor(255,0,0)))
        #self.closeVidLbl.setStyleSheet("#closeVidLbl{font-family: Arial; font-size: 16pt; color: #525856; font-weight: 200;}")
        #self.closeVidLbl.setText("<span style=\"color: #525856;\">&#x2715;</span>")
        return self.oldCloseVidLblLeaveEvent(ev)
    
    def playPauseBtnClickHandler(self):
        print("B"*20,self.detectionFlag,self.isPlayFlag,self.allowRecording)
        if self.isPlayFlag:
            # pauses the playing
            self.isPlayFlag = False
            self.allowRecording = False
            self.playPauseBtn.setIcon(self.playIcon)
            self.playPauseBtn.setToolTip("Play")
            if self.detectionFlag != 2:
                self.inter.detectionComplete.disconnect(self.videoObj.emitFrame)
            self.videoObj.getFrame.disconnect(self.inter.detect)
            if self.detectionFlag != 2 and self.detectionVideoRecordingFlag:
                # for detection video recording
                self.detectionVideoRecordingTimer.stop()
            if self.detectionFlag == 1:
                # To stop the raw video recording. We have put check for video by url only
                # because that uses an internal qtimer, so to pause it needs to be stopped.
                # whereas live video doesnot use a timer and is live, therefore no need to
                # stop anything in live video explicitly, just disconnecting signals stops
                # the cycle.
                self.startStopTimerSignal.emit(False)
            if self.detectionFlag == 0:
                self.pauseRVidRecForLiveVidSignal.emit()

        else:
            # resumes the playing
            self.isPlayFlag = True
            self.playPauseBtn.setIcon(self.pauseIcon)
            self.playPauseBtn.setToolTip("Pause")
            if self.detectionFlag != 2:
                self.inter.detectionComplete.connect(self.videoObj.emitFrame)
            self.videoObj.getFrame.connect(self.inter.detect)
            self.inter.detectionComplete.emit()
            self.allowRecording = True
            if self.detectionFlag != 2 and self.detectionVideoRecordingFlag:
                self.detectionVideoRecordingTimer.start()
            if self.detectionFlag == 1:
                self.startStopTimerSignal.emit(True)
            if self.detectionFlag == 0:
                self.resumeRVidRecForLiveVidSignal.emit()


    @qtc.pyqtSlot()
    def closeVideoImage(self):
        
        self.isStopped = True
        self.polypFoundFlag = False
        self.playPauseBtn.setIcon(self.pauseIcon)
        self.playPauseBtn.setToolTip("Pause")
        if self.isPlayFlag:
            if self.detectionFlag != 2:
                self.inter.detectionComplete.disconnect()
            self.videoObj.getFrame.disconnect()
        else:
            self.inter.detectionComplete[np.ndarray,list].disconnect()
        
        self.inter.inferenceTime.disconnect()
        if self.detectionFlag != 2:
            self.rVidRecToggle.toggled.disconnect()
            self.dVidRecToggle.toggled.disconnect()
            #self.startRawVideoRecordingSignal.disconnect()
            self.dsGenrToggle.toggled.disconnect()
        if self.detectionFlag == 0:
            self.pauseRVidRecForLiveVidSignal.disconnect(self.videoObj.pauseRVidRecording)
            self.resumeRVidRecForLiveVidSignal.disconnect(self.videoObj.resumeRVidRecording)
            self.vidSlider.sliderMoved.disconnect()
        elif self.detectionFlag == 1:
            self.startByURLSignal.disconnect()
            self.startStopTimerSignal.disconnect(self.videoObj.startStopTimer)
            self.videoObj.videoEnded.disconnect(self.playPauseBtn.click)
        elif self.detectionFlag == 2:
            self.startByURLSignal.disconnect()
            self.rVidRecToggle.setCheckable(True)
            self.dVidRecToggle.setCheckable(True)
            self.dsGenrToggle.setCheckable(True)

        # check if recording, if recording the stop it
        self.dsGenrHandler(False)
        #manualStopVideoObj = True
        #if self.rVidRecToggle.isChecked():
        if self.rawVideoRecordingFlag:
            self.startRawVideoRecordingSignal.emit(False,self.settings.value("singleVideoFile",False,bool),"",True)
            self.rVidRecToggle.setChecked(False)
            #manualStopVideoObj = False
        
        if self.dVidRecToggle.isChecked():
            #self.detectionVideoRecordingHandler(False)
            self.detectionVideoRecordingStop()
            self.dVidRecToggle.setChecked(False)
        elif self.previousDetectionVideoRecordingSingleFileFlag:
            self.detectionVideoRecordingStop()
        
        if self.dsGenrToggle.isChecked():
            self.dsGenrToggle.setChecked(False)
            self.dsGenrHandler(False)
        #self.startRawVideoRecordingSignal.disconnect()   commented it because it was preventing the signal with false flag to be emmitted!
        
        self.objs[self.video_thread] = self.videoObj
        #self.objs.append(self.video_thread)
        #self.objs.append(self.videoObj)
        
        print("i am about to end this mans whole career!")
        #self.video_thread.quit()
        print("OOOOOOO",threading.get_ident())
        #self.videoObj.destroyed.connect(self.removeFromQueue)
        #self.video_thread.destroyed.connect(self.removeFromQueue)

        #self.video_thread.deleteLater()
        self.video_thread.finished.connect(lambda: print("VIDEO THREAD FINISHED!"))

        self.videoObj.requestDelete.connect(self.killVideoThread)
        self.stopVideoProcessing.connect(self.videoObj.stop)
        self.stopVideoProcessing.connect(self.videoObj.stopVideoProcessing)
        self.stopVideoProcessing.emit()
        #if manualStopVideoObj:
        #    pas
        
        timer = qtc.QTimer()
        timer.singleShot(500, self.clearDetailLblVals)
        timer.start()

        # resetting/syncing the alarm settings
        self.dequeLength = self.settings.value("dequeLength",4,int)
        self.polypDetectedDeque = collections.deque(self.dequeLength*[False], self.dequeLength)
        self.playAlarmflag = True
        #self.videoObj.requestDelete.connect(lambda: print("delete has been requested"))
        #self.videoObj.deleteLater()
        #writeLocker = qtc.QWriteLocker(self.lock)
        #self.vidLbl.deleteLater()
        #writeLocker.unlock()
        print("videoObj",id(self.videoObj))
        print("video thread",id(self.video_thread))

        self.vidWidget.setVisible(False)
        self.rWidget.setVisible(True)
        self.detectionFlag = None
        
        self.detectionStarted(False)

        # delete bookmark references
        if self.SPWidget1.isVisible() == False:
            for widgets in self.refs:
                try:
                    widgets.deleteLater()
                except:
                    pass
            self.refs = list()
            self.showDetails()

        # reset all variables
        self.isPlayFlag = False
        self.allowRecording = False
        self.newBookmarkAddedFlag = True

    def removeFromQueue(self):

        obj = self.sender()
        for x in self.objs.keys():
            if x is obj:
                #self.objs.remove(obj)
                y = self.objs[x]
                self.objs.pop(x)
                print("id removed from list:",id(x),id(y),x,y)
                return
        
        print("no match found!",id(obj),obj,self.objs)

    @qtc.pyqtSlot()
    def killVideoThread(self):
        #print("before ",self.videoObj.objectName(),self.video_thread.objectName())
        print(id(self.sender()),self.objs,self.sender())
        for localVideo_thread,localVideoObj in self.objs.items():
            if localVideoObj is self.sender():
                localVideoObj.disconnect()
                self.objs.pop(localVideo_thread)
                localVideoObj.deleteLater()
                localVideo_thread.quit()
                localVideo_thread.wait(3000)
                localVideo_thread.deleteLater()
                print("DELETED")
                return
        
        #self.vidLayout.removeWidget(self.vidLbl)
        self.vidLbl.clear()
        #self.vidLbl.deleteLater()
        #del self.frame
        #del self.vidLbl
        #self.repaint(0,0,2000,2000)
        #self.vidWidget.setUpdatesEnabled(True)
        #self.vidWidget.update()
        #self.vidWidget.repaint()
        print("after no obj killed!",self.objs,self.sender())

        '''self.videoObj.disconnect()
        self.videoObj.deleteLater()
        self.video_thread.quit()
        self.video_thread.wait(3000)
        self.video_thread.deleteLater()'''
        #print("after ",self.videoObj.objectName())
        #print("after ",self.videoObj.objectName(),self.video_thread.objectName())
    '''def vidSliderEnterEvent(self,ev):
        print("entering")
        return self.old1(ev)
    
    def vidSliderLeaveEvent(self,ev):
        print("leaving")
        return self.old2(ev)

    def vidSliderMouseMoveEvent(self,ev):
        #print(ev.pos(),ev.localPos(),ev.screenPos(),ev.type())
        #if ev.x()>0:
        #    self.vidSlider.setStyleSheet(self.vidSliderHoverQSS)
        #    self.old(ev)
        print(ev.type())
        return self.old(ev)'''

    def clearDetailLblVals(self):
        self.modeVal.setText("-")
        self.FPSVal.setText("-")
        self.rPathVal.setText("-")
        self.rPathVal.setToolTip("")
        self.lastDetectVal.setText("-")
        self.infVal.setText("-")
    
    @qtc.pyqtSlot()
    def correctSystemHandler(self):
        if not self.isStopped: #detection still running
            if type(self.frame) == np.ndarray:
                self.singleFrame.emit(self.frame,self.settings.value("dbGenrDir",qtc.QDir.homePath(),str),"correctSystem_"+str(self.polypFoundFlag)+"_")


    @qtc.pyqtSlot()
    def emitSingleFrame(self):
        if type(self.frame) == np.ndarray:
            self.singleFrame.emit(self.frame,self.settings.value("dbGenrDir",qtc.QDir.homePath(),str),self.settings.value("dbGenrPrefix","sc_",str))
        
    @qtc.pyqtSlot()
    def killCapFrameThread(self):
        self.capFrameThread.quit()
        self.singleFrameObj.deleteLater()
        self.capFrameThread.deleteLater()

    @qtc.pyqtSlot(str)
    @qtc.pyqtSlot(bool)
    def saveCam(self,x):
        self.detectionFlag = 0   # 0 for live cam
        self.detectionStarted(True)
        self.isStopped = False
        self.actualFPS = None
        self.isPlayFlag = True
        print("saveCam",x,type(x))
        self.counter = 0
        if x:
            print("got here")
            self.lastDetect = None
            #Update the side panel labels:
            self.modeVal.setText("Live")
            

            self.rWidget.setVisible(False)
            self.vidWidget.setVisible(True)
            self.lbl = qtw.QLabel("Video")
            #self.vidLbl = qtw.QLabel()
            #self.vidLayout.addWidget(self.lbl,0,0)
            #self.vidLayout.addWidget(self.vidLbl,2,1,1,1)
            
            ##self.inter = videoByQCamera.interfacer()
            
            #self.cam = qtmm.QCamera(self.camDict[x])
            print(type(self.camDict),type(x),x)
            
            #self.videoObj.setCamera(self.cam)
            #self.videoObj.start()
            #self.fps = self.videoObj.frameRate()
            #self.FPSVal.setText(str(self.fps))
            self.video_thread = qtc.QThread(parent = self)
            self.videoObj.moveToThread(self.video_thread)
            #self.video_thread.started.connect(self.videoObj.start)
            #ss.finished.connect(video_thread.quit)
            self.videoObj.FPSSignal.connect(self.setFPS)
            print(1)
            self.video_thread.start()
            print(2)
            self.setCam.connect(self.videoObj.setCamera)
            print(3)
            self.startByCamSignal.connect(self.videoObj.start)
            print(4)
            #self.setCam.emit(self.cam)
            self.setCam.emit(x)
            print(5)
            self.startByCamSignal.emit()
            print(6)
            self.vidSlider.setMaximum(100)
            self.vidSlider.setValue(100)
            self.vidSlider.sliderMoved.connect(lambda x: self.vidSlider.setValueManually(100,True))
            self.videoObj.currentTimePos.connect(self.setTotalTime)
            self.videoObj.currentTimePos.connect(self.setCurrentTime)
            ##self.inter_thread = qtc.QThread()
            ##self.inter.moveToThread(self.inter_thread)
            #ss.finished.connect(video_thread.quit)
            ##self.inter_thread.start()
            
            self.inter.detectionComplete.connect(self.videoObj.emitFrame)
            self.videoObj.getFrame.connect(self.inter.detect)
            #self.stopVideoProcessing.connect(self.videoObj.stopVideoProcessing)    # shifted to the closeVideoImage
            self.lastDetect = time.time()
            self.inter.detectionComplete[np.ndarray,list].connect(self.displayFrame)
            self.toggleBtnSyncer()
            self.rVidRecToggle.toggled.connect(lambda x: print("local switch handler"))
            self.rVidRecToggle.toggled.connect(self.emitRawVideoRecordingSignal)
            #self.rVidRecToggle.toggled.connect(self.videoObj.rawVideoRecordingHandler)
            self.videoObj.rawVideoRecordingStarted.connect(self.setRawVideoRecordingStartTime)
            self.startRawVideoRecordingSignal.connect(self.videoObj.rawVideoRecordingHandler)
            self.dVidRecToggle.toggled.connect(self.detectionVideoRecordingHandler)
            self.dsGenrToggle.toggled.connect(self.dsGenrHandler)
            self.inter.inferenceTime.connect(self.infVal.setText)
            self.inter.inferenceTime.connect(self.setActualFPS)
            self.pauseRVidRecForLiveVidSignal.connect(self.videoObj.pauseRVidRecording)
            self.resumeRVidRecForLiveVidSignal.connect(self.videoObj.resumeRVidRecording)
            self.pp = 0
            #v.start()
    
    def dsGenrHandler(self,flag):

        # self.dbGenrFlag by default if False so if this method is called first time with flag false, it will just return,
        # or if it has set up the dsGenrThreads and stuff so it will go on to delete and stop dataset generation.
        if self.isStopped and self.dbGenrFlag == False:
            return
        self.dbGenrFlag = flag
        if self.actualFPS == None:
            # change timer to signal or direct function call to avoid the race condition when closing the video
            timer = qtc.QTimer()
            timer.singleShot(2000,lambda: self.dsGenrHandler(flag))

            return
        if self.dbGenrFlag:
            delay = self.settings.value("dGenrGap",100,int) * self.actualFPS   # this will normalize the frame according to how much frames are being displayed on screen. for eg, delay of 30 on a 30FPS original video will not result in 1 frame saved per sec but instead if 10 FPS on screen, then after 3 sec.
            self.dbGenrObj = videoByQCamera.dbGenr(self.settings.value("dbGenrDir",qtc.QDir.homePath(),str),self.settings.value("dbGenrPrefix","image_",str), delay ,self.settings.value("maxDGenrImgCount",100,int))
            self.dbGenrThread = qtc.QThread(parent = self)
            self.dbGenrObj.moveToThread(self.dbGenrThread)
            self.dbGenrFrame.connect(self.dbGenrObj.saveFrame)
            self.dbGenrObj.getFrame.connect(self.emitDbGenrFrame)
            self.dbGenrObj.requestDelete.connect(self.killDbGenrThread)
            self.dbGenrThread.start()
        else:
            self.dbGenrObj.getFrame.disconnect()
            self.dbGenrFrame.disconnect()
            self.stopDbGenr.connect(self.dbGenrObj.stop)
            self.stopDbGenr.emit()

    @qtc.pyqtSlot()
    def emitDbGenrFrame(self):
        if type(self.frame) == np.ndarray:
            self.dbGenrFrame.emit(self.frame)
        else:
            #TODO something to handle it
            pass

    @qtc.pyqtSlot()
    def killDbGenrThread(self):
        
        self.dbGenrThread.quit()
        self.dbGenrThread.wait(3000)
        self.dbGenrObj.deleteLater()
        self.dbGenrThread.deleteLater()
        
    def setActualFPS(self,num):
        x = float(num[:-2])
        if x<1.0:
            self.actualFPS = 1/x   # -2 to remove the "s" character at the end
            self.inter.inferenceTime.disconnect(self.setActualFPS)
            #self.modeVal.setText(str(self.actualFPS)+"_"+num)

    def detectionVideoRecordingHandler(self,startFlag):

        if self.isStopped and self.detectionVideoRecordingFlag == False:
            return

        self.detectionVideoRecordingFlag = startFlag
        print("reached recording handler")
        if not self.allowRecording:
            timer = qtc.QTimer()
            timer.singleShot(2000,lambda: self.detectionVideoRecordingHandler(startFlag))
            #timer.timeout.connect(lambda: print("i got called! "*5))
            return
        if self.detectionVideoRecordingFlag:
            if self.previousDetectionVideoRecordingSingleFileFlag:
                self.detectionVideoRecordingTimer.start() 
                return
            if self.actualFPS == None:
                timer = qtc.QTimer()
                timer.singleShot(2000,lambda: self.detectionVideoRecordingHandler(startFlag))
                return
            #fpms = 1000/self.fps #frames per milli second (1 sec = 1000 ms)
            fpms = 1000/self.actualFPS
            self.recorderThread = qtc.QThread(parent = self)
            path = os.path.join(self.settings.value("rVRDir",qtc.QDir.homePath(),str),self.settings.value("videoPrefix","vid_",str))+qtc.QDateTime.currentDateTime().toString("dd_MM_yyyy hh_mm_ss")+".mp4"#".avi"
            self.detectionVideoRecordingPath = path
            self.previousDetectionVideoRecordingSingleFileFlag = self.settings.value("singleVideoFile",False,bool)
            #self.cameraRecorder = videoByQCamera.cameraRecorder(path,self.fps,self.frameWidth,self.frameHeight,self.settings.value("singleVideoFile",False,bool)) # change the singleVideoFile variable for two different types of recording i-e live and url/path
            self.cameraRecorder = videoByQCamera.cameraRecorder(path,self.actualFPS,self.frameWidth,self.frameHeight,self.settings.value("singleVideoFile",False,bool)) # change the singleVideoFile variable for two different types of recording i-e live and url/path
            self.cameraRecorder.startRawVideoRecording()  # creates opencv recorder object
            self.detectionVideoRecordingTimer = qtc.QTimer()
            self.detectionVideoRecordingTimer.setInterval(fpms)
            self.cameraRecorder.moveToThread(self.recorderThread)
            self.recorderThread.start()
            self.stopDetectionVideoRecording.connect(self.cameraRecorder.stopRecording)
            self.detectionVideoRecordingTimer.timeout.connect(self.detectionVideoRecordingFrameEmitter)
            self.detectionVideoRecordingFrame.connect(self.cameraRecorder.addFrameToRecorder)
            self.detectionVideoRecordingTimer.start()
            self.detectionVideoRecordingStartTime = time.time()
            print("recording started",self.frameWidth,self.frameHeight)
            #kl
        elif self.settings.value("singleVideoFile",False,bool) == True:   # TODO recheck this
            self.detectionVideoRecordingTimer.stop()
            self.previousDetectionVideoRecordingSingleFileFlag = True
            #self.stopDetectionVideoRecording.emit()
            print("single file true")
        else:
            self.detectionVideoRecordingStop()

    def detectionVideoRecordingStop(self):
        '''
        This functions completely stops the detection recording (like force stop)
        '''
        self.detectionVideoRecordingPath = None
        self.objs[self.recorderThread] = self.cameraRecorder
        self.detectionVideoRecordingTimer.stop()
        #self.recorderThread.finished.connect(self.killThread)
        self.detectionVideoRecordingFrame.disconnect()##
        self.cameraRecorder.requestDelete.connect(self.killVideoThread)
        self.detectionVideoRecordingTimer.deleteLater()
        self.stopDetectionVideoRecording.emit(True)
        self.previousDetectionVideoRecordingSingleFileFlag = False
            
    @qtc.pyqtSlot()
    def killThread(self):
        print("thread killed")
        self.objs.pop(self.sender())
        self.recorderThread.quit()
        self.recorderThread.wait(3000)
        self.recorderThread.deleteLater()
        self.cameraRecorder.deleteLater()
    
    @qtc.pyqtSlot()
    def detectionVideoRecordingFrameEmitter(self):
        print("emit frame to record",self.pp)
        if not self.allowRecording:
            return
        if type(self.finalConvertedFrame) == np.ndarray:
            self.detectionVideoRecordingFrame.emit(self.finalConvertedFrame)
            self.pp += 1
        #cv2.imshow("sample",self.finalConvertedFrame)
        #cv2.waitKey()
        #cv2.imwrite("D:/testImg1.png",self.finalConvertedFrame)
        #self.cameraRecorder.addFrameToRecorder(self.finalConvertedFrame)

        #ajldn
        #self.detectionVideoRecordingFrame.emit(self.frame)

    def displayFrame(self,frame,l):
        #show Frame
        #self.counter += 1
        #print("display",self.counter)
        print("DDDDDDDD",threading.get_ident())
        
        if self.isPlayFlag==False:
            print("ARGH "*20)
        if self.allowRecording == False:
            self.var = False
        #self.maxVideoFrameSize = (600,800)  # height, width
        self.maxVideoFrameSize = (self.settings.value("maxVideoFrameHeight",600,int),self.settings.value("maxVideoFrameHeight",800,int))  # height, width
        self.bboxColor = qtg.QColor(self.settings.value("boxColor","#FFFFFF",str))
        self.bboxWidth = self.settings.value("bboxWidth",5,int)
        if type(frame) is np.ndarray:
            print("frame.shape in displayFrame",frame.shape,self.maxVideoFrameSize)
            self.frame = frame
            qimg = self.get_qimage(frame)
            self.frameWidth = qimg.size().width()
            self.frameHeight = qimg.size().height()
            print(self.frameWidth,self.frameHeight,qimg.size(),qimg.format())
            #xmp
            if (self.maxVideoFrameSize[0] - frame.shape[0]) < 0 or (self.maxVideoFrameSize[1] - frame.shape[1]) < 0 :
                # resize the frame if the viewport is smaller than video
                qimg = qimg.scaled(self.maxVideoFrameSize[1],self.maxVideoFrameSize[0],qtc.Qt.KeepAspectRatio,qtc.Qt.SmoothTransformation)
                #qimg = qimg.scaled(self.maxVideoFrameSize[1],self.maxVideoFrameSize[0],qtc.Qt.IgnoreAspectRatio,qtc.Qt.SmoothTransformation)
                h_diff = frame.shape[0] - qimg.size().height()
                w_diff = frame.shape[1] - qimg.size().width()
                
                self.frameWidth = qimg.size().width()
                self.frameHeight = qimg.size().height()
                #if h_diff > w_diff:
                
                h_ratio = 1-(h_diff/frame.shape[0])
                w_ratio = 1-(w_diff/frame.shape[1])
                print(l,h_ratio,w_ratio)
                l = [[int(x[0]*w_ratio),int(x[1]*h_ratio),int(x[2]*w_ratio),int(x[3]*h_ratio)] for x in l]
                print("resized",qimg.size(),l)
            pix = qtg.QPixmap.fromImage(qimg)
            p = qtg.QPainter(pix)
            p.setPen(qtg.QPen(self.bboxColor, self.bboxWidth, qtc.Qt.SolidLine))
            p.setBrush(qtc.Qt.NoBrush)
            p.setRenderHint(qtg.QPainter.Antialiasing, True)
            for x in l:
                p.drawRect(int(x[0]),int(x[2]),int(x[1]-x[0]),int(x[3]-x[2]))
                # TODO check if the percentage should be displayed and display it if enabled

                #if self.lastDetect is None:
            if len(l)>0:
                # we use the condition instead of the above for loop because above for loop can draw multiple bboxes on a single frame, so in a loop iterating multile times, the last detect value would get zero as self.lastDetect would get updated each iteration.
                self.lastDetect = time.time()
                self.polypFoundFlag = True
                self.alarmHandle(True)
            else:
                self.polypFoundFlag = False
                self.alarmHandle(False)
            
            self.lastDetectVal.setText("{:.2f}s".format(time.time()-self.lastDetect))
                
                
            p.end()
            #writeLocker = qtc.QWriteLocker(self.lock)
            #self.vidLbl.setFixedSize(pix.size())
            #self.vidLbl.adjustSize()
            self.vidLbl.setPixmap(pix)
            #self.vidLbl.setMargin(10)
            
            #if self.detectionFlag == 0:
                #self.vidLbl.setFixedSize(pix.size())
            #    self.vidLbl.setFixedSize(100,100)
            print("pix.size()",pix.size(),self.vidLbl.maximumSize(),self.vidLbl.rect(),self.vidLbl.frameRect(),self.vidLbl.contentsRect(),self.vidLbl.geometry(),self.vidLbl.frameGeometry())
            #r = self.vidLbl.geometry()
            #r.setX(0)
            #r.setY(0)
            #self.vidLbl.setGeometry(r)
            #self.vidLbl.setFrameGeometry(r)

            #writeLocker.unlock()
            ######self.allowRecording = True  # helps keep in check if the detection video recorder is invoked before frame being set.
            if self.var:
                try:
                    print("\t\t\t",self.recorderThread.isFinished())
                except:
                    pass

            if self.detectionVideoRecordingFlag:
                self.var = True
                t1 = time.time()
                qimg = pix.toImage()#.convertToFormat(4)
                ptr = qimg.constBits()
                #print(type(ptr),ptr)
                depth = qimg.depth()
                print("depth",depth,qimg.byteCount(),qimg.format())
                #asdo
                #ptr.setsize(self.frameHeight * self.frameWidth * (depth//8))
                ptr.setsize(qimg.byteCount())
                #self.finalConvertedFrame = np.frombuffer(ptr)
                #self.finalConvertedFrame = np.ndarray(shape = (self.frameHeight,self.frameWidth,4),buffer = ptr,dtype = np.ubyte)
                #print("a",self.finalConvertedFrame[230][230],self.finalConvertedFrame.dtype)
                self.finalConvertedFrame = np.ndarray(shape = (self.frameHeight,self.frameWidth,4),buffer = ptr,dtype  = np.uint8)
                #print("b",self.finalConvertedFrame[400][400])

                #print("shape before reshaping",self.finalConvertedFrame.shape)
                #self.finalConvertedFrame = copy.deepcopy(self.finalConvertedFrame.reshape((self.frameHeight,self.frameWidth,depth//8)))
                
                #self.finalConvertedFrame = np.ndarray(shape = (self.frameHeight,self.frameWidth,4),buffer = ptr,dtype  = np.ubyte)
                self.finalConvertedFrame = copy.deepcopy(self.finalConvertedFrame)
                #print(self.finalConvertedFrame)
                #cv2.imshow("out",self.finalConvertedFrame)
                #cv2.waitKey()
                #jasdkj
                x = np.empty((self.frameHeight,self.frameWidth,3),dtype=np.uint8)
                cv2.cvtColor(np.array(self.finalConvertedFrame),cv2.COLOR_BGRA2BGR,x)
                self.finalConvertedFrame = x
                #convertedFrame = convertedFrame.reshape((self.height,self.width,2))
                print("time for detectionVideoRecording conversion",time.time()-t1)
                #print(type(self.finalConvertedFrame),self.finalConvertedFrame.shape)
                #qimg.save('D:/temp.png', 'png')
                
        else:
            print(type(frame))
    
    def get_qimage(self, image: np.ndarray):
        height, width, colors = image.shape
        bytesPerLine = 3 * width
        QImage = qtg.QImage

        image = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        #image = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB32)

        image = image.rgbSwapped()
        #image.convertTo(QImage.Format_RGB32)
        return image


    def handleLiveVideo(self):
        self.videoObj = videoByQCamera.video()
        print(id(self.videoObj))

        #description
        self.camDict = {x.description():x for x in self.videoObj.getCamerasList()}
        print("camDict",self.camDict)
        LiveVideo_Dialog = liveVideoDialog(self.camDict,self)
        LiveVideo_Dialog.result.connect(self.saveCam)
        LiveVideo_Dialog.result[bool].connect(self.saveCam)
        LiveVideo_Dialog.exec()
    
        #cam = qtmm.QCamera(self.video.getCamerasList()[0])

    def customDragEnterEvent(self,e):

        print("mime",e.mimeData().formats(),e.mimeData().hasUrls())
        if e.mimeData().hasUrls():
            urls = e.mimeData().urls()
            if len(urls)==1:
                if urls[0].toString().split('.')[-1] in ["avi","mp4","mkv","png","jpg","jpeg"]:
                    e.acceptProposedAction()
        
        #e.ignore()

    def customDropEvent(self,e):

        if e.mimeData().hasUrls():
            print("urls",e.mimeData().urls())
            self.filename = e.mimeData().urls()[0].toString(qtc.QUrl.PreferLocalFile | qtc.QUrl.NormalizePathSegments)
            print(type(self.filename),self.filename)
            self.startVideoByPath()

    def onBtnClick(self):
        if self.flag:
            self.SPWidget.setFixedWidth(0)
            #self.btn.setText(">>")
            self.btn.setIcon(qtg.QIcon(self.expand))
        else:
            self.SPWidget.setFixedWidth((491.95 * self.widthScale)+0.5)  #350
            #self.btn.setText("<<")
            self.btn.setIcon(qtg.QIcon(self.collapse))
        self.flag = not(self.flag)

    def showBkmrks(self):
        #self._SPWidget1Height = self.SPWidget1.height()
        #self.SPWidget1.setFixedHeight(0)
        if self.detectionFlag != 1:
            self.addBkmrkNotifLbl.setText("<span style=\"color: #D60404;\">Start detection first</span>")
            timer = qtc.QTimer()
            timer.singleShot(2000,lambda: self.addBkmrkNotifLbl.setText(""))
            return
        if self.newBookmarkAddedFlag:
            self.bkmrkFileContents = self.bookmarkObj.read(self.filename[:-4]+".txt")
            print("path of bookmark", self.filename[:-4]+".txt")
            print("len of self.bkmrkFileContents",len(self.bkmrkFileContents))
            for widgets in self.refs:
                widgets.deleteLater()
            #self.SPWidget2.setFixedHeight(self._SPWidget1Height)
            px = 0
            py = -1
            self.refs = list()
            for x in range(len(self.bkmrkFileContents)):
                btn = qtw.QPushButton(self.bkmrkFileContents[x][1])
                #widget = qtw.QWidget()
                widget = bookmarkWidget()
                widgetLayout = qtw.QVBoxLayout()
                widgetLayout.setSpacing(0)
                widget.setLayout(widgetLayout)
                widget.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))

                lbl = marqueeLabel(parent = widget)
                #lbl = qtw.QLabel(parent = widget)
                lbl.setText(self.bkmrkFileContents[x][1])
                shape = tuple(np.array(self.bkmrkFileContents[0][2][1:-2].split(", "),dtype = np.uint32))
                arr = np.array(self.bkmrkFileContents[x][3][1:-2].split(", "),dtype = np.uint8).reshape(shape)
                qimg = self.get_qimage(arr).scaled((200*self.widthScale)+0.5,(120*self.heightScale)+0.5,qtc.Qt.KeepAspectRatio,qtc.Qt.SmoothTransformation)
                pix = qtg.QPixmap.fromImage(qimg)
                frameLabel = qtw.QLabel(parent = widget)
                frameLabel.setPixmap(pix)
                widgetLayout.addWidget(frameLabel)
                widgetLayout.addWidget(lbl)
                print(self.bkmrkFileContents[x][0][:-1],type(self.bkmrkFileContents[x][0][:-1]))
                widget.seekToFrame = int(self.bkmrkFileContents[x][0][:-1])
                print("seekToFrame",x,widget.seekToFrame)
                widget.setFixedSize((200*self.widthScale)+0.5,(200*self.heightScale)+0.5)
                #widget.mousePressEvent = lambda ev: self.vidSlider.setValueManually(self.childAt(ev.windowPos().toPoint()).parent().seekToFrame)
                widget.seekToFrameSignal.connect(self.vidSlider.setValueManually)
                
                if py==1:
                    px += 1
                    py = 0
                else:
                    py += 1
                self.bkmrkDisplayLayout.addWidget(widget,px,py)
                #self.bkmrkDisplayLayout.addWidget(btn,px,py)
                self.refs.append(widget)
            self.scroll.setWidget(self.bkmrkDisplay)
            self.SPLay2.addWidget(self.scroll,1,0)

        self.SPWidget1.setVisible(False)
        self.SPWidget2.setVisible(True)
        self.newBookmarkAddedFlag = False


    def showDetails(self):
        #self.SPWidget2.setFixedHeight(0)
        self.SPWidget2.setVisible(False)
        self.SPWidget1.setVisible(True)
        #self.SPWidget1.setFixedHeight(self._SPWidget1Height)

    def alarmHandle(self,x:bool):
        
        if not self.settings.value("playAlarm",True,bool):
            # Dont play the alarm if the play alarm is False
            return
        
        self.polypDetectedDeque.appendleft(x)
        countTrue = 0
        for x in self.polypDetectedDeque:
            if x == True:
                countTrue += 1
        #countFalse = self.dequeLength - countTrue
        
        if countTrue/self.dequeLength >= self.settings.value("alarmThreshold",0.50,float):
            # play sound
            if self.playAlarmflag:
                self.player.play()
                #self.playAlarm.emit()
                self.chkVar += 1
                self.playAlarmflag = False
        else:
            self.playAlarmflag = True

    def saveFile(self,key):
        #filename, _ = qtw.QFileDialog.getSaveFileName()
        dir = qtw.QFileDialog.getExistingDirectory(directory=self.settings.value(key,type = str))
        print("dir",type(dir),dir)
        if dir is not "":
            self.settings.setValue(key,dir)
        #print("filename",filename,_)
        '''if filename:
            try:
                print(filename)
            except Exception as e:
                qtw.QMessageBox.critical(f"Could not load file: {e}")
        '''
    def openFile(self):
        print(qtc.QDir.homePath())

        filename, _ = qtw.QFileDialog().getOpenFileName(self,
                                        "Select a file to open…",
                                        qtc.QDir.homePath(),
                                        'Images (*.png *.jpeg *.jpg) ;; Videos (*.mp4 *.avi *.mkv)',
                                        'Videos (*.mp4 *.avi *.mkv)',
                                        qtw.QFileDialog.DontResolveSymlinks 
                                        )
        
        
        #print("filename",filename,_)
        if filename:
            try:
                self.filename = filename
                if self.filename.split(".")[-1] in ["png","jpeg","jpg"]:
                    self.startImageByPath()
                else:
                    self.startVideoByPath()
            except Exception as e:
                qtw.QMessageBox.critical(self,"Error",f"Could not load file: {e}")
                self.rWidget.setVisible(True)
                self.vidWidget.setVisible(False)
                self.modeVal.setText("-")

        
    def startVideoByPath(self):
        self.detectionFlag = 1  # 1 for video detection via path
        print("startVideoByPath",self.filename)
        print("got here")
        self.actualFPS = None
        self.detectionStarted(True)
        self.pp = 0
        self.isStopped = False
        self.isPlayFlag = True
        self.rWidget.setVisible(False)
        self.vidWidget.setVisible(True)

        #Update the side panel labels:
        self.modeVal.setText("Pre-Recorded video")

        self.lbl = qtw.QLabel("Video")
        #self.vidLbl = qtw.QLabel()
        #self.vidLayout.addWidget(self.lbl,0,0)
        #self.vidLayout.addWidget(self.vidLbl,2,1,1,1)
        
        ##self.inter = videoByQCamera.interfacer()
        self.videoObj = videoByQCamera.video()
        print("qtc.QDateTime.currentDateTime().toString()",qtc.QDateTime.currentDateTime().toString("dd_MM_yyyy hh_mm_ss"),type(qtc.QDateTime.currentDateTime().toString()))
        #self.videoObj.setFilePath(os.path.join(self.settings.value("rVRDir",qtc.QDir.homePath(),str),self.settings.value("videoPrefix","vid_",str))+qtc.QDateTime.currentDateTime().toString("dd_MM_yyyy hh_mm_ss")+".avi")
        self.videoObj.setUrl(self.filename)

        self.video_thread = qtc.QThread()
        self.videoObj.moveToThread(self.video_thread)
        #ss.finished.connect(video_thread.quit)
        self.video_thread.start()

        ##self.videoObj.startByURL()
        #print("done till here")
        ####self.fps = self.videoObj.frameRate()
        ####self.frameCount = self.videoObj.frameCount()
        #print("done till here2")
        ####self.FPSVal.setText(str(self.fps))
        ####self.vidSlider.setMaximum(self.frameCount)
        '''self.videoObj.FPSSignal.connect(self.setFPS)
        self.videoObj.FPSSignal.connect(self.vidSlider.setFPS,qtc.Qt.QueuedConnection)
        self.videoObj.frameCount.connect(self.vidSlider.setMaximum,qtc.Qt.QueuedConnection)
        self.videoObj.frameCount.connect(self.setTotalTime)
        #self.videoObj.currentFramePos.connect(self.vidSliderPosHandler)
        #self.videoObj.currentFramePos.connect(self.vidSlider.setValueWithoutSignal)
        self.videoObj.currentFramePos.connect(self.vidSlider.setValue,qtc.Qt.QueuedConnection)
        self.videoObj.currentFramePos.connect(self.setCurrentTime)
        self.vidSlider.sliderMoved.connect(self.videoObj.setFrameNumber,qtc.Qt.QueuedConnection)
        self.vidSlider.sliderMoved.connect(app.processEvents)
        #self.vidSlider.sliderMoved.connect(self.lambda x: self.newSliderPos = x)'''
        
        self.videoObj.FPSSignal.connect(self.setFPS)
        self.videoObj.FPSSignal.connect(self.vidSlider.setFPS,qtc.Qt.QueuedConnection)
        self.videoObj.frameCount.connect(self.vidSlider.setMaximum,qtc.Qt.QueuedConnection)
        self.videoObj.frameCount.connect(self.setTotalTime)
        #self.videoObj.currentFramePos.connect(self.vidSliderPosHandler)
        #self.videoObj.currentFramePos.connect(self.vidSlider.setValueWithoutSignal)
        self.videoObj.currentFramePos.connect(self.vidSlider.setValue,qtc.Qt.QueuedConnection)
        self.videoObj.currentFramePos.connect(self.setCurrentTime)
        self.vidSlider.val.connect(self.videoObj.setFrameNumber,qtc.Qt.QueuedConnection)
        self.videoObj.videoEnded.connect(self.playPauseBtn.click)
        #self.vidSlider.sliderMoved.connect(app.processEvents)
        #self.vidSlider.sliderMoved.connect(self.lambda x: self.newSliderPos = x)
        print(2)
        ##self.inter_thread = qtc.QThread()
        ##self.inter.moveToThread(self.inter_thread)
        #ss.finished.connect(video_thread.quit)
        ##self.inter_thread.start()
        self.startByURLSignal.connect(self.videoObj.startByURL)
        self.inter.detectionComplete.connect(self.videoObj.emitFrame)
        self.videoObj.getFrame.connect(self.inter.detect)
        self.lastDetect = time.time()
        self.inter.detectionComplete[np.ndarray,list].connect(self.displayFrame)
        self.startByURLSignal.emit()
        self.toggleBtnSyncer()
        self.rVidRecToggle.toggled.connect(lambda x: print("local switch handler"))
        self.rVidRecToggle.toggled.connect(self.emitRawVideoRecordingSignal)
        #self.rVidRecToggle.toggled.connect(self.videoObj.rawVideoRecordingHandler)
        self.dVidRecToggle.toggled.connect(self.detectionVideoRecordingHandler)
        self.videoObj.rawVideoRecordingStarted.connect(self.setRawVideoRecordingStartTime)
        self.startRawVideoRecordingSignal.connect(self.videoObj.rawVideoRecordingHandler)
        self.inter.inferenceTime.connect(self.infVal.setText)
        self.inter.inferenceTime.connect(self.setActualFPS)
        self.dsGenrToggle.toggled.connect(self.dsGenrHandler)
        self.startStopTimerSignal.connect(self.videoObj.startStopTimer)
        #self.rVidRecToggle.toggled.connect(lambda x: qtw.QToolTip.showText(self.rVidRecToggle.mapToGlobal(qtc.QPoint(0,0)),"Wait for video to start",self.rVidRecToggle))
        #v.start()

    def startImageByPath(self):
        self.detectionFlag = 2  # 2 for image detection via path
        print("startVideoByPath",self.filename)
        print("got here")
        self.actualFPS = None
        self.pp = 0
        self.detectionStarted(True)
        self.isStopped = False
        self.isPlayFlag = True
        self.rWidget.setVisible(False)
        self.vidWidget.setVisible(True)

        #Update the side panel labels:
        self.modeVal.setText("Pre-Recorded Image")

        self.lbl = qtw.QLabel("Video")
        self.vidLbl = qtw.QLabel()
        #self.vidLbl.setObjectName("vidLbl")
        self.vidLbl.setAutoFillBackground(False)
        #self.vidLayout.addWidget(self.lbl,0,0)
        self.vidLayout.addWidget(self.vidLbl,2,1,1,1)
        
        ##self.inter = videoByQCamera.interfacer()
        self.videoObj = videoByQCamera.video()
        print("qtc.QDateTime.currentDateTime().toString()",qtc.QDateTime.currentDateTime().toString("dd_MM_yyyy hh_mm_ss"),type(qtc.QDateTime.currentDateTime().toString()))
        #self.videoObj.setFilePath(os.path.join(self.settings.value("rVRDir",qtc.QDir.homePath(),str),self.settings.value("videoPrefix","vid_",str))+qtc.QDateTime.currentDateTime().toString("dd_MM_yyyy hh_mm_ss")+".avi")
        self.videoObj.setUrl(self.filename,isImageFlag = True)
        ##self.videoObj.startByURL()
        #print("done till here")
        ##self.fps = self.videoObj.frameRate()
        #print("done till here2")
        ##self.FPSVal.setText(str(self.fps))
        self.video_thread = qtc.QThread()
        self.videoObj.moveToThread(self.video_thread)
        #ss.finished.connect(video_thread.quit)
        self.video_thread.start()
        print(2)
        ##self.inter_thread = qtc.QThread()
        ##self.inter.moveToThread(self.inter_thread)
        #ss.finished.connect(video_thread.quit)
        ##self.inter_thread.start()
        self.startByURLSignal.connect(self.videoObj.startByURL)
        #self.inter.detectionComplete.connect(self.videoObj.emitFrame)
        self.videoObj.getFrame.connect(self.inter.detect)
        self.lastDetect = time.time()
        self.inter.detectionComplete[np.ndarray,list].connect(self.displayFrame)
        self.startByURLSignal.emit()
        # raw video recording and detection video recording not available for static image detection
        #self.rVidRecToggle.toggled.connect(lambda x: print("local switch handler"))
        #self.rVidRecToggle.toggled.connect(self.emitRawVideoRecordingSignal)
        
        #self.dVidRecToggle.toggled.connect(self.detectionVideoRecordingHandler)
        #self.startRawVideoRecordingSignal.connect(self.videoObj.rawVideoRecordingHandler)
        self.rVidRecToggle.setCheckable(False)
        self.dVidRecToggle.setCheckable(False)
        self.dsGenrToggle.setCheckable(False)
        #self.rVidRecToggle.toggled.connect(self.rVidRecToggle.toggle)  # TODO verify this doesn't cause infinite loop
        #self.dVidRecToggle.toggled.connect(self.dVidRecToggle.toggle)  # TODO verify this doesn't cause infinite loop
        self.inter.inferenceTime.connect(self.infVal.setText)
        self.inter.inferenceTime.connect(self.setActualFPS)
        #self.dsGenrToggle.toggled.connect(self.dsGenrHandler)
        #self.rVidRecToggle.toggled.connect(lambda x: qtw.QToolTip.showText(self.rVidRecToggle.mapToGlobal(qtc.QPoint(0,0)),"Wait for video to start",self.rVidRecToggle))
        #v.start()
    def vidSliderPosHandler(self,x):
        # TODO delete this method
        self.vidSlider.setValue(x)

    def emitRawVideoRecordingSignal(self,x):
        #if not self.settings.value("singleVideoFile",False,bool):
        # TODO fix bug: if single file mode, the rpathval still gets updated whereas it shouldn't
        path = os.path.join(self.settings.value("rVRDir",qtc.QDir.homePath(),str),self.settings.value("videoPrefix","vid_",str)) + qtc.QDateTime.currentDateTime().toString("dd_MM_yyyy hh_mm_ss")+".mp4"
        #if self.rawVideoRecordingFlag and not self.settings.value("singleVideoFile",False,bool):
        '''if x and not self.rawVideoRecordingFlag:
            if not self.previousRawVideoRecordingFlag:
                self.rPathVal.setText(path)
        else:
            if not self.settings.value("singleVideoFile",False,bool):
                self.rPathVal.setText("-")
                self.previousRawVideoRecordingFlag = False
            else:
                self.previousRawVideoRecordingFlag = True'''
        
        if x and not self.rawVideoRecordingFlag:
            self.rPathVal.setText(path)
            self.rawVideoRecordingFlag = True
        else:
            if not self.settings.value("singleVideoFile",False,bool):
                self.rPathVal.setText("-")
                self.rawVideoRecordingFlag = False
            else:
                self.rawVideoRecordingFlag = True

        print("emitRawVideoRecordingSignal", path)
        #kxmc
        self.startRawVideoRecordingSignal.emit(x,self.settings.value("singleVideoFile",False,bool),path,False)
        #self.rawVideoRecordingFlag = x


    def show_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()

    def showAbout(self):
        about_Dialog = aboutDialog(self)
        about_Dialog.exec()

    def showHelp(self):
        help_Dialog = helpDialog(self)
        help_Dialog.exec()

    def detectionStarted(self,flag):
        # set menu actions enabled or disabled
        
        self.openFileAction.setEnabled(not(flag))
        self.closeFileAction.setEnabled(flag)
        self.playPauseAction.setEnabled(flag)

    def toggleBtnSyncer(self):
        if self.rVidRecToggle.isChecked():
            self.setRawVideoRecordingStartTime(True)
            self.emitRawVideoRecordingSignal(True)
        if self.dVidRecToggle.isChecked():
            self.detectionVideoRecordingHandler(True)
        if self.dsGenrToggle.isChecked():
            self.dsGenrHandler(True)


    def exitRoutine(self):
        print("self.chkVar",self.chkVar)
        if self.detectionFlag != None:
            self.closeVideoImage()
        timer = qtc.QTimer()
        timer.singleShot(2000,app.quit)


class liveVideoDialog(qtw.QDialog):
    """Dialog for live camera selection"""

    result = qtc.pyqtSignal([str],[bool])
    def __init__(self,camDict, parent=None):
        super().__init__(parent, modal=True)
        #self.setWindowFlags(qtc.Qt.WindowTitleHint | qtc.Qt.WindowSystemMenuHint)
        #self.setWhatsThis("False")
        screen = app.primaryScreen()
        #print(screen.size(),screen.geometry())
        #print(screen.devicePixelRatio,app.devicePixelRatio)
        #print(screen.logicalDotsPerInch(),screen.physicalDotsPerInch())
        #print(screen.manufacturer(),screen.model())
        self.widthScale = screen.size().width() / 1920
        self.heightScale = screen.size().height() / 1080
        
        self.text = None
        self.setWindowTitle("Select a camera...")
        self.setFixedSize((421.669 * self.widthScale)+0.5,(281.25 * self.heightScale) + 0.5) #(300,200)
        self.layout = qtw.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        
        self.upperWidget = qtw.QWidget()
        self.upperLayout = qtw.QVBoxLayout()
        self.upperWidget.setLayout(self.upperLayout)
        self.upperLayout.setContentsMargins((28.11 * self.widthScale)+0.5,0,(28.11 * self.widthScale)+0.5,0) #LTRB # 20,0,20,0

        self.layout.addWidget(self.upperWidget)

        self.camLbl = qtw.QLabel("Cameras")
        self.camLbl.setObjectName("camLbl")
        self.camLbl.setSizePolicy(qtw.QSizePolicy.Maximum,qtw.QSizePolicy.Maximum)
        print("camLbl",self.camLbl.size(),self.camLbl.sizePolicy())

        self.dropdown = qtw.QComboBox(self,editable=False)
        l = list(camDict.keys())
        l.insert(0,"Select camera...")
        self.dropdown.addItems(l)
        self.dropdown.model().item(0).setEnabled(False)
        self.dropdown.currentTextChanged.connect(self.handleTextChanged)
        self.dropdown.setFixedWidth((337.335 * self.widthScale)+0.5)#(240)
        self.dropdown.setObjectName("dropdown")
        self.dropdown.setView(qtw.QListView(self))
        #self.dropdown.setContentsMargins(20,5,20,5)
        print("has frame",self.dropdown.hasFrame())
        #self.dropdown.setFrame(False)
        #self.camLbl.setContentsMargins(20,5,20,5)

        self.btnHolderWidget = qtw.QWidget()
        self.btnHolderLayout = qtw.QGridLayout()
        self.btnHolderWidget.setLayout(self.btnHolderLayout)
        self.btnHolderWidget.setObjectName("btnHolderWidget")
        self.btnHolderWidget.setFixedHeight((70.3125 * self.heightScale)+0.5)#(50)

        self.okBtn = qtw.QPushButton("Ok")
        self.cancelBtn = qtw.QPushButton("Cancel")

        self.okBtn.clicked.connect(self.onOk)
        self.cancelBtn.clicked.connect(self.onCancel)
        self.okBtn.setFixedSize((140.556 * self.widthScale)+0.5,(42.1875 * self.heightScale)+0.5)#(100,30)
        self.cancelBtn.setFixedSize((140.556 * self.widthScale)+0.5,(42.1875 * self.heightScale)+0.5)#(100,30)
        self.space = qtw.QWidget()
        self.space.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)
        
        self.upperLayout.addWidget(self.camLbl)
        self.upperLayout.addWidget(self.dropdown)
        self.layout.addWidget(self.btnHolderWidget)
        #self.layout.addWidget(self.camLbl,0,0,1,4)
        #self.layout.addWidget(self.dropdown,1,0,1,4)
        #self.layout.addWidget(self.btnHolderWidget,2,0,1,4)
        self.btnHolderLayout.addWidget(self.space,0,0)
        self.btnHolderLayout.addWidget(self.okBtn,0,1)
        self.btnHolderLayout.addWidget(self.cancelBtn,0,2)
        
        #self.layout.addWidget(self.authorsNameLbl2,2,2,2,1)
        self.emitted = False
 
    def onOk(self):
        if self.text is not None:
            self.result[str].emit(self.text)
            self.emitted = True
            self.close()
        else:
            self.onCancel()
    
    def onCancel(self):
        self.result[bool].emit(False)
        self.emitted = True
        self.close()

    def handleTextChanged(self,text):
        self.text = text
        #self.close()

    def closeEvent(self,ev):
        if not self.emitted:
            self.result[bool].emit(False)
        ev.accept()

class aboutDialog(qtw.QDialog):
    """Dialog for about dialog"""

    def __init__(self, parent=None):
        super().__init__(parent, modal=True)
        #self.setWindowFlags(qtc.Qt.WindowTitleHint | qtc.Qt.WindowSystemMenuHint)
        #self.setWhatsThis("False")
        screen = app.primaryScreen()
        #print(screen.size(),screen.geometry())
        #print(screen.devicePixelRatio,app.devicePixelRatio)
        #print(screen.logicalDotsPerInch(),screen.physicalDotsPerInch())
        #print(screen.manufacturer(),screen.model())
        self.widthScale = screen.size().width() / 1920
        self.heightScale = screen.size().height() / 1080

        self.setWindowTitle("About")
        self.setMinimumHeight((562.5 * self.heightScale)+0.5)#(400)
        self.layout = qtw.QGridLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins((28.11 * self.widthScale)+0.5,(7.0312 * self.heightScale)+0.5,(28.11 * self.widthScale)+0.5,(7.0312 * self.heightScale)+0.5)#(20,5,20,5)
        
        self.aboutLbl = qtw.QLabel("About")
        self.aboutLbl.setObjectName("aboutLbl")
        self.finalLogo = qtg.QPixmap(':/icons/final_fyp_logo2.svg').scaledToHeight((30.9375 * self.heightScale)+0.5,qtc.Qt.SmoothTransformation) #22
        self.logoLbl = qtw.QLabel()
        self.logoLbl.setPixmap(self.finalLogo)
        self.aboutTextLbl = qtw.QLabel()
        self.aboutTextLbl.setText("Exero is made as a Final Year Project by students of Sir Syed University of Engineering and Technology. This version is a complete software package which is capable of working in realtime as well as offline to detect polyps. Exero can also save the video and images with and/or without detection.")
        self.aboutTextLbl.setWordWrap(True)
        self.authorsLbl = qtw.QLabel("Authors")
        self.authorsLbl.setStyleSheet("QLabel{font-weight: bold;}")
        self.authorsNameLbl1 = qtw.QLabel("Zeeshan Zulfiqar Ali\nSyyeda Dua Raza")
        self.authorsNameLbl2 = qtw.QLabel("Shahab Younus\nZeeshan Amir Khan")
        
        self.layout.addWidget(self.aboutLbl,0,0)
        self.layout.addWidget(self.logoLbl,0,3,qtc.Qt.AlignHCenter)
        self.layout.addWidget(self.aboutTextLbl,1,0,1,4)
        self.layout.addWidget(self.authorsLbl,2,0)
        self.layout.addWidget(self.authorsNameLbl1,2,1,2,1)
        self.layout.addWidget(self.authorsNameLbl2,2,2,2,1)

class helpDialog(qtw.QDialog):
    """Dialog for Help"""
    
    def __init__(self, parent=None):
        super().__init__(parent, modal=True)
        screen = app.primaryScreen()
        #print(screen.size(),screen.geometry())
        #print(screen.devicePixelRatio,app.devicePixelRatio)
        #print(screen.logicalDotsPerInch(),screen.physicalDotsPerInch())
        #print(screen.manufacturer(),screen.model())
        self.widthScale = screen.size().width() / 1920
        self.heightScale = screen.size().height() / 1080

        self.setWindowTitle("Help")
        self.setMinimumHeight((843.75 * self.heightScale)+0.5)#(600)
        self.setMinimumWidth((1080 * self.widthScale)+0.5)
        self.sizeHint = lambda: qtc.QSize((1200 * self.widthScale)+0.5,(843.75 * self.heightScale)+0.5)

        self.layout = qtw.QHBoxLayout()
        self.setLayout(self.layout)
        self.lLayout = qtw.QVBoxLayout()
        self.lWidget = qtw.QWidget()
        self.lWidget.setLayout(self.lLayout)
        self.layout.addWidget(self.lWidget)
        self.lWidget.setObjectName("helpLWidget")
        #self.lWidget.setObjectName("settingLWidget")
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.lWidget.setFixedWidth((421.669 * self.widthScale)+0.5)#(300)
        #self.layout.addWidget(qtw.QLabel("testing"))
        self.lLayout.setSpacing(0)
        self.lLayout.setContentsMargins(0,0,0,0)
        
        self.helpLbl = qtw.QLabel("Help")
        self.helpLbl.setObjectName("helpLbl")
        self.lLayout.addWidget(self.helpLbl)
        self.helpLbl.setContentsMargins((22.489 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5,(14.055 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5)#(16,20, 10,20)
        self.l1 = clickLabel("Overview")
        self.vsoLbl = clickLabel("Video saving options")
        self.dmLbl = clickLabel("Detection models")
        self.l2 = clickLabel("Dataset Generation")
        self.sysCorrOptLbl = clickLabel("System Correct option")
        self.bkmrkLbl2 = clickLabel("Bookmark")
        self.l1.clicked.connect(lambda: self.changeContent(self.l1))
        self.vsoLbl.clicked.connect(lambda: self.changeContent(self.vsoLbl))
        self.dmLbl.clicked.connect(lambda: self.changeContent(self.dmLbl))
        self.l2.clicked.connect(lambda: self.changeContent(self.l2))
        self.sysCorrOptLbl.clicked.connect(lambda: self.changeContent(self.sysCorrOptLbl))
        self.bkmrkLbl2.clicked.connect(lambda: self.changeContent(self.bkmrkLbl2))
        self.lLayout.addWidget(self.l1)
        self.lLayout.addWidget(self.vsoLbl)
        self.lLayout.addWidget(self.dmLbl)
        self.lLayout.addWidget(self.l2)
        self.lLayout.addWidget(self.sysCorrOptLbl)
        self.lLayout.addWidget(self.bkmrkLbl2)
        self.l1.setObjectName("l1")
        self.vsoLbl.setObjectName("vsoLbl")
        self.dmLbl.setObjectName("dmLbl")
        self.l2.setObjectName("l2")
        self.sysCorrOptLbl.setObjectName("sysCorrOptLbl")
        self.bkmrkLbl2.setObjectName("bkmrkLbl2")
        self.l1.setContentsMargins((14.0556 * self.widthScale)+0.5,(8.4375 * self.heightScale)+0.5,0,(7.0312 * self.heightScale)+0.5) #(10,6,0,5)
        #self.vsoLbl.setContentsMarginsself.layout.setContentsMargins((14.0556 * self.widthScale)+0.5,(7.0312 * self.heightScale)+0.5,0,(7.0312 * self.heightScale)+0.5) #(10,5,0,5)
        self.vsoLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,(7.0312 * self.heightScale)+0.5,0,(7.0312 * self.heightScale)+0.5) #(10,5,0,5)
        self.dmLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,(7.0312 * self.heightScale)+0.5,0,(7.0312 * self.heightScale)+0.5) #(10,5,0,5)
        self.l2.setContentsMargins((14.0556 * self.widthScale)+0.5,(7.0312 * self.heightScale)+0.5,0,(7.0312 * self.heightScale)+0.5) #(10,5,0,5)
        self.sysCorrOptLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,(7.0312 * self.heightScale)+0.5,0,(7.0312 * self.heightScale)+0.5) #(10,5,0,5)
        self.bkmrkLbl2.setContentsMargins((14.0556 * self.widthScale)+0.5,(7.0312 * self.heightScale)+0.5,0,(7.0312 * self.heightScale)+0.5) #(10,5,0,5)
        #print(self.l2.contentsMargins())
        self.sp = qtw.QWidget()
        self.lLayout.addWidget(self.sp)
        self.sp.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)
        self.currentSelected = None

        self.rLayout = qtw.QVBoxLayout()
        self.rWidget = qtw.QWidget()
        self.rWidget.setLayout(self.rLayout)
        self.layout.addWidget(self.rWidget)
        self.rLayout.setContentsMargins(0,0,0,0)
        self.rLayout.setSpacing(0)
        
        #self.rLayout.addWidget(qtw.QLabel("testing"))
        #self.general()
        self.active = None
        self.l1.clicked.connect(self.overview)
        self.l1.clicked.emit()    # Shows the overview panel by default
        self.vsoLbl.clicked.connect(self.vso)
        self.dmLbl.clicked.connect(self.dm)
        self.l2.clicked.connect(self.dgnr)
        #self.l2.clicked.emit()
        self.sysCorrOptLbl.clicked.connect(self.sysCorrOpt)
        self.bkmrkLbl2.clicked.connect(self.bkmrk)
        #self.rLayout.addWidget(self.settingsHolderWidget)

    def clearLayout(self,layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def addBtns(self):
        #self.sp2 = qtw.QWidget()
        #self.rLayout.addWidget(self.sp2)
        #self.sp2.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)
        #self.sp2.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.Expanding)
        self.okBtn = qtw.QPushButton("Ok")
        self.okBtn.setFixedSize((140.556 * self.widthScale)+0.5,(42.1875 * self.heightScale)+0.5)#(100,30)
        self.sp3 = qtw.QWidget()
        self.bLayout = qtw.QHBoxLayout()
        self.bWidget = qtw.QWidget()
        self.bWidget.setObjectName("bWidget")
        self.bWidget.setLayout(self.bLayout)
        self.rLayout.addWidget(self.bWidget)
        self.bLayout.addWidget(self.sp3)
        self.bLayout.addWidget(self.okBtn)
        self.bLayout.setContentsMargins((14.0556 * self.widthScale)+0.5,0,(14.0556 * self.widthScale)+0.5,0)#(10,0,10,0)
        self.bLayout.setSpacing((14.0556 * self.widthScale)+0.5) #(10)
        self.bWidget.setFixedHeight((70.3125 * self.heightScale)+0.5) #(50)
        self.sp3.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)
        self.sp3.setMinimumWidth((351.39 * self.widthScale)+0.5) #(250)

        self.okBtn.clicked.connect(lambda: self.done(qtw.QDialog.Accepted))

    def changeContent(self,callerWidget):
        if self.currentSelected:
            oldWidget = self.findChild(clickLabel, self.currentSelected)
            oldWidget.setStyleSheet("#"+self.currentSelected+"{ background-color: #FAFAFA;}") #border-right: 1px solid red;
            cm = oldWidget.contentsMargins()
            cm.setLeft(cm.left()-((7.027 * self.widthScale)+0.5)) #5
            oldWidget.setContentsMargins(cm)
        self.currentSelected = callerWidget.objectName()
        callerWidget.setStyleSheet("#"+self.currentSelected+"{ background-color: #F0F0F0;}") #border-right: 1px solid #F0F0F0;
        cm = callerWidget.contentsMargins()
        cm.setLeft(cm.left()+((7.027 * self.widthScale)+0.5)) #6   # TODO Check if it was 5 or 6
        callerWidget.setContentsMargins(cm)
    
    def overview(self):
        
        if self.active is not None:
            #self.active.setFixedHeight(0)
            self.clearLayout(self.rLayout)
        
        self.scroll = qtw.QScrollArea()
        self.scroll.setObjectName("helpScroll")
        
        #self.scroll.setFixedSize((410.9375*self.widthScale)+0.5,(940.556*self.heightScale)+0.5)  # 150,100
        self.scroll.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)

        self.settingsHolderLayout = qtw.QGridLayout()
        self.settingsHolderWidget = qtw.QWidget()
        self.settingsHolderWidget.setLayout(self.settingsHolderLayout)
        
        self.rLayout.addWidget(self.settingsHolderWidget)
        
        self.titleLbl = qtw.QLabel("Overview")
        self.titleLbl.setObjectName("subTitleLbl")
        self.titleLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5,(28.111 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5)#(10,20,20,20)
        #print(self.titleLbl.size(),self.titleLbl.rect())
        #self.bboxColorWidget = qtw.QColorDialog()
        self.textLbl = qtw.QLabel("Exero is a medical software incorporated with state of the art Artificial algorithm working to detect polyps from colonoscopy sessions. This software provides many features, most of which are self intuitive and are explained in other sections.\n\nStart detection on live video gives option to select the live video source. User can select the video source and start the detection right away or can alternatively, click to browse or drag and drop the video or image to start the detection on that. In case of detection on pre-recorded video, live raw video recording option will not be available, and in case of detection on pre-recorded image, the options live raw video recording, live detection video recording, & dataset generation will not be available.")
        self.textLbl.setWordWrap(True)
        self.textLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,0,(14.0556 * self.widthScale)+0.5,0) #(10,0,10,0)
        self.sp2 = qtw.QWidget()
        self.sp2.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)

        self.settingsHolderLayout.addWidget(self.titleLbl,0,0)
        self.settingsHolderLayout.addWidget(self.textLbl,1,0,1,2)
        self.settingsHolderLayout.addWidget(self.sp2,2,0)
        self.scroll.setWidget(self.settingsHolderWidget)
        self.scroll.setWidgetResizable(True)
        self.rLayout.addWidget(self.scroll)

        self.addBtns()
        self.active = self.settingsHolderWidget  # maybe replace with self.scroll but since no real usage of self.active other than to see if its the first category to load, we'll keep it as it is cuz i lazy.

    def bkmrk(self):
        
        if self.active is not None:
            #self.active.setFixedHeight(0)
            self.clearLayout(self.rLayout)

        self.scroll = qtw.QScrollArea()
        self.scroll.setObjectName("helpScroll")
        
        #self.scroll.setFixedSize((410.9375*self.widthScale)+0.5,(940.556*self.heightScale)+0.5)  # 150,100
        self.scroll.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)

        self.settingsHolderLayout = qtw.QGridLayout()
        self.settingsHolderWidget = qtw.QWidget()
        self.settingsHolderWidget.setLayout(self.settingsHolderLayout)
        
        self.rLayout.addWidget(self.settingsHolderWidget)
        
        self.titleLbl = qtw.QLabel("Bookmark")
        self.titleLbl.setObjectName("subTitleLbl")
        self.titleLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5,(28.111 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5)#(10,20,20,20)
        #self.bboxColorWidget = qtw.QColorDialog()
        self.textLbl = qtw.QLabel("Exero provides a bookmark functionality which can be very useful in marking important parts in a video. User can bookmark in realtime with the bookmark title. This feature would be specific to each video and a seperate file will be generated which will contain data regarding bookmark. During live recording, bookmarks can be viewed/modified or deleted. During playback of pre-recorded video, the bookmarks can be viewed and double clicking on them would take the video to that specific instance of bookmark, however the double click to seek feature would not be available in live videos which are being recorded. Bookmark can also be edited and added in the pre-recorded video.")
        self.textLbl.setWordWrap(True)
        self.textLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,0,(14.0556 * self.widthScale)+0.5,0)#(10,0,10,0)
        self.sp2 = qtw.QWidget()
        self.sp2.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)

        self.settingsHolderLayout.addWidget(self.titleLbl,0,0)
        self.settingsHolderLayout.addWidget(self.textLbl,1,0,1,2)
        self.settingsHolderLayout.addWidget(self.sp2,2,0)
        self.scroll.setWidget(self.settingsHolderWidget)
        self.scroll.setWidgetResizable(True)
        self.rLayout.addWidget(self.scroll)

        self.addBtns()
        self.active = self.settingsHolderWidget


    def sysCorrOpt(self):
        
        if self.active is not None:
            #self.active.setFixedHeight(0)
            self.clearLayout(self.rLayout)

        self.scroll = qtw.QScrollArea()
        self.scroll.setObjectName("helpScroll")
        
        #self.scroll.setFixedSize((410.9375*self.widthScale)+0.5,(940.556*self.heightScale)+0.5)  # 150,100
        self.scroll.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)

        self.settingsHolderLayout = qtw.QGridLayout()
        self.settingsHolderWidget = qtw.QWidget()
        self.settingsHolderWidget.setLayout(self.settingsHolderLayout)
        
        self.rLayout.addWidget(self.settingsHolderWidget)
        
        self.titleLbl = qtw.QLabel("System Correct Option")
        self.titleLbl.setObjectName("subTitleLbl")
        self.titleLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5,(28.111 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5) #(10,20,20,20)
        #self.bboxColorWidget = qtw.QColorDialog()
        self.textLbl = qtw.QLabel("The System Correct option provided in side panel provides the ability for the user to save the frame with correct label for reference and later diagnosis. This feature can be very beneficial to enable developers to train model in areas where the model lacks currently. This option would not change anything in the algorithm or its working but will save the frame for later use. \n\nNote: Using this feature will save the frame irrespective of if generate dataset option is enabled or not. ")
        self.textLbl.setWordWrap(True)
        self.textLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,0,(14.0556 * self.widthScale)+0.5,0) #(10,0,10,0)
        self.sp2 = qtw.QWidget()
        self.sp2.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)

        self.settingsHolderLayout.addWidget(self.titleLbl,0,0)
        self.settingsHolderLayout.addWidget(self.textLbl,1,0,1,2)
        self.settingsHolderLayout.addWidget(self.sp2,2,0)
        self.scroll.setWidget(self.settingsHolderWidget)
        self.scroll.setWidgetResizable(True)
        self.rLayout.addWidget(self.scroll)

        self.addBtns()
        self.active = self.settingsHolderWidget

    def vso(self):
        
        if self.active is not None:
            #self.active.setFixedHeight(0)
            self.clearLayout(self.rLayout)
        
        self.scroll = qtw.QScrollArea()
        self.scroll.setObjectName("helpScroll")
        
        #self.scroll.setFixedSize((410.9375*self.widthScale)+0.5,(940.556*self.heightScale)+0.5)  # 150,100
        self.scroll.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)

        self.settingsHolderLayout = qtw.QGridLayout()
        self.settingsHolderWidget = qtw.QWidget()
        self.settingsHolderWidget.setLayout(self.settingsHolderLayout)
        
        self.rLayout.addWidget(self.settingsHolderWidget)
        
        self.titleLbl = qtw.QLabel("Video Saving Options")
        self.titleLbl.setObjectName("subTitleLbl")
        self.titleLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5,(28.111 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5) #(10,20,20,20)
        #self.bboxColorWidget = qtw.QColorDialog()
        self.textLbl = qtw.QLabel("Exero provides wide array of video saving options. User can enable/disable the options during the detection. Users are provided the ability to specify in settings whether they want to produce a single video file in the end or multiple in case of multiple video recording on/off commands. Live raw video recording options saves the video as it recieves, without passing ot the detection module. Live detection video recording option saves the video after the detection i.e. the bounding box would be visible in the output video file.")
        self.textLbl.setWordWrap(True)
        self.textLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,0,(14.0556 * self.widthScale)+0.5,0)#(10,0,10,0)
        self.sp2 = qtw.QWidget()
        self.sp2.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)

        self.settingsHolderLayout.addWidget(self.titleLbl,0,0)
        self.settingsHolderLayout.addWidget(self.textLbl,1,0,1,2)
        self.settingsHolderLayout.addWidget(self.sp2,2,0)
        self.scroll.setWidget(self.settingsHolderWidget)
        self.scroll.setWidgetResizable(True)
        self.rLayout.addWidget(self.scroll)

        self.addBtns()
        self.active = self.settingsHolderWidget

    def dgnr(self):
        
        if self.active is not None:
            #self.active.setFixedHeight(0)
            self.clearLayout(self.rLayout)

        self.scroll = qtw.QScrollArea()
        self.scroll.setObjectName("helpScroll")
        
        #self.scroll.setFixedSize((410.9375*self.widthScale)+0.5,(940.556*self.heightScale)+0.5)  # 150,100
        self.scroll.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)
        self.settingsHolderLayout = qtw.QGridLayout()
        self.settingsHolderWidget = qtw.QWidget()
        self.settingsHolderWidget.setLayout(self.settingsHolderLayout)
        
        
        #self.rLayout.addWidget(self.settingsHolderWidget)
        
        
        self.titleLbl = qtw.QLabel("Dataset Generation")
        self.titleLbl.setObjectName("subTitleLbl")
        self.titleLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5,(28.111 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5) #(10,20,20,20)
        #self.bboxColorWidget = qtw.QColorDialog()

        self.textLbl = qtw.QLabel("Exero provides dataset generation feature which generates dataset with minimal interaction of user. This feature, if enabled, works in background. User can specify in settings the interval with which the frame is saved for the dataset and whether it should save the those frames which doesn't contain polyps (as negative examples). XML files according to the pascal VOC format is generated along with the frame. The saved images doesn't contain bounding box and the corresponding xml file contain the bounding box information. This can be potentially be used to train the model externally.\n\nNote: While dataset generation option is enabled, correct system button will result in flipping the corresponding state i.e. if a frame is not detected by the system to contain polyp, and the user presses the correct system button, the frame will be saved as a polyp positive but the corresponding xml file would have undefined(or possibly full frame) as the bounding box. If the frame is detected to contain polyp and the button is pressed then, if save negative image option(in settings) is enabled than the frame is saved in negative folder and if it disabled then the frame is not saved by this module, however the correct system has its own seperate functionality and will save the frame seperately regardless if its being saved in dataset generation folder or not.")
        self.textLbl.setWordWrap(True)
        self.textLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,0,(14.0556 * self.widthScale)+0.5,0)#(10,0,10,0)
        self.sp2 = qtw.QWidget()
        self.sp2.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)
        self.settingsHolderLayout.addWidget(self.titleLbl,0,0)
        self.settingsHolderLayout.addWidget(self.textLbl,1,0,1,2)
        self.settingsHolderLayout.addWidget(self.sp2,2,0)
        self.scroll.setWidget(self.settingsHolderWidget)
        self.scroll.setWidgetResizable(True)
        self.rLayout.addWidget(self.scroll)
        self.addBtns()
        self.active = self.settingsHolderWidget

    '''def showColorDialog(self):

        self.bboxColorDialog = qtw.QColorDialog(self.boxColor, self)
        #self.bboxColorDialog.setOptions(qtw.QColorDialog.NoButtons)
        #print()
        for x in self.bboxColorDialog.findChild(qtw.QDialogButtonBox).findChildren(qtw.QPushButton):
            #print(x,x.objectName()+".")
            x.setMinimumWidth((140.556 * self.widthScale)+0.5)#(100)
        print(self.bboxColorDialog.exec())
        self.boxColor = self.bboxColorDialog.selectedColor()
        self.bboxColorWidget.setBoxColor(self.boxColor)'''

    def dm(self):
        
        if self.active is not None:
            #self.active.setFixedHeight(0)
            self.clearLayout(self.rLayout)
        
        self.scroll = qtw.QScrollArea()
        self.scroll.setObjectName("helpScroll")
        
        self.scroll.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)

        self.settingsHolderLayout = qtw.QGridLayout()
        self.settingsHolderWidget = qtw.QWidget()
        self.settingsHolderWidget.setLayout(self.settingsHolderLayout)
        
        self.rLayout.addWidget(self.settingsHolderWidget)
        
        self.titleLbl = qtw.QLabel("Detection Model")
        self.titleLbl.setObjectName("subTitleLbl")
        self.titleLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5,(28.111 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5) #(10,20,20,20)
        #self.bboxColorWidget = qtw.QColorDialog()
        self.textLbl = qtw.QLabel("Exero's core functionality is based on detection of polyps, which is performed using object detection model. The object detection model is pre-trained to detect polyps, although not perfect but it tries its best.")
        self.textLbl.setWordWrap(True)
        self.textLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,0,(14.0556 * self.widthScale)+0.5,0) #(10,0,10,0)
        self.sp2 = qtw.QWidget()
        self.sp2.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)

        self.settingsHolderLayout.addWidget(self.titleLbl,0,0)
        self.settingsHolderLayout.addWidget(self.textLbl,1,0,1,2)
        self.settingsHolderLayout.addWidget(self.sp2,2,0)
        #print("dm ", self.settingsHolderLayout.spacing())
        self.scroll.setWidget(self.settingsHolderWidget)
        self.scroll.setWidgetResizable(True)
        self.rLayout.addWidget(self.scroll)

        self.addBtns()
        self.active = self.settingsHolderWidget


class SettingsDialog(qtw.QDialog):
    """Dialog for setting the settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent, modal=True)
        screen = app.primaryScreen()
        #print(screen.size(),screen.geometry())
        #print(screen.devicePixelRatio,app.devicePixelRatio)
        #print(screen.logicalDotsPerInch(),screen.physicalDotsPerInch())
        #print(screen.manufacturer(),screen.model())
        self.widthScale = screen.size().width() / 1920
        self.heightScale = screen.size().height() / 1080

        self.initSettings()

        self.setMinimumHeight((843.75 * self.heightScale)+0.5)#(600)
        self.layout = qtw.QHBoxLayout()
        self.setLayout(self.layout)
        self.lLayout = qtw.QVBoxLayout()
        self.lWidget = qtw.QWidget()
        self.lWidget.setLayout(self.lLayout)
        self.layout.addWidget(self.lWidget)
        self.lWidget.setObjectName("settingLWidget")
        #self.lWidget.setObjectName("settingLWidget")
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.lWidget.setFixedWidth((421.669 * self.widthScale)+0.5)#(300)
        #self.layout.addWidget(qtw.QLabel("testing"))
        self.lLayout.setSpacing(0)
        self.lLayout.setContentsMargins(0,0,0,0)
        
        self.settingsLbl = qtw.QLabel("Settings")
        self.settingsLbl.setObjectName("settingsLbl")
        self.lLayout.addWidget(self.settingsLbl)
        self.settingsLbl.setContentsMargins((22.489 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5,(14.055 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5)#(16,20, 10,20)
        self.l1 = clickLabel("General")
        #self.shortcutLbl = clickLabel("Shortcuts")
        self.videoLbl = clickLabel("Video")
        self.l2 = clickLabel("Advanced")
        self.l1.clicked.connect(lambda: self.changeContent(self.l1))
        #self.shortcutLbl.clicked.connect(lambda: self.changeContent(self.shortcutLbl))
        self.videoLbl.clicked.connect(lambda: self.changeContent(self.videoLbl))
        self.l2.clicked.connect(lambda: self.changeContent(self.l2))
        self.lLayout.addWidget(self.l1)
        #self.lLayout.addWidget(self.shortcutLbl)
        self.lLayout.addWidget(self.videoLbl)
        self.lLayout.addWidget(self.l2)
        self.l1.setObjectName("l1")
        #self.shortcutLbl.setObjectName("shortcutLbl")
        self.videoLbl.setObjectName("videoLbl")
        self.l2.setObjectName("l2")
        self.l1.setContentsMargins((14.0556 * self.widthScale)+0.5,(8.4375 * self.heightScale)+0.5,0,(7.0312 * self.heightScale)+0.5) #(10,6,0,5)
        #self.shortcutLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,(7.0312 * self.heightScale)+0.5,0,(7.0312 * self.heightScale)+0.5) #(10,5,0,5)
        self.videoLbl.setContentsMargins((14.0556 * self.widthScale)+0.5,(7.0312 * self.heightScale)+0.5,0,(7.0312 * self.heightScale)+0.5) #(10,5,0,5)
        self.l2.setContentsMargins((14.0556 * self.widthScale)+0.5,(7.0312 * self.heightScale)+0.5,0,(7.0312 * self.heightScale)+0.5) #(10,5,0,5)
        #print(self.l2.contentsMargins())
        self.sp = qtw.QWidget()
        self.lLayout.addWidget(self.sp)
        self.sp.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)
        self.currentSelected = None

        self.rLayout = qtw.QVBoxLayout()
        self.rWidget = qtw.QWidget()
        self.rWidget.setLayout(self.rLayout)
        self.layout.addWidget(self.rWidget)
        self.rLayout.setContentsMargins(0,0,0,0)
        self.rLayout.setSpacing(0)
        
        #self.rLayout.addWidget(qtw.QLabel("testing"))
        #self.general()
        self.active = None
        self.currentDisplayed = None
        self.l1.clicked.connect(self.general)
        self.l1.clicked.emit()
        self.videoLbl.clicked.connect(self.video)
        self.l2.clicked.connect(self.advanced)

        #self.rLayout.addWidget(self.settingsHolderWidget)

    def initSettings(self):
        self.settings = settings.getObj()
        self.settingsDict = self.settings.getSettingsDict()
        self.settingsChangeDict = {}

    def clearLayout(self,layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def addBtns(self):
        self.sp2 = qtw.QWidget()
        self.rLayout.addWidget(self.sp2)
        self.sp2.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)

        self.saveBtn = qtw.QPushButton("Save")
        self.cancelBtn = qtw.QPushButton("Cancel")
        self.rtdBtn = qtw.QPushButton("Reset to default")
        self.rtdBtn.setToolTip("Resets all setting to the defaults")
        self.saveBtn.setFixedSize((140.556 * self.widthScale)+0.5,(42.1875 * self.heightScale)+0.5)#(100,30)
        self.cancelBtn.setFixedSize((140.556 * self.widthScale)+0.5,(42.1875 * self.heightScale)+0.5)#(100,30)
        self.sp3 = qtw.QWidget()
        self.rtdBtn.setFixedSize((210.83455 * self.widthScale)+0.5,(42.1875 * self.heightScale)+0.5)#(150,30)
        self.bLayout = qtw.QHBoxLayout()
        self.bWidget = qtw.QWidget()
        self.bWidget.setObjectName("bWidget")
        self.bWidget.setLayout(self.bLayout)
        self.rLayout.addWidget(self.bWidget)
        self.bLayout.addWidget(self.rtdBtn)
        self.bLayout.addWidget(self.sp3)
        self.bLayout.addWidget(self.saveBtn)
        self.bLayout.addWidget(self.cancelBtn)
        self.bLayout.setContentsMargins((14.0556 * self.widthScale)+0.5,0,(14.0556 * self.widthScale)+0.5,0)#(10,0,10,0)
        self.bLayout.setSpacing((14.0556 * self.widthScale)+0.5) #(10)
        self.bWidget.setFixedHeight((70.3125 * self.heightScale)+0.5) #(50)
        self.sp3.setSizePolicy(qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.MinimumExpanding)
        self.sp3.setMinimumWidth((351.39 * self.widthScale)+0.5) #(250)

        self.rtdBtn.clicked.connect(self.settings.reset)
        self.rtdBtn.clicked.connect(self.initSettings)
        self.rtdBtn.clicked.connect(lambda: self.currentDisplayed())
        self.saveBtn.clicked.connect(lambda: self.settings.saveSettings(self.settingsChangeDict))
        self.cancelBtn.clicked.connect(lambda: self.done(qtw.QDialog.Rejected))
        

    def changeContent(self,callerWidget):
        # Changes the color of the selected option on left panel
        if self.currentSelected:
            oldWidget = self.findChild(clickLabel, self.currentSelected)
            oldWidget.setStyleSheet("#"+self.currentSelected+"{ background-color: #FAFAFA;}") #border-right: 1px solid red;
            cm = oldWidget.contentsMargins()
            cm.setLeft(cm.left()-((7.027 * self.widthScale)+0.5)) #5
            oldWidget.setContentsMargins(cm)
        self.currentSelected = callerWidget.objectName()
        callerWidget.setStyleSheet("#"+self.currentSelected+"{ background-color: #F0F0F0;}") #border-right: 1px solid #F0F0F0;
        cm = callerWidget.contentsMargins()
        cm.setLeft(cm.left()+((7.027 * self.widthScale)+0.5)) #5
        callerWidget.setContentsMargins(cm)
    
    def video(self):
        
        if self.active is not None:
            #self.active.setFixedHeight(0)
            self.clearLayout(self.rLayout)
        
        self.currentDisplayed = self.video

        self.settingsHolderLayout = qtw.QGridLayout()
        self.settingsHolderWidget = qtw.QWidget()
        self.settingsHolderWidget.setLayout(self.settingsHolderLayout)
        
        self.rLayout.addWidget(self.settingsHolderWidget)
        
        self.titleLbl = qtw.QLabel("Video")
        self.titleLbl.setObjectName("settingsSubTitleLbl")
        self.titleLbl.setContentsMargins(0,0,0,(22.5 * self.heightScale)+0.5)#(0,0,0,16)
        
        self.addPrefixLabel = qtw.QLabel("Add prefix to video title")
        #self.bboxColorWidget = qtw.QColorDialog()
        self.addPrefix = qtw.QLineEdit(str(self.settingsDict["videoPrefix"]),self,placeholderText="prefix")

        self.singleFileLabel = qtw.QLabel("Save single file")
        self.singleFileLabel.setToolTip("Enabling this would ensure that only one video file is generated at the end by combining all the separate recorded chunks.")
        self.singleFileBox = qtw.QCheckBox(self)
        self.singleFileBox.setChecked(self.settingsDict["singleVideoFile"]=="True")

        self.settingsHolderLayout.addWidget(self.titleLbl,0,0)
        self.settingsHolderLayout.addWidget(self.addPrefixLabel,1,0)
        self.settingsHolderLayout.addWidget(self.addPrefix,1,1)
        self.settingsHolderLayout.addWidget(self.singleFileLabel,2,0)
        self.settingsHolderLayout.addWidget(self.singleFileBox,2,1)
        self.addPrefix.setSizePolicy(qtw.QSizePolicy.Preferred,qtw.QSizePolicy.Preferred)
        #print(self.addPrefix.height(),self.addPrefix.sizeHint(),self.addPrefix.sizePolicy().horizontalPolicy(),qtw.QSizePolicy.Ignored,qtw.QSizePolicy.Preferred,qtw.QSizePolicy.MinimumExpanding,qtw.QSizePolicy.Expanding,qtw.QSizePolicy.Minimum,qtw.QSizePolicy.Maximum,qtw.QSizePolicy.Fixed)
        #self.addPrefix.setMinimumWidth(100)
        #self.addPrefixLabel.setMinimumWidth(640)
        #self.bboxColorLabel.setContentsMargins(10,0,10,0)
        #self.bboxColorLabel.setContentsMargins(10,0,10,0)
        self.settingsHolderWidget.setContentsMargins((14.0556 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5,(28.111 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5) #(10,20,20,10)
        self.settingsHolderLayout.setSpacing((14.0556 * self.widthScale)+0.5) #(10)

        self.addBtns()
        self.active = self.settingsHolderWidget

        #self.addPrefix.textEdited.connect(lambda x: print("appPrefix", x))
        self.addPrefix.textEdited.connect(lambda x: self.settingsChangeDict.update({"videoPrefix":str(x)}))
        self.singleFileBox.stateChanged.connect(lambda: self.settingsChangeDict.update({"singleVideoFile":str(self.singleFileBox.isChecked())}))
        self.addPrefix.textEdited.connect(lambda x: self.settingsDict.update({"videoPrefix":str(x)}))
        self.singleFileBox.stateChanged.connect(lambda: self.settingsDict.update({"singleVideoFile":str(self.singleFileBox.isChecked())}))

        #self.singleFileBox.stateChanged.

        '''print("a", self.settingsHolderLayout.getContentsMargins(),self.settingsHolderLayout.spacing())
        print(self.bboxColorLabel.getContentsMargins(),self.bboxColorLabel.contentsRect())
        print(self.bboxColorWidget.getContentsMargins(),self.bboxColorWidget.contentsRect())
        print(self.titleLbl.getContentsMargins(),self.titleLbl.contentsRect())
        print(self.bboxWidthSpin.getContentsMargins(),self.bboxWidthSpin.contentsRect())'''

    def general(self):
        
        if self.active is not None:
            #self.active.setFixedHeight(0)
            self.clearLayout(self.rLayout)
        
        self.currentDisplayed = self.general

        self.settingsHolderLayout = qtw.QGridLayout()
        self.settingsHolderWidget = qtw.QWidget()
        self.settingsHolderWidget.setLayout(self.settingsHolderLayout)
        
        self.rLayout.addWidget(self.settingsHolderWidget)
        
        self.titleLbl = qtw.QLabel("General")
        self.titleLbl.setObjectName("settingsSubTitleLbl")
        self.titleLbl.setContentsMargins(0,0,0,(22.5 * self.heightScale)+0.5)#(0,0,0,16)
        
        self.bboxColorLabel = qtw.QLabel("Bounding Box Color")
        #self.bboxColorWidget = qtw.QColorDialog()
        #self.boxColor = qtg.QColor(self.settings.value("boxColor","#E57272",str))
        self.boxColor = qtg.QColor(str(self.settingsDict["boxColor"]))
        self.bboxColorWidget = clickLabel(a=True, boxColor = self.boxColor, widthScale = self.widthScale, heightScale = self.heightScale)
        self.bboxColorWidget.clicked.connect(self.showColorDialog)

        self.bboxWidthLabel = qtw.QLabel("Bounding Box Width")
        self.bboxWidthSpin = qtw.QSpinBox(self,maximum=10,minimum=0,singleStep=1)
        #self.bboxWidthSpin.setValue(self.settings.value("bboxWidth","4",int))
        self.bboxWidthSpin.setValue(int(self.settingsDict["bboxWidth"]))
        self.bboxWidthSpin.setMinimumHeight((30.9 * self.heightScale)+0.5)#22)
        self.bboxWidthSpin.setSizePolicy(qtw.QSizePolicy.Preferred,qtw.QSizePolicy.Preferred)
        ##self.showAccLabel = qtw.QLabel("Show Accuracy")
        ##self.showAccChkBox = qtw.QCheckBox(self)
        ##self.showAccChkBox.setChecked(self.settingsDict["showAccuracy"]=="True")
        #print("self.settingsDict[\"showAccuracy\"]",type(self.settingsDict["showAccuracy"]),bool(self.settingsDict["showAccuracy"]),self.showAccChkBox.isChecked())
        self.playAlarmLabel = qtw.QLabel("Play Alarm")
        self.playAlarmLabel.setToolTip("Enable sound to be played when polyp is detected")
        self.playAlarmChkBox = qtw.QCheckBox(self)
        self.playAlarmChkBox.setChecked(self.settingsDict["playAlarm"]=="True")

        self.maxDGenrImgCountLabel = qtw.QLabel("Maximum Database Generation Images")
        self.maxDGenrImgCountLabel.setToolTip("Limit maximum images generated for database")
        self.maxDGenrImgCountSpin = qtw.QSpinBox(self,maximum=5000,minimum=0,singleStep=1)
        #self.bboxWidthSpin.setValue(self.settings.value("bboxWidth","4",int))
        self.maxDGenrImgCountSpin.setValue(int(self.settingsDict["maxDGenrImgCount"]))
        self.maxDGenrImgCountSpin.setMinimumHeight((30.9 * self.heightScale)+0.5)#22)

        #print("width",self.bboxColorLabel.width())
        self.settingsHolderLayout.addWidget(self.titleLbl,0,0)
        self.settingsHolderLayout.addWidget(self.bboxColorLabel,1,0)
        self.settingsHolderLayout.addWidget(self.bboxColorWidget,1,1)
        self.settingsHolderLayout.addWidget(self.bboxWidthLabel,2,0)
        self.settingsHolderLayout.addWidget(self.bboxWidthSpin,2,1)
        ##self.settingsHolderLayout.addWidget(self.showAccLabel,3,0)
        ##self.settingsHolderLayout.addWidget(self.showAccChkBox,3,1)
        self.settingsHolderLayout.addWidget(self.playAlarmLabel,3,0)
        self.settingsHolderLayout.addWidget(self.playAlarmChkBox,3,1)
        self.settingsHolderLayout.addWidget(self.maxDGenrImgCountLabel,4,0)
        self.settingsHolderLayout.addWidget(self.maxDGenrImgCountSpin,4,1)

        #self.bboxColorLabel.setContentsMargins(10,0,10,0)
        #self.bboxColorLabel.setContentsMargins(10,0,10,0)
        self.settingsHolderWidget.setContentsMargins((14.0556 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5,(28.111 * self.widthScale)+0.5,(14.0625 * self.heightScale)+0.5) #(10,20,20,10)
        self.settingsHolderLayout.setSpacing((14.0556 * self.widthScale)+0.5)#10)

        self.addBtns()
        self.active = self.settingsHolderWidget

        #self.showAccChkBox.stateChanged.connect(lambda: print(str(self.showAccChkBox.isChecked())))
        self.bboxWidthSpin.valueChanged.connect(lambda: self.settingsChangeDict.update({"bboxWidth":str(self.bboxWidthSpin.value())}))
        #self.showAccChkBox.stateChanged.connect(lambda: self.settingsChangeDict.update({"showAccuracy":str(self.showAccChkBox.isChecked())}))
        self.bboxWidthSpin.valueChanged.connect(lambda: self.settingsDict.update({"bboxWidth":str(self.bboxWidthSpin.value())}))
        ##self.showAccChkBox.stateChanged.connect(lambda: self.settingsDict.update({"showAccuracy":str(self.showAccChkBox.isChecked())}))
        self.playAlarmChkBox.stateChanged.connect(lambda: self.settingsDict.update({"playAlarm":str(self.playAlarmChkBox.isChecked())}))
        self.playAlarmChkBox.stateChanged.connect(lambda: self.settingsChangeDict.update({"playAlarm":str(self.playAlarmChkBox.isChecked())}))
        self.maxDGenrImgCountSpin.valueChanged.connect(lambda: self.settingsDict.update({"maxDGenrImgCount":str(self.maxDGenrImgCountSpin.value())}))
        self.maxDGenrImgCountSpin.valueChanged.connect(lambda: self.settingsChangeDict.update({"maxDGenrImgCount":str(self.maxDGenrImgCountSpin.value())}))
        #self.bboxWidthSpin.valueChanged.connect(lambda: (self.settingsDict["bboxWidth"]:=str(self.bboxWidthSpin.value())))
        #self.showAccChkBox.valueChanged.connect(lambda: (self.settingsDict["showAccuracy"]:=str(self.showAccChkBox.checked())))
        

        '''print("a", self.settingsHolderLayout.getContentsMargins(),self.settingsHolderLayout.spacing())
        print(self.bboxColorLabel.getContentsMargins(),self.bboxColorLabel.contentsRect())
        print(self.bboxColorWidget.getContentsMargins(),self.bboxColorWidget.contentsRect())
        print(self.titleLbl.getContentsMargins(),self.titleLbl.contentsRect())
        print(self.bboxWidthSpin.getContentsMargins(),self.bboxWidthSpin.contentsRect())'''


    def showColorDialog(self):

        self.bboxColorDialog = qtw.QColorDialog(self.boxColor, self)
        #self.bboxColorDialog.setOptions(qtw.QColorDialog.NoButtons)
        #print()
        for x in self.bboxColorDialog.findChild(qtw.QDialogButtonBox).findChildren(qtw.QPushButton):
            #print(x,x.objectName()+".")
            x.setMinimumWidth((140.556 * self.widthScale)+0.5)#(100)
        self.bboxColorDialog.colorSelected.connect(lambda: self.settingsChangeDict.update({"boxColor":str(self.bboxColorDialog.selectedColor().name())}))
        self.bboxColorDialog.colorSelected.connect(lambda: self.settingsDict.update({"boxColor":str(self.bboxColorDialog.selectedColor().name())}))
        self.bboxColorDialog.colorSelected.connect(lambda: print("color",str(self.bboxColorDialog.selectedColor().name())))

        flag = self.bboxColorDialog.exec()
        if flag ==1:
            self.boxColor = self.bboxColorDialog.selectedColor()
            self.bboxColorWidget.setBoxColor(self.boxColor)


    def advanced(self):
        
        if self.active is not None:
            #self.active.setFixedHeight(0)
            self.clearLayout(self.rLayout)

        self.currentDisplayed = self.advanced

        self.settingsHolderLayout = qtw.QGridLayout()
        self.settingsHolderWidget = qtw.QWidget()
        self.settingsHolderWidget.setLayout(self.settingsHolderLayout)
        
        self.rLayout.addWidget(self.settingsHolderWidget)
        
        self.titleLbl = qtw.QLabel("Advanced")
        self.titleLbl.setObjectName("settingsSubTitleLbl")
        self.titleLbl.setContentsMargins(0,0,0,(22.5 * self.heightScale)+0.5)#(0,0,0,16)

        self.dGenrGapLabel = qtw.QLabel("Dataset Generation Save each frame after")
        #self.bboxColorWidget = qtw.QColorDialog()
        self.dGenrGapSpin = qtw.QSpinBox(self,minimum=0,suffix=" Frames",singleStep=1)
        self.dGenrGapSpin.setMinimumHeight((30.9 * self.heightScale)+0.5)#(22)
        self.dGenrGapSpin.setValue(int(self.settingsDict["dGenrGap"]))
        self.accThresLabel = qtw.QLabel("Accuracy Threshold")
        self.accThresSpin = qtw.QSpinBox(self,maximum=100,minimum=0,suffix=" %",singleStep=1)
        self.accThresSpin.setMinimumHeight((30.9 * self.heightScale)+0.5)#(22)
        self.accThresSpin.setValue(int(self.settingsDict["accThres"]))
        ##self.rfaLabel = qtw.QLabel("Recent frame adaption")
        ##self.rfaChkBox = qtw.QCheckBox(self)
        ##self.rfaChkBox.setChecked(self.settingsDict["rfa"]=="True")
        self.dequeLengthLabel = qtw.QLabel("Deque Length")
        self.dequeLengthLabel.setToolTip("Length of the double ended queue used in determining new polyp instance")
        self.dequeLengthSpin = qtw.QSpinBox(self,maximum=200,minimum=0,singleStep=1)
        self.dequeLengthSpin.setMinimumHeight((30.9 * self.heightScale)+0.5)#(22)
        self.dequeLengthSpin.setValue(int(self.settingsDict["dequeLength"]))

        self.alarmThreshLabel = qtw.QLabel("Alarm Threshold")
        self.alarmThreshLabel.setToolTip("The threshold used to trigger alarm")
        self.alarmThreshSpin = qtw.QSpinBox(self,maximum=100,minimum=1,suffix="%",singleStep=1)
        self.alarmThreshSpin.setMinimumHeight((30.9 * self.heightScale)+0.5)#(22)
        self.alarmThreshSpin.setValue(int(float(self.settingsDict["alarmThreshold"])*100))

        self.maxVideoFrameLabel = qtw.QLabel("Maximum size of Video Frame")
        self.maxVideoFrameLabel.setToolTip("Sets the Maximum size of the view area of video in terms of width x height")
        self.maxVideoFrameWidth = qtw.QLineEdit(str(self.settingsDict["maxVideoFrameWidth"]),self,placeholderText="Width")
        self.maxVideoFrameHeight = qtw.QLineEdit(str(self.settingsDict["maxVideoFrameHeight"]),self,placeholderText="Height")
        self.maxVideoFrameWidth.setInputMask("D000")
        self.maxVideoFrameHeight.setInputMask("D000")
        self.maxVideoFrameWidth.setToolTip("Width")
        self.maxVideoFrameHeight.setToolTip("Height")
        #self.maxVideoFrameSpin.setMinimumHeight((30.9 * self.heightScale)+0.5)#(22)
        #self.maxVideoFrameSpin.setValue(int(float(self.settingsDict["alarmThreshold"])*100))

        self.settingsHolderLayout.addWidget(self.titleLbl,0,0,1,4)
        self.settingsHolderLayout.addWidget(self.dGenrGapLabel,1,0,1,2)
        self.settingsHolderLayout.addWidget(self.dGenrGapSpin,1,2,1,2)
        self.settingsHolderLayout.addWidget(self.accThresLabel,2,0,1,2)
        self.settingsHolderLayout.addWidget(self.accThresSpin,2,2,1,2)
        ##self.settingsHolderLayout.addWidget(self.rfaLabel,3,0)
        ##self.settingsHolderLayout.addWidget(self.rfaChkBox,3,1)
        self.settingsHolderLayout.addWidget(self.dequeLengthLabel,3,0,1,2)
        self.settingsHolderLayout.addWidget(self.dequeLengthSpin,3,2,1,2)
        self.settingsHolderLayout.addWidget(self.alarmThreshLabel,4,0,1,2)
        self.settingsHolderLayout.addWidget(self.alarmThreshSpin,4,2,1,2)
        self.settingsHolderLayout.addWidget(self.maxVideoFrameLabel,5,0,1,2)
        self.settingsHolderLayout.addWidget(self.maxVideoFrameWidth,5,2,1,1)
        self.settingsHolderLayout.addWidget(self.maxVideoFrameHeight,5,3,1,1)


        self.settingsHolderWidget.setContentsMargins((14.0556 * self.widthScale)+0.5,(28.125 * self.heightScale)+0.5,(28.111 * self.widthScale)+0.5,(14.0625 * self.heightScale)+0.5) #(10,20,20,10)
        self.settingsHolderLayout.setSpacing((14.0556 * self.widthScale)+0.5)#(10)
        #self.dGenrGapSpin.rect(qtc.QRect(0,0,640,480))
        #print("b", self.settingsHolderLayout.getContentsMargins(),self.settingsHolderLayout.spacing())
        #print(self.dGenrGapSpin.getContentsMargins(),self.dGenrGapSpin.contentsRect())
        #print(self.dGenrGapLabel.getContentsMargins(),self.dGenrGapLabel.contentsRect())
        #print(self.titleLbl.getContentsMargins(),self.titleLbl.contentsRect())
        #print(self.accThresSpin.getContentsMargins(),self.accThresSpin.contentsRect())
        self.addBtns()
        self.active = self.settingsHolderWidget

        self.dGenrGapSpin.valueChanged.connect(lambda: self.settingsChangeDict.update({"dGenrGap":str(self.dGenrGapSpin.value())}))
        ##self.rfaChkBox.stateChanged.connect(lambda: self.settingsChangeDict.update({"rfa":str(self.rfaChkBox.isChecked())}))
        self.dGenrGapSpin.valueChanged.connect(lambda: self.settingsDict.update({"dGenrGap":str(self.dGenrGapSpin.value())}))
        ##self.rfaChkBox.stateChanged.connect(lambda: self.settingsDict.update({"rfa":str(self.rfaChkBox.isChecked())}))
        self.accThresSpin.valueChanged.connect(lambda: self.settingsChangeDict.update({"accThres":str(self.accThresSpin.value())}))
        self.accThresSpin.valueChanged.connect(lambda: self.settingsDict.update({"accThres":str(self.accThresSpin.value())}))
        self.dequeLengthSpin.valueChanged.connect(lambda: self.settingsChangeDict.update({"dequeLengthSpin":str(self.dequeLengthSpin.value())}))
        self.dequeLengthSpin.valueChanged.connect(lambda: self.settingsDict.update({"dequeLengthSpin":str(self.dequeLengthSpin.value())}))
        self.alarmThreshSpin.valueChanged.connect(lambda: self.settingsChangeDict.update({"alarmThreshold":str(self.alarmThreshSpin.value()/100)}))
        self.alarmThreshSpin.valueChanged.connect(lambda: self.settingsDict.update({"alarmThreshold":str(self.alarmThreshSpin.value()/100)}))
        self.maxVideoFrameWidth.textEdited.connect(lambda x: self.settingsChangeDict.update({"maxVideoFrameWidth":str(x)}))
        self.maxVideoFrameHeight.textEdited.connect(lambda x: self.settingsDict.update({"maxVideoFrameHeight":str(x)}))
        self.maxVideoFrameWidth.textEdited.connect(lambda x: self.settingsDict.update({"maxVideoFrameWidth":str(x)}))
        self.maxVideoFrameHeight.textEdited.connect(lambda x: self.settingsChangeDict.update({"maxVideoFrameHeight":str(x)}))

def setApp(a):
    global app
    app = a
    print("app set")

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    app.setAttribute(qtc.Qt.AA_DisableWindowContextHelpButton)
    mw = MainWindow()
    sys.exit(app.exec())

# TODO add close event method which closes all the threads before closing the application. Check if its even possible. (To rectify this error which i got when i suddenly close the app)
'''Fatal Python error: could not acquire lock for <_io.BufferedWriter name='<stdout>'> at interpreter shutdown, possibly due to daemon threads

Thread 0x00002e18 (most recent call first):

Thread 0x00003b50 (most recent call first):
  File "d:\zeeshan work\fyp gui\Exero\exero\object_detection\videoByQCamera.py", line 348 in detect

Current thread 0x0000338c (most recent call first):'''