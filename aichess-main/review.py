import pygame
import sys
import time
import pickle
import copy
from game import Board, move_id2move_action

pygame.init()
size = width, height = 700, 700
screen = pygame.display.set_mode(size)
pygame.display.set_caption("中国象棋 对局回放")
bg_image = pygame.image.load('imgs/board.png')
bg_image = pygame.transform.smoothscale(bg_image, size)

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

def board2image(board):
    return_image_rect = []
    for i in range(10):
        for j in range(9):
            piece = board[i][j]
            if piece != '一一':
                str2image_rect[piece].center = (j * x_ratio + x_bais, i * y_ratio + y_bais)
                return_image_rect.append((str2image[piece], copy.deepcopy(str2image_rect[piece])))
    return return_image_rect

# 读取保存的棋谱数据
with open("last_game_moves.pkl", "rb") as f:
    move_list = pickle.load(f)

board = Board()
board.init_board(start_player=1)
step = 0
auto_play = False

# 棋盘坐标参数（与 humanplay.py 保持一致）
x_ratio = 80
y_ratio = 72
x_bais = 30
y_bais = 25

while True:
    screen.blit(bg_image, (0, 0))
    for image, image_rect in board2image(board.state_deque[-1]):
        screen.blit(image, image_rect)
    # 步数显示
    font = pygame.font.SysFont("SimHei", 32)
    step_surface = font.render(f"第 {step} 步", True, (30, 30, 30))
    screen.blit(step_surface, (20, 20))
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and step < len(move_list):
                board.do_move(move_list[step])
                step += 1
            elif event.key == pygame.K_LEFT and step > 0:
                # 回退一步：重置棋盘并重放到step-1
                board.init_board(start_player=1)
                for i in range(step-1):
                    board.do_move(move_list[i])
                step -= 1
            elif event.key == pygame.K_SPACE:
                auto_play = not auto_play

    if auto_play and step < len(move_list):
        board.do_move(move_list[step])
        step += 1
        time.sleep(0.5)