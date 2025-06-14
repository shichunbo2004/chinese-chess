import pygame
import sys
import copy
import pickle
from game import move_action2move_id, move_id2move_action, Game, Board
import subprocess
import os


class Human:
    def __init__(self):
        self.agent = 'HUMAN'

    def get_action(self, move):
        # move从鼠标点击事件触发
        if move_action2move_id.__contains__(move):
            move = move_action2move_id[move]
        else:
            move = -1
        return move

    def set_player_ind(self, p):
        self.player = p


# 初始化pygame
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('bgm/1.mp3')
pygame.mixer.music.set_volume(0.03)
pygame.mixer.music.play(loops=-1, start=0.0)

size = width, height = 700, 700
bg_image = pygame.image.load('imgs/board.png')  # 图片位置
bg_image = pygame.transform.smoothscale(bg_image, size)

clock = pygame.time.Clock()
fullscreen = False
# 创建指定大小的窗口
screen = pygame.display.set_mode(size)
# 设置窗口标题
pygame.display.set_caption("中国象棋")

# 删除 fire_image 相关加载
# fire_image = pygame.transform.smoothscale(pygame.image.load("imgs/fire.png").convert_alpha(), (width // 10, height // 10))
# fire_image.set_alpha(200)

# 制作一个从字符串到pygame.surface对象的映射
str2image = {
    '红车': pygame.transform.smoothscale(pygame.image.load("imgs/hongche.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
    '红马': pygame.transform.smoothscale(pygame.image.load("imgs/hongma.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
    '红象': pygame.transform.smoothscale(pygame.image.load("imgs/hongxiang.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
    '红士': pygame.transform.smoothscale(pygame.image.load("imgs/hongshi.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
    '红帅': pygame.transform.smoothscale(pygame.image.load("imgs/hongshuai.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
    '红炮': pygame.transform.smoothscale(pygame.image.load("imgs/hongpao.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
    '红兵': pygame.transform.smoothscale(pygame.image.load("imgs/hongbing.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
    '黑车': pygame.transform.smoothscale(pygame.image.load("imgs/heiche.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
    '黑马': pygame.transform.smoothscale(pygame.image.load("imgs/heima.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
    '黑象': pygame.transform.smoothscale(pygame.image.load("imgs/heixiang.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
    '黑士': pygame.transform.smoothscale(pygame.image.load("imgs/heishi.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
    '黑帅': pygame.transform.smoothscale(pygame.image.load("imgs/heishuai.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
    '黑炮': pygame.transform.smoothscale(pygame.image.load("imgs/heipao.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
    '黑兵': pygame.transform.smoothscale(pygame.image.load("imgs/heibing.png").convert_alpha(), (width // 10 - 10, height // 10 - 10)),
}
str2image_rect = {key: value.get_rect() for key, value in str2image.items()}

# 根据棋盘列表获得最新位置
# 返回一个由image和rect对象组成的列表
x_ratio = 80
y_ratio = 72
x_bais = 30
y_bais = 25
def board2image(board):
    return_image_rect = []
    for i in range(10):
        for j in range(9):
            piece = board[i][j]
            if piece != '一一':
                str2image_rect[piece].center = (j * x_ratio + x_bais, i * y_ratio + y_bais)
                return_image_rect.append((str2image[piece], copy.deepcopy(str2image_rect[piece])))
    return return_image_rect


fire_rect = pygame.Rect(0, 0, 0, 0)
fire_rect.center = (0 * x_ratio + x_bais, 3 * y_ratio + y_bais)

# 加载两个玩家
board = Board()
start_player = 1  # 开始的玩家

player1 = Human()
player2 = Human()

board.init_board(start_player)
p1, p2 = 1, 2
player1.set_player_ind(1)
player2.set_player_ind(2)
players = {p1: player1, p2: player2}

# 切换玩家
swicth_player = True
draw_fire = False
move_action = ''
first_button = False

illegal_move_msg = ""
illegal_move_time = 0

# 新增高亮圆环函数（蓝色高亮，亮度高）
def draw_selected_effect(surface, pos, radius=36, color=(80, 180, 255, 220)):
    """在指定位置绘制半透明高亮蓝色圆环"""
    effect_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(effect_surf, color, (radius, radius), radius, 8)
    surface.blit(effect_surf, (pos[0] - radius, pos[1] - radius))

start_i_j = None  # 在变量区初始化

move_list = []  # 新增：保存每步move_id

while True:
    # 填充背景
    screen.blit(bg_image, (0, 0))
    for image, image_rect in board2image(board=board.state_deque[-1]):
        screen.blit(image, image_rect)
    if draw_fire and start_i_j is not None:
        # 亮蓝色高亮圆环
        draw_selected_effect(screen, fire_rect.center, radius=36, color=(80, 180, 255, 220))

        # --- 可落点蓝色小圆点 ---
        # 只在选中棋子时显示
        # start_i_j: (j, i)
        start_y, start_x = start_i_j[1], start_i_j[0]
        for move_id in board.availables:
            action = move_id2move_action[move_id]  # 这里去掉 board.
            sy, sx, ey, ex = int(action[0]), int(action[1]), int(action[2]), int(action[3])
            if sy == start_y and sx == start_x:
                # 目标格中心坐标
                cx = ex * x_ratio + x_bais
                cy = ey * y_ratio + y_bais
                pygame.draw.circle(screen, (80, 180, 255), (cx, cy), 10)  # 蓝色小圆点
    # 轮到谁行动提示（正中央显示）
    current_player = board.get_current_player_id()
    action_font = pygame.font.SysFont("SimHei", 48, bold=True)
    if current_player == 1:
        action_text = "红方行动"
        action_color = (220, 30, 30)
    else:
        action_text = "黑方行动"
        action_color = (30, 30, 30)
    action_surface = action_font.render(action_text, True, action_color)
    action_rect = action_surface.get_rect(center=(width // 2, height // 2))
    # 半透明底色
    action_bg = pygame.Surface((action_rect.width + 40, action_rect.height + 20), pygame.SRCALPHA)
    action_bg.fill((255, 255, 255, 180))
    screen.blit(action_bg, (action_rect.left - 20, action_rect.top - 10))
    screen.blit(action_surface, action_rect)

    # 非法走法提示显示2秒（右下角，红色加粗，半透明底色）
    if illegal_move_msg:
        now = pygame.time.get_ticks()
        if now - illegal_move_time < 2000:
            tip_font = pygame.font.SysFont("SimHei", 28, bold=True)
            tip_surface = tip_font.render(illegal_move_msg, True, (255, 0, 0))
            tip_rect = tip_surface.get_rect(bottomright=(width - 20, height - 20))
            tip_bg = pygame.Surface((tip_rect.width + 16, tip_rect.height + 8), pygame.SRCALPHA)
            tip_bg.fill((255, 255, 255, 180))
            screen.blit(tip_bg, (tip_rect.left - 8, tip_rect.top - 4))
            screen.blit(tip_surface, tip_rect)
        else:
            illegal_move_msg = ""

    # 更新界面
    pygame.display.update()
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if not first_button:
                # 只允许点击己方棋子才选中
                for i in range(10):
                    for j in range(9):
                        if abs(80 * j + 30 - mouse_x) < 30 and abs(72 * i + 25 - mouse_y) < 30:
                            piece = board.state_deque[-1][i][j]
                            # 判断是否己方棋子
                            if (current_player == 1 and piece.startswith('红')) or (current_player == 2 and piece.startswith('黑')):
                                first_button = True
                                start_i_j = j, i
                                fire_rect.center = (start_i_j[0] * x_ratio + x_bais, start_i_j[1] * y_ratio + y_bais)
                            break
            elif first_button:
                for i in range(10):
                    for j in range(9):
                        if abs(80 * j + 30 - mouse_x) < 30 and abs(72 * i + 25 - mouse_y) < 30:
                            piece = board.state_deque[-1][i][j]
                            # 如果再次点击己方棋子，则切换选中
                            if (current_player == 1 and piece.startswith('红')) or (current_player == 2 and piece.startswith('黑')):
                                start_i_j = j, i
                                fire_rect.center = (start_i_j[0] * x_ratio + x_bais, start_i_j[1] * y_ratio + y_bais)
                                # 保持first_button为True，等待目标格
                            else:
                                # 不是己方棋子，视为目标格
                                end_i_j = j, i
                                move_action = str(start_i_j[1]) + str(start_i_j[0]) + str(end_i_j[1]) + str(end_i_j[0])
                            break

    if swicth_player:
        current_player = board.get_current_player_id()  # 当前玩家id
        player_in_turn = players[current_player]  # 决定当前玩家的代理

    if player_in_turn.agent == 'HUMAN':
        draw_fire = True
        swicth_player = False
        if len(move_action) == 4:
            move = player_in_turn.get_action(move_action)
            if move != -1 and move in board.availables:
                board.do_move(move)
                move_list.append(move)  # 记录每步
                swicth_player = True
                move_action = ''
                draw_fire = False
                first_button = False
            else:
                move_action = ''
                illegal_move_msg = "非法走法，请重新选择"
                illegal_move_time = pygame.time.get_ticks()

    end, winner = board.game_end()
    if end:
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont("SimHei", 60, bold=True)
        if winner == 1:
            result_text = "游戏结束，红方获胜！"
        elif winner == 2:
            result_text = "游戏结束，黑方获胜！"
        else:
            result_text = "游戏结束，平局！"
        text_surface = font.render(result_text, True, (255, 215, 0))
        text_rect = text_surface.get_rect(center=(width // 2, height // 2 - 40))
        screen.blit(text_surface, text_rect)

        # 保存棋谱
        with open("last_game_moves.pkl", "wb") as f:
            pickle.dump(move_list, f)

        # 创建按钮
        btn_font = pygame.font.SysFont("SimHei", 36, bold=True)
        # 两个按钮一样大
        review_btn_rect = pygame.Rect(width // 2 - 140, height // 2 + 20, 150, 60)
        exit_btn_rect = pygame.Rect(width // 2 + 10, height // 2 + 20, 150, 60)

        pygame.draw.rect(screen, (80, 180, 255), review_btn_rect, border_radius=12)
        pygame.draw.rect(screen, (220, 80, 80), exit_btn_rect, border_radius=12)
        review_text = btn_font.render("对局回放", True, (255, 255, 255))
        exit_text = btn_font.render("退出游戏", True, (255, 255, 255))
        screen.blit(review_text, review_text.get_rect(center=review_btn_rect.center))
        screen.blit(exit_text, exit_text.get_rect(center=exit_btn_rect.center))
        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if review_btn_rect.collidepoint(event.pos):
                        pygame.quit()
                        subprocess.call([sys.executable, "review.py"])
                        waiting = False
                        break
                    elif exit_btn_rect.collidepoint(event.pos):
                        pygame.quit()
                        if os.path.exists("last_game_moves.pkl"):
                            os.remove("last_game_moves.pkl")
                        sys.exit()
        break