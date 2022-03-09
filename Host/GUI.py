from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
# from communication import Communication
from class_making import Communication
import math
from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit

pg.setConfigOption('background', (255, 255, 255))  # UA Gray: (130, 138, 143) Changes color of the main page elements
pg.setConfigOption('foreground', (158, 27, 50))  # Crimson: (158, 27, 50)

# Interface variables
app = QtGui.QApplication([])  # Must be defined outside the class
view = pg.GraphicsView()
Layout = pg.GraphicsLayout()  # The kind of layout being used - found in pyqtgraph library
view.setCentralItem(Layout)
view.show()
view.setWindowTitle('Performance Characteristics')
view.resize(1200, 700)


# Fonts for text items
font = QtGui.QFont()
font.setPixelSize(100)


# Title at top
text = """
Alabama Rocketry Association Hot Fire Module.
"""
Layout.addLabel(text, col=1, colspan=40)
Layout.nextRow()

# Put vertical label on left side
Layout.addLabel('Sensor Arrays - Visual Representations of Trends',
                angle=-90, rowspan=3)

Layout.nextRow()
# Save data buttons

# Buttons style
style = "background-color:rgb(158, 27, 50);color:rgb(0,0,0);font-size:14px;"

'''
# Creating an interactive "save" button. Runs the class from "data_handler" to collect and store in a csv.
lb = Layout.addLayout(colspan=21)
proxy = QtGui.QGraphicsProxyWidget()
save_button = QtGui.QPushButton('Start storage')
save_button.setStyleSheet(style)
save_button.clicked.connect(data_base.start)
proxy.setWidget(save_button)
lb.addItem(proxy)
lb.nextCol()

# QGraphicsProxyWidget creates the interactive button I THINK
proxy2 = QtGui.QGraphicsProxyWidget()
end_save_button = QtGui.QPushButton('Stop storage')
end_save_button.setStyleSheet(style)
end_save_button.clicked.connect(data_base.stop)
proxy2.setWidget(end_save_button)
lb.addItem(proxy2)
'''

Layout.nextRow()

# Altitude graph
l1 = Layout.addLayout(colspan=20, rowspan=2)
l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))


# Pressure Graph 1
press_graph1 = l11.addPlot(title="Pressure Triad # 1 (Helium)")

# Making another pressure graph
press_graph2 = l11.addPlot(title="Pressure Triad # 2 (Ethanol)")


l1.nextRow()  # Moving the
l12 = l1.addLayout(rowspan=1, border=(83, 83, 83))


# Pressure Graph 2
press_graph3 = l12.addPlot(title="Pressure Triad # 3 (LOX)")


# Temperature graph
temp_graph = l12.addPlot(title="Temperature (ºc)")

# Time, battery and free fall graphs
l2 = Layout.addLayout(border=(83, 83, 83))


# Time graph
time_graph = l2.addPlot(title="Time (min)")
time_graph.hideAxis('bottom')
time_graph.hideAxis('left')
time_text = pg.TextItem('AAAAAAAAAAAAAAAAAAAAAA', anchor=(0.5, 0.5), color="b")
time_text.setFont(font)
time_text.setText('')
time_graph.addItem(time_text)
sec_total = 0
sec = 0
mins = 0
hours = 0
time_since_start = ''


def update_time(sec_total, time_inc):
    global time_text, sec, mins, hours, time_since_start
    sec += (time_inc/1000)
    mins = sec_total // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60
    time_since_start = "{0}:{1}:{2}".format(int(hours), int(mins), round(sec,1))
    time_text.setText(time_since_start)



# l2.nextRow()
'''
# Battery graph
battery_graph = l2.addPlot(title="Battery Status")
battery_graph.hideAxis('bottom')
battery_graph.hideAxis('left')
battery_text = pg.TextItem("test", anchor=(0.5, 0.5), color="w")
battery_text.setFont(font)
battery_graph.addItem(battery_text)


def update_battery(value_chain):
    pass


l2.nextRow()
textbox = l2.QLineEdit()
textbox.resize(280,40)
textbox.show()

freeFall_graph = l2.addPlot(title="Free Fall")
freeFall_graph.hideAxis('bottom')
freeFall_graph.hideAxis('left')
freeFall_text = pg.TextItem("test", anchor=(0.5, 0.5), color="w")
freeFall_text.setFont(font)
freeFall_graph.addItem(freeFall_text)


def update_freeFall(value_chain):
    global freeFall_text
    freeFall_text.setText('')
    if(value_chain[2] == '0'):
        freeFall_text.setText('No')
    else:
        freeFall_text.setText('Yes')
'''

if __name__ == '__main__':  # Any code in this block will ONLY be run if you run the file "GUI.py" directly
    print('Run just this file and look! You can see this now.')
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_() # This command .exec runs the program and opens everything above
