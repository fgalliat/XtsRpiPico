from machine import Pin, PWM
import utime

class Buzzer:
    # 22 -> PWM Buzzer
    def __init__(self, buzzPinNum=22):
        self.mute = False
        self.buz = PWM(Pin(buzzPinNum))
        
    def tone(self, frequency):
        self.buz.duty_u16(1000)
        self.buz.freq(frequency)
        
    def noTone(self):
        self.buz.duty_u16(0)

    def beep(self, freq, duration):
        self.tone(freq)
        utime.sleep( duration / 1000 )
        # utime.usleep( duration )
        self.noTone()

# ---------------

def test():
    buzz = Buzzer()

    #buzz.tone(440)
    #utime.sleep(0.25)
    #buzz.noTone()
    buzz.beep(880, 100)

# test()