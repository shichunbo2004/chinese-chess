import pygame
import sys
import copy
import time
from game import move_action2move_id, move_id2move_action, Game, Board
from mcts import MCTSPlayer
from config import CONFIG

if CONFIG['use_frame'] == 'paddle':
    from paddle_net import PolicyValueNet
elif CONFIG['use_frame'] == 'pytorch':
    from pytorch_net import PolicyValueNet
else:
    print('暂不支持您选择的框架')

# 初始化pygame
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('bgm/2.mp3')
pygame.mixer.music.set_volume(0.03)
pygame.mixer.music.play(loops=-1, start=0.0)

size = width, height = 700, 700
bg_image = pygame.image.load('imgs/board.png')
bg_image = pygame.transform.smoothscale(bg_image, size)

clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("中国象棋 机机对战")

# 棋子图片加载
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

# 棋盘坐标参数
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

# 高亮圆环
def draw_selected_effect(surface, pos, radius=36, color=(80, 180, 255, 220)):
    effect_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(effect_surf, color, (radius, radius), radius, 8)
    surface.blit(effect_surf, (pos[0] - radius, pos[1] - radius))

fire_rect = pygame.Rect(0, 0, 0, 0)
fire_rect.center = (0 * x_ratio + x_bais, 3 * y_ratio + y_bais)

# AI玩家设置
if CONFIG['use_frame'] == 'paddle':
    policy_value_net = PolicyValueNet(model_file='current_policy.model')
elif CONFIG['use_frame'] == 'pytorch':
    policy_value_net = PolicyValueNet(model_file='current_policy.pkl')
else:
    print('暂不支持您选择的框架')

board = Board()
start_player = 1  # 红方先手
player1 = MCTSPlayer(policy_value_net.policy_value_fn, c_puct=5, n_playout=800, is_selfplay=0)
player2 = MCTSPlayer(policy_value_net.policy_value_fn, c_puct=5, n_playout=800, is_selfplay=0)

board.init_board(start_player)
p1, p2 = 1, 2
player1.set_player_ind(1)
player2.set_player_ind(2)
players = {p1: player1, p2: player2}

swicth_player = True
draw_fire = False
move_action = ''
first_button = False
start_i_j = None

while True:
    # 绘制棋盘和棋子
    screen.blit(bg_image, (0, 0))
    for image, image_rect in board2image(board=board.state_deque[-1]):
        screen.blit(image, image_rect)

    # 轮到谁行动提示
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
    action_bg = pygame.Surface((action_rect.width + 40, action_rect.height + 20), pygame.SRCALPHA)
    action_bg.fill((255, 255, 255, 180))
    screen.blit(action_bg, (action_rect.left - 20, action_rect.top - 10))
    screen.blit(action_surface, action_rect)

    pygame.display.update()
    clock.tick(60)
    time.sleep(0.5)  # 每步延迟，便于观察

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    if swicth_player:
        current_player = board.get_current_player_id()
        player_in_turn = players[current_player]

    # AI自动走子
    move = player_in_turn.get_action(board)
    board.do_move(move)
    swicth_player = True

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
        text_rect = text_surface.get_rect(center=(width // 2, height // 2))
        tip_font = pygame.font.SysFont("SimHei", 36)
        tip_surface = tip_font.render("请关闭窗口退出游戏", True, (255, 255, 255))
        tip_rect = tip_surface.get_rect(center=(width // 2, height // 2 + 60))
        screen.blit(text_surface, text_rect)
        screen.blit(tip_surface, tip_rect)
        pygame.display.update()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
        break