import sys
from PyQt4 import QtGui, QtCore
import time
import mmap
import struct

def set_reg0(mem, reg0_edit):
    # Get the reg0 value from the GUI
    reg0_value = int(reg0_edit.text())

    # Write the reg0 value to memory
    mem.seek(0)
    mem.write(struct.pack('l', reg0_value))

    # Sleep for a short time
    time.sleep(0.5)

def check_reg1(mem, reg1_display, led_display):
    # Read the reg1 value from memory
    mem.seek(4)
    reg1_value = struct.unpack('l', mem.read(4))[0]

    # Update the GUI with the reg1 value
    reg1_display.setText(str(reg1_value))

    # Update the LED status
    if reg1_value == -2147483647:
        led_display.setText('OFF')
        led_display.setStyleSheet('background-color: #FF0000; color: white; font-size: 24px; padding: 20px; border-radius: 10px;')
    else:
        led_display.setText('ON')
        led_display.setStyleSheet('background-color: #AAFF00; color: white; font-size: 24px; padding: 20px; border-radius: 10px;')

def main():
    app = QtGui.QApplication(sys.argv)
    # Create the widget
    widget = QtGui.QWidget()

    # Create the UI elements
    reg0_label = QtGui.QLabel('reg0 value:')
    reg0_edit = QtGui.QLineEdit()
    set_button = QtGui.QPushButton('Set reg0')
    reg1_label = QtGui.QLabel('reg1 value:')
    reg1_display = QtGui.QLabel('')
    led_label = QtGui.QLabel('LED status:')
    led_display = QtGui.QLabel('OFF')
    led_display.setStyleSheet('background-color: #880000; color: white; font-size: 24px; padding: 20px; border-radius: 10px;')

    # Create the layout
    layout = QtGui.QGridLayout()
    layout.addWidget(reg0_label, 0, 0)
    layout.addWidget(reg0_edit, 0, 1)
    layout.addWidget(set_button, 1, 0, 1, 2)
    layout.addWidget(reg1_label, 2, 0)
    layout.addWidget(reg1_display, 2, 1)
    layout.addWidget(led_label, 3, 0)
    layout.addWidget(led_display, 3, 1)

    # Set the layout for the widget
    widget.setLayout(layout)

    # Connect the signal for the button press
    set_button.clicked.connect(lambda: set_reg0(mem, reg0_edit))

    # Create a timer to check the reg1 value every 10 ms (100 Hz)
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: check_reg1(mem, reg1_display, led_display))
    timer.start(10)

    # Open dev mem and set the base address
    with open("/dev/mem", "r+b") as f:
        mem = mmap.mmap(f.fileno(), 1000, offset=0x43c00000)

    # Show the widget
    widget.show()

    # Run the event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
