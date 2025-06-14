import pygame
import sys
import subprocess

pygame.init()
size = width, height = 700, 700
screen = pygame.display.set_mode(size)
pygame.display.set_caption("中国象棋 - 主菜单")
font = pygame.font.SysFont("SimHei", 60, bold=True)
btn_font = pygame.font.SysFont("SimHei", 36, bold=True)
tip_font = pygame.font.SysFont("SimHei", 24)

bg_color = (235, 220, 180)
btn_color = (80, 180, 255)
btn_hover = (120, 220, 255)
btn_text_color = (30, 30, 30)
border_color = (180, 80, 80)
shadow_color = (180, 180, 180)
title_color = (200, 40, 40)

buttons = [
    {"text": "人人对战", "rect": pygame.Rect(250, 220, 200, 60), "file": "humanplay.py"},
    {"text": "人机对战", "rect": pygame.Rect(250, 320, 200, 60), "file": "UIplay2.py"},
    {"text": "机机对战", "rect": pygame.Rect(250, 420, 200, 60), "file": "collect.py"},
]

def draw_menu():
    # 渐变背景
    for y in range(height):
        color = (
            bg_color[0] + int((255 - bg_color[0]) * y / height * 0.2),
            bg_color[1] + int((255 - bg_color[1]) * y / height * 0.2),
            bg_color[2] + int((255 - bg_color[2]) * y / height * 0.2),
        )
        pygame.draw.line(screen, color, (0, y), (width, y))
    # 标题阴影
    title = font.render("中国象棋", True, title_color)
    shadow = font.render("中国象棋", True, shadow_color)
    title_rect = title.get_rect(center=(width // 2, 110))
    shadow_rect = shadow.get_rect(center=(width // 2 + 4, 114))
    screen.blit(shadow, shadow_rect)
    screen.blit(title, title_rect)
    # 按钮
    mouse_pos = pygame.mouse.get_pos()
    for btn in buttons:
        color = btn_hover if btn["rect"].collidepoint(mouse_pos) else btn_color
        # 按钮阴影
        shadow_rect = btn["rect"].copy()
        shadow_rect.move_ip(4, 4)
        pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=16)
        # 按钮本体
        pygame.draw.rect(screen, color, btn["rect"], border_radius=16)
        pygame.draw.rect(screen, border_color, btn["rect"], 3, border_radius=16)
        text = btn_font.render(btn["text"], True, btn_text_color)
        text_rect = text.get_rect(center=btn["rect"].center)
        screen.blit(text, text_rect)
    # 底部提示
    tip = tip_font.render("请选择模式，ESC退出", True, (100, 100, 100))
    tip_rect = tip.get_rect(center=(width // 2, height - 40))
    screen.blit(tip, tip_rect)
    pygame.display.update()

while True:
    draw_menu()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in buttons:
                if btn["rect"].collidepoint(event.pos):
                    pygame.quit()
                    subprocess.call([sys.executable, btn["file"]])
                    sys.exit()