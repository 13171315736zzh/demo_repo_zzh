#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
俄罗斯方块 - Tetris
使用方向键左右移动，上键旋转，下键加速下落，空格键硬降落
"""

import pygame
import random
import sys

# 初始化
pygame.init()

# 常量
CELL_SIZE = 30
COLS = 10
ROWS = 20
SCREEN_WIDTH = CELL_SIZE * COLS + 200  # 右侧留出信息区
SCREEN_HEIGHT = CELL_SIZE * ROWS
FPS = 60
FALL_SPEED = 500  # 毫秒

# 颜色 (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 0, 0),        # 空
    (0, 255, 255),    # I - 青色
    (255, 255, 0),    # O - 黄色
    (128, 0, 128),    # T - 紫色
    (0, 255, 0),      # S - 绿色
    (255, 0, 0),      # Z - 红色
    (0, 0, 255),      # J - 蓝色
    (255, 165, 0),    # L - 橙色
]

# 方块形状定义 (每个形状的旋转状态)
SHAPES = [
    [],  # 0 空
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
]


class Tetromino:
    """方块类"""
    def __init__(self, shape_type):
        self.type = shape_type
        self.shape = [row[:] for row in SHAPES[shape_type]]
        self.color = COLORS[shape_type]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        """顺时针旋转"""
        self.shape = [list(row) for row in zip(*self.shape[::-1])]


class TetrisGame:
    """游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块 - Tetris")
        self.clock = pygame.time.Clock()
        self.grid = [[0] * COLS for _ in range(ROWS)]
        self.current_piece = None
        self.next_piece = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.last_fall = pygame.time.get_ticks()
        self.spawn_piece()

    def spawn_piece(self):
        """生成新方块"""
        if self.next_piece is None:
            self.next_piece = Tetromino(random.randint(1, 7))
        self.current_piece = self.next_piece
        self.next_piece = Tetromino(random.randint(1, 7))
        self.current_piece.x = COLS // 2 - len(self.current_piece.shape[0]) // 2
        self.current_piece.y = 0
        if self.collision(self.current_piece):
            self.game_over = True

    def collision(self, piece, offset_x=0, offset_y=0):
        """检测碰撞"""
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + offset_x
                    new_y = piece.y + y + offset_y
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                        return True
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return True
        return False

    def lock_piece(self):
        """锁定当前方块到网格"""
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    grid_y = self.current_piece.y + y
                    grid_x = self.current_piece.x + x
                    if 0 <= grid_y < ROWS and 0 <= grid_x < COLS:
                        self.grid[grid_y][grid_x] = self.current_piece.type
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        """消除满行"""
        lines_to_clear = []
        for y in range(ROWS):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [0] * COLS)
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += len(lines_to_clear) * 100 * self.level
            self.level = self.lines_cleared // 10 + 1

    def move(self, dx, dy):
        """移动方块"""
        if self.game_over:
            return
        if not self.collision(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            if dy > 0:
                self.score += 2

    def rotate_piece(self):
        """旋转方块"""
        if self.game_over:
            return
        old_shape = self.current_piece.shape
        self.current_piece.rotate()
        if self.collision(self.current_piece):
            self.current_piece.shape = old_shape

    def hard_drop(self):
        """硬降落"""
        if self.game_over:
            return
        while not self.collision(self.current_piece, 0, 1):
            self.current_piece.y += 1
            self.score += 5
        self.lock_piece()

    def draw_cell(self, x, y, color, offset_x=0, offset_y=0):
        """绘制单个格子"""
        rect = pygame.Rect(
            offset_x + x * CELL_SIZE,
            offset_y + y * CELL_SIZE,
            CELL_SIZE - 1,
            CELL_SIZE - 1
        )
        pygame.draw.rect(self.screen, color, rect)
        # 高光
        pygame.draw.rect(self.screen, WHITE, rect, 1)

    def draw_grid(self):
        """绘制网格和已固定的方块"""
        for y in range(ROWS):
            for x in range(COLS):
                if self.grid[y][x]:
                    self.draw_cell(x, y, COLORS[self.grid[y][x]])

    def draw_piece(self, piece, offset_x=0, offset_y=0):
        """绘制当前方块"""
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_cell(
                        piece.x + x, piece.y + y,
                        piece.color, offset_x, offset_y
                    )

    def draw_next_piece(self):
        """绘制下一个方块预览"""
        font = pygame.font.Font(None, 36)
        text = font.render("下一个:", True, WHITE)
        self.screen.blit(text, (COLS * CELL_SIZE + 20, 30))
        for y, row in enumerate(self.next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.draw_cell(
                        x + 2, y + 2,
                        self.next_piece.color,
                        COLS * CELL_SIZE + 20, 60
                    )

    def draw_info(self):
        """绘制分数等信息"""
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"分数: {self.score}", True, WHITE)
        level_text = font.render(f"等级: {self.level}", True, WHITE)
        lines_text = font.render(f"消除: {self.lines_cleared} 行", True, WHITE)
        self.screen.blit(score_text, (COLS * CELL_SIZE + 20, 180))
        self.screen.blit(level_text, (COLS * CELL_SIZE + 20, 220))
        self.screen.blit(lines_text, (COLS * CELL_SIZE + 20, 260))
        # 操作说明
        help_font = pygame.font.Font(None, 24)
        helps = ["← → 移动", "↑ 旋转", "↓ 加速", "空格 硬落"]
        for i, h in enumerate(helps):
            self.screen.blit(help_font.render(h, True, GRAY),
                           (COLS * CELL_SIZE + 20, 320 + i * 25))

    def draw_game_over(self):
        """绘制游戏结束"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.Font(None, 48)
        text = font.render("游戏结束!", True, WHITE)
        score_text = font.render(f"最终分数: {self.score}", True, WHITE)
        restart_text = font.render("按 R 重新开始", True, GRAY)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(text, rect)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        """主循环"""
        while True:
            # 下落逻辑
            fall_interval = max(100, FALL_SPEED - (self.level - 1) * 50)
            now = pygame.time.get_ticks()
            if not self.game_over and now - self.last_fall > fall_interval:
                if not self.collision(self.current_piece, 0, 1):
                    self.current_piece.y += 1
                    self.last_fall = now
                else:
                    self.lock_piece()
                    self.last_fall = now

            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.__init__()
                        continue
                    if self.game_over:
                        continue
                    if event.key == pygame.K_LEFT:
                        self.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.move(0, 1)
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()

            # 绘制
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_piece(self.current_piece)
            self.draw_next_piece()
            self.draw_info()
            if self.game_over:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = TetrisGame()
    game.run()
