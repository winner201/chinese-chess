"""
中国象棋 - 玩家 vs 电脑 (Python源码)
"""
import pygame, sys, random

pygame.init()
BOARD_SIZE = 10
GRID_SIZE = 60
MARGIN = 50
WIDTH = BOARD_SIZE * GRID_SIZE + MARGIN * 2
HEIGHT = (BOARD_SIZE + 1) * GRID_SIZE + MARGIN * 2
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("中国象棋 - 玩家执红先手")
FONT = pygame.font.SysFont("simsun", 28)
SMALL_FONT = pygame.font.SysFont("simsun", 20)
PIECE_R = GRID_SIZE // 2 - 4
BG = pygame.Color(240, 210, 160)
LINE = pygame.Color(0, 0, 0)
RED = pygame.Color(200, 30, 30)
BLACK = pygame.Color(20, 20, 20)
HIGHLIGHT = pygame.Color(255, 255, 0, 80)
SELECTED = pygame.Color(0, 180, 0, 100)

def pos(x, y):
    return (MARGIN + x * GRID_SIZE, MARGIN + y * GRID_SIZE)

def grid(cx, cy):
    gx = round((cx - MARGIN) / GRID_SIZE)
    gy = round((cy - MARGIN) / GRID_SIZE)
    gx = max(0, min(8, gx))
    gy = max(0, min(9, gy))
    return gx, gy

PIECE_NAMES = {
    0: "帅", 1: "仕", 2: "相", 3: "车", 4: "马", 5: "炮", 6: "兵",
    7: "将", 8: "士", 9: "象", 10: "车", 11: "马", 12: "炮", 13: "卒"
}
IS_RED = {0,1,2,3,4,5,6}
IS_BLACK = {7,8,9,10,11,12,13}

INIT_BOARD = [
    [3, 4, 2, 1, 0, 1, 2, 4, 3],
    [None, None, None, None, None, None, None, None, None],
    [None, 5, None, None, None, None, None, 5, None],
    [6, None, 6, None, 6, None, 6, None, 6],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [13, None, 13, None, 13, None, 13, None, 13],
    [None, 12, None, None, None, None, None, 12, None],
    [None, None, None, None, None, None, None, None, None],
    [10, 11, 9, 8, 7, 8, 9, 11, 10],
]

class Board:
    def __init__(self):
        self.grid = [row[:] for row in INIT_BOARD]
        self.selected = None
        self.valid_moves = []
        self.last_move = None

    def piece_at(self, x, y):
        if 0 <= x < 9 and 0 <= y < 10:
            return self.grid[y][x]
        return None

    def is_enemy(self, x, y, is_red_turn):
        p = self.piece_at(x, y)
        if p is None: return False
        return (p in IS_RED) != is_red_turn

    def in_palace(self, x, y, is_red):
        if is_red:
            return 3 <= x <= 5 and 0 <= y <= 2
        else:
            return 3 <= x <= 5 and 7 <= y <= 9

    def is_friendly(self, x, y, is_red):
        p = self.piece_at(x, y)
        if p is None: return False
        return (p in IS_RED) == is_red

    def get_valid_moves(self, x, y):
        piece = self.piece_at(x, y)
        if piece is None: return []
        is_red = piece in IS_RED
        moves = []

        if piece == 0:  # 帅
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x+dx, y+dy
                if self.in_palace(nx, ny, True) and not self.is_friendly(nx, ny, True):
                    moves.append((nx, ny))
            for dy in range(1, 10):
                nx, ny = x, y - dy
                if 0 <= ny < 10:
                    p = self.piece_at(nx, ny)
                    if p == 7:
                        moves.append((nx, ny))
                        break
                    elif p is not None:
                        break

        elif piece == 7:  # 将
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x+dx, y+dy
                if self.in_palace(nx, ny, False) and not self.is_friendly(nx, ny, False):
                    moves.append((nx, ny))
            for dy in range(1, 10):
                nx, ny = x, y + dy
                if 0 <= ny < 10:
                    p = self.piece_at(nx, ny)
                    if p == 0:
                        moves.append((nx, ny))
                        break
                    elif p is not None:
                        break

        elif piece in (1, 8):  # 仕/士
            for dx, dy in [(1,1),(1,-1),(-1,1),(-1,-1)]:
                nx, ny = x+dx, y+dy
                if self.in_palace(nx, ny, is_red) and not self.is_friendly(nx, ny, is_red):
                    moves.append((nx, ny))

        elif piece in (2, 9):  # 相/象
            for dx, dy in [(2,2),(2,-2),(-2,2),(-2,-2)]:
                nx, ny = x+dx, y+dy
                mx, my = x+dx//2, y+dy//2
                if 0 <= nx < 9 and 0 <= ny < 10:
                    if self.piece_at(mx, my) is None and not self.is_friendly(nx, ny, is_red):
                        if is_red and ny > 4: continue
                        if not is_red and ny < 5: continue
                        moves.append((nx, ny))

        elif piece in (3, 10):  # 车
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                for i in range(1, 10):
                    nx, ny = x+dx*i, y+dy*i
                    if 0 <= nx < 9 and 0 <= ny < 10:
                        if self.is_friendly(nx, ny, is_red): break
                        moves.append((nx, ny))
                        if self.piece_at(nx, ny) is not None: break

        elif piece in (4, 11):  # 马
            for dx, dy in [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]:
                nx, ny = x+dx, y+dy
                mx, my = x+dx//2, y+dy//2
                if 0 <= nx < 9 and 0 <= ny < 10:
                    if self.piece_at(mx, my) is None and not self.is_friendly(nx, ny, is_red):
                        moves.append((nx, ny))

        elif piece in (5, 12):  # 炮
            for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                jumped = False
                for i in range(1, 10):
                    nx, ny = x+dx*i, y+dy*i
                    if 0 <= nx < 9 and 0 <= ny < 10:
                        if not jumped:
                            if self.is_friendly(nx, ny, is_red): break
                            if self.piece_at(nx, ny) is not None: jumped = True
                            else: moves.append((nx, ny))
                        else:
                            if self.is_friendly(nx, ny, is_red): break
                            moves.append((nx, ny))
                            if self.piece_at(nx, ny) is not None: break

        elif piece in (6, 13):  # 兵/卒
            if is_red:
                if y <= 4:
                    for dx in [-1, 0, 1]:
                        nx, ny = x+dx, y+1
                        if 0 <= nx < 9 and 0 <= ny < 10 and not self.is_friendly(nx, ny, True):
                            moves.append((nx, ny))
                else:
                    for dx, dy in [(-1, 1), (1, 1)]:
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < 9 and not self.is_friendly(nx, ny, True):
                            moves.append((nx, ny))
                    nx, ny = x, y+1
                    if not self.is_friendly(nx, ny, True):
                        moves.append((nx, ny))
            else:
                if y >= 5:
                    for dx in [-1, 0, 1]:
                        nx, ny = x+dx, y-1
                        if 0 <= nx < 9 and 0 <= ny < 10 and not self.is_friendly(nx, ny, False):
                            moves.append((nx, ny))
                else:
                    for dx, dy in [(-1, -1), (1, -1)]:
                        nx, ny = x+dx, y-1
                        if 0 <= nx < 9 and not self.is_friendly(nx, ny, False):
                            moves.append((nx, ny))
                    nx, ny = x, y-1
                    if not self.is_friendly(nx, ny, False):
                        moves.append((nx, ny))

        return moves

    def move(self, fx, fy, tx, ty):
        captured = self.grid[ty][tx]
        self.grid[ty][tx] = self.grid[fy][fx]
        self.grid[fy][fx] = None
        self.last_move = ((fx, fy), (tx, ty))
        return captured

    def get_all_pieces(self, is_red):
        pieces = []
        for y in range(10):
            for x in range(9):
                p = self.grid[y][x]
                if p is not None and (p in IS_RED) == is_red:
                    pieces.append((x, y))
        return pieces

    def computer_move_simple(self):
        """简单AI"""
        is_red = False
        pieces = self.get_all_pieces(is_red)
        all_moves = []
        values = {0:10000,7:10000,1:100,8:100,2:100,9:100,3:500,10:500,4:300,11:300,5:300,12:300,6:50,13:50}

        for (x, y) in pieces:
            piece = self.piece_at(x, y)
            raw = self.get_valid_moves(x, y)
            for (tx, ty) in raw:
                captured = self.piece_at(tx, ty)
                score = values.get(captured, 0) + random.randint(0, 15)
                if captured in (0, 7):
                    return (x, y, tx, ty)
                all_moves.append((score, x, y, tx, ty))

        all_moves.sort(reverse=True)
        if all_moves:
            _, x, y, tx, ty = all_moves[0]
            return (x, y, tx, ty)
        return None


def draw_board():
    WIN.fill(BG)
    for x in range(9):
        for y in range(10):
            cx, cy = pos(x, y)
            if y < 10:
                pygame.draw.line(WIN, LINE, pos(x, 0 if y == 0 else y), pos(x, 9 if y == 9 else y), 2)
            if x < 8:
                if y not in (0, 9):
                    pygame.draw.line(WIN, LINE, pos(x, y), pos(x if x < 8 else 8, y), 2)
                else:
                    pygame.draw.line(WIN, LINE, pos(x, 0), pos(x, 9), 2)
            if x == 0 or x == 8:
                pygame.draw.line(WIN, LINE, pos(x, 0), pos(x, 9), 2)
    pygame.draw.line(WIN, LINE, pos(3,0), pos(5,2), 2)
    pygame.draw.line(WIN, LINE, pos(5,0), pos(3,2), 2)
    pygame.draw.line(WIN, LINE, pos(3,7), pos(5,9), 2)
    pygame.draw.line(WIN, LINE, pos(5,7), pos(3,9), 2)
    pygame.draw.line(WIN, LINE, pos(0, 4), pos(8, 4), 2)
    pygame.draw.line(WIN, LINE, pos(0, 5), pos(8, 5), 2)
    rh = FONT.render("楚 河", True, BLACK)
    wh = FONT.render("汉 界", True, BLACK)
    WIN.blit(rh, (pos(2, 4)[0] - rh.get_width()//2, pos(4, 4)[1] - rh.get_height()//2))
    WIN.blit(wh, (pos(5, 5)[0] - wh.get_width()//2, pos(5, 5)[1] - wh.get_height()//2))
    for (px, py) in [(1,2),(7,2),(1,7),(7,7)]:
        cx, cy = pos(px, py)
        for b1, b2 in [(-5,-5),(5,-5),(-5,5),(5,5)]:
            bx, by = cx+b1, cy+b2
            if 0 <= bx - MARGIN <= 8*GRID_SIZE and 0 <= by - MARGIN <= 9*GRID_SIZE:
                pygame.draw.circle(WIN, BLACK, (bx, by), 2)
    for (px, py) in [(0,3),(2,3),(4,3),(6,3),(8,3),(0,6),(2,6),(4,6),(6,6),(8,6)]:
        cx, cy = pos(px, py)
        for b1, b2 in [(-5,-5),(5,-5)] if px != 0 else [(-5,-5),(5,-5)]:
            bx, by = cx+b1, cy+b2
            pygame.draw.circle(WIN, BLACK, (bx, by), 2)


def draw_piece(x, y, piece, selected=False):
    cx, cy = pos(x, y)
    color = RED if piece in IS_RED else BLACK
    if selected:
        pygame.draw.circle(WIN, SELECTED, (cx, cy), PIECE_R + 6)
    pygame.draw.circle(WIN, color, (cx, cy), PIECE_R)
    pygame.draw.circle(WIN, BG, (cx, cy), PIECE_R - 2)
    pygame.draw.circle(WIN, color, (cx, cy), PIECE_R - 2, 2)
    name = PIECE_NAMES[piece]
    txt = FONT.render(name, True, color)
    WIN.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))


def draw_last_move():
    if board.last_move:
        (fx,fy),(tx,ty) = board.last_move
        for px, py in [(fx,fy),(tx,ty)]:
            pygame.draw.circle(WIN, (200,200,0,100), pos(px,py), PIECE_R+6, 3)


def draw_valid_moves(moves):
    for (mx, my) in moves:
        cx, cy = pos(mx, my)
        if board.piece_at(mx, my) is None:
            pygame.draw.circle(WIN, (0,150,0), (cx, cy), 6)
            pygame.draw.circle(WIN, BG, (cx, cy), 3)
        else:
            pygame.draw.circle(WIN, (200,0,0), (cx, cy), PIECE_R + 4, 3)


board = Board()
player_red = True
game_over = False
result_msg = ""
running = True

while running:
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mx, my = e.pos
            gx, gy = grid(mx, my)
            if player_red:
                if board.selected is None:
                    p = board.piece_at(gx, gy)
                    if p is not None and p in IS_RED:
                        board.selected = (gx, gy)
                        board.valid_moves = board.get_valid_moves(gx, gy)
                else:
                    fx, fy = board.selected
                    if (gx, gy) in board.valid_moves:
                        board.move(fx, fy, gx, gy)
                        board.selected = None
                        board.valid_moves = []
                        player_red = False
                    elif board.piece_at(gx, gy) in IS_RED:
                        board.selected = (gx, gy)
                        board.valid_moves = board.get_valid_moves(gx, gy)
                    else:
                        board.selected = None
                        board.valid_moves = []
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_r:
                board = Board()
                player_red = True
                game_over = False
                result_msg = ""

    if not player_red and not game_over:
        pygame.time.delay(400)
        move = board.computer_move_simple()
        if move:
            fx, fy, tx, ty = move
            board.move(fx, fy, tx, ty)
            player_red = True
            if board.piece_at(tx, ty) in (0, 7):
                game_over = True
                result_msg = "你赢了！" if board.piece_at(tx, ty) == 7 else "电脑赢了！"

    draw_board()
    draw_last_move()
    for y in range(10):
        for x in range(9):
            p = board.piece_at(x, y)
            if p is not None:
                sel = board.selected == (x, y)
                draw_piece(x, y, p, selected=sel)
    if board.selected and board.valid_moves:
        draw_valid_moves(board.valid_moves)

    if not game_over:
        turn_txt = "你的回合（红方）" if player_red else "电脑思考中（黑方）..."
        tip = SMALL_FONT.render(turn_txt, True, (50,50,50))
        WIN.blit(tip, (10, 10))
        hint = SMALL_FONT.render("R键 重新开始", True, (120,120,120))
        WIN.blit(hint, (WIDTH - hint.get_width() - 10, 10))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,150))
        WIN.blit(overlay, (0,0))
        msg = FONT.render(result_msg, True, (255,200,0))
        WIN.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - msg.get_height()//2 - 30))
        sub = SMALL_FONT.render("按 R 重新开始", True, (200,200,200))
        WIN.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))

    pygame.display.flip()

pygame.quit()
