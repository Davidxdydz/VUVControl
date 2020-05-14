import serial
import time
from PyQt5.QtWidgets import QInputDialog,QSpinBox,QTextBrowser,QApplication

class MotorControl:
    def __init__(self,parent,port,estimatedGrating):
        """Attempts to connect to port, BLOCKING WITH 250s timeout!

            Parameters
            ----------
            parent : 
                the main ui object
            port : String
                the name of the arduino's COMPORT
            estimatedGrating : int
                last grating number the motor was
        """
        self.ser = serial.Serial(port.device, timeout=250)
        self.parent = parent
        self.estimatedGrating = estimatedGrating
        if self.ser.is_open:
            self.log(f"opened on {self.ser.port}...")
            QApplication.processEvents()
            response = self.ser.readline().decode()
            if response:
                self.log(response)
            else:
                self.log("Motor does not respond")
                raise Exception("Motor does not respond")
        else:
            self.log("COM port can't be opened")
            raise Exception("COM port can't be opened")
        self.is_open = True

    def calibrate(self):
        """starts the calibration process
        """
        n,result = QInputDialog.getInt(self.parent, "Setup","Input current grating",self.estimatedGrating)
        if not result:
            return
        offset = self.parent.offsetSpinBox.value()
        print(n/10.0+offset)
        self.setCurrentWavelength(n/10.0+offset)
        self.estimatedGrating = n

    def getResponse(self):
        response = self.ser.readline().decode()
        response = response.strip('\r\n')
        if response:
            self.log(response)
            if response[:5] == "error":
                raise Exception(response)
        else:
            self.log("Motor does not respond")
            raise Exception("Motor does not respond")
        return response

    def log(self, message):
        print(message)

    def sendCommand(self,command,value = 0):
        self.ser.write(f"${command} {float(value):.2f}".encode())
        return self.getResponse()

    def goToWavelength(self,wavelength):
        self.sendCommand("gtw",wavelength)
        offset = self.parent.offsetSpinBox.value()
        self.estimatedGrating = int((wavelength-offset)*10)

    def setCurrentWavelength(self,wavelength):
        self.sendCommand("caw",wavelength)
    def cleanup(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
    def __del__(self):
        self.cleanup()

class MotorControlDummy(MotorControl):
    #A dummy class to test when no motor is available
    #simulates time delay waiting for response
    #always returns no error on the motor part
    #does not simulate connection issues at the moment
    def __init__(self,parent,estimatedGrating,timescale = 1):
        self.log("opened on DUMMYPORT")
        self.timescale = timescale
        self.delay(1)
        self.log("connected and ready!")
        self.is_open = True
        self.commands = {"caw":(1,"yey")}
        self.parent = parent
        self.estimatedGrating = estimatedGrating

    def delay(self,duration):
        time.sleep(duration*self.timescale)

    def getResponse(self,command):
        if command not in self.commands:
            return "error"
        self.delay(self.commands[command][0])
        return self.commands[command][1]

    def sendCommand(self,command,value = 0):
        self.log(f"Simulating:${command} {float(value)}")
        return self.getResponse(command)
    def cleanup(self):
        return