from PyQt4 import QtCore,QtGui
import switcher
import serialportcontext

class SerialPortInput(QtGui.QTextEdit):
    def __init__(self,parent = None):
        super(SerialPortInput,self).__init__(parent)
        self._is_hex = False
        self.installEventFilter(self)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
    """       
    def keyPressEvent(self, qKeyEvent):
        print (qKeyEvent.key()) 
        if (qKeyEvent.modifiers() & QtCore.Qt.ShiftModifier):
            self.shift = True
            print 'shift'
        QtGui.QTextEdit.keyPressEvent(self, qKeyEvent)
        if qKeyEvent.key() == QtCore.Qt.Key_Return:
            print('Enter Pressed')
        else:
            super().keyPressEvent(qKeyEvent)
        QtGui.QTextEdit.keyPressEvent(self, qKeyEvent)
        #if self._is_hex:
            #event.setText("%2dX " % (ord(str(event.text()))))
        #    hex_data = "%02X " % (ord(str(event.text())))
        #    qhex_data = QtCore.QString("%s" % hex_data)
            #print('hex_data = %s' % hex_data)
        #    new_event = QtGui.QKeyEvent(event.type(),event.key(),event.modifiers(),
        #                               qhex_data,
        #                                event.isAutoRepeat(),event.count())
        #    return super(SerialPortInput,self).keyPressEvent(new_event)
        #else:
        #    return super(SerialPortInput,self).keyPressEvent(event)
            #line_keyboard = raw_input()
            #print line_keyboard
            #context._recvkeyboardSignal_.emit(line_keyboard)
        
    def setIsHex(self,isHex):
        self._is_hex = isHex
    """
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