20171013:
1. 实现HEX收发后，新增了不能循环发送的BUG，原因是：其他分支的send函数调用时，参数错误。
2. menu bar左侧的白色遮挡块仍然不知道原因。

20171012:
1. 实现HEX数据格式的发送和接收。
2. 对callback有了进一步了解，callback的用处是下层传数据给上层，如果上层的数据或参数要传给下层，需要正常的函数调用。

20170416:
reference websit:
1. PyQt Class Reference : http://pyqt.sourceforge.net/Docs/PyQt4/classes.html
2. PyQt4 Reference Guide� : http://pyqt.sourceforge.net/Docs/PyQt4/index.html
3. ASCII value table : http://blog.csdn.net/wswqiang/article/details/11173877
4. Qt key (keyboard) value list: https://wenku.baidu.com/view/a3da6e5af242336c1fb95e1e.html

# Next Step
1. Data received QTextEdit, receive the commands that keypress from keyboard.
2. study the 'threading' module.
3. study 'pyserial' module.
4. Add the analysis Function of test log to Serial GUI tool. (test log about :wf1801,ap230d ,and so on.)
5. 

# pyqt-serialport
serial port with pyqt
