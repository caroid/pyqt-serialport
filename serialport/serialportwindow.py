# -*- coding: utf-8 -*-
#from serialport import serialportform
#from serialport import *
from PyQt4 import QtCore,QtGui, uic
from PyQt4.QtGui import QTextCursor
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT
import sys,os
import platform
from __builtin__ import int
import serialportcontext
import serialportedittext
import switcher
from enaml.widgets.combo_box import ComboBox
import threading
import time

qtCreatorFile = "serialport/serialportform.ui"  # Enter file here.
#serialportform.Ui_SerialPortWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
class SerialPortWindow(QtGui.QMainWindow,Ui_MainWindow):
    _receive_signal = QtCore.pyqtSignal(str)
    _receive_keyboard_signal = QtCore.pyqtSignal(str)
    _auto_send_signal = QtCore.pyqtSignal()
    def __init__(self):
        super(SerialPortWindow,self).__init__()
        QtGui.QMainWindow.__init__(self)
        #serialportform.Ui_SerialPortWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.initForms()
        
    def initForms(self):
        #init serial ports
        # if enable the next setup, make main window can not to resize in running.
        #self.setFixedSize(QtCore.QSize(821, 646))
        
        if platform.system() == "Windows":
            ports = QtCore.QStringList()
            for i in range(8):
                ports.append("COM%d" %((i+1)))    
            self.comboBoxPort.addItems(ports)
        else:
            #todo:scan system serial port
            self.__scanSerialPorts__()
        
        #init bauds
        bauds = ["300", "600", "1200", "1800", "2400", "4800", "9600", "19200", "38400", "57600", "115200", "230400", "460800", "500000", "576000", "921600", "1000000", "1152000", "1500000", "2000000", "2500000", "3000000", "3500000", "4000000"];
        self.comboBoxBaud.addItems(bauds)
        #self.comboBoxBaud.setCurrentIndex(len(bauds) - 1)
        self.comboBoxBaud.setCurrentIndex(6)
        
        checks = ["None","Odd","Even","Zero","One"]
        self.comboBoxCheckSum.addItems(checks)
        self.comboBoxCheckSum.setCurrentIndex(len(checks) - 1)
        
        bits = ["4 Bits","5 Bits","6 Bits" ,"7 Bits","8 Bits"]
        self.comboBoxBits.addItems(bits)
        self.comboBoxBits.setCurrentIndex(len(bits) - 1)
        
        stopbits = ["1 Bit","1.5 Bits","2 Bits"];
        self.comboBoxStopBits.addItems(stopbits)
        self.comboBoxStopBits.setCurrentIndex(0)
        
        
        
        port = str(self.comboBoxPort.currentText())
        baud = int("%s" % self.comboBoxBaud.currentText(),10)
        self._serial_context_ = serialportcontext.SerialPortContext(port = port,baud = baud)
        
        self._serial_edittext_ = serialportedittext.SerialPortInput()
        self._serial_edittext_.__init__(self)
        #self._serial_edittext_.keyPressEvent(self,e)
                
        self.checkBoxCD.setEnabled(False)
        self.checkBoxCTS.setEnabled(False)
        self.checkBoxDSR.setEnabled(False)
        self.checkBoxGND.setEnabled(False)
        self.checkBoxRI.setEnabled(False)
        self.checkBoxDSR.setEnabled(False)
        self.checkBoxRXD.setEnabled(False)
        self.checkBoxTXD.setEnabled(False)
        self.checkBoxDTR.setChecked(True)  
        self.checkBoxRTS.setChecked(True)      
        
        self.lineEditReceivedCounts.setText("0")
        self.lineEditSentCounts.setText("0")
        
        self.pushButtonOpenSerial.clicked.connect(self.__open_serial_port__)
        self._receive_signal.connect(self.__display_recv_data__)
        self._receive_keyboard_signal.connect(self.__display_recv_keyboard_data__)
        self.pushButtonClearRecvArea.clicked.connect(self.__clear_recv_area__)
        self.pushButtonSendData.clicked.connect(self.__send_data__)
        self.checkBoxSendHex.clicked.connect(self.__set_send_hex__)
        self.checkBoxDisplayHex.clicked.connect(self.__set_display_hex__)
        self.checkBoxCD.clicked.connect(self.__set_cd__)
        self.checkBoxRTS.clicked.connect(self.__set_rts__)
        self.checkBoxDTR.clicked.connect(self.__set_dtr__)
        self.pushButtonClearAllCounts.clicked.connect(self.__clear_all_counts)
        self.pushButtonClearRecvCounts.clicked.connect(self.__clear_recv_counts)
        self.pushButtonClearSentCounts.clicked.connect(self.__clear_send_counts)
        self.checkBoxSendLooping.clicked.connect(self.__handle_send_looping__)
        self._auto_send_signal.connect(self.__auto_send_update__)
        self.pushButtonOpenRecvFile.clicked.connect(self.__save_recv_file__)
        self.pushButtonOpenSendFile.clicked.connect(self.__open_send_file__)
        
        self._is_auto_sending = False
        self._recv_file_ = None
        self._recv_key_value_ = None
        print 'caroid1'+ str(type(self._recv_file_))
        self._send_file_ = None
        self._send_file_data = ''

        #self.textEditSent.connect(self.textEditSent,SIGNAL("textChanged()"),self.textEditSent,SLOT("__im_send_data__()"))
        self.textEditSent.textChanged.connect(self.__im_send_data__)
        #self._send_thread = threading.Thread(target=self.__im_send_data__,args=(self,))
        #self._is_auto_sending = True
        #self._send_thread.setDaemon(True)
        #self._send_thread.start()
        
    def __open_send_file__(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, caption=QtCore.QString("Open Send File"))
        try:
           
            if filename and self.checkBoxSendFile.isChecked():
                self._send_file_ = open(filename)
                while True:
                    line = self._send_file_.readline()
                    if not line:
                        break
                    else:
                        self._send_file_data += line
                self._send_file_.close()
                self._send_file_ = None
            self.textEditSent.clear()
            if len(self._send_file_data) > 0:
                self.textEditSent.setText(self._send_file_data)
            
        except Exception,e:
            print(e)
            QtGui.QMessageBox.critical(self,u"打开文件",u"无法打开文件,请检查!")
            
    def __save_recv_file__(self):
        #filename = QtGui.QFileDialog.getSaveFileName(self, caption=QtCore.QString("Save Received File"))
        dirname = '/home/user/0_CIG/0_project/0_maintenance/uart_print/'
        time_of_created = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time())) 
        filename = dirname + time_of_created + '.txt'
        print 'caroid2'+ str(type(self._recv_file_))
        try:
            if self._recv_file_ != None:
                self._recv_file_.flush()
                self._recv_file_.close()
                print 'caroid3'+ str(type(self._recv_file_))
            if filename and self.checkBoxSaveAsFile.isChecked():
                self._recv_file_ = open(filename,"a+")
                print 'caroid4'+ str(type(self._recv_file_))
                data = str(self.textEditReceived.toPlainText())
                if len(data) > 0:
                    self._recv_file_.write(data)
                    print 'caroid5'+ str(type(self._recv_file_))
                
        except Exception,e:
            QtGui.QMessageBox.critical(self,u"保存文件",u"无法保存文件,请检查!")
             
    def closeEvent(self,event):
        self._is_auto_sending = False
        if self._serial_context_.isRunning():
            self._serial_context_.close()
        if self._recv_file_ != None:
            self._recv_file_.flush()
            self._recv_file_.close()
    
    def __handle_send_looping__(self):
        #if self._is_auto_sending:
            self._is_auto_sending = False
            self.pushButtonSendData.setEnabled(True)
        
        
        
    def __clear_all_counts(self):
        self.lineEditReceivedCounts.setText("0")
        self.lineEditSentCounts.setText("0")
        self._serial_context_.clearAllCounts()
        
    def __clear_send_counts(self):
        self._serial_context_.clearSentCounts()
        self.lineEditSentCounts.setText("0")
    
    def __clear_recv_counts(self):
        self._serial_context_.clearRecvCounts()
        self.lineEditReceivedCounts.setText("0")
      
    def __set_dtr__(self):
        self._serial_context_.setDTR(self.checkBoxDTR.isChecked())
        
    def __set_rts__(self):
        self._serial_context_.setRTS(self.checkBoxRTS.isChecked())
    
    def __set_cd__(self):
        self._serial_context_.setCD(self.checkBoxCD.isChecked())
        
    def __scanSerialPorts__(self):
        ports = []
        for i in range(32):
            ports.append("/dev/ttyS%d" % i)
        for i in range(32):
            ports.append("/dev/ttyUSB%d" % i)
        self.comboBoxPort.addItems(ports)
        self.comboBoxPort.setCurrentIndex(32)
        
    def __open_serial_port__(self):
        if  self._serial_context_.isRunning():
            self._serial_context_.close()
            self.pushButtonOpenSerial.setText(u'打开')
        else:
            try:
                #
                #port = self.comboBoxPort.currentIndex()
                selected_port = str(self.comboBoxPort.currentText())
                print 'caroid-port: '+selected_port + ' check'
                #baud = int("%s" % self.comboBoxBaud.currentText(),10)
                selected_baud = int("%s" % self.comboBoxBaud.currentText(),10)
                print 'caroid-baud: '+ str(selected_baud) + ' check'
                #self._serial_context_ = serialportcontext.SerialPortContext(port = '/dev/ttyUSB0',baud = 9600)
                self._serial_context_ = serialportcontext.SerialPortContext(port=selected_port, baud=selected_baud)
                self._serial_context_.registerReceivedCallback(self.__data_received__)
                self._serial_context_.registerkeyboardReceivedCallback(self.__data_keyboard_received__)
                self.checkBoxDTR.setChecked(True)
                self._serial_context_.setDTR(True)
                self.checkBoxRTS.setChecked(True)
                self._serial_context_.setRTS(True)
                self._serial_context_.open()
                self.pushButtonOpenSerial.setText(u'关闭')

                #self._serial_context_.getRecIsHex(self.checkBoxSendHex.isChecked()) #self.checkBoxDisplayHex.isChecked())
            except Exception,e:
                QtGui.QMessageBox.critical(self,u"打开端口",u"打开端口失败,请检查!")
            
    def __data_received__(self,data):
        #print("In buffer:%s", data)
        self._receive_signal.emit(data)
        if self._recv_file_ != None and self.checkBoxSaveAsFile.isChecked():
            self._recv_file_.write(data)
            print 'caroid6'+ str(type(self._recv_file_))
            

    def __data_keyboard_received__(self,data):
        #print('recv:%s' % data)
        self._receive_keyboard_signal.emit(data)
        
            
    def __set_display_hex__(self):
        self.textEditReceived.clear()
        
    def __display_recv_keyboard_data__(self,data):
        #self._serial_context_.write(data)
        self._serial_context_.send_keyboard(data)
        
        
    
    def __display_recv_data__(self,data):
        if self.checkBoxDisplayHex.isChecked():
            self.textEditReceived.insertPlainText(data)
            self.textEditReceived.insertPlainText(' ')
            self.textEditReceived.moveCursor(QTextCursor.End)
        else:
            for l in xrange(len(data)):
                self.textEditReceived.insertPlainText(data[l])
                self.textEditReceived.moveCursor(QTextCursor.End)
                
        if self.checkBoxNewLine.isChecked():
            self.textEditReceived.insertPlainText("\n")
                    
        self.lineEditReceivedCounts.setText("%d" % self._serial_context_.getRecvCounts())


        
    def __clear_recv_area__(self):
        self.textEditReceived.clear()
        
    def __clear_send_area__(self):
        self.textEditSent.clear()
        
    def __set_send_hex__(self):
        self.textEditSent.clear()
        self.textEditSent.setIsHex(self.checkBoxSendHex.isCheckable())
        
    def __send_data__(self):
        data = str(self.textEditSent.toPlainText())
        
        if self._serial_context_.isRunning():
            if len(data) > 0:
                self._serial_context_.send(data, self.checkBoxSendHex.isChecked(), self.checkBoxDisplayHex.isChecked())
                self.lineEditSentCounts.setText("%d" % self._serial_context_.getSendCounts())
                if self.checkBoxEmptyAfterSent.isChecked():
                    self.textEditSent.clear()
            
                if self.checkBoxSendLooping.isChecked():
                    self.pushButtonSendData.setEnabled(False)
                    delay = self.spinBox.value() * 100.0 / 1000.0
                    self._auto_send_thread = threading.Thread(target=self.__auto_send__,args=(delay,))
                    
                    self._is_auto_sending = True
                    self._auto_send_thread.setDaemon(True)
                    self._auto_send_thread.start()
    
    @pyqtSlot()
    def __im_send_data__(self):
        data = str(self.textEditSent.toPlainText())
        if len(data) == 0:
            print 'have no commands  to emit.'
            return
        print data,len(data),data[len(data)-1]
        if data[len(data)-1] == '\b'or data[len(data)-1] == '\t'or data[len(data)-1] == '\n':
            if self._serial_context_.isRunning():
                if len(data) > 0:
                    self._serial_context_.send(data, self.checkBoxSendHex.isChecked(), self.checkBoxDisplayHex.isChecked())
                    self.lineEditSentCounts.setText("%d" % self._serial_context_.getSendCounts())
                    self.textEditSent.clear()
                
                
                    
    def __auto_send__(self,delay):
        while self._is_auto_sending:
            if self.checkBoxSendFile.isChecked():
                if len(self._send_file_data) > 0:
                    self._serial_context_.send(self._send_file_data, self.checkBoxSendHex.isChecked(), self.checkBoxDisplayHex.isChecked())
                    self._auto_send_signal.emit()
                    break
            else:
                data = str(self.textEditSent.toPlainText())
                if self._serial_context_.isRunning():
                    if len(data) > 0:
                        self._serial_context_.send(data, self.checkBoxSendHex.isChecked(), self.checkBoxDisplayHex.isChecked())
                        #self.textEditSent.clear()
                        self._auto_send_signal.emit()
                        
            time.sleep(delay)
            
    def __auto_send_update__(self):
        self.lineEditSentCounts.setText("%d" % self._serial_context_.getSendCounts())
       
        if self.checkBoxSendFile.isChecked():
            if len(self._send_file_data) > 0:
                self.textEditSent.setText(self._send_file_data)
                
        if self.checkBoxEmptyAfterSent.isChecked():
            self.textEditSent.clear()

            

    """                
    def __auto_send__(self,delay):
        while self._is_auto_sending:
            if self.checkBoxSendFile.isChecked():
                if len(self._send_file_data) > 0:
                    self._serial_context_.send(self._send_file_data, self.checkBoxSendHex.isChecked())
                    self._auto_send_signal.emit()
                    break
            else:
                data = str(self.textEditSent.toPlainText())
                if self._serial_context_.isRunning():
                    if len(data) > 0:
                        self._serial_context_.send(data, self.checkBoxSendHex.isChecked())
                        self._auto_send_signal.emit()
                        
            time.sleep(delay)
            
    def __auto_send_update__(self):
        self.lineEditSentCounts.setText("%d" % self._serial_context_.getSendCounts())
       
        if self.checkBoxSendFile.isChecked():
            if len(self._send_file_data) > 0:
                self.textEditSent.setText(self._send_file_data)
                
        if self.checkBoxEmptyAfterSent.isChecked():
            self.textEditSent.clear()
    
    def keyReleaseEvent(self, QKeyEvent):
        if QKeyEvent.key()==QtCore.Qt.Key_Control:
            self.textEditReceived.ctrlPressed=False
            print("The ctrl key is released up")
        return super(SerialPortWindow,self).keyReleaseEvent(QKeyEvent)
    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key()==QtCore.Qt.Key_Control:
            self.textEditReceived.ctrlPressed=True
            print("The ctrl key is holding down")
        if QKeyEvent.key()==QtCore.Qt.Key_Question:
            cmds = str(unichr(0x3F))
        if QKeyEvent.key()==QtCore.Qt.Key_Escape:
            cmds = '\e'
        if QKeyEvent.key()==QtCore.Qt.Key_Tab:
            cmds = '\t'
        if QKeyEvent.key()== 0x20 :#QtCore.Qt.Key_Backspace:
            cmds = str(unichr(0x20)) # '\b'
        if QKeyEvent.key()==QtCore.Qt.Key_Return:
            cmds = '\n'
        else :
            cmds = switcher.key_to_char(QKeyEvent.key())
        self.textEditReceived.insertPlainText(cmds)
        #self.textEditSent.insertPlainText(switcher.key_to_char(QKeyEvent.key()))
        self.textEditReceived.moveCursor(QTextCursor.End)
        #self.textEditSent.moveCursor(QTextCursor.End)
        self._serial_context_.send(cmds, self.checkBoxSendHex.isChecked())
        
        return super(SerialPortWindow,self).keyPressEvent(QKeyEvent)
    """
    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key()==QtCore.Qt.Key_Control:
            self.textEditReceived.ctrlPressed=True
            print("The ctrl key is holding down")
        if QKeyEvent.key()==QtCore.Qt.Key_Up:
            self.textEditReceived.ctrlPressed=True
            print("The Key_Up key is holding down")
        if QKeyEvent.key()==QtCore.Qt.Key_Question:
            cmds = str(unichr(0x3F))
        if QKeyEvent.key()==QtCore.Qt.Key_Escape:
            cmds = '\e'
        if QKeyEvent.key()==QtCore.Qt.Key_Tab:
            cmds = '\t'
        if QKeyEvent.key()== 0x20 :#QtCore.Qt.Key_Backspace:
            cmds = str(unichr(0x20)) # '\b'
        if QKeyEvent.key()==QtCore.Qt.Key_Return:
            cmds = '\n'
        else :
            cmds = switcher.key_to_char(QKeyEvent.key())
        self.textEditReceived.insertPlainText(cmds)
        #self.textEditSent.insertPlainText(switcher.key_to_char(QKeyEvent.key()))
        self.textEditReceived.moveCursor(QTextCursor.End)
        #self.textEditSent.moveCursor(QTextCursor.End)
        self._serial_context_.send(cmds, self.checkBoxSendHex.isChecked())
        
        return super(SerialPortWindow,self).keyPressEvent(QKeyEvent)        
            