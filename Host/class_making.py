# from GUI import press_graph1, press_graph2, press_graph3, temp_graph, sec_total
import time
import pandas as pd
import numpy as np
import csv
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
import pyqtgraph as pg
import random
import serial
import serial.tools.list_ports
# from communication import Communication


# This class will be used to define all sensors and sensor operations, including graphing
class Sensor:
    def __init__(self, input_name, input_type, input_ar_num, input_pos, input_file, input_data_read, input_time_inc):
        global time_increment
        self.name = input_name      # The given name of the sensor
        self.type = input_type      # The type of sensor (pressure, temp, etc)
        self.arr = input_ar_num     # Specifies which sensor array the sensor is part of
        self.pos = input_pos        # If in sensor array configuration, specifies order of sensors (should be 0-2)
        # self.pin0 = input_pin0      # The first sensor associated pin on the BBB
        # self.pin1 = input_pin1      # The second sensor associated pin on the BBB
        self.file = input_file      # The file name associated with the sensor
        self.data_read = input_data_read    # If true, this will read from the csv instead of generating data
        self.time_inc = input_time_inc  # Setting the update time interval
        self.avg_data = []          # A list that will average the given data
        self.time = sec_total
        
        
        if self.type == 'Pressure':
            if self.arr == 1:
                self.plot = press_graph1.plot(pen=(0, 0, 0))
                self.text_display = pg.TextItem('AAAAAAAAAAAAAAAAAAAAAA', anchor=(0.5, 0.5), color="black")
                self.text_display.setFont(font)
                text_graph1.addItem(self.text_display)
            
            # 
            elif self.arr == 2:
                self.plot = press_graph2.plot(pen=(205, 58, 27))
                self.text_display = pg.TextItem('AAAAAAAAAAAAAAAAAAAAAA', anchor=(0.5, 0.5), color="r")
                self.text_display.setFont(font)
                text_graph2.addItem(self.text_display)
            
            # Setting graphics for LOX graph/ text
            elif self.arr == 3:
                self.plot = press_graph3.plot(pen=(56, 152, 242))
                self.text_display = pg.TextItem('AAAAAAAAAAAAAAAAAAAAAA', anchor=(0.5, 0.5), color="b")
                self.text_display.setFont(font)
                text_graph3.addItem(self.text_display)
            else:
                print('Error with {}: check that it has an array value of 1-3'.format(self.name))
        
        elif self.type == 'Temperature':
            self.plot = temp_graph.plot(pen=(102, 252, 241))
            self.text_display = pg.TextItem('AAAAAAAAAAAAAAAAAAAAAA', anchor=(0.5, 0.5), color="g")
            self.text_display.setFont(font)
            text_graph4.addItem(self.text_display)
        
        else:
            raise Exception('Error with sensor type, "{}" is not one of the options, in "{}".'.format(self.type, self.name))

        self.data = np.zeros(int(20*(1000/self.time_inc)), dtype=float)  # An initially empty list used to contain data for plotting

    # This function is used to process csv files from PTs - returns the value corresponding to the psi of this sensor
    def csv_tail(self):
        with open(self.file, "r") as f:
            self.name
            for line in f:  # Skips to the end of the file, returns the last line as a string
                pass
            line = line.strip()  # Stripping the \n character
            line = line.split(',')  # Splitting the string into parts based off of comma
            # float_line = [float(x) for x in line[1:]]  # Converts the data values into floats (REMOVES TIME STAMP)
            float_value = float(line[self.pos + 1])  # Yoinks the associated psi data value from the csv

        return float_value

    # This function will read the sensor based off of its type - whether a temperature or a pressure sensor
    def read_sensor(self):
        self.name
        if self.type == 'Pressure':
            # print("I'm reading pressure")
            if self.data_read == 'CSV':
                sensor_data = self.csv_tail()
            elif self.data_read == 'Dummy':
                sensor_data = round(random.uniform(100, 300), 2)

        elif self.type == 'Temperature':
            if self.data_read == 'CSV':
                sensor_data = self.csv_tail()
            elif self.data_read == 'Dummy':
                sensor_data = round(random.uniform(100, 300), 2)
            # print("I'm reading temperature")

        else:
            print('You should not be able to get to this - pressure class read_sensor method')
        return sensor_data

    # This function will update the graph with data read for this sensor
    def graph_update(self, time):
        self.data[:-1] = self.data[1:]
        self.data[-1] = self.read_sensor()
        #if self.type == "Pressure":
        self.text_update()
        time_shifted = (time)*(1000/self.time_inc) - len(self.data)
        self.plot.setData(self.data)
        self.plot.setPos(time_shifted, 0)

    def text_update(self):
        self.text_display.setText(str(self.data[-1]))

    def average(self):
        print("I will be used to create the average of the data")

    def volt_to_psi(self):
        print("I will convert voltages to PSI for us to understand")

    def save_data(self):
        data_df = pd.DataFrame(self.data, columns=['Time', 'P0'])


# This class will be used to control and define valves in the system
# class Valve:
#     def __init__(self, input_name, input_type, input_pin):
#         self.name = input_name
#         self.type = input_type
#         self.pin = input_pin
#         self.state = 'AHHHHHH AHHHHHHHHH'
#         self.df = pd.DataFrame(columns={'time', 'position'})

#     def open(self):
#         t = time.process_time()
#         print("I will open the valve")S
#         self.state = 'open'

#     def close(self):
#         print("I will close the valve")
#         self.state = 'closed'

#     def get_state(self):
#         print(self.name, 'is', self.state)


'''
    GUI SETUP AND COMMANDS =======================================================================================
'''

pg.setConfigOption('background', (255, 255, 255))  # UA Gray: (130, 138, 143) Changes color of the main page elements
pg.setConfigOption('foreground', (158, 27, 50))  # Crimson: (158, 27, 50)

# Interface variables
app = QApplication([])  # Must be defined outside the class
view = pg.GraphicsView()
Layout = pg.GraphicsLayout()  # The kind of layout being used - found in pyqtgraph library
view.setCentralItem(Layout)
view.show()
view.setWindowTitle('Performance Characteristics')
view.resize(1200, 700)


# Fonts for text items
font = QtGui.QFont()
font.setPixelSize(75) # IF LOOKING TO CHANGE FONT SIZE CHANGE THIS VALUE

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

Layout.nextRow()

# Altitude graph
l1 = Layout.addLayout(colspan=100, rowspan=100)
l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))

# Pressure Graph 1
press_graph1 = l11.addPlot(title="Pressure Triad # 1 (Pressurant)")

# Making another pressure graph
press_graph2 = l11.addPlot(title="Pressure Triad # 2 (Fuel)")


l1.nextRow()  # Moving the row down to the next for temperature and LOX pressure
l12 = l1.addLayout(rowspan=1, border=(83, 83, 83))

# Pressure Graph 3
press_graph3 = l12.addPlot(title="Pressure Triad # 3 (LOX)")

# Temperature graph
temp_graph = l12.addPlot(title="Temperature (ºc)")



# Pressurant, fuel, and LOX tanks pressures graphs, as well as time
l2 = Layout.addLayout(border=(83, 83, 83))


# Creating the Pressurant Tank pressure reading graph
l2.nextRow()
text_graph1 = l2.addPlot(title="Pressurant Tank Pressure Readings")
text_graph1.hideAxis('bottom')
text_graph1.hideAxis('left')

# Creating the Fuel Tank pressure reading graph
l2.nextRow()
text_graph2 = l2.addPlot(title="Fuel Tank Pressure Readings")
text_graph2.hideAxis('bottom')
text_graph2.hideAxis('left')

# Creating the LOX Tank pressure reading graph
l2.nextRow()
text_graph3 = l2.addPlot(title="LOX Tank Pressure Readings")
text_graph3.hideAxis('bottom')
text_graph3.hideAxis('left')

# Creating the Temperature Graph
l2.nextRow()
text_graph4 = l2.addPlot(title="Test Temperature Readings")
text_graph4.hideAxis('bottom')
text_graph4.hideAxis('left')

# Creating the time plot graph and text object
l2.nextRow()
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


# def update_time(sec_total, time_inc):
#     global time_text, sec, mins, hours, time_since_start
#     sec += (time_inc/1000)
#     mins = sec_total // 60
#     sec = sec % 60
#     hours = mins // 60
#     mins = mins % 60
#     time_since_start = "{0}:{1}:{2}".format(int(hours), int(mins), round(sec,1))
#     time_text.setText(time_since_start)


if __name__ == '__main__':
    print('This will print when this file is run directly, but this will not print if this file is being imported.')
    # test_valve = Valve('Valve 1','Shutoff', 1)
    # test_valve2 = Valve('Valve 2', 'Shutoff', 2)
    sensor1 = Sensor(flakjfljkajklf)
    sensor1.name = "New name"
    