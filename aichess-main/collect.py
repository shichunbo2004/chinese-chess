"""自我对弈收集数据（可视化）"""
import random
from collections import deque
import copy
import os
import pickle
import time
import pygame
import sys
from game import Board, Game, move_action2move_id, move_id2move_action, flip_map
from mcts import MCTSPlayer
from config import CONFIG

if CONFIG['use_redis']:
    import my_redis, redis

import zip_array

if CONFIG['use_frame'] == 'paddle':
    from paddle_net import PolicyValueNet
elif CONFIG['use_frame'] == 'pytorch':
    from pytorch_net import PolicyValueNet
else:
    print('暂不支持您选择的框架')

# --- Pygame 初始化与资源 ---
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('bgm/2.MP3')
pygame.mixer.music.set_volume(0.03)
pygame.mixer.music.play(loops=-1, start=0.0)

size = width, height = 700, 700
bg_image = pygame.image.load('imgs/board.png')
bg_image = pygame.transform.smoothscale(bg_image, size)
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("中国象棋 自我对弈收集（可视化）")

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

# --- 采集流程类 ---
class CollectPipelineVisual:

    def __init__(self, init_model=None):
        self.board = Board()
        self.game = Game(self.board)
        self.temp = 1
        self.n_playout = CONFIG['play_out']
        self.c_puct = CONFIG['c_puct']
        self.buffer_size = CONFIG['buffer_size']
        self.data_buffer = deque(maxlen=self.buffer_size)
        self.iters = 0
        if CONFIG['use_redis']:
            self.redis_cli = my_redis.get_redis_cli()

    def load_model(self):
        if CONFIG['use_frame'] == 'paddle':
            model_path = CONFIG['paddle_model_path']
        elif CONFIG['use_frame'] == 'pytorch':
            model_path = CONFIG['pytorch_model_path']
        else:
            print('暂不支持所选框架')
        try:
            self.policy_value_net = PolicyValueNet(model_file=model_path)
            print('已加载最新模型')
        except:
            self.policy_value_net = PolicyValueNet()
            print('已加载初始模型')
        self.mcts_player = MCTSPlayer(self.policy_value_net.policy_value_fn,
                                      c_puct=self.c_puct,
                                      n_playout=self.n_playout,
                                      is_selfplay=1)

    def get_equi_data(self, play_data):
        extend_data = []
        for state, mcts_prob, winner in play_data:
            extend_data.append(zip_array.zip_state_mcts_prob((state, mcts_prob, winner)))
            state_flip = state.transpose([1, 2, 0])
            state = state.transpose([1, 2, 0])
            for i in range(10):
                for j in range(9):
                    state_flip[i][j] = state[i][8 - j]
            state_flip = state_flip.transpose([2, 0, 1])
            mcts_prob_flip = copy.deepcopy(mcts_prob)
            for i in range(len(mcts_prob_flip)):
                mcts_prob_flip[i] = mcts_prob[move_action2move_id[flip_map(move_id2move_action[i])]]
            extend_data.append(zip_array.zip_state_mcts_prob((state_flip, mcts_prob_flip, winner)))
        return extend_data

    def collect_selfplay_data(self, n_games=1):
        for i in range(n_games):
            self.load_model()
            play_data = []
            self.board.init_board(start_player=1)
            self.game = Game(self.board)
            mcts_player = self.mcts_player
            end = False
            while not end:
                # --- 可视化部分 ---
                screen.blit(bg_image, (0, 0))
                for image, image_rect in board2image(self.board.state_deque[-1]):
                    screen.blit(image, image_rect)
                # 轮到谁行动提示
                current_player = self.board.get_current_player_id()
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
                time.sleep(0.3)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                # --- AI走子并收集 ---
                move, move_prob = mcts_player.get_action_with_prob(self.board)
                self.board.do_move(move)
                state = copy.deepcopy(self.board.current_state())
                play_data.append((state, move_prob, current_player))
                end, winner = self.board.game_end()
            # --- 结束界面 ---
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
            # --- 数据保存与扩充 ---
            play_data = self.get_equi_data(play_data)
            # 后续保存逻辑与原collect.py一致
            if CONFIG['use_redis']:
                while True:
                    try:
                        for d in play_data:
                            self.redis_cli.rpush('train_data_buffer', pickle.dumps(d))
                        self.redis_cli.incr('iters')
                        self.iters = self.redis_cli.get('iters')
                        print("存储完成")
                        break
                    except:
                        print("存储失败")
                        time.sleep(1)
            else:
                if os.path.exists(CONFIG['train_data_buffer_path']):
                    while True:
                        try:
                            with open(CONFIG['train_data_buffer_path'], 'rb') as data_dict:
                                data_file = pickle.load(data_dict)
                                self.data_buffer = deque(maxlen=self.buffer_size)
                                self.data_buffer.extend(data_file['data_buffer'])
                                self.iters = data_file['iters']
                                del data_file
                                self.iters += 1
                                self.data_buffer.extend(play_data)
                            print('成功载入数据')
                            break
                        except:
                            time.sleep(30)
                else:
                    self.data_buffer.extend(play_data)
                    self.iters += 1
            data_dict = {'data_buffer': self.data_buffer, 'iters': self.iters}
            with open(CONFIG['train_data_buffer_path'], 'wb') as data_file:
                pickle.dump(data_dict, data_file)
        return self.iters

    def run(self):
        try:
            while True:
                iters = self.collect_selfplay_data()
                print('batch i: {}, episode_len: {}'.format(
                    iters, len(self.data_buffer)))
        except KeyboardInterrupt:
            print('\n\rquit')

if __name__ == "__main__":
    collecting_pipeline = CollectPipelineVisual(init_model='current_policy.model')
    collecting_pipeline.run()