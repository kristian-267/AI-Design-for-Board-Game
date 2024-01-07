import math
import numpy as np

UP, DOWN, LEFT, RIGHT = range(4)


class AI():
    def get_action(self, board):
        best_action, _ = self.expectimax(board)
        return best_action

    # Calculate score of feature monotonicity
    def monotonicity(self, grid):
        score = [0, 0, 0, 0]

        for x in range(4):
            current = 0
            next = current + 1
            while next < 4:
                while next < 3 and not grid[next, x]:
                    next += 1
                current_tile = grid[current, x]
                current_value = math.log(current_tile, 2) if current_tile else 0
                next_tile = grid[next, x]
                next_value = math.log(next_tile, 2) if next_tile else 0
                if current_value > next_value:
                    score[0] += (next_value - current_value)
                elif next_value > current_value:
                    score[1] += (current_value - next_value)
                current = next
                next += 1

        for y in range(4):
            current = 0
            next = current + 1
            while next < 4:
                while next < 3 and not grid[y, next]:
                    next += 1
                current_tile = grid[y, current]
                current_value = math.log(current_tile, 2) if current_tile else 0
                next_tile = grid[y, next]
                next_value = math.log(next_tile, 2) if next_tile else 0
                if current_value > next_value:
                    score[2] += (next_value - current_value)
                elif next_value > current_value:
                    score[3] += (current_value - next_value)
                current = next
                next += 1

        return max(score[0], score[1]) + max(score[2], score[3])

    # Calculate score of feature smoothless
    def smoothless(self, grid):
        score = 0
        s_grid = np.sqrt(grid)

        for i in range(3):
            score -= np.sum(np.abs(s_grid[:, i] - s_grid[:, i + 1]))
            score -= np.sum(np.abs(s_grid[i, :] - s_grid[i + 1, :]))

        return score

    # Calculate score of feature number of empty tiles
    def number_EmptyTiles(self, board):

        return len(board.get_available_tiles())

    # Calculate score of feature sum of squares of all values
    def sum_SquareValues(self, grid):

        return np.sum(np.power(grid, 2))

    # calculate evaluation function
    def eval(self, board):
        grid = board.grid

        M = self.monotonicity(grid)
        S = self.smoothless(grid)
        Ne = self.number_EmptyTiles(board)
        Sv = self.sum_SquareValues(grid)

        w_M = 10000.0
        w_S = 3.0
        w_Ne = 150000.0
        w_Sv = 1.0

        utility = M * w_M + np.power(S, w_S) + Ne * w_Ne + Sv * w_Sv

        return utility

    # Get best decision
    def expectimax(self, board, depth=0):
        actions = board.get_available_actions()
        next_states = []

        for action in actions:
            state = board.clone()
            state.player_move(action)
            next_states.append((action, state))

        max_utility = float('-inf')
        best_action = None

        for next_state in next_states:
            utility = self.expect_value(next_state[1], depth + 1)

            if utility >= max_utility:
                max_utility = utility
                best_action = next_state[0]

        return best_action, max_utility

    # Decision on MAX node
    def max_value(self, board, depth=0):
        actions = board.get_available_actions()
        n_action = len(actions)

        if n_action == 0:
            return self.eval(board)

        utility = float('-inf')

        for action in actions:
            next_state = board.clone()
            next_state.player_move(action)
            utility = max(utility, self.expect_value(next_state, depth + 1))

        return utility

    # Decision on CHANCE node
    def expect_value(self, board, depth=0):
        actions = board.get_available_actions()
        empty_tiles = board.get_available_tiles()
        n_action = len(actions)
        n_empty = len(empty_tiles)

        if n_empty >= 6 and depth >= 3:
            return self.eval(board)

        if n_empty >= 0 and depth >= 5:
            return self.eval(board)

        if n_action == 0:
            return self.eval(board)

        possible_tiles = []

        chance_2 = (0.9 * (1 / n_empty))
        chance_4 = (0.1 * (1 / n_empty))

        for tile in empty_tiles:
            possible_tiles.append((tile, 2, chance_2))
            possible_tiles.append((tile, 4, chance_4))

        exp_utility = 0

        for tile in possible_tiles:
            next_state = board.clone()
            next_state.insert_tile(tile[0], tile[1])
            utility = self.max_value(next_state, depth + 1)
            exp_utility += utility * tile[2]

        return exp_utility
