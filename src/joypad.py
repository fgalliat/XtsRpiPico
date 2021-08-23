from machine import Pin, ADC
import utime

class Joypad:
    # 26, 27 -> ADC x & y
    # 8, 9   -> PULLUP a & b 
    def __init__(self, xPinNum=26, yPinNum=27, bt0PinNum=8, bt1PinNum=9):
        self.x = 0.0
        self.y = 0.0
        self.a = False
        self.b = False
        self._xAxis = ADC(Pin( xPinNum ))
        self._yAxis = ADC(Pin( yPinNum ))
        self._bt0 = Pin(bt0PinNum, Pin.IN, Pin.PULL_UP)
        self._bt1 = Pin(bt1PinNum, Pin.IN, Pin.PULL_UP)

    def poll(self):
        tmpX = self._xAxis.read_u16()
        tmpY = self._yAxis.read_u16()
        
        self.x = 0.0
        self.y = 0.0
        self.a = (self._bt0.value() == 0)
        self.b = (self._bt1.value() == 0)
        
        # print(tmpY)
        
        if ( tmpX > 53000 ):
            self.x = -1.0
        elif ( tmpX < 15000 ):
            self.x = 1.0
        
        if ( tmpY > 51000 ): # fixed that values lower because of screen
            self.y = -1.0
        elif ( tmpY < 15000 ):
            self.y = 1.0

# ---------------

def test():
    pad = Joypad()

    while True:
        pad.poll()
        
        xv = pad.x
        yv = pad.y
        
        if ( xv < -0.5 ):
            print('Left')
        elif ( xv > 0.5 ):
            print('Right')
        
        if ( yv < -0.5 ):
            print('Up')
        if ( yv > 0.5 ):
            print('Down')
        
        if ( pad.a ):
            print('[A]')
        if ( pad.b ):
            print('[B]')
        
        utime.sleep(0.1)
