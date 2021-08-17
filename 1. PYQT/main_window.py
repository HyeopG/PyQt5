import cv2
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import numpy as np
from PIL import Image
from PIL import ImageQt

form_class = uic.loadUiType("C:\\PYQT\\1. PYQT\\main_window.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.dataset = []
        self.nowData = []

        self.pushOpen.clicked.connect(self.openFunction)
        self.pushSave.clicked.connect(self.saveFunction)
        self.ShowImg.clicked.connect(self.ShowImgFunction)
        self.RotationImg.clicked.connect(self.RotationImgFunction)
        self.horizontalScrollBar.actionTriggered.connect(self.scrollBarFunction)
        self.Zoom.clicked.connect(self.ZoomFunction)
        self.allSave.clicked.connect(self.allSaveFunction)

    def MakeImg(self, Ndata):
        # x, y값 설정
        x = len(Ndata)
        y = len(Ndata)

        img = Image.new("RGB", (x,y))
        data = np.array(img)
        
        # 하나의 이미지 행렬을 만들어준다.
        count = 0
        for i in range(x):
            for j in range(y):
                data[i][j] = Ndata[i][j]
        return data

    def allSaveFunction(self):
        if self.dataset:
            degree = int(self.plainTextEdit_2.toPlainText())
            zoomNum = float(self.plainTextEdit_3.toPlainText())

            if degree % 360 == 0 and zoomNum <= 0:
                return
            
            self.saveData = []  # 데이터셋 초기화.
            for i in range(len(self.dataset)):
                if zoomNum > 0:
                    dst = cv2.resize(self.MakeImg(self.dataset[i]), None, fx = zoomNum, fy = zoomNum, interpolation=cv2.INTER_CUBIC)
                else:
                    dst = self.MakeImg(self.dataset[i])

                width = dst.shape[0]
                height = dst.shape[1]

                if degree % 360 != 0:
                    matrix = cv2.getRotationMatrix2D((width/2, height/2), degree, 1)
                    src = cv2.warpAffine(dst, matrix, (width, height))
                    self.saveData.append(src)
                else:
                    self.saveData.append(src)
        self.dataset = self.saveData

    def ZoomFunction(self):
        if self.dataset:
            zoomNum = float(self.plainTextEdit_3.toPlainText())

            if zoomNum <= 0:
                return

            width = len(self.nowData)
            height = len(self.nowData)

            dst = cv2.resize(self.MakeImg(self.nowData), None, fx = zoomNum, fy = zoomNum, interpolation=cv2.INTER_CUBIC)

            self.nowData = []
            for x in range(dst.shape[0]):
                temp = []
                for y in range(dst.shape[1]):
                    temp.append(dst[x][y][0])
                self.nowData.append(temp)

            resultImg = Image.fromarray(dst)
            self.photo.setPixmap(ImageQt.toqpixmap(resultImg))


    def scrollBarFunction(self):
        sValue = self.horizontalScrollBar.value()
        self.plainTextEdit.setPlainText(str(sValue))

        if self.dataset:
            self.plainTextEdit_2.setPlainText("0")
            self.plainTextEdit_3.setPlainText("0")

            if sValue >= len(self.dataset) or sValue < 0:
                return

            self.nowData = self.dataset[self.m_num]

            # 결과 출력하기
            resultImg = Image.fromarray(self.MakeImg(self.dataset[sValue]))
            self.photo.setPixmap(ImageQt.toqpixmap(resultImg))


    def RotationImgFunction(self):
        if self.dataset:
            # 각도 받아오기.
            degree = int(self.plainTextEdit_2.toPlainText())
            if degree % 360 == 0:
                return
            
            width = len(self.nowData)
            height = len(self.nowData)

            # 회전 매트릭스 생성.
            matrix = cv2.getRotationMatrix2D((width/2, height/2), degree, 1)
            src = cv2.warpAffine(self.MakeImg(self.nowData), matrix, (width, height))
        
            self.nowData = []
            for x in range(src.shape[0]):
                temp = []
                for y in range(src.shape[1]):
                    temp.append(src[x][y][0])
                self.nowData.append(temp)

            # 결과 출력하기.
            resultImg = Image.fromarray(src)
            self.photo.setPixmap(ImageQt.toqpixmap(resultImg))


    def ShowImgFunction(self):
        if self.dataset:
            self.m_num = int(self.plainTextEdit.toPlainText())
            self.plainTextEdit_2.setPlainText("0")
            self.plainTextEdit_3.setPlainText("0")
            self.horizontalScrollBar.setValue(self.m_num)

            if self.m_num >= len(self.dataset) or self.m_num < 0:
                return

            self.nowData = self.dataset[self.m_num]

            # 결과 출력하기
            resultImg = Image.fromarray(self.MakeImg(self.nowData))
            self.photo.setPixmap(ImageQt.toqpixmap(resultImg))

    def openFunction(self):
        fname = QFileDialog.getOpenFileName(self, 'Open File', '',
                                            'Mnist File(*.idx3-ubyte *.IDX3-UBYTE)')
        if fname[0] == "":
            return

        with open(fname[0], mode='rb') as f:
            data = f.read(16) # 헤더읽기

            #sizeData, Dsize = 이미지전체 개수!
            sizeData = (hex(data[4])+hex(data[5])+hex(data[6])+hex(data[7])).split("0x")
            sizeData.pop(0)
        
            Dsize = int("0x"+sizeData[0]+sizeData[1]+sizeData[2]+sizeData[3], 16)

            #dataX, dataY = x와 y의 크기
            sizeX = (hex(data[8])+hex(data[9])+hex(data[10])+hex(data[11])).split("0x")
            sizeX.pop(0)
            sizeY = (hex(data[12])+hex(data[13])+hex(data[14])+hex(data[15])).split("0x")
            sizeY.pop(0)

            dataX = int("0x"+sizeX[0]+sizeX[1]+sizeX[2]+sizeX[3], 16)
            dataY = int("0x"+sizeY[0]+sizeY[1]+sizeY[2]+sizeY[3], 16)

            #dateset에 mnist이미지 삽입.
            self.dataset = []
            count = 0
            data = f.read()
            for size in range(Dsize):
                savedataX = []
                for x in range(dataX):
                    savedataY = []
                    for y in range(dataY):
                        savedataY.append(data[count])
                        count+=1
                    savedataX.append(savedataY)
                self.dataset.append(savedataX)

            self.horizontalScrollBar.setRange(0, len(self.dataset) - 1)
            f.close()

    def saveFunction(self):
        fname = QFileDialog.getSaveFileName(self, 'Save File', '',
                                    'Mnist File(*.idx3-ubyte *.IDX3-UBYTE)')
        if fname[0] == "":
            return
        with open(fname[0], mode='wb') as f:
            f.write(bytes([0,0,8,3]))

            self.writePushHax(f, len(self.saveData))
            self.writePushHax(f, len(self.saveData[0]))
            self.writePushHax(f, len(self.saveData[0]))

            for size in range(len(self.saveData)):
                for x in range(len(self.saveData[size])):
                    for y in range(len(self.saveData[size])):
                        f.write(bytes([self.saveData[size][x][y][0]]))

    def writePushHax(self, f, value):
            size = hex(value)
            start = 2
            stack = 0 # 바이트만들기 위한 갯수 스택
            for i in range(8, 1, -1):
                if len(size)-2 < i:
                    stack += 1
                    if stack%2 == 0:
                        f.write(bytes([0]))

                elif i%2 == 1:      # 홀수이면 0과 한자리 값을 넣고 짝수칸으로 갈 수 있도록!
                    f.write(bytes([0+int("0x"+size[start], 16)]))
                    start += 1
                    continue

                elif i%2 == 0:
                    for num in range(start, i+1, 2):
                        temp = int("0x"+size[num], 16)*16 + int("0x"+size[num+1], 16)
                        f.write(bytes([temp]))
                    break


        


app = QApplication(sys.argv)
mainWindow = WindowClass() 
mainWindow.show()
app.exec_()