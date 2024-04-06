import pygame
import win32api
import win32con
import time
import comtypes.client
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import random
from PIL import Image,ImageSequence

# 获取默认的音频输出设备
speakers = AudioUtilities.GetSpeakers()
interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
# 获取音量接口的指针
volume = cast(interface, POINTER(IAudioEndpointVolume))
# 初始化pygame
pygame.init()

# 设置屏幕大小
screen_width, screen_height = 400, 150
screen = pygame.display.set_mode((screen_width, screen_height))

# 设置标题
pygame.display.set_caption("音量控制小游戏")

# 定义颜色
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# 设置音量条属性
volume_bar_height = 40
volume_bar_width = screen_width - 100
volume_bar_x = (screen_width - volume_bar_width) // 3
volume_bar_y = screen_height - volume_bar_height - 10

# 初始化音量
current_volume = 0.0
max_volume = 100

# 按钮属性
button_text = "Fighting"
button_size = 20
button_width, button_height = button_size * len(button_text), button_size * 2
button_x = (screen_width - button_width) // 2
button_y = volume_bar_y - button_height - 20
# 加载GIF动画
volume_gif = Image.open('./wna.gif')
frames = ImageSequence.Iterator(volume_gif)
house_img = Image.open('./house2.png').convert('RGBA')
house_img = house_img.resize((volume_bar_height, volume_bar_height), Image.ANTIALIAS)
house_img = pygame.image.fromstring(house_img.tobytes(), house_img.size, 'RGBA')
# 记录最后一次点击时间
last_click_time = time.time()

def control_volume(cur_volume):
    global volume
    # 设置音量级别
    volume.SetMasterVolumeLevelScalar(cur_volume, None) 

# 更新音量的函数
def update_volume(new_volume):
    global current_volume
    # 限制音量在0到最大值之间
    current_volume = min(max(new_volume, 0), max_volume)
    # 将音量转换为百分比
    volume_percentage = int(current_volume / max_volume * 100)
    # 更新音量条的颜色填充
    # screen.fill(BLUE, (volume_bar_x, volume_bar_y, volume_bar_width * volume_percentage / 100, volume_bar_height))
    draw_gif(volume_percentage)
    control_volume(volume_percentage/100.)


# 处理点击事件并更新音量
def handle_click():
    global last_click_time
    current_time = time.time()
    click_interval = current_time - last_click_time
    last_click_time = current_time
    # new_volume = 1 / click_interval*3
    new_volume = current_volume + 1/click_interval
    # 根据点击频率调整音量
    # if click_interval < 0.2:
    #     new_volume = current_volume + click_interval*5
    # else:
    #     new_volume = current_volume - 1
    update_volume(new_volume)


# 处理未点击事件并更新音量
def handle_no_click():
    new_volume = current_volume - 1
    update_volume(new_volume)

    

# 绘制按钮
def draw_button():
    pygame.draw.rect(screen, WHITE, (button_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, GRAY, (button_x, button_y, button_width, button_height), 2)
    font = pygame.font.Font(None, button_size)
    text = font.render(button_text, True, BLUE)
    screen.blit(text, (button_x + button_width // 2 - text.get_width() // 2, button_y + button_height // 2 - text.get_height() // 2))

def draw_gif(volume_percentage):
    global volume_bar_width, volume_bar_y, current_frame_index, frames,volume_bar_height
    # 获取当前帧
    try:
        frame = frames[current_frame_index].convert('RGBA')
        current_frame_index += 1
    except IndexError:
        # 如果索引超出范围，重置到第一帧
        current_frame_index = 0
        frame = frames[current_frame_index].convert('RGBA')

    # 调整帧的大小以适应屏幕
    frame = frame.resize((volume_bar_height, volume_bar_height), Image.ANTIALIAS)

    # 将PIL图像转换为pygame Surface
    frame = pygame.image.fromstring(frame.tobytes(), frame.size, 'RGBA')
    # 显示当前帧
    screen.blit(frame, (volume_bar_x+volume_percentage/100 * volume_bar_width, volume_bar_y))  # 假设动画从屏幕左上角开始
current_frame_index = 0
# 主循环
running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
            handle_click()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                handle_click()

    handle_no_click()
    
    screen.blit(house_img, (volume_bar_width + volume_bar_x, volume_bar_y))
    # 绘制音量条和按钮
    pygame.draw.rect(screen, GRAY, (volume_bar_x, volume_bar_y, volume_bar_width+volume_bar_height, volume_bar_height), 2)
    update_volume(current_volume)
    draw_button()
    
    pygame.display.flip()
    # pygame.time.wait(10)  # 控制帧率
    pygame.time.Clock().tick(30)  # 控制游戏帧率为30帧每秒

# 停止pygame
pygame.quit()