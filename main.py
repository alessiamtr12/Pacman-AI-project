import heapq
import random
import sys

import pygame
import math
from board import boards
from button import Button
pygame.init()

try:
    pygame.mixer.music.load('assets/music/horia.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(loops=-1)
except pygame.error as e:
    print(f"Cannot load music fil {e}")

WIDTH = 700
WINDOW_WIDTH = 900
HEIGHT = 750
PLAYER_W, PLAYER_H = 50, 50
HALF_W = PLAYER_W // 2
HALF_H = PLAYER_H // 2
screen = pygame.display.set_mode([WINDOW_WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
font_bigger = pygame.font.Font('freesansbold.ttf', 70)
font_medium = pygame.font.Font('freesansbold.ttf', 40)
level = boards
PI = math.pi
counter = 0
direction = 0
direction_command = 0
clyde_direction = 0
clyde_direction_command = 0
turns_allowed = [False, False, False, False]
player_speed = 2
show_paths = False
manual_mode = True
MODE_CLASSIC = 0
MODE_GHOST = 1
mode = MODE_CLASSIC

player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (50, 50)))

blinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (42, 42))
pinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (42, 42))
inky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (42, 42))
clyde_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (42, 42))
spooked_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (35, 35))
dead_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/dead.png'), (35, 35))

snowflake_image = pygame.transform.scale(pygame.image.load(f'assets/img1.png'), (20, 20))
snowflakeBIG_image = pygame.transform.scale(pygame.image.load(f'assets/snowflake.png'), (30, 30))
chimney_image = pygame.transform.scale(pygame.image.load(f'assets/chimney.png'), (42, 42))

chimney_timer = 0
CHIMNEY_TIMER_LIMIT = 5 * fps
chimney_locations = [(18, 12), (2, 3), (5, 27), (29, 2)]
chimney_respawn_timer = 0
CHIMNEY_TIMER_SPAWN_LIMIT = 10 * fps
current_chimney_index = 0
chimney_appear = False


fruit_image = pygame.transform.scale(pygame.image.load(f'assets/fruit.png'), (42, 42))
fruit_pos = (18, 15)
dots_eaten = 0
fruit_timer = 0
fruit_appear = False
FRUIT_TIMER_LIMIT = 10 * fps

player_x = 100
player_y = 120

blinky_x = 320
blinky_y = 290
blinky_direction = 2

pinky_x = 337
pinky_y = 263
pinky_direction = 2

inky_x = 313
inky_y = 311
inky_direction = 2

clyde_x = 337
clyde_y = 311
clyde_direction = 2

LIVES = 3
GHOST_START_POS = {
    'blinky': (320, 290, 2),
    'pinky': (337, 263, 2),
    'inky': (313, 311, 2),
    'clyde': (337, 311, 2)
}
PLAYER_START_POS = (100, 120, 0)
GHOST_BOX = (14, 14)
GHOST_EXIT_TARGET = (14, 10)

ICE_BLUE = (173, 216, 230)

valid_turns=  [False, False, False, False] #r, l, u, d
eaten_ghost = [False, False, False, False]
blinky_dead = False
pinky_dead = False
inky_dead = False
clyde_dead = False

blinky_frightened = False
pinky_frightened = False
inky_frightened = False
clyde_frightened = False

blinky_box = False
pinky_box = False
inky_box = False
clyde_box = False

ghost_speed = 2
score = 0
powerup = False
powerup_count = 0

OPPOSITE = {0: 1, 1: 0, 2: 3, 3: 2}
game_mode = "scatter"
SCATTER_TIME = 7 * fps
CHASE_TIME = 10 *fps

BLINKY_SCATTER_TARGET = (2, 27)  # Top-right
PINKY_SCATTER_TARGET = (2, 2)    # Top-left
INKY_SCATTER_TARGET = (30, 27)   # Bottom-right
CLYDE_SCATTER_TARGET = (30, 2)   # Bottom-left

BLINKY_LOOP = [(2, 27), (2, 22), (6, 22), (6, 27)]
PINKY_LOOP = [(2, 2), (6, 2), (6, 6), (2, 6)]
INKY_LOOP = [(30, 27), (30, 16), (27, 16), (24, 19), (24, 22), (27, 22), (27, 27)]
CLYDE_LOOP = [(30, 2), (30, 13), (27, 13), (24, 10), (24, 7), (27, 7), (27, 2)]

blinky_scatter_index = 0
pinky_scatter_index = 0
inky_scatter_index = 0
clyde_scatter_index = 0
clyde_direction_command = clyde_direction

from collections import deque

def tile_sizes():
    #ret tile height,width
    num1 = ((HEIGHT - 50) // 32)
    num2 = (WIDTH // 30)
    return num1, num2

def rc_to_center(r, c):
    #ret center px for a tile
    th, tw = tile_sizes()  # th = tile height, tw = tile width
    x = c * tw + tw // 2
    y = r * th + th // 2
    return x, y

def to_tile(cx, cy):
    #from pixel to tile coordinate row,col
    num1, num2 = tile_sizes()
    return cy // num1, cx // num2

def tile_center_from_center(centerx, centery):
    #ret center of current tile (px)
    num1, num2 = tile_sizes()
    col = centerx // num2
    row = centery // num1
    cx = col * num2 + num2//2
    cy = row * num1 + num1//2
    return cx, cy

def passable(r, c, in_box=False, dead=False, alt_mode = False):
    #check next tile for both pacman and ghost
    if r < 0 or r >= len(level) or c < 0 or c >= len(level[0]):
        return False
    t = level[r][c]
    if t < 3: return True
    if t == 9 and (in_box or dead or alt_mode): return True
    return False

def get_pinky_target(player_rc, direction):
    r, c = player_rc
    # 4 tiles ahead of pacman
    if direction == 0:  # r
        tr, tc = r, c + 4
    elif direction == 1:  # l
        tr, tc = r, c - 4
    elif direction == 2:  # u
        tr, tc = r - 4, c - 4
    elif direction == 3:  # d
        tr, tc = r + 4, c
    else:
        return player_rc

    while not passable(tr, tc) and (tr, tc) != (r, c):
        if tr > r:
            tr -= 1
        elif tr < r:
            tr += 1
        if tc > c:
            tc -= 1
        elif tc < c:
            tc += 1

    return (tr, tc)

def get_inky_target(player_rc, direction, blinky_rc):
    pr, pc = player_rc
    br, bc = blinky_rc

    if direction == 0:  # r
        tr, tc = pr, pc + 2
    elif direction == 1:  # l
        tr, tc = pr, pc - 2
    elif direction == 2:  # u
        tr, tc = pr - 2, pc - 2
    elif direction == 3:  # d
        tr, tc = pr + 2, pc
    else:
        return player_rc

    #inkys target is at the same dist from pacman as blinky but in opposite dir
    new_tr = tr + (tr - br)
    new_tc = tc + (tc - bc)

    while not passable(new_tr,new_tc) and (new_tr,new_tc) != (pr,pc):
        if new_tr < pr:
            new_tr += 1
        elif new_tr > pr:
            new_tr -= 1
        if new_tc < pc:
            new_tc += 1
        elif new_tc > pc:
            new_tc -= 1

    return new_tr, new_tc

def bfs_next_tile(start_rc, goal_rc, forbid_dir=None, in_box=False, dead=False):
    #returns only next tile of the best path
    if start_rc == goal_rc:
        return None, None

    sr, sc = start_rc
    gr, gc = goal_rc

    # r l u d
    dirs = [(0, (0, 1)), (1, (0, -1)), (2, (-1, 0)), (3, (1, 0))]
    if forbid_dir is not None:
        opposite = {0:1, 1:0, 2:3, 3:2}[forbid_dir]
        dirs = [d for d in dirs if d[0] != opposite] + [d for d in dirs if d[0] == opposite]

    q = deque([(sr, sc)])
    prev = {(sr, sc): None}

    while q:
        r, c = q.popleft()
        for index, (dr, dc) in dirs:
            nr,nc = check_tunnel(r+dr, c+dc)
            if (nr, nc) in prev:
                continue
            if not passable(nr, nc, in_box=in_box, dead=dead):
                continue
            prev[(nr, nc)] = (r, c)
            if (nr, nc) == (gr, gc):
                step = (nr, nc)
                path = []
                while prev[step] != (sr, sc):
                    path.append(step)
                    step = prev[step]
                path.append((sr, sc))
                return step,path
            q.append((nr, nc))
    return None, None

def dfs_next_tile(start_rc, goal_rc, forbid_dir=None, in_box=False, dead=False):
    if start_rc == goal_rc:
        return None, None

    sr, sc = start_rc
    gr, gc = goal_rc

    # direction list: (dir_code, (dr, dc))
    dirs = [(0, (0, 1)), (1, (0, -1)), (2, (-1, 0)), (3, (1, 0))]
    if forbid_dir is not None:
        opposite = {0: 1, 1: 0, 2: 3, 3: 2}[forbid_dir]
        dirs = [d for d in dirs if d[0] != opposite] + [d for d in dirs if d[0] == opposite]

    stack = [(sr, sc)]
    prev = {(sr, sc): None}
    found = False

    while stack:
        r, c = stack.pop()
        if (r, c) == (gr, gc):
            found = True
            break
        for index, (dr, dc) in dirs:
            nr, nc = check_tunnel(r + dr, c + dc)
            if (nr, nc) not in prev and passable(nr, nc, in_box=in_box, dead=dead):
                prev[(nr, nc)] = (r, c)
                stack.append((nr, nc))

    if not found:
        return None, None

    step = (gr, gc)
    path = []
    while prev[step] != (sr, sc):
        path.append(step)
        step = prev[step]
    path.append((sr, sc))
    path.reverse()

    #make sure next tile is adjacent
    if len(path) >= 2:
        next_rc = path[1]
    else:
        next_rc = None

    return next_rc, path


def frightened_next_tile(start_rc, goal_rc, forbid_dir=None, in_box=False, dead=False):
    # strategy to run away from pacman (goal)
    sr, sc = start_rc

    # r l u d
    dirs = [(0, (0, 1)), (1, (0, -1)), (2, (-1, 0)), (3, (1, 0))]
    best_dist = -1
    best_next_rc = None

    for index, (dr, dc) in dirs:
        if forbid_dir is not None and index == OPPOSITE[forbid_dir]:
            continue
        nr, nc = check_tunnel(sr+dr , sc+dc)
        if passable(nr, nc, in_box=in_box, dead=dead):
            dist = h_manhattan_distance((nr, nc), goal_rc)
            #go as far as it can
            if dist > best_dist:
                best_dist = dist
                best_next_rc = (nr, nc)

    #no move was found, turn around
    if best_next_rc is None and forbid_dir is not None:
        opposite = {0: 1, 1: 0, 2: 3, 3: 2}[forbid_dir]
        dr, dc = dirs[opposite][1]
        nr, nc = sr + dr, sc + dc
        if passable(nr, nc, in_box=in_box, dead=dead):
            best_next_rc = (nr, nc)

    return best_next_rc, []

def h_manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def a_star_next_tile(start_rc, goal_rc, forbid_dir=None, in_box=False, dead=False):

    if start_rc == goal_rc:
        return None, None

    g_score = {start_rc: 0}
    h_score = h_manhattan_distance(start_rc, goal_rc)
    f_score = {start_rc: h_score}

    open_heap = [(h_score, start_rc)]
    prev = {start_rc: None}

    # r l u d
    dirs = [(0, (0, 1)), (1, (0, -1)), (2, (-1, 0)), (3, (1, 0))]

    while open_heap:

        current_f, current_rc = heapq.heappop(open_heap)

        if current_rc == goal_rc:
            break

        current_dirs = list(dirs)
        if forbid_dir is not None:
            opposite = {0: 1, 1: 0, 2: 3, 3: 2}[forbid_dir]
            current_dirs = [d for d in dirs if d[0] != opposite]  + [d for d in dirs if d[0] == opposite]

        for index, (dr, dc) in current_dirs:
            neighbor_rc = (current_rc[0] + dr, current_rc[1] + dc)
            nr, nc = neighbor_rc

            if not passable(nr, nc, in_box=in_box, dead=dead):
                continue

            tentative_g = g_score[current_rc] + 1

            if neighbor_rc not in g_score or tentative_g < g_score[neighbor_rc]:
                g_score[neighbor_rc] = tentative_g
                h_score = h_manhattan_distance(neighbor_rc, goal_rc)
                f_score[neighbor_rc] = tentative_g + h_score
                heapq.heappush(open_heap, (f_score[neighbor_rc], neighbor_rc))
                prev[neighbor_rc] = current_rc

    if goal_rc not in prev:
        return None, None

    step = goal_rc
    path = []
    while step != start_rc:
        path.append(step)
        step = prev[step]
    path.append(start_rc)
    path.reverse()

    next_rc = None
    if len(path) >= 2:
        next_rc = path[1]

    return next_rc, path

def dir_from_step(next_rc, cur_rc):
    #based on the next tile, it determines the direction
    if not next_rc: return None
    (nr, nc), (r, c) = next_rc, cur_rc
    if nr == r and (nc - c) % len(level[0]) == 1: return 0  # right
    if nr == r and (c - nc) % len(level[0]) == 1: return 1  # left
    if nc == c and nr == r - 1: return 2  # up
    if nc == c and nr == r + 1: return 3  # down
    return None

def draw_path(path, color):
    num1 = ((HEIGHT - 50) // 32)
    num2 = (WIDTH // 30)
    if not path:
        return
    for tile in path:
        row, col = tile
        x = col * num2
        y = row * num1
        path_rect = pygame.Surface((num2, num1), pygame.SRCALPHA)
        path_rect.fill(color)
        screen.blit(path_rect,(x,y))

class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, dir, dead, frightened, box, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + HALF_W
        self.center_y = self.y_pos + HALF_H
        self.target = target
        self.speed = speed
        self.img = img
        self.in_box = box
        self.dir = dir
        self.dead = dead
        self.frightened = frightened
        self.id = id
        self.turns , self.in_box = self.check_col()
        self.rect = self.draw()

    def draw(self):
        if (not powerup and not self.dead) or (eaten_ghost[self.id] and powerup and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_ghost[self.id]:
            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect

    def check_col(self):
        r, c = to_tile(self.center_x, self.center_y)
        self.in_box = 13 <= r <= 15 and 12 <= c <= 16

        self.turns = [False, False, False, False]

        rr, rc = check_tunnel(r, c + 1)
        if passable(rr, rc, in_box=self.in_box, dead=self.dead):
            self.turns[0] = True

        rr, rc = check_tunnel(r, c - 1)
        if passable(rr, rc, in_box=self.in_box, dead=self.dead):
            self.turns[1] = True

        if passable(r - 1, c, in_box=self.in_box, dead=self.dead):
            self.turns[2] = True

        if passable(r + 1, c, in_box=self.in_box, dead=self.dead):
            self.turns[3] = True

        return self.turns, self.in_box

    def move(self, target_rc, strategy : callable):
        self.turns, self.in_box = self.check_col()

        g_rc = to_tile(self.center_x, self.center_y)

        # gets next tile from bfs and compute dir
        next_rc, path = strategy(
            start_rc=g_rc,
            goal_rc=target_rc,
            forbid_dir=self.dir,
            in_box=self.in_box,
            dead=self.dead
        )
        new_dir = dir_from_step(next_rc, g_rc)

        if new_dir is not None and self.turns[new_dir]:
            self.dir = new_dir

        # advance according to current dir
        if self.dir == 0 and self.turns[0]:
            self.x_pos += self.speed
        elif self.dir == 1 and self.turns[1]:
            self.x_pos -= self.speed
        elif self.dir == 2 and self.turns[2]:
            self.y_pos -= self.speed
        elif self.dir == 3 and self.turns[3]:
            self.y_pos += self.speed
        else:
            # if no better move,  pick any open pos
            for d in range(4):
                if self.turns[d]:
                    self.dir = d
                    if d == 0: self.x_pos += self.speed
                    if d == 1: self.x_pos -= self.speed
                    if d == 2: self.y_pos -= self.speed
                    if d == 3: self.y_pos += self.speed
                    break

        # for tunnel
        if self.x_pos > WIDTH - PLAYER_W: self.x_pos = -PLAYER_W
        if self.x_pos < -PLAYER_W: self.x_pos = WIDTH - PLAYER_W

        # update centers
        self.center_x = self.x_pos + HALF_W
        self.center_y = self.y_pos + HALF_H
        self.rect = self.draw()

        return self.x_pos, self.y_pos, self.dir, path


def draw_board():
    num1 = ((HEIGHT - 50) // 32)
    num2 = (WIDTH // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):
            center_x = j * num2 + (0.5 * num2)
            center_y = i * num1 + (0.5 * num1)

            if fruit_appear == True and i == fruit_pos[0] and j == fruit_pos[1]:
                W, H = chimney_image.get_size()
                top_left_x = center_x - (W / 2)
                top_left_y = center_y - (H / 2)
                screen.blit(fruit_image, (top_left_x, top_left_y))

            if chimney_appear == True and i == chimney_locations[current_chimney_index][0] and j == chimney_locations[current_chimney_index][1] and control_scheme == 'normal':
                W, H = chimney_image.get_size()
                top_left_x = center_x - (W / 2)
                top_left_y = center_y - (H / 2)
                screen.blit(chimney_image, (top_left_x, top_left_y))

            if level[i][j] == 1:
                W, H = snowflake_image.get_size()
                top_left_x = center_x - (W / 2)
                top_left_y = center_y - (H / 2)
                screen.blit(snowflake_image, (top_left_x, top_left_y))

            if level[i][j] == 2:
                W, H = snowflakeBIG_image.get_size()
                top_left_x = center_x - (W / 2)
                top_left_y = center_y - (H / 2)
                screen.blit(snowflakeBIG_image, (top_left_x, top_left_y))

            if level[i][j] == 3:
                pygame.draw.line(screen, ICE_BLUE, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 4:
                pygame.draw.line(screen, ICE_BLUE, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)

            if level[i][j] == 5:
                pygame.draw.arc(screen, ICE_BLUE, [(j * num2 - (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1],0, PI / 2, 3)

            if level[i][j] == 6:
                pygame.draw.arc(screen, ICE_BLUE, [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1],PI/2, PI, 3)

            if level[i][j] == 7:
                pygame.draw.arc(screen, ICE_BLUE, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.5 * num1)), num2, num1], PI,3 * PI / 2, 3)

            if level[i][j] == 8:
                pygame.draw.arc(screen, ICE_BLUE,[(j * num2 - (num2 * 0.5)), (i * num1 - (0.5 * num1)), num2, num1], 3 * PI / 2,2 * PI, 3)

            if level[i][j] == 9:
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),(j * num2 + num2, i * num1 + (0.5 * num1)), 3)

def check_col(score1, power, power_count, eaten_ghost):
    num1 = ((HEIGHT - 50) // 32)
    num2 = (WIDTH // 30)
    global blinky_frightened, pinky_frightened, inky_frightened, clyde_frightened
    global dots_eaten
    global fruit_appear

    center_x = player_x + PLAYER_W // 2
    center_y = player_y + PLAYER_H // 2

    if center_x < 0:
        wrapped_center_x = center_x + WIDTH + PLAYER_W
    elif center_x >= WIDTH:
        wrapped_center_x = center_x - WIDTH - PLAYER_W
    else:
        wrapped_center_x = center_x

    r = center_y // num1
    c = wrapped_center_x // num2

    if not (0 <= r < len(level) and 0 <= c < len(level[0])):
        return score1, power, power_count, eaten_ghost

    if 0 < player_x < WIDTH - PLAYER_W:

        if fruit_appear == True and r == fruit_pos[0] and c == fruit_pos[1]:
            score1 += 100
            fruit_appear = False

        if level[r][c] == 1:
            level[r][c] = 0
            score1 += 10
            dots_eaten += 1

        if level[r][c] == 2:
            level[r][c] = 0
            score1 += 50
            power = True
            power_count = 0
            eaten_ghost = [False, False, False, False]
            blinky_frightened = True
            pinky_frightened = True
            inky_frightened = True
            clyde_frightened = True
    return score1, power, power_count, eaten_ghost

def draw_player():
    if direction == 0:
        screen.blit(player_images[counter // 5], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (player_x, player_y))

def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 710))
    lives_text = font.render(f'Lives: {LIVES}', True, 'white')
    screen.blit(lives_text, (10, 730))

def reset_positions():
    global player_x, player_y, direction, direction_command
    global blinky_x, blinky_y, blinky_direction
    global pinky_x, pinky_y, pinky_direction
    global inky_x, inky_y, inky_direction
    global clyde_x, clyde_y, clyde_direction

    player_x, player_y, direction = PLAYER_START_POS
    direction_command = 0

    blinky_x, blinky_y, blinky_direction = GHOST_START_POS['blinky']
    pinky_x, pinky_y, pinky_direction = GHOST_START_POS['pinky']
    inky_x, inky_y, inky_direction = GHOST_START_POS['inky']
    clyde_x, clyde_y, clyde_direction = GHOST_START_POS['clyde']

def check_tunnel(r,c):
    if r == 15 :
        if c<0: c = len(level[0]) -1
        elif c>=len(level[0]): c = 0

    return r,c

def check_position(centerx, centery, alt_mode = False):
    #check possible turns using helper fct
    turns = [False, False, False, False]
    r, c = to_tile(centerx, centery)

    new_r, new_c = check_tunnel(r, c + 1)
    if passable(new_r, new_c, alt_mode=alt_mode): turns[0] = True  # right

    new_r, new_c = check_tunnel(r, c - 1)
    if passable(new_r, new_c, alt_mode=alt_mode): turns[1] = True  # left

    if passable(r - 1, c, alt_mode=alt_mode): turns[2] = True  # up
    if passable(r + 1, c, alt_mode=alt_mode): turns[3] = True  # down
    return turns
def move_player(player_x, player_y, direction, direction_command, turns_allowed, centerx, centery, log= False, alt_mode = True):
    prev_x, prev_y = player_x, player_y 

    
    if direction_command != direction and turns_allowed[direction_command]:
        turning_perp = (direction in (0, 1) and direction_command in (2, 3)) or \
                       (direction in (2, 3) and direction_command in (0, 1))
        if alt_mode:
            if turning_perp:
                cx, cy = tile_center_from_center(centerx, centery)
                if direction_command in (2, 3):
                    player_x = int(round(cx - HALF_W))
                else:
                    player_y = int(round(cy - HALF_W))
        direction = direction_command

    moved = False
    if turns_allowed[direction]:
        if direction == 0: 
            player_x += player_speed
            moved = True
        elif direction == 1: 
            player_x -= player_speed
            moved = True
        elif direction == 2: 
            player_y -= player_speed
            moved = True
        elif direction == 3: 
            player_y += player_speed
            moved = True

    if log:
        if moved:
            moves_str = ["RIGHT", "LEFT", "UP", "DOWN"]
            valid_moves = [moves_str[i] for i, t in enumerate(turns_allowed) if t]
            print(f"Pac-Man moved. Valid turns now: {valid_moves}")
            log_pacman_move(direction)

    return player_x, player_y, direction

def no_food_left():
    return not any(1 in row or 2 in row for row in level)



def log_pacman_move(direction):
    moves = ["RIGHT", "LEFT", "UP", "DOWN"]
    print(f"Pac-Man moves: {moves[direction]}")

def sense_ghost(player_x, player_y, ghosts, radius=200):
    
    nearby = []
    for ghost in ghosts:
        dx = (ghost.center_x) - player_x
        dy = (ghost.center_y) - player_y
        dist = math.sqrt(dx**2 + dy**2)
        if dist <= radius:
            nearby.append((ghost, dist))
    
    return nearby


def reflex_agent(player_rc, nearby, direction):
    score = [0, 0, 0, 0] #rlud
    legal_moves = legal_moves_minmax(player_rc)

    for dir_idx, turn in legal_moves:
        next_r, next_c = turn

        if dir_idx == OPPOSITE[direction]: score[dir_idx] -=500
        if dir_idx == direction: score[dir_idx] += 10

        if level[next_r][next_c] == 0: #pellet
            score[dir_idx] += 1

        if level[next_r][next_c] == 1: #pellet
            score[dir_idx] += 10

        if level[next_r][next_c] == 2: #powerup
            score[dir_idx] += 100

        for ghost, dist in nearby:
            ghost_r, ghost_c = to_tile(ghost.center_x, ghost.center_y)
            dist = abs(next_r - ghost_r) + abs(next_c - ghost_c)

            if dist < 4:
                score[dir_idx] -= 100 /max(1, dist)

    moves_str = ["RIGHT", "LEFT", "UP", "DOWN"]
    valid_moves = [moves_str[i] for i, t in enumerate(legal_moves) if t]
    print(f"Valid turns: {valid_moves}")
    print(f"Scores (R,L,U,D): {score}")
    best = score.index(max(score))
    if best<0 : return 0
    else: return best

def legal_moves_minmax(rc):
    r, c = rc
    moves = []
    dirs = [(0, (0, 1)), (1, (0, -1)), (2, (-1, 0)), (3, (1, 0))]

    for dir_idx, (dr, dc) in dirs:
        nr, nc = check_tunnel(r + dr, c + dc)
        if passable(nr, nc):
            moves.append((dir_idx, (nr, nc)))
    return moves

def is_terminal_minmax(p_rc , g_rcs, depth_left):
    if p_rc in g_rcs: return True
    if depth_left == 0: return True
    if no_food_left(): return True
    return False

def evaluation_minmax(p_rc, g_rcs, food_tiles):
    if p_rc in g_rcs:
        if game_mode == 'frightened': return 1000000
        else: return -1000000

    ghost_dists = [h_manhattan_distance(p_rc, g_rc) for g_rc in g_rcs]
    min_ghost_dist = min(ghost_dists) if ghost_dists else 999

    if food_tiles:
        pellet_dists = [h_manhattan_distance(p_rc, f_rc) for f_rc in food_tiles]
        min_pellet_dist = min(pellet_dists)
    else:
        min_pellet_dist = 0

    SAFE_DIST = 6

    if game_mode=='frightened':
        if min_ghost_dist >= SAFE_DIST:
            ghost_weight = 3.0
            pellet_weight = 2.0
        else:
            ghost_weight = 6.0
            pellet_weight = 1.0

        ghost_term = -ghost_weight * min_ghost_dist
    else:
        if min_ghost_dist >= SAFE_DIST:
            #prefer going after food
            ghost_weight = 1.0
            pellet_weight = 6.0
        else:
            # prefer running from a ghost
            ghost_weight = 6.0
            pellet_weight = 1.0

        ghost_term = ghost_weight * min_ghost_dist

    pellet_term = -pellet_weight * min_pellet_dist #flip the sign so that pacman picks the min dist(best)

    return ghost_term + pellet_term

def minmax(agent, depth_left, p_rc, g_rcs, food_tiles):
    if is_terminal_minmax(p_rc, g_rcs, depth_left):
        return evaluation_minmax(p_rc, g_rcs, food_tiles)

    if agent == 0:
        #pacman
        best = -math.inf
        moves = legal_moves_minmax(p_rc)
        if not moves: return evaluation_minmax(p_rc, g_rcs, food_tiles)

        for _, next_pac_rc in moves:
            val = minmax(1, depth_left, next_pac_rc, g_rcs, food_tiles)
            if val > best:
                best = val
        return best
    else:
        #ghosts
        ghost_idx = agent -1
        best = math.inf
        current_ghost_rc = g_rcs[ghost_idx]
        moves = legal_moves_minmax(current_ghost_rc)
        if not moves:
            return evaluation_minmax(p_rc, g_rcs, food_tiles)
        for _, next_ghost_rc in moves:
            new_ghost_rcs = list(g_rcs)
            new_ghost_rcs[ghost_idx] = next_ghost_rc
            new_ghost_rcs = tuple(new_ghost_rcs)

            next_agent = agent+1
            next_depth = depth_left
            if next_agent == 5:
                next_agent = 0
                next_depth = depth_left -1
            val = minmax(next_agent, next_depth, p_rc, new_ghost_rcs, food_tiles)
            if val < best:
                best = val
        return best

def minmax_helper(p_rc, g_rcs, food_tiles, current_dir):
    best_dir = 0
    best = -math.inf
    root_moves = legal_moves_minmax(p_rc)
    if not root_moves:
        return 0
    for dir_idx, next_p_rc in root_moves:
        val = minmax(1, 1, next_p_rc, g_rcs, food_tiles)

        if next_p_rc in food_tiles: val +=200
        if dir_idx == OPPOSITE[current_dir]: val -= 1000
        elif dir_idx == current_dir: val += 10

        for ghost_rc in g_rcs:
            if powerup and next_p_rc == ghost_rc: val +=1000

        val += 0.01 * dir_idx

        if val > best:
            best = val
            best_dir = dir_idx
    return best_dir

def alpha_beta(agent, depth_left, p_rc, g_rcs, food_tiles, alpha = -math.inf, beta = math.inf):
    if is_terminal_minmax(p_rc, g_rcs, depth_left):
        return evaluation_minmax(p_rc, g_rcs, food_tiles)

    if agent == 0:
        best = -math.inf
        moves = legal_moves_minmax(p_rc)
        if not moves: return evaluation_minmax(p_rc, g_rcs, food_tiles)

        for _, next_p_rc in moves:
            val = alpha_beta(1, depth_left, next_p_rc, g_rcs, food_tiles, alpha, beta)

            if val>best: best=val
            if best>alpha: alpha = best

            if beta <= alpha: break

        return best
    else:
        #ghosts
        ghost_idx = agent -1
        best = math.inf
        current_g_rc = g_rcs[ghost_idx]
        moves = legal_moves_minmax(current_g_rc)

        if not moves: return evaluation_minmax(p_rc, g_rcs, food_tiles)
        for _, next_g_rc in moves:
            new_g_rcs = list(g_rcs)
            new_g_rcs[ghost_idx] = next_g_rc
            new_g_rcs = tuple(new_g_rcs)

            next_agent = agent+1
            next_depth = depth_left
            if next_agent == 5:
                next_agent = 0
                next_depth = depth_left -1

            val = alpha_beta(next_agent, next_depth, p_rc, new_g_rcs, food_tiles, alpha, beta)
            if val < best: best = val
            if best < beta: beta = best

            if beta<=alpha: break
        return best

def alpha_beta_helper(p_rc, g_rcs, food_tiles, current_dir):
    best_dir = 0
    best_val = -math.inf

    root_moves = legal_moves_minmax(p_rc)
    if not root_moves:
        return current_dir

    for dir_idx, next_p_rc in root_moves:
        val = alpha_beta(1, 2, next_p_rc, g_rcs, food_tiles, current_dir)

        if next_p_rc in food_tiles: val += 200
        if dir_idx == OPPOSITE[current_dir]: val -=1000
        elif dir_idx == current_dir: val += 10
        #val += 0.01 * dir_idx

        if val > best_val:
            best_val = val
            best_dir = dir_idx

    return best_dir

def draw_button(screen, rect, text, mouse_pos):
    color = (150, 150, 150)

    if rect.collidepoint(mouse_pos):
        color = (200, 200, 200)

    pygame.draw.rect(screen, color, rect, border_radius=12)

    label = FONT.render(text, True, (0, 0, 0))
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)


def start_menu(screen):
    clock = pygame.time.Clock()
    try:
        bg_raw = pygame.image.load("assets/start.png").convert()
        scale_factor = max(WINDOW_WIDTH / bg_raw.get_width(), HEIGHT / bg_raw.get_height())
        new_size = (
            int(bg_raw.get_width() * scale_factor),
            int(bg_raw.get_height() * scale_factor)
        )
        bg_scaled = pygame.transform.scale(bg_raw, new_size)
        bg_image = center_crop(bg_scaled, WINDOW_WIDTH, HEIGHT)

    except FileNotFoundError:
        print("Background image not found, using default color.")
        bg_image = pygame.Surface((WINDOW_WIDTH, HEIGHT))
        bg_image.fill((20, 20, 20))

    overlay = pygame.Surface((WINDOW_WIDTH, HEIGHT))
    overlay.set_alpha(100)
    overlay.fill((0, 0, 0))

    button_width, button_height = 300, 80
    center_x = (WINDOW_WIDTH // 2) - (button_width // 2)

    classic_rect = pygame.Rect(center_x, 200, button_width, button_height)
    ghost_rect = pygame.Rect(center_x, 350, button_width, button_height)

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if classic_rect.collidepoint(mouse_pos):
                    return MODE_CLASSIC
                if ghost_rect.collidepoint(mouse_pos):
                    return MODE_GHOST

        screen.blit(bg_image, (0, 0))
        screen.blit(overlay, (0, 0))
        title = FONT.render("Select Game Mode", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        screen.blit(title, title_rect)

        draw_button(screen, classic_rect, "Classic Mode", mouse_pos)
        draw_button(screen, ghost_rect, "Alternate Mode", mouse_pos)

        pygame.display.flip()
        clock.tick(60)


def ghost_state(ghost, ghost_dead, game_mode, player_rc, scatter_index, scatter_loop, current_strat):
    if ghost_dead:
        return current_strat, GHOST_BOX, scatter_index

    if ghost.in_box:
        return bfs_next_tile, GHOST_EXIT_TARGET, scatter_index
    if game_mode == "chase":
        return current_strat, player_rc, scatter_index
    if game_mode == "scatter":
        ghost_rc = to_tile(ghost.center_x, ghost.center_y)

        if ghost_rc == scatter_loop[scatter_index]:
            scatter_index = (scatter_index + 1) % len(scatter_loop)
        return current_strat, scatter_loop[scatter_index], scatter_index
    return frightened_next_tile, player_rc, scatter_index

def center_crop(surface, crop_width, crop_height):
    sw, sh = surface.get_size()

    # crop area centered
    x = (sw - crop_width) // 2
    y = (sh - crop_height) // 2

    # ensure valid area
    x = max(x, 0)
    y = max(y, 0)
    crop_width = min(crop_width, sw)
    crop_height = min(crop_height, sh)

    # create subsurface (this is the crop!)
    return surface.subsurface((x, y, crop_width, crop_height)).copy()

current_strategy_func = bfs_next_tile
current_strategy_name = 'BFS'
pacman_strategy_name = 'Manual'


bfs_button = Button(x=720, y=100, width=160, height=50, text='BFS')
dfs_button = Button(x=720, y=170, width=160, height=50, text='DFS')
a_star_button = Button(x=720, y=240, width=160, height=50, text='A*')
reflex_button = Button(x=720, y=310, width=160, height=50, text='Reflex Agent')
minmax_button = Button(x=720, y=380, width=160, height=50, text='Minmax')
alpha_beta_button = Button(x=720, y=420, width=160, height=50, text='Alpha Beta')

mode_timer = 0
running = True
control_scheme = 'normal'
screen = pygame.display.set_mode((900, 800))
FONT = pygame.font.SysFont(None, 48)

title = FONT.render("Select Game Mode", True, (255, 255, 255))
mode = start_menu(screen)
while running:

    if counter < 19:
        counter += 1
    else: counter = 0

    if dots_eaten >= 70:
        fruit_appear = True
        fruit_timer = 0
        dots_eaten = 0
    if fruit_appear == True:
        fruit_timer += 1
        if fruit_timer > FRUIT_TIMER_LIMIT:
            fruit_appear = False
            fruit_timer = 0



    if powerup and powerup_count < 600:
        powerup_count += 1
    elif powerup and powerup_count >= 600:
        powerup_count = 0
        powerup = False
        eaten_ghost = [False, False, False, False]
        blinky_frightened = True
        pinky_frightened = True
        inky_frightened = True
        clyde_frightened = True
    if control_scheme == 'normal':
        chimney_respawn_timer += 1
        if chimney_respawn_timer >= CHIMNEY_TIMER_SPAWN_LIMIT:
            chimney_appear = True
            current_chimney_index = random.randint(0, 3)
            chimney_respawn_timer = 0

    if control_scheme == 'chimney':
        chimney_timer += 1
        if chimney_timer >= CHIMNEY_TIMER_LIMIT:
            chimney_timer = 0
            control_scheme = 'normal'

    if not powerup:
        mode_timer += 1
        if game_mode == 'scatter':
            if mode_timer >= SCATTER_TIME:
                mode_timer = 0
                game_mode = 'chase'
        elif game_mode == 'chase':
            if mode_timer >= CHASE_TIME:
                mode_timer = 0
                game_mode = 'scatter'
                clyde_scatter_index = 0
                blinky_scatter_index = 0
                pinky_scatter_index = 0
                inky_scatter_index = 0
        elif game_mode == 'frightened':
            game_mode = 'chase'
    else:
        game_mode = 'frightened'
        mode_timer = 0

    if mode == MODE_CLASSIC:
        if manual_mode:
            pacman_strategy_name = 'Manual'
        center_x = player_x + HALF_W
        center_y = player_y + HALF_H
        player_rc = to_tile(center_x, center_y)

        if player_rc == chimney_locations[current_chimney_index]:
            if control_scheme == 'normal':
                overlay = pygame.Surface((WINDOW_WIDTH, HEIGHT))
                overlay.set_alpha(180)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                try:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('assets/music/chimney.mp3')
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(loops=-1)
                except pygame.error as e:
                    print(f"Cannot load music file: {e}")

                msg = font_medium.render('You entered the magic chimney', True, 'white')
                msg_rect = msg.get_rect(center=(WINDOW_WIDTH // 2, HEIGHT // 2))
                screen.blit(msg, msg_rect)

                pygame.display.flip()
                pygame.time.delay(1000)
                control_scheme = 'chimney'
                try:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('assets/music/horia.mp3')
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(loops=-1)
                except pygame.error as e:
                    print(f"Cannot load music file: {e}")

        DARK_BLUE = (0, 0, 51)
        screen.fill(DARK_BLUE)
        draw_board()
        bfs_button.draw(screen)
        dfs_button.draw(screen)
        a_star_button.draw(screen)
        reflex_button.draw(screen)
        minmax_button.draw(screen)
        alpha_beta_button.draw(screen)
        active_text_surf = font.render(f'Mode: {current_strategy_name}', True, 'white')
        screen.blit(active_text_surf, (WIDTH + 20, 50))
        active_text_surf1 = font.render(f'Mode: {pacman_strategy_name}', True, 'white')
        screen.blit(active_text_surf1, (WIDTH + 20, 290))
        draw_player()
        draw_misc()


        blinky = Ghost(blinky_x, blinky_y, None, ghost_speed, blinky_img, blinky_direction, blinky_dead, blinky_frightened, blinky_box, 0)
        pinky = Ghost(pinky_x, pinky_y, None, ghost_speed, pinky_img, pinky_direction, pinky_dead, pinky_frightened, pinky_box, 1)
        inky = Ghost(inky_x, inky_y, None, ghost_speed, inky_img, inky_direction, inky_dead, inky_frightened, inky_box,  2)
        clyde = Ghost(clyde_x, clyde_y, None, ghost_speed, clyde_img, clyde_direction, clyde_dead, clyde_frightened, clyde_box, 3)

        ghosts = [blinky, pinky, inky, clyde]

        turns_allowed = check_position(center_x, center_y)

        if manual_mode:
            player_x, player_y, direction = move_player(
            player_x, player_y, direction, direction_command, turns_allowed, center_x, center_y, log= True
            )
        else:
            #here goes autonomous
            match pacman_strategy_name:
                case 'Reflex Agent':
                    nearby = sense_ghost(player_x, player_y, ghosts)
                    pac_rc = to_tile(center_x, center_y)
                    move = reflex_agent(pac_rc, nearby, direction)
                    print( move)
                    player_x, player_y, direction = move_player(player_x, player_y, direction, move, turns_allowed, center_x, center_y, log = True)

                case 'Minmax Agent':
                    pac_rc = to_tile(center_x, center_y)
                    ghost_rcs = [to_tile(g.center_x, g.center_y) for g in ghosts]
                    food_tiles_minmax = [(r, c)
                                for r, row in enumerate(level)
                                for c, val in enumerate(row)
                                if val in (1, 2)]
                    move = minmax_helper(pac_rc, ghost_rcs, food_tiles_minmax,direction)
                    player_x, player_y, direction = move_player(player_x, player_y, direction, move, turns_allowed, center_x, center_y, log = True)

                case 'Alpha_Beta Agent':
                    pac_rc = to_tile(center_x, center_y)
                    ghost_rcs = [to_tile(g.center_x, g.center_y) for g in ghosts]
                    food_tiles_minmax = [(r, c)
                                        for r, row in enumerate(level)
                                        for c, val in enumerate(row)
                                        if val in (1, 2)]
                    move = alpha_beta_helper(pac_rc, ghost_rcs, food_tiles_minmax, direction)
                    player_x, player_y, direction = move_player(player_x, player_y, direction, move, turns_allowed, center_x,
                                                                center_y, log = True)

        center_x = player_x + HALF_W
        center_y = player_y + HALF_H
        player_rc = to_tile(center_x, center_y)

        active_strategy = current_strategy_func

        if blinky_dead:
            active_strategy_blinky = current_strategy_func
            blinky_target = GHOST_BOX
        elif blinky.in_box:
            active_strategy_blinky = bfs_next_tile
            blinky_target = GHOST_EXIT_TARGET
        elif game_mode == 'chase' or (game_mode == 'frightened' and blinky_frightened == False):
            active_strategy_blinky = current_strategy_func
            blinky_target = player_rc
            #blinky_scatter_index = 0
        elif game_mode == 'scatter':
            active_strategy_blinky = current_strategy_func
            if to_tile(blinky.center_x, blinky.center_y) == BLINKY_LOOP[blinky_scatter_index]:
                blinky_scatter_index = (blinky_scatter_index + 1) % len(BLINKY_LOOP)
            blinky_target = BLINKY_LOOP[blinky_scatter_index]
        else:  # frightened
                active_strategy_blinky = frightened_next_tile
                blinky_target = player_rc

        if pinky_dead:
            active_strategy_pinky = current_strategy_func
            pinky_target = GHOST_BOX
        elif pinky.in_box:
            active_strategy_pinky = bfs_next_tile
            pinky_target = GHOST_EXIT_TARGET

        elif game_mode == 'chase' or (game_mode == 'frightened' and pinky_frightened == False):
            active_strategy_pinky = current_strategy_func
            pinky_target = get_pinky_target(player_rc, direction)
            #pinky_scatter_index = 0
        elif game_mode == 'scatter':
            active_strategy_pinky = current_strategy_func
            if to_tile(pinky.center_x, pinky.center_y) == PINKY_LOOP[pinky_scatter_index]:
                pinky_scatter_index = (pinky_scatter_index + 1) % len(PINKY_LOOP)
            pinky_target = PINKY_LOOP[pinky_scatter_index]
        else:  # frightened
            active_strategy_pinky = frightened_next_tile
            pinky_target = player_rc

        if inky_dead:
            active_strategy_inky = current_strategy_func
            inky_target = GHOST_BOX
        elif inky.in_box:
            active_strategy_inky = bfs_next_tile
            inky_target = GHOST_EXIT_TARGET
        elif game_mode == 'chase' or (game_mode == 'frightened' and inky_frightened == False):
            active_strategy_inky = current_strategy_func
            blinky_rc = to_tile(blinky.center_x, blinky.center_y)
            inky_target = get_inky_target(player_rc, direction, blinky_rc)
            #inky_scatter_index = 0
        elif game_mode == 'scatter':
            active_strategy_inky = current_strategy_func
            if to_tile(inky.center_x, inky.center_y) == INKY_LOOP[inky_scatter_index]:
                inky_scatter_index = (inky_scatter_index + 1) % len(INKY_LOOP)
            inky_target = INKY_LOOP[inky_scatter_index]
        else:  # frightened
            active_strategy_inky = frightened_next_tile
            inky_target = player_rc

        if clyde_dead:
            active_strategy_clyde = current_strategy_func
            clyde_target = GHOST_BOX
        elif clyde.in_box:
            active_strategy_clyde = bfs_next_tile
            clyde_target = GHOST_EXIT_TARGET
        elif game_mode == 'chase' or (game_mode == 'frightened' and clyde_frightened == False):
            active_strategy_clyde = current_strategy_func
            clyde_rc = to_tile(clyde.center_x, clyde.center_y)
            distance = h_manhattan_distance(clyde_rc, player_rc)
            if distance >= 8:
                clyde_target = player_rc
            else:
                if clyde_rc == CLYDE_LOOP[clyde_scatter_index]:
                    clyde_scatter_index = (clyde_scatter_index + 1) % len(CLYDE_LOOP)
                clyde_target = CLYDE_LOOP[clyde_scatter_index]
        elif game_mode == 'scatter':
            active_strategy_clyde = current_strategy_func
            if to_tile(clyde.center_x, clyde.center_y) == CLYDE_LOOP[clyde_scatter_index]:
                clyde_scatter_index = (clyde_scatter_index + 1) % len(CLYDE_LOOP)
            clyde_target = CLYDE_LOOP[clyde_scatter_index]
        else:  # frightened
            active_strategy_clyde = frightened_next_tile
            clyde_target = player_rc

        blinky_x, blinky_y, blinky_direction, path_blinky = blinky.move(blinky_target, active_strategy_blinky)
        pinky_x, pinky_y, pinky_direction, path_pinky = pinky.move(pinky_target, active_strategy_pinky)
        inky_x, inky_y, inky_direction, path_inky = inky.move(inky_target, active_strategy_inky)
        clyde_x, clyde_y, clyde_direction, path_clyde = clyde.move(clyde_target, active_strategy_clyde)

        player_rect = pygame.Rect(player_x + 10, player_y + 10, PLAYER_W - 20, PLAYER_H - 20)
        ghosts = [blinky, pinky, inky, clyde]

        for ghost in ghosts:
            if player_rect.colliderect(ghost.rect):
                if not powerup:
                    LIVES -= 1
                    score -= 500
                    if LIVES == 0:

                        img = pygame.image.load("assets/horia-brenciu-suparat.jpg").convert_alpha()

                        scale_factor = max(WINDOW_WIDTH / img.get_width(), HEIGHT / img.get_height())
                        img = pygame.transform.scale(
                            img,
                            (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor))
                        )

                        crop = center_crop(img, WINDOW_WIDTH, HEIGHT)
                        crop.set_alpha(128)
                        screen.blit(crop, (0, 0))

                        msg = font_bigger.render('GAME OVER', True, 'white')
                        msg_rect = msg.get_rect(center=(WINDOW_WIDTH // 2, HEIGHT // 2))
                        screen.blit(msg, msg_rect)

                        pygame.display.flip()
                        pygame.time.delay(3000)
                        running = False
                        break
                    else:
                        reset_positions()
                        pygame.time.delay(1000)


                elif powerup and ghost.frightened == True and not ghost.dead and not eaten_ghost[ghost.id]:
                    score += 200
                    eaten_ghost[ghost.id] = True
                    ghost.frightened = False
                    ghost.dead = True
                    if ghost.id == 0:
                        blinky_dead = True
                        blinky_frightened = False
                    elif ghost.id == 1:
                        pinky_dead = True
                        pinky_frightened = False
                    elif ghost.id == 2:
                        inky_dead = True
                        inky_frightened = False
                    elif ghost.id == 3:
                        clyde_dead = True
                        clyde_frightened = False
                elif powerup and ghost.frightened == False and not ghost.dead:
                    LIVES -= 1
                    score -= 500
                    if LIVES == 0:
                        overlay = pygame.Surface((WINDOW_WIDTH, HEIGHT))
                        overlay.set_alpha(180)
                        overlay.fill((0, 0, 0))
                        screen.blit(overlay, (0, 0))

                        msg = font_bigger.render('GAME OVER', True, 'white')
                        msg_rect = msg.get_rect(center=(WINDOW_WIDTH // 2, HEIGHT // 2))
                        screen.blit(msg, msg_rect)

                        pygame.display.flip()
                        pygame.time.delay(3000)
                        running = False
                        break
                    else:
                        reset_positions()
                        pygame.time.delay(1000)
            if blinky_dead and to_tile(blinky.center_x, blinky.center_y) == GHOST_BOX:
                blinky_dead = False
                blinky_frightened = False
            if pinky_dead and to_tile(pinky.center_x, pinky.center_y) == GHOST_BOX:
                pinky_dead = False
                pinky_frightened = False
            if inky_dead and to_tile(inky.center_x, inky.center_y) == GHOST_BOX:
                inky_dead = False
                inky_frightened = False
            if clyde_dead and to_tile(clyde.center_x, clyde.center_y) == GHOST_BOX:
                clyde_dead = False
                clyde_frightened = False

        if show_paths:
            RED = (255, 60, 60, 50)
            PINK = (255, 170, 200, 50)
            CYAN = (0, 255, 255, 50)
            ORANGE = (255, 165, 0, 50)

            draw_path(path_blinky, RED)
            draw_path(path_pinky, PINK)
            draw_path(path_inky, CYAN)
            draw_path(path_clyde, ORANGE)

        score,  powerup, powerup_count, eaten_ghost = check_col(score, powerup, powerup_count, eaten_ghost)

        if no_food_left():
            img = pygame.image.load("assets/horia-brenciu-fericit.jpg").convert_alpha()

            scale_factor = max(WINDOW_WIDTH / img.get_width(), HEIGHT / img.get_height())
            img = pygame.transform.scale(
                img,
                (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor))
            )

            crop = center_crop(img, WINDOW_WIDTH, HEIGHT)
            crop.set_alpha(128)
            screen.blit(crop, (0, 0))

            win_msg = font_bigger.render('YOU WIN!', True, 'white')
            win_rect = win_msg.get_rect(center=(WINDOW_WIDTH // 2, HEIGHT // 2))
            screen.blit(win_msg, win_rect)

            pygame.display.flip()
            pygame.time.delay(3000)
            running = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if bfs_button.handle_event(event):
                current_strategy_func = bfs_next_tile
                current_strategy_name = 'BFS'
            if dfs_button.handle_event(event):
                current_strategy_func = dfs_next_tile
                current_strategy_name = 'DFS'
            if a_star_button.handle_event(event):
                current_strategy_func = a_star_next_tile
                current_strategy_name = 'A*'
            if  reflex_button.handle_event(event):
                pacman_strategy_name = 'Reflex Agent'
                manual_mode = False
            if minmax_button.handle_event(event):
                pacman_strategy_name = 'Minmax Agent'
                manual_mode = False
            if alpha_beta_button.handle_event(event):
                pacman_strategy_name = 'Alpha_Beta Agent'
                manual_mode = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    show_paths = not show_paths
                if event.key == pygame.K_m:
                    manual_mode = True
                    pacman_strategy_name = 'Manual'

                if control_scheme == 'normal':
                    if event.key == pygame.K_RIGHT:
                        direction_command = 0
                    if event.key == pygame.K_LEFT:
                        direction_command = 1
                    if event.key == pygame.K_UP:
                        direction_command = 2
                    if event.key == pygame.K_DOWN:
                        direction_command = 3

                elif control_scheme == 'chimney':
                    if event.key == pygame.K_UP:  # UP key
                        direction_command = 0  # Maps to RIGHT
                    if event.key == pygame.K_DOWN:  # DOWN key
                        direction_command = 1  # Maps to LEFT
                    if event.key == pygame.K_LEFT:  # LEFT key
                        direction_command = 2  # Maps to UP
                    if event.key == pygame.K_RIGHT:  # RIGHT key
                        direction_command = 3  # Maps to DOWN

                if event.type == pygame.KEYUP:
                    if control_scheme == 'normal':
                        if event.key == pygame.K_RIGHT and direction_command == 0:
                            direction_command = direction
                        if event.key == pygame.K_LEFT and direction_command == 1:
                            direction_command = direction
                        if event.key == pygame.K_UP and direction_command == 2:
                            direction_command = direction
                        if event.key == pygame.K_DOWN and direction_command == 3:
                            direction_command = direction

                    elif control_scheme == 'chimney':
                        if event.key == pygame.K_UP and direction_command == 0:
                            direction_command = direction
                        if event.key == pygame.K_DOWN and direction_command == 1:
                            direction_command = direction
                        if event.key == pygame.K_LEFT and direction_command == 2:
                            direction_command = direction
                        if event.key == pygame.K_RIGHT and direction_command == 3:
                            direction_command = direction
    if mode == MODE_GHOST:
        center_x = player_x + HALF_W
        center_y = player_y + HALF_H
        player_rc = to_tile(center_x, center_y)
        screen.fill('black')
        draw_board()
        draw_player()
        turns_allowed = check_position(center_x, center_y)

        blinky = Ghost(blinky_x, blinky_y, None, ghost_speed, blinky_img, blinky_direction, blinky_dead, blinky_frightened, blinky_box, 0)
        pinky = Ghost(pinky_x, pinky_y, None, ghost_speed, pinky_img, pinky_direction, pinky_dead, pinky_frightened, pinky_box, 1)
        inky = Ghost(inky_x, inky_y, None, ghost_speed, inky_img, inky_direction, inky_dead,inky_frightened,  inky_box, 2)
        clyde = Ghost(clyde_x, clyde_y, None, ghost_speed, clyde_img, clyde_direction, clyde_dead, clyde_frightened, clyde_box, 3)
        ghosts = [blinky, pinky, inky, clyde]

        # pacman moves using minmax
        pac_rc = to_tile(center_x, center_y)
        ghost_rcs = [to_tile(g.center_x, g.center_y) for g in ghosts]
        food_tiles_minmax = [(r, c) for r, row in enumerate(level) for c, val in enumerate(row) if val in (1, 2)]
        move = minmax_helper(pac_rc, ghost_rcs, food_tiles_minmax, direction)
        player_x, player_y, direction = move_player(player_x, player_y, direction, move, turns_allowed, center_x,
                                                    center_y)
        center_x = player_x + HALF_W
        center_y = player_y + HALF_H
        player_rc = to_tile(center_x, center_y)

        tile = level[player_rc[0]][player_rc[1]]
        if tile == 1:
            level[player_rc[0]][player_rc[1]] = 0
        elif tile == 2:
            level[player_rc[0]][player_rc[1]] = 0
            powerup = True
            powerup_count = 0

        # logic for other ghosts
        active_strategy_blinky, blinky_target, blinky_scatter_index = ghost_state(blinky, blinky_dead, game_mode,
                                                                                  player_rc, blinky_scatter_index,
                                                                                  BLINKY_LOOP, current_strategy_func)
        active_strategy_pinky, pinky_target, pinky_scatter_index = ghost_state(pinky, pinky_dead, game_mode, player_rc,
                                                                               pinky_scatter_index, PINKY_LOOP,
                                                                               current_strategy_func)
        active_strategy_inky, inky_target, inky_scatter_index = ghost_state(inky, inky_dead, game_mode, player_rc,
                                                                            inky_scatter_index, INKY_LOOP,
                                                                            current_strategy_func)
        blinky_x, blinky_y, blinky_direction, path_blinky = blinky.move(blinky_target, active_strategy_blinky)
        pinky_x, pinky_y, pinky_direction, path_pinky = pinky.move(pinky_target, active_strategy_pinky)
        inky_x, inky_y, inky_direction, path_inky = inky.move(inky_target, active_strategy_inky)

        player_rect = pygame.Rect(player_x + 10, player_y + 10, PLAYER_W - 20, PLAYER_H - 20)
        ghosts = [blinky, pinky, inky, clyde]

        for ghost in ghosts:
            if player_rect.colliderect(ghost.rect):
                if not powerup:
                    LIVES -= 1
                    score -= 500
                    if LIVES == 0:
                        #game over
                        overlay = pygame.Surface((WINDOW_WIDTH, HEIGHT))
                        overlay.set_alpha(180)
                        overlay.fill((0, 0, 0))
                        screen.blit(overlay, (0, 0))
                        msg = font_bigger.render('GAME OVER', True, 'white')
                        msg_rect = msg.get_rect(center=(WINDOW_WIDTH // 2, HEIGHT // 2))
                        screen.blit(msg, msg_rect)
                        pygame.display.flip()
                        pygame.time.delay(3000)
                        running = False
                        break
                    else:
                        reset_positions()
                        pygame.time.delay(1000)
                elif powerup and not ghost.dead and not eaten_ghost[ghost.id]:
                    score += 200
                    eaten_ghost[ghost.id] = True
                    ghost.dead = True

            if ghost.dead and to_tile(ghost.center_x, ghost.center_y) == GHOST_BOX:
                ghost.dead = False

       
        turns_allowed_clyde = check_position(clyde.center_x, clyde.center_y, alt_mode=True)

        
        clyde_x, clyde_y, clyde_direction = move_player(
            clyde_x, clyde_y,
            clyde_direction,
            clyde_direction_command,
            turns_allowed_clyde,
            clyde.center_x, clyde.center_y,
            log=False,
            alt_mode=False
        )

        
        clyde.center_x = clyde_x + HALF_W
        clyde.center_y = clyde_y + HALF_H

        
        clyde.rect = pygame.Rect(
        clyde.center_x - 18,
        clyde.center_y - 18,
        36,
        36
        )


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    clyde_direction_command = 0
                if event.key == pygame.K_LEFT:
                    clyde_direction_command = 1
                if event.key == pygame.K_UP:
                    clyde_direction_command = 2
                if event.key == pygame.K_DOWN:
                    clyde_direction_command = 3

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT and clyde_direction_command == 0:
                    clyde_direction_command = clyde_direction
                if event.key == pygame.K_LEFT and clyde_direction_command == 1:
                    clyde_direction_command = clyde_direction
                if event.key == pygame.K_UP and clyde_direction_command == 2:
                    clyde_direction_command = clyde_direction
                if event.key == pygame.K_DOWN and clyde_direction_command == 3:
                    clyde_direction_command = clyde_direction

    if player_x > WIDTH:
        player_x = -PLAYER_W
    elif player_x < -PLAYER_W:
        player_x = WIDTH

    pygame.display.flip()
    timer.tick(fps)

pygame.quit()