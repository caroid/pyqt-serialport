import serial
import threading
import time
import platform
import signal
from PyQt4 import QtCore
import binascii

from pykeyboard import PyKeyboard

class SerialPortContext(QtCore.QObject,object):
    _recvSignal_ = QtCore.pyqtSignal(str,name="recvsignal")
    _recvkeyboardSignal_ = QtCore.pyqtSignal(str,name="recvkeyboardsignal")
    
    def __init__(self,port = None,baud = 115200,bits = 8,stop_bits = 1,check=None):
        super(SerialPortContext,self).__init__()
        self._port_ = port
        if self._port_ == None:
            if platform.system() == "Windows":
                self._port_ = 1
            else:
                self._port_ = "/dev/ttyUSB0"
                
        self._baud_ = baud
        if self._baud_ <= 50 or self._baud_ > 4000000:
            self._baud_ = 4000000
       
        self._is_running_ = False
        self._all_counts_ = 0
        self._recv_counts_ = 0
        self._sent_counts_ = 0
        self._serial_port_ = None
        #self._received_thread_ = threading.Thread(target=self.__recv_func__, args=(self,))
        self._RXD_ = None
        self._CD_ = None
        self._DTR_ = None
        self._RTS_ = None

        self.RecIsHex = 0
        #self.getRecIsHex(self,isHex)
        
    #def getRecIsHex(self,isHex):
    #    self.RecIsHex = isHex


    def getAllCounts(self):
        return self._all_counts_
    
    def getSendCounts(self):
        return self._sent_counts_
    
    def getRecvCounts(self):
        return self._recv_counts_
       
    def clearAllCounts(self):
        self._all_counts_ = 0
        self._recv_counts_ = 0
        self._sent_counts_ = 0
        
    def clearRecvCounts(self):
        self._recv_counts_ = 0
    def clearSentCounts(self):
        self._sent_counts_ = 0
       
    def setRXD(self,value):
        self._RXD_ = value
        if self._serial_port_ == None:
            self._RXD_ = value
        else:
            self._serial_port_.setRTS(value)
    
    def setCD(self,value):
        self._CD_ = value
        if self._serial_port_ == None:
            self._CD_ = value
        else:
            self._serial_port_.setDTR(value)
        
    def setDTR(self,value = True):
        self._DTR_ = value
        if self._serial_port_ == None:
            self._DTR_ = value
        else:
            self._serial_port_.setDTR(value)
    def setRTS(self,value = True):
        self._RTS_ = value
        if self._serial_port_ == None:
            self._RTS_ = value
        else:
            self._serial_port_.setRTS(value)
        
    def __recv_func__(self,context):
        print("start serial port + ") + str(type(context))
        #self.getRecIsHex(self, isHex)
        print 'self.RecIsHex = ',self.RecIsHex
        while context.isRunning():
            line = context._serial_port_.read()
            hex_list = [hex(ord(i)) for i in line]
            # With No timeout set. ser.read() is blocking until the number of bytes is read.
            if not self.RecIsHex:
                context._recvSignal_.emit(line)
            else:
                context._recvSignal_.emit(hex_list[0])
            #hex_list = [hex(ord(i)) for i in line]
            print "In buffer:",hex_list
            buf_len = len(line)
            #print "buf_len:",buf_len
            self._recv_counts_ += buf_len
            self._all_counts_ += self._recv_counts_ + self._recv_counts_
            
        print("close serial port")

    def __recv_keyboard_func__(self,context):
#         print("start serial port")
        while context.isRunning():
            line_keyboard = raw_input()
            print line_keyboard
            # With No timeout set. ser.read() is blocking until the number of bytes is read.
            context._recvkeyboardSignal_.emit(line_keyboard)
            
        print("close serial port")
        
    def registerReceivedCallback(self,callback):
        self._recvSignal_.connect(callback)
        #print callback

    def registerkeyboardReceivedCallback(self,callback):
        self._recvkeyboardSignal_.connect(callback)
        #print callback
        
    def open(self):
        self._serial_port_ = serial.Serial(self._port_,int(self._baud_))
        self._serial_port_.setRTS(self._RTS_)
        self._serial_port_.setDTR(self._DTR_)
        self._received_thread_ = threading.Thread(target = self.__recv_func__,args=(self,))
        self._is_running_ = True
        self._received_thread_.setDaemon(True)
        self._received_thread_.setName("SerialPortRecvThread")
        self._received_thread_.start()
        
        self._received_keyboard_thread = threading.Thread(target = self.__recv_keyboard_func__,args=(self,))
        #self._received_keyboard_thread.setDaemon(True)
        self._received_keyboard_thread.setName("SerialPortRecvkeyboardThread")
        self._received_keyboard_thread.start()
        for item in threading.enumerate():
            print item
        
         
    def close(self):
        print("serial context is running: %s" % self.isRunning())
        self._is_running_ = False
        self._serial_port_.close()
        # when closebutton pused, threading is running now, should be deleted.
            
    def send(self,data,isHex,RecIsHex):
        if not self.isRunning():
            return
        self.RecIsHex = RecIsHex
        if not isHex:
            buff = data.encode("utf-8")
            self._serial_port_.write(buff)
            buf_len = len(data)
            self._sent_counts_ += buf_len
            self._all_counts_ += self._recv_counts_ + self._recv_counts_

        else:
            hex_datas = data.split(' ')
            buffer = ''
            for d in hex_datas:
                buffer += d
            print(buffer.decode('hex'))
            buf_len = len(buffer)
            self._sent_counts_ += buf_len
            self._all_counts_ += self._recv_counts_ + self._recv_counts_
            self._serial_port_.write(buffer.decode("hex"))
        
        
    def send_keyboard(self,str):
        self._serial_port_.write(str + '\n')
    

    def isRunning(self):
        return self._is_running_ and self._serial_port_.isOpen()
         
        
        
