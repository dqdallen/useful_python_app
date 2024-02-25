import pygame
import random
import win32api
import win32con
import win32gui
import ctypes
import sys

# 初始化pygame
pygame.init()

# 设置屏幕大小
infoObject = pygame.display.Info()
screen_width = infoObject.current_w
screen_height = infoObject.current_h
screen = pygame.display.set_mode((screen_width, screen_height))

fuchsia = (0, 0, 0)  # Transparency color
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(
    hwnd,
    win32con.GWL_EXSTYLE,
    win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED,
)
# Set window transparency color, LWA_COLORKEY, LWA_ALPHA
win32gui.SetLayeredWindowAttributes(
    hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY
)

# ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001)
# 设置窗口为最上层
# win32gui.SetWindowPos(
#     hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
# )
win32gui.SetWindowPos(
    hwnd,
    win32con.HWND_TOPMOST,
    0,
    0,
    screen_width,
    screen_height,
    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
)
# 设置游戏窗口标题
pygame.display.set_caption("Circle Game")
# 设置颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
press_step = 0
click_cnt = 0
scale_gap_time = None  # ms
gen_gap_time = None
# 游戏主循环
running = True
state = "start"

# 难度选项
difficulty_options = {
    "Easy": (800, 800, 20),
    "Hard": (300, 300, 70),
    "Mid": (500, 500, 50),
    "Random": (None, None, None),
    "Biggner": (1000, 1000, 5),
}
difficulty_arr = ["Biggner", "Easy", "Mid", "Hard", "Random"]
selected_difficulty = "Biggner"
# 设置圆圈的初始参数
circles = []
circle_radius = 5  # 圆圈的初始半径
circle_growth_rate = 1  # 圆圈每秒增长的大小
last_gen_time = 0
circle_num = 20


def draw_text(surface, text, x, y, color, font_size=36):
    font = pygame.font.SysFont("fangsong", font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)


def draw_options(screen, selected_difficulty):
    draw_text(screen, selected_difficulty, screen_width // 2, 100, GREEN)
    draw_text(screen, "按Up键切换模式（Press \"Up\" to change mode）", screen_width // 2, 300, GREEN)


def start_screen():
    global selected_difficulty, scale_gap_time, gen_gap_time, state, press_step, circle_num, difficulty_options
    # running = True
    # while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                press_step += 1
                if press_step >= len(difficulty_options):
                    press_step = 0
                previous_difficulty = selected_difficulty
                selected_difficulty = difficulty_arr[press_step]
                scale_gap_time, gen_gap_time, circle_num = difficulty_options[
                    previous_difficulty
                ]

            elif event.key == pygame.K_RETURN:
                state = "game"

    screen.fill(fuchsia)
    draw_options(screen, selected_difficulty)
    pygame.display.update()


def game():
    global scale_gap_time, gen_gap_time, circles, circle_radius, circle_growth_rate, last_gen_time, circle_num, click_cnt
    if scale_gap_time is None or gen_gap_time is None:
        scale_gap_time = random.randint(200, 1000)
        gen_gap_time = random.randint(200, 1000)
        circle_num = random.randint(20, 100)

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            click_cnt += 1
            # 鼠标点击事件处理
            mouse_pos = pygame.mouse.get_pos()
            for circle in circles[:]:
                if circle["rect"].collidepoint(mouse_pos):
                    circles.remove(circle)
                    break

    # 生成新的圆圈
    cur_time = pygame.time.get_ticks()
    if len(circles) == 0 or (
        len(circles) < circle_num
        and cur_time - last_gen_time > gen_gap_time
    ):  # 屏幕上最多显示的圆圈数量
        new_circle = {
            "center": (
                random.randint(0, screen_width),
                random.randint(0, screen_height),
            ),
            "radius": circle_radius,
            "color": (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            ),
            "last_time": pygame.time.get_ticks(),
        }
        new_circle["rect"] = pygame.Rect(
            new_circle["center"][0] - new_circle["radius"],
            new_circle["center"][1] - new_circle["radius"],
            new_circle["radius"] * 2,
            new_circle["radius"] * 2,
        )
        circles.append(new_circle)
        last_gen_time = pygame.time.get_ticks()

    # 更新圆圈大小
    for circle in circles:
        if circle["last_time"] - cur_time > scale_gap_time:
            continue
        new_radius = circle["radius"] + circle_growth_rate
        # 限制圆圈半径不超过屏幕宽度或高度的一半
        max_radius = min(screen_width, screen_height) / 2
        new_radius = min(new_radius, max_radius)
        circle["radius"] = new_radius
        circle["rect"] = pygame.Rect(
            circle["center"][0] - circle["radius"],
            circle["center"][1] - circle["radius"],
            circle["radius"] * 2,
            circle["radius"] * 2,
        )

    # 渲染屏幕
    screen.fill(fuchsia)
    for circle in circles:
        # 只渲染圆圈在屏幕内的部分
        visible_rect = circle["rect"].clip(screen.get_rect())
        pygame.draw.circle(
            screen, circle["color"], visible_rect.center, visible_rect.width // 2
        )
    font = pygame.font.SysFont("fangsong", 30)
    click_text = font.render(f"点击个数（click times）: {click_cnt}", True, RED)
    text_rect = click_text.get_rect()
    text_rect.center = (screen_width // 2, 30)  # 屏幕顶部中间
    screen.blit(click_text, text_rect)
    # 更新屏幕显示
    pygame.display.flip()
    pygame.time.Clock().tick(30)  # 控制游戏帧率为30帧每秒


if __name__ == "__main__":
    while running:
        if state == "start":
            start_screen()
        elif state == "game":
            game()
        else:
            print("error")
            exit()