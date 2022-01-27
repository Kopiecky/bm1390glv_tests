from ctypes import *
from turtle import color
from dwfconstants import *
import bm1390glv_reg as REG
import time
import sys

class BM1390:
    def __init__(self):
        if sys.platform.startswith("win"):
            self.dwf = cdll.dwf
        elif sys.platform.startswith("darwin"):
            self.dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
        else:
            self.dwf = cdll.LoadLibrary("libdwf.so")
        self.device = c_int()
        self.iNak = c_int()
        self.__open(1e5)
        #time.sleep(0.5)

    def __enablePositiveSupply(self, voltage):
        self.dwf.FDwfAnalogIOChannelNodeSet(self.device, c_int(0), c_int(0), c_double(True))
        self.dwf.FDwfAnalogIOChannelNodeSet(self.device, c_int(0), c_int(1), c_double(voltage))
        self.dwf.FDwfAnalogIOEnableSet(self.device, c_int(True))

    def __read(self, register):
        self.rgRX = (c_ubyte*6)()

        self.dwf.FDwfDigitalI2cWriteRead(self.device, c_int(REG.BM1390GLV_SLAVE_ADDRES << 1), (c_ubyte*1)(register), c_int(1), self.rgRX, c_int(1), byref(self.iNak))
        if self.iNak.value != 0:
            print("NAK "+ str(self.iNak.value))
            quit(0)
        return self.rgRX[0]

    def __write(self, register, value):
        self.dwf.FDwfDigitalI2cWrite(self.device, c_int(REG.BM1390GLV_SLAVE_ADDRES << 1), (c_ubyte*2)(register, value), c_int(2), byref(self.iNak))
        if self.iNak.value != 0:
            print("Device test NAK " + str(self.iNak.value))
            quit(0)

    def __convert_pressure(self, raw_pressure):
         return (raw_pressure[0] * pow(2, 14) + raw_pressure[1] * pow(2, 6) + raw_pressure[2]) / 2048

    def __convert_temperature(self, raw_temperature):
        return ((raw_temperature[0] * pow(2, 8) + raw_temperature[1])/32)



    def __open(self, sampleRate):
        version = create_string_buffer(16)
        self.dwf.FDwfGetVersion(version)
        print("DWF Version: " + str(version.value))

        print("Opening device")
        self.dwf.FDwfDeviceOpen(c_int(-1), byref(self.device))

        if(self.device == hdwfNone.value):
            print("Failed to open device")
            quit(0)

        self.__enablePositiveSupply(3.0)

        print("Configuring I2C ...")

        self.dwf.FDwfDigitalI2cRateSet(self.device, c_double(sampleRate))
        self.dwf.FDwfDigitalI2cSclSet(self.device, c_int(0))
        self.dwf.FDwfDigitalI2cSdaSet(self.device, c_int(1))
        self.dwf.FDwfDigitalI2cClear(self.device, byref(self.iNak))
        if self.iNak.value == 0:
            print("I2C bus error. Check the pull-ups.")
            quit(0)

        self.__write(REG.BM1390GLV_POWER_DOWN, 1)
        self.__write(REG.BM1390GLV_RESET, 1)
        self.__write(REG.BM1390GLV_MODE_CONTROL, 130)
        #self.__write(REG.BM1390GLV_FIFO_CONTROL, 2)
        #time.sleep(1)

    def read_pressure(self):
        raw_pressure = []
        raw_pressure.append(self.__read(REG.BM1390GLV_PRESSURE_1))
        raw_pressure.append(self.__read(REG.BM1390GLV_PRESSURE_2))
        raw_pressure.append(self.__read(REG.BM1390GLV_PRESSURE_3))

        return (self.__convert_pressure(raw_pressure))

    def read_temperature(self):
        raw_temperature = []
        raw_temperature.append(self.__read(REG.BM1390GLV_TEMPERATURE_1))
        raw_temperature.append(self.__read(REG.BM1390GLV_TEMPERATURE_2))
        return (self.__convert_temperature(raw_temperature))
 


        

