from PyQt5.QtWidgets import QApplication, QWidget, QFormLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt
import sys

b = 60
f = 6
ps = .006

xNumPix = 752
yNumPix = 480

cx = xNumPix/2
cy = yNumPix/2

class BallPositionFormApp(QWidget):
    def __init__(self):
        super(BallPositionFormApp, self).__init__()
        self.ballCentroidXLeft = 0
        self.ballCentroidXRight = 0
        self.ballCentroidYLeft = 0
        self.ballCentroidYRight = 0

        # calculated values
        self.x = 0
        self.y = 0
        self.z = 0

        self.outputText = QLabel("")

        self.setWindowTitle("Lab 2")

        self.formLayout = QFormLayout()

        # Row 1, Label 1 - centroid x of the ball, left image
        row1Label = QLabel("Ball Centroid x - Left Image (px)")

        # Row 1, Input 1 - centroid x  of the ball, left image
        row1TextInput = QLineEdit()
        row1TextInput.setValidator(QIntValidator())
        row1TextInput.setAlignment(Qt.AlignRight)
        row1TextInput.setText(str(self.ballCentroidXLeft))
        row1TextInput.textChanged.connect(self.handleChangeLeftX)

        self.formLayout.addRow(row1Label, row1TextInput)

        # Row 2, Label 2 - centroid y of the ball, left image
        row2Label = QLabel("Ball Centroid y - Left Image (px)")

        # Row 2, Input 2 - centroid y of the ball, left image
        row2TextInput = QLineEdit()
        row2TextInput.setValidator(QIntValidator())
        row2TextInput.setAlignment(Qt.AlignRight)
        row2TextInput.setText(str(self.ballCentroidYLeft))
        row2TextInput.textChanged.connect(self.handleChangeLeftY)

        self.formLayout.addRow(row2Label, row2TextInput)

        # Row 3, Label 3 - centroid x of the ball, right image
        row3Label = QLabel("Ball Centroid x - Right Image (px)")

        # Row 3, Input 3 - centroid y of the ball, right image
        row3TextInput = QLineEdit()
        row3TextInput.setValidator(QIntValidator())
        row3TextInput.setAlignment(Qt.AlignRight)
        row3TextInput.setText(str(self.ballCentroidYLeft))
        row3TextInput.textChanged.connect(self.handleChangeRightX)

        self.formLayout.addRow(row3Label, row3TextInput)

        # Row 4, Label 4 - centroid y of the ball, right image
        row4Label = QLabel("Ball Centroid y - Right Image (px)")

        # Row 4, Input 4 - centroid y of the ball, right image
        row4TextInput = QLineEdit()
        row4TextInput.setValidator(QIntValidator())
        row4TextInput.setAlignment(Qt.AlignRight)
        row4TextInput.setText(str(self.ballCentroidYRight))
        row4TextInput.textChanged.connect(self.handleChangeRightY)

        self.formLayout.addRow(row4Label, row4TextInput)

        # Row 5 - Button
        btn = QPushButton("Calculate")
        btn.clicked.connect(self.calculateOutputValues)
        self.formLayout.addRow(btn)

        # Output
        self.formLayout.addRow(self.outputText)

        # Apply layout
        self.setLayout(self.formLayout)

    def handleChangeLeftX(self, text):
        self.ballCentroidXLeft = int(text)
        return

    def handleChangeLeftY(self, text):
        self.ballCentroidYLeft = int(text)
        return

    def handleChangeRightX(self, text):
        self.ballCentroidXRight = int(text)
        return

    def handleChangeRightY(self, text):
        self.ballCentroidYRight = int(text)
        return

    def calculateOutputValues(self):
        d = (abs((self.ballCentroidXLeft-cx)-(self.ballCentroidXRight-cx))*ps)
        
        if d <= 0:
            self.outputText.setText = "Invalid depth value: %d" % d
            return

        if self.ballCentroidYLeft < cy:
            self.outputText.setText = "Invalid negative value calculating Y"
            return

        if self.ballCentroidXLeft < cx:
            self.outputText.setText = "Invalid negative value calculating X"
            return
            
        self.z = (b*f) / d
        self.x = self.z * (self.ballCentroidXLeft - cx) * ps / f
        self.y = self.z * (self.ballCentroidYLeft - cy) * ps / f

        self.showOutputValues()
        return

    def showOutputValues(self):
        text = "Z: %d mm X: %d mm Y: %d mm" % (self.z, self.x, self.y)
        self.outputText.setText(text)
        return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = BallPositionFormApp()
    form.show()
    sys.exit(app.exec_())
