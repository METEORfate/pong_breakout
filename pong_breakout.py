# 导入必要的模块
import pygame  # Pygame 是一个用于开发游戏的 Python 库
import sys  # sys 模块提供对解释器使用或维护的一些变量的访问
import random  # random 模块用于生成随机数

# 定义网格的列数和行数
C, R = 11, 20  # 网格有 11 列和 20 行

FPS = 20  # 游戏帧率设置为每秒 20 帧
MOVE_SPACE = 3  # 球移动的速度（单位：帧）

BAT_LENGTH = 6  # 球拍的长度（占据的列数）
BRICK_LAYER = 4  # 砖块的层数

CELL_SIZE = 40  # 每个单元格的大小为 40x40 像素
PADDING = 2  # 单元格之间的间距

# 计算窗口的宽度和高度
WIN_WIDTH = CELL_SIZE * C  # 窗口宽度为 11 * 40 = 440 像素
WIN_HEIGHT = CELL_SIZE * R  # 窗口高度为 20 * 40 = 800 像素

# 定义颜色字典，用于绘制不同元素的颜色
COLORS = {
    "bg": (200, 200, 200),  # 背景颜色
    "player": (65, 105, 225),  # 球拍颜色（皇家蓝）
    "ball": (200, 50, 50),  # 球的颜色（红色）
    "brick": (50, 50, 50),  # 砖块颜色（深灰色）
    "line": (225, 225, 225),  # 网格线颜色（白色）
    "score": (0, 128, 0),  # 分数颜色（绿色）
    "over": (255, 0, 0)  # 游戏结束时的文字颜色（红色）
}

# 定义方向字典，用于表示球的移动方向
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

# 初始化 Pygame
pygame.init()  # 必须调用此函数以初始化 Pygame 的所有子模块

# 创建主窗体
clock = pygame.time.Clock()  # 创建一个时钟对象，用于控制游戏的帧率
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))  # 创建一个窗口，大小为 WIN_WIDTH x WIN_HEIGHT
pygame.display.set_caption('Pong Breakout by Big Shuang')  # 设置窗口标题

# 加载字体
FONTS = [  # 创建不同大小的字体对象
    pygame.font.Font(pygame.font.get_default_font(), font_size) for font_size in [48, 36, 24]
]

# 定义 Brick 类，表示一块砖
class Brick(pygame.sprite.Sprite):
    def __init__(self, c, r, color="bg"):
        super().__init__()  # 调用父类的构造函数

        self.cr = [c, r]  # 砖块在网格中的坐标
        brick_x = c * CELL_SIZE + PADDING  # 砖块的 x 坐标
        brick_y = r * CELL_SIZE + PADDING  # 砖块的 y 坐标

        self.image = pygame.Surface((CELL_SIZE - 2 * PADDING, CELL_SIZE - 2 * PADDING))  # 创建一个表面对象
        self.image.fill(COLORS[color])  # 填充颜色

        self.rect = self.image.get_rect()  # 获取矩形区域
        self.rect.move_ip(brick_x, brick_y)  # 将矩形移动到指定位置

# 定义 BrickManager 类，管理所有砖块
class BrickManager(pygame.sprite.Group):
    def __init__(self, rnum):
        super().__init__()

        for ri in range(rnum):  # 遍历每一层
            for ci in range(C):  # 遍历每一列
                brick = Brick(ci, ri, "brick")  # 创建一块砖
                self.add(brick)  # 添加到组中

    def check_hit(self, ball):  # 检查球是否击中了砖块
        ball_cr = tuple(ball.cr)
        for brick in self.sprites():
            if tuple(brick.cr) == ball_cr:  # 如果球的位置与某块砖的位置相同
                self.remove(brick)  # 移除该砖块
                return True

        return False

# 定义 Ball 类，表示球
class Ball(Brick):
    def __init__(self, c, r, color="ball"):
        super().__init__(c, r, color)

        self.direction = [1, 1]  # 球的初始移动方向

    def move(self):  # 移动球
        new_c = self.cr[0] + self.direction[0]
        self.cr[0] = new_c
        ball_x = new_c * CELL_SIZE + PADDING

        self.rect.left = ball_x

        new_r = self.cr[1] + self.direction[1]
        self.cr[1] = new_r
        ball_y = new_r * CELL_SIZE + PADDING

        self.rect.top = ball_y

    def check_collide_with_wall(self):  # 检查球是否与墙壁发生碰撞
        new_c = self.cr[0] + self.direction[0]
        if not (0 <= new_c < C):  # 如果超出左右边界
            self.direction[0] = -self.direction[0]  # 反转水平方向

        new_r = self.cr[1] + self.direction[1]
        if new_r < 0:  # 如果超出上边界
            self.direction[1] = -self.direction[1]  # 反转垂直方向
        elif new_r >= R:  # 如果超出下边界
            return False

        return True

    def check_collide_with_bat(self, bat):  # 检查球是否与球拍发生碰撞
        new_c = self.cr[0] + self.direction[0]
        new_r = self.cr[1] + self.direction[1]
        if new_r == R - 1 and bat.c <= new_c < bat.c + bat.cnum:  # 如果球碰到球拍
            self.direction[1] = -self.direction[1]  # 反转垂直方向
            new_c = self.cr[0] + bat.mc
            if 0 <= new_c < C:
                self.cr[0] = new_c
                self.check_collide_with_wall()

# 定义 Bat 类，表示球拍
class Bat(pygame.sprite.Sprite):
    def __init__(self, c, batlen):
        super().__init__()

        self.cnum = batlen  # 球拍的长度
        self.c = c  # 球拍的起始列
        self.mc = 0  # 球拍的移动方向
        bat_x = c * CELL_SIZE
        bat_y = (R - 1) * CELL_SIZE

        self.image = pygame.Surface((CELL_SIZE * self.cnum, CELL_SIZE))  # 创建一个表面对象
        self.image.fill(COLORS["player"])  # 填充颜色

        self.rect = self.image.get_rect()  # 获取矩形区域
        self.rect.move_ip(bat_x, bat_y)  # 将矩形移动到指定位置

    def move(self):  # 移动球拍
        new_c = self.c + self.mc
        if 0 <= new_c <= C - self.cnum:  # 检查球拍是否超出边界
            self.c = new_c
            bat_x = self.c * CELL_SIZE

            self.rect.left = bat_x

# 初始化游戏对象
bm = BrickManager(BRICK_LAYER)  # 创建砖块管理器
bat = Bat((C - BAT_LENGTH) // 2, BAT_LENGTH)  # 创建球拍
ball = Ball(C // 2 - 1, R - 2)  # 创建球

running = False  # 游戏运行状态标志
time_count = 0  # 时间计数器

# 显示开始信息
start_info = FONTS[2].render("Press any key to start game", True, COLORS["score"])  # 创建文本对象
text_rect = start_info.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2))  # 获取文本矩形区域
win.blit(start_info, text_rect)  # 将文本绘制到屏幕上

# 主循环
while True:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 如果点击关闭按钮
            pygame.quit()
            sys.exit()

        if running:  # 如果游戏正在运行
            if event.type == pygame.KEYDOWN:  # 如果按下键盘
                if event.key == pygame.K_LEFT or event.key == ord('a'):  # 左移
                    bat.mc = -1
                if event.key == pygame.K_RIGHT or event.key == ord('d'):  # 右移
                    bat.mc = 1
            elif event.type == pygame.KEYUP:  # 如果松开键盘
                if (event.key == pygame.K_LEFT or event.key == ord('a')) and bat.mc == -1:  # 停止左移
                    bat.mc = 0
                if (event.key == pygame.K_RIGHT or event.key == ord('d')) and bat.mc == 1:  # 停止右移
                    bat.mc = 0
        else:  # 如果游戏未开始
            if event.type == pygame.KEYDOWN:  # 如果按下键盘
                bm = BrickManager(BRICK_LAYER)  # 重置砖块
                bat = Bat((C - BAT_LENGTH) // 2, BAT_LENGTH)  # 重置球拍
                ball = Ball(C // 2 - 1, R - 2)  # 重置球
                running = True  # 开始游戏

    if running:  # 如果游戏正在运行
        win.fill(COLORS["bg"])  # 填充背景颜色

        # 绘制网格线
        for ci in range(C):
            cx = CELL_SIZE * ci
            pygame.draw.line(win, COLORS["line"], (cx, 0), (cx, R * CELL_SIZE))
        for ri in range(R):
            ry = CELL_SIZE * ri
            pygame.draw.line(win, COLORS["line"], (0, ry), (C * CELL_SIZE, ry))

        # 移动球拍并绘制
        bat.move()
        win.blit(bat.image, bat.rect)

        # 控制球的移动
        if (time_count + 1) % MOVE_SPACE == 0:
            if ball.check_collide_with_wall():  # 检查球是否与墙壁碰撞
                ball.check_collide_with_bat(bat)  # 检查球是否与球拍碰撞
                ball.move()  # 移动球
                bm.check_hit(ball)  # 检查球是否击中砖块
            else:
                print("Game Over")
                texts = ["Game Over", "Brick Left: %d" % len(bm.sprites()), "Press Any Key to Restart game"]
                for ti, text in enumerate(texts):
                    over_info = FONTS[ti].render(text, True, COLORS["over"])
                    text_rect = over_info.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2 + 48 * ti))
                    win.blit(over_info, text_rect)
                running = False

            if len(bm.sprites()) == 0:  # 如果所有砖块都被击碎
                texts = ["You Win!", "Brick nums: %d" % (BRICK_LAYER * C), "Press Any Key to Restart game"]
                for ti, text in enumerate(texts):
                    over_info = FONTS[ti].render(text, True, COLORS["score"])
                    text_rect = over_info.get_rect(center=(WIN_WIDTH / 2, WIN_HEIGHT / 2 + 48 * ti))
                    win.blit(over_info, text_rect)
                running = False

        # 绘制球和砖块
        win.blit(ball.image, ball.rect)
        bm.draw(win)

        time_count += 1  # 增加时间计数器

    clock.tick(FPS)  # 控制帧率
    pygame.display.update()  # 更新屏幕显示