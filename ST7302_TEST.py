import ST7302_122250 as P_EDP
from machine import Pin, SPI,I2C,lightsleep,deepsleep,freq,reset
import machine,time


spi = SPI(2, baudrate=20000000, sck = Pin(26), mosi = Pin(27), miso = Pin(34))

for i in range(4):
    edp = P_EDP.ST7302(spi, cs = Pin(25), dc = Pin(33), rst = Pin(32), busy = Pin(35), rot = i)
    edp.font_load("GB2312-24.fon")
    edp.font_set(0x23,0,1,0)
    edp.text("温度:%4.1f℃"%(25.1+i),0,0,1)
    edp.text("湿度:%4.1fRh"%(25.1+i),0,30,1)
    edp.text("气压:%5.1fKpa"%(25.1+i),0,60,1)
    edp.text("方向:%d"%(i),0,90,1)
    if edp.width>edp.height:
        edp.show_bmp("pic/bw%3.3d.bmp"%(i%54),0,170,40)
    else:
        edp.show_bmp("pic/bw%3.3d.bmp"%(i%54),0,40,170)
    edp.show()
    time.sleep(4)
    
import math
import array

for a in range(120):
    ll=array.array("h")
    edp.fill(0)
    t=6
    for i in range(t*2):
        if i%2==0:
            l=60
        else:
            l=29
        ll.append(int(math.cos(math.pi/36*a+math.pi*2*i/(t*2))*l))
        ll.append(int(math.sin(math.pi/36*a+math.pi*2*i/(t*2))*l))
    edp.poly(edp.width//2,edp.height//2,ll,1,1)
    edp.show()

ll=array.array("b")
for i in range(640):
    ll.append(int(math.sin(math.pi*8*(i+a)/160)*127))
for a in range(100):
    edp.fill(0)
    edp.curve(ll[a:a+edp.width-1],1,1,0,edp.height//2,2)
    edp.curve(ll[a+10:a+edp.width-1+10],1,1,0,edp.height//2,2)
    edp.show()

edp.fill(0)
edp.show()
reset()


