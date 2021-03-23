import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import random



class GameState():
    def __init__(self, p_init=0.3):
        # initialize figure
        self._fig, self._ax = plt.subplots(figsize=(5, 5))
        self._frames = 0

        self._fig.tight_layout()

        # generate puzzle
        self._grid = self.generate(p_init)

        # initialize adjacency matrix
        self._adj = np.ones((9, 9, 9), dtype=np.int)

    def generate(self, p_init):
        # define constants, helper functions
        base = 3
        side = 9

        def pattern(i, j): return (i // base + (i % base) * base + j) % side
        def shuffle(s): return random.sample(s, len(s))

        # randomize rows, columns, numbers of baseline pattern
        r_base = range(base)
        rows = [m * base + i for m in shuffle(r_base) for i in shuffle(r_base)]
        cols = [m * base + j for m in shuffle(r_base) for j in shuffle(r_base)]
        nums = shuffle(range(1, side + 1))

        # produce grid from randomized baseline pattern
        G = np.array([[nums[pattern(i, j)] for j in cols] for i in rows])

        # remove a subset of the grid
        n_init = int(side * side * p_init)
        n_remove = side * side - n_init

        if n_init < 17:
            print('error: at least 17 hints are required for a complete 9x9 puzzle')

        indices = random.sample(range(side * side), n_remove)
        indices = np.array([(idx // side, idx % side) for idx in indices], dtype=np.int)
        indices = indices[:, 0], indices[:, 1]

        G[indices] = 0

        return G

    def block(self, A, m):
        i0 = (m // 3) * 3
        j0 = (m %  3) * 3

        return A[i0:(i0 + 3), j0:(j0 + 3)]

    def block_from(self, A, i, j):
        i0 = i // 3 * 3
        j0 = j // 3 * 3

        return A[i0:(i0 + 3), j0:(j0 + 3)]

    def is_valid(self, i, j, k):
        G = self._grid

        # validate row, column, block
        G_row = G[i, :]
        G_col = G[:, j]
        G_blk = self.block_from(G, i, j).reshape(-1)

        return \
            np.all(G_row != k) and \
            np.all(G_col != k) and \
            np.all(G_blk != k)

    def is_closed_set(self, A_sub, values):
        # compute union of spaces covered by values
        U = np.bitwise_or(A_sub[:, values], axis=1)

        # determine whether the union set is closed
        return np.sum(U) == len(values)

    def render(self, args):
        G = self._grid
        A = self._adj

        # unpack arguments
        # node_updates, text = args

        # print frame number
        print('rendering frame %d' % (self._frames))
        self._frames += 1

        # clear figure
        ax = self._ax
        ax.clear()

        cmap = colors.ListedColormap([
            'white',
            'red',
            'sienna',
            'orange',
            'yellow',
            'yellowgreen',
            'green',
            'cyan',
            'blue',
            'purple',
        ])
        ax.imshow(G, cmap=cmap, alpha=0.5, vmin=0, vmax=9)

        # draw grid
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])

        for i in range(9):
            for j in range(9):
                if G[i, j] != 0:
                    text = '%d' % (G[i, j])
                    size='xx-large'
                else:
                    text = [['%d' % (k1 + k2 + 1) if A[i, j, k1 + k2] else ' ' for k2 in range(3)] for k1 in range(0, 9, 3)]
                    text = '\n'.join([' '.join([text[k1][k2] for k2 in range(3)]) for k1 in range(3)])
                    size='xx-small'

                ax.text(j, i, text, c='k', family='monospace', size=size, ha='center', va='center')

    def apply(self, i, j, k):
        G = self._grid
        A = self._adj

        # if k is not a candidate for A_ij, return failure
        if A[i, j, k] == 0:
            print('warning: invalid apply at (%d, %d, %d)' % (i, j, k))
            return False

        # remove all other candidates from A_ij
        A[i, j, :] = 0

        # remove k from current row, column, block
        A[i, :, k] = 0
        A[:, j, k] = 0
        self.block_from(A, i, j)[:, :, k] = 0

        # set G_ij to k
        G[i, j] = k + 1

        # return success
        return True

    def do_init(self):
        G = self._grid

        for i in range(9):
            for j in range(9):
                if G[i, j] != 0:
                    self.apply(i, j, G[i, j] - 1)

    def do_move(self):
        A = self._adj

        # if A_ij has only one candidate k,
        # then set A_ij to k
        for i in range(9):
            for j in range(9):
                if A[i, j].sum() == 1:
                    k = np.where(A[i, j] == 1)[0][0]
                    self.apply(i, j, k)
                    return True

        # if row A_i has only one space A_ij with candidate k,
        # then set A_ij to k
        for i in range(9):
            A_row = A[i, :]
            for k in range(9):
                if A_row[:, k].sum() == 1:
                    j = np.where(A_row[:, k] == 1)[0][0]
                    self.apply(i, j, k)
                    return True

        # if col A_j has only one space A_ij with candidate k,
        # then set A_ij to k
        for j in range(9):
            A_col = A[:, j]
            for k in range(9):
                if A_col[:, k].sum() == 1:
                    i = np.where(A_col[:, k] == 1)[0][0]
                    self.apply(i, j, k)
                    return True

        # if blk A_m has only one space A_ij with candidate k,
        # then set A_ij to k
        for m in range(9):
            A_blk = self.block(A, m).reshape(-1, 9)
            for k in range(9):
                if A_blk[:, k].sum() == 1:
                    n = np.where(A_blk[:, k] == 1)[0][0]
                    i = (m // 3) * 3 + n // 3
                    j = (m %  3) * 3 + n %  3
                    self.apply(i, j, k)
                    return True

        # if k occupies only one row/col in a block,
        # remove k from that row/col in adjacent blocks
        # NOTE: should often be handled by checking rows/cols for single k
        pass

        # if k occupies only two rows/cols across two blocks,
        # remove k from those rows/cols in third block
        # NOTE: should often be handled by checking rows/cols for single k
        pass

        # if candidates (k1, k2, ..., kn) occupy a set of exactly n spaces in a row/col/blk,
        # then remove all other candidates from those spaces
        pass

        return False

    def is_done(self):
        G = self._grid

        # make sure the grid is completely filled
        if np.any(G == 0):
            return False

        # validate each row
        for i in range(9):
            G_row = G[i, :]
            for k in range(9):
                if np.sum(G_row == k + 1) != 1:
                    return False

        # validate each column
        for j in range(9):
            G_col = G[:, j]
            for k in range(9):
                if np.sum(G_col == k + 1) != 1:
                    return False

        # validate each block
        for m in range(9):
            G_blk = self.block(G, m).reshape(-1)
            for k in range(9):
                if np.sum(G_blk == k + 1) != 1:
                    return False

        return True

    def animate(self):
        # draw initial state
        yield ([], None)

        # initialize adjacency matrix
        self.do_init()

        # draw updated state
        yield ([], None)

        # play for several rounds
        while True:
            # do a move
            success = self.do_move()

            if success:
                yield ([], None)
            else:
                print('error: agent is stuck')
                yield ([], 'I\'m stuck!')
                break

            # check if agent is done
            if self.is_done():
                yield ([], 'Done!')
                break
