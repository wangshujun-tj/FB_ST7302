#必须在2023/3/1以后的fb-boost固件支持下使用


from micropython import const
from time import sleep_ms
import framebuf,ustruct

class ST7302(framebuf.FrameBuffer):   
    def __init__(self, spi, cs, dc, rst, busy, rot=0): 
        self.EPD_WHITE  = const(0)
        self.EPD_RED    = const(1)
        self.EPD_BLACK  = const(2)    
        self.spi = spi
        self.cs = cs
        self.cs.init(self.cs.OUT, value=1)
        self.dc = dc
        self.dc.init(self.dc.OUT, value=0)
        if rst is not None:
            self.rst = rst
            self.rst.init(self.rst.OUT, value=0)
        else:
            self.rst = None
        self.busy = busy
        self.busy.init(self.busy.IN)
        self.rot=rot
        self.width  = 122
        self.height = 250            

        self.buffer = bytearray(33*125)
        if self.rot==0:
            self.width  = 122
            self.height = 250            
            super().__init__(self.buffer, self.width, self.height, framebuf.ST7302+framebuf.MX)
        elif self.rot==1:
            self.height = 122
            self.width  = 250            
            super().__init__(self.buffer, self.width, self.height, framebuf.ST7302+framebuf.MV)
        elif self.rot==2:
            self.width  = 122
            self.height = 250            
            super().__init__(self.buffer, self.width, self.height, framebuf.ST7302+framebuf.MY)   
        else:
            self.height = 122
            self.width  = 250            
            super().__init__(self.buffer, self.width, self.height, framebuf.ST7302+framebuf.MV+framebuf.MX+framebuf.MY)
        #madctl 0 MX 1MY 2MV
        self.reset()

        self.write_cmd(0x38, None)          #High power mode
        self.write_cmd(0xEB, b'\x02')       #Enable OTP 
        self.write_cmd(0xD7, b'\x68')       #OTP Load Control
        self.write_cmd(0xD1, b'\x01')      #Auto Power Control
        self.write_cmd(0xC0, b'\x80')       #Gate Voltage Setting VGH=12V ; VGL=-5V 
        self.write_cmd(0xC1, b'\x28\x28\x28\x28\x14\x00')    #VSH Setting 
        self.write_cmd(0xC2, b'\x00\x00\x00\x00')    #VSL Setting VSL=0 
        self.write_cmd(0xCB, b'\x14')       #VCOMH Setting 
        self.write_cmd(0xB4, b'\xA5\x66\x01\x00\x00\x40\x01\x00\x00\x40')
                                            #Gate EQ Setting HPM EQ LPM EQ 
        self.write_cmd(0x11, None)          #Sleep out
        sleep_ms(10)
        self.write_cmd(0xC7, b'\xA6\xE9')   #OSC Setting 
        self.write_cmd(0xB2, b'\x01\x05')   #Frame Rate Control
        self.write_cmd(0xB0, b'\x64')       #Duty Setting  250duty/4=63
        self.write_cmd(0x36, b'\x00')       #Memory Data Access Control
        self.write_cmd(0x3A, b'\x11')       #Data Format Select 4 write for 24 bit
        self.write_cmd(0xB9, b'\x23')       #Source Setting
        self.write_cmd(0xB8, b'\x09')       #Panel Setting Frame inversion 间隔和交错
        self.write_cmd(0xD0, b'\x1F')       #
        self.write_cmd(0x29, None)          #Display on
        self.write_cmd(0xB9,b'\xE3')        #enable CLR RAM
        sleep_ms(10)
        self.write_cmd(0xB9,b'\x23')        #enable CLR RAM
        self.write_cmd(0x72,b'\x00')        #Destress OFF
        self.write_cmd(0x38,None)           #High Power Mode ON
        sleep_ms(10)


    def write_cmd(self, command, data=None):
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self.write_data(data)

    def write_data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)


    def reset(self):
        if self.rst is None:
            self.write_cmd(0x12,None)  #SWRESET
        else:
            self.rst(0)
            sleep_ms(30)
            self.rst(1)
        sleep_ms(150)

    def show(self):        
        self.write_cmd(0x2A, b'\x19\x23')      #Set RAM X address counter
        self.write_cmd(0X2B, b'\x00\x7C')   #Set RAM Y address counter
        self.write_cmd(0x2C, self.buffer) #Write RAM

    def sleep(self,state):
        if state==0:
            self.write_cmd(0x38,None)           #High Power Mode ON
        else:
            self.write_cmd(0x39,None)           #Low Power Mode ON
            
        self.write_cmd(0x10,b'\x01')

        