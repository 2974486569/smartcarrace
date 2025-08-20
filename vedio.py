import sensor, image, time
import seekfree, pyb
from machine import Pin
import sensor, image, time, mjpeg
import os
from machine import Pin

key = Pin("C9", Pin.IN_PUP)  # 按键初始化（上拉输入）

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()
lcd = seekfree.LCD180(1)
lcd.full()

# 创建视频文件计数器
counter_file = "/sd/video_counter.txt"

# 尝试读取计数器值
try:
    with open(counter_file, "r") as f:
        video_counter = int(f.read().strip())
except:
    video_counter = 0  # 文件不存在或读取失败，从0开始

# 状态变量
recording = False      # 当前是否正在录制
last_key_state = 1     # 上一次按键状态（初始为松开状态）
m = None               # MJPEG对象初始化

# 显示初始状态
lcd.full(0)
lcd.show_str('Ready.', 25, 50, lcd.GREEN, 1)

try:
    while True:
        img = sensor.snapshot()
        current_key_state = key.value()
        clock.tick()

        # 检测按键下降沿（按下）
        if not recording and current_key_state == 0:
            # 开始新录制
            recording = True
            video_filename = "/sd/video_{}.mjpeg".format(video_counter)
            print("Start recording to:", video_filename)
            m = mjpeg.Mjpeg(video_filename)

            # 显示录制状态
            lcd.show_image(img, 320, 240, 25, 50, zoom=4)
            lcd.show_str('Recording...', 25, 50, lcd.RED, 1)
            start_time = time.ticks_ms()  # 记录开始时间

        # 录制中
        if recording:
            # 添加当前帧
            m.add_frame(img)
            lcd.show_image(img, 320, 240, 25, 50, zoom=4)

            # 显示录制时间
            elapsed = time.ticks_diff(time.ticks_ms(), start_time) // 1000
            lcd.show_str('Rec: {}s'.format(elapsed), 25, 50, lcd.RED, 1)

            # 检测按键上升沿（松开）
            if current_key_state == 1:
                # 结束录制
                recording = False
                m.close(clock.fps())
                print("Recording stopped. FPS:", clock.fps())

                # 更新计数器
                video_counter += 1
                with open(counter_file, "w") as f:
                    f.write(str(video_counter))
                print("Counter updated to", video_counter)

                # 显示完成提示
                lcd.full(0)
                lcd.show_str('Saved {}'.format(video_counter-1), 25, 50, lcd.GREEN, 1)
                time.sleep_ms(1000)  # 短暂显示

                # 立即显示准备状态
                lcd.show_str('Ready.', 25, 50, lcd.GREEN, 1)

        # 非录制状态显示实时画面
        if not recording:
            lcd.show_image(img, 320, 240, 25, 50, zoom=4)
            if current_key_state == 1:  # 确保按键松开状态
                lcd.show_str('Ready.', 25, 50, lcd.GREEN, 1)

        # 更新按键状态
        last_key_state = current_key_state

        # 显示帧率（调试用）
        # print("FPS:", clock.fps())

except Exception as e:
    print("Error:", e)
    # 确保异常时关闭文件
    if m is not None:
        m.close(clock.fps())
finally:
    # 程序结束时确保文件关闭
    if m is not None:
        m.close(clock.fps())
    print("Program ended")
