import numpy as np
from numba import jit
from random import randint

dirs = [UP, DOWN, LEFT, RIGHT] = range(4)


# Merge tiles with same value
@jit
def merge_tiles(s):
    for i in [0, 1, 2, 3]:
        for j in [0, 1, 2]:
            if s[i][j] == s[i][j + 1] and s[i][j] != 0:
                s[i][j] *= 2
                s[i][j + 1] = 0
    return s

# Move all tiles to the left direction
@jit
def move_tiles(s):
    z = np.zeros((4, 4))
    for i in [0, 1, 2, 3]:
        c = 0
        for j in [0, 1, 2, 3]:
            if s[i][j] != 0:
                z[i][c] = s[i][j]
                c += 1
    return z

# Check whether exists empty tiles along different directions
@jit
def get_available_from_zeros(s):
    uc, dc, lc, rc = False, False, False, False

    v_saw_0 = [False, False, False, False]
    v_saw_1 = [False, False, False, False]

    for i in [0, 1, 2, 3]:
        saw_0 = False
        saw_1 = False

        for j in [0, 1, 2, 3]:
            if s[i][j] == 0:
                saw_0 = True
                v_saw_0[j] = True

                if saw_1:
                    rc = True
                if v_saw_1[j]:
                    dc = True

            if s[i][j] > 0:
                saw_1 = True
                v_saw_1[j] = True

                if saw_0:
                    lc = True
                if v_saw_0[j]:
                    uc = True

    return [uc, dc, lc, rc]


class GameBoard:
    def __init__(self):
        self.grid = np.zeros((4, 4))

    def clone(self):
        grid_copy = GameBoard()
        grid_copy.grid = np.copy(self.grid)
        return grid_copy

    # Create initial state of 2048
    def init_state(self):
        # self.board = GameBoard()
        self.computer_move()
        self.computer_move()

    def insert_tile(self, pos, value):
        self.grid[pos[0]][pos[1]] = value

    # Get positions of all empty tiles
    def get_available_tiles(self):
        tiles = []
        for x in range(4):
            for y in range(4):
                if self.grid[x][y] == 0:
                    tiles.append((x, y))
        return tiles

    # Get maximum value on board
    def get_max_tile(self):
        return np.amax(self.grid)

    # Get transition state based on specific action
    def player_move(self, act, get_avail_call=False):
        if get_avail_call:
            clone = self.clone()

        if act == UP:  # Rotate the board 90 degree counterclockwise
            self.grid = self.grid[:, ::-1].T
        elif act == DOWN:  # Rotate the board 180 degree counterclockwise
            self.grid = self.grid.T[:, ::-1]
        elif act == RIGHT:  # Rotate the board 90 degree clockwise
            self.grid = self.grid[:, ::-1]
            self.grid = self.grid[::-1, :]

        self.grid = move_tiles(self.grid)
        self.grid = merge_tiles(self.grid)
        self.grid = move_tiles(self.grid)

        if act == UP:  # Rotate the board 90 degree clockwise
            self.grid = self.grid.T[:, ::-1]
        elif act == DOWN:  # Rotate the board 180 degree clockwise
            self.grid = self.grid[:, ::-1].T
        elif act == RIGHT:  # Rotate the board 90 degree counterclockwise
            self.grid = self.grid[:, ::-1]
            self.grid = self.grid[::-1, :]

        # Check whether the action changes state
        if get_avail_call:
            return not (clone.grid == self.grid).all()
        else:
            return None

    # Replace an empty tile with value 2 or 4
    def computer_move(self):
        if randint(1, 100) <= 90:
            value = 2
        else:
            value = 4

        cells = self.get_available_tiles()
        pos = cells[randint(0, len(cells) - 1)] if cells else None

        if pos is None:
            return None
        else:
            self.insert_tile(pos, value)
            return pos

    def get_available_actions(self, dirs=dirs):
        available_actions = []

        a1 = get_available_from_zeros(self.grid)

        for x in dirs:
            if not a1[x]:
                board_clone = self.clone()

                if board_clone.player_move(x, True):
                    available_actions.append(x)

            else:
                available_actions.append(x)

        return available_actions

    def get_tile_value(self, pos):
        return self.grid[pos[0]][pos[1]]
