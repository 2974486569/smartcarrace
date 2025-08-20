import sensor
import time
import math
from machine import UART
uart = UART(2, baudrate = 115200)

num = 1 #几种颜色1
thresholds = [
    # (0, 100, 18, 127, 2, 73),    #红
    (0, 100, -128, -18, -10, 54),  #绿
    # (0, 100, -32, 20, 58, 127),  #黄
    #(32, 100, 5, 127, -28, -5),   #紫

]
color = [#(255, 0, 0),             #红
         (0, 255, 0),             #绿
        #  (255,255,0),             #黄
         #(255,255,255),             #紫
]


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # 必须关闭以进行颜色跟踪
sensor.set_auto_whitebal(False)  # 必须关闭以进行颜色跟踪
clock = time.clock()

# 只有像素数超过“pixel_threshold”且面积超过“area_threshold”的blob才会被
# “find_blobs”返回。如果更改了“pixels_threshold”和“area_threshold”，请进行相应调整。
# 相机分辨率。不要设置"merge=True"，因为这会合并我们不想要的色块。
def find(img):
    global num
    i = 0
    all_blobs = []
    while i < num:
        for blob in img.find_blobs([thresholds[i]], pixels_threshold=400, area_threshold=200):
            #print(blob.area())
            if blob.area()>8000:
                all_blobs.append((blob, i, blob.area()))
                img.draw_rectangle(blob.rect(), color=color[i])
                img.draw_cross(blob.cx(), blob.cy(), color=color[i])
            #print(blob.area())
        i = i + 1
    if all_blobs:
        largest_blob = max(all_blobs, key=lambda x: x[2])  # Sort by area (x[2])
        color_index = largest_blob[1]  # Get the color index of the largest blob
        if color_index == 0:
            uart.write("g")
            print('g')
        # if color_index == 0:
        #     uart.write("r")
        #     print('r')
        # if color_index == 1:
        #     uart.write("g")
        #     print('g')
        # if color_index == 2:
        #     uart.write("y")
        #     print('y')
        #if color_index == 3:
            #uart.write("p")
            #print('p')







uart_num = 0
flag = 0
while True:
    clock.tick()
    img = sensor.snapshot()
    uart_num = uart.any()       # 获取当前串口数据数量
    if(uart_num):
        uart_str = uart.read(uart_num).strip() # 读取串口数据
        if(uart_str == b'N'):
            flag = 1
        elif(uart_str == b'F'):
            flag = 0
    if(flag == 1):
        find(img)
    #uart.write("y")
    #print(clock.fps())
