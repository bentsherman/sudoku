import argparse
import matplotlib as mpl
import matplotlib.animation
import time

from gamestate import GameState



def main():
    # parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-frames', help='number of frames to render', type=int, default=100)
    parser.add_argument('--frame-interval', help='length of each frame in ms', type=int, default=1000)
    parser.add_argument('--p-init', help='proportion of initial hints', type=float, default=0.3)

    args = parser.parse_args()

    # initialize game state
    game = GameState(p_init=args.p_init)

    # initialize animation
    t0 = time.perf_counter()

    anim = mpl.animation.FuncAnimation(game._fig, game.render, frames=game.animate, save_count=args.n_frames, interval=args.frame_interval)
    anim.save('sudoku.mp4')

    t1 = time.perf_counter()

    # print performance metrics
    t = t1 - t0
    q = args.n_frames / t
    print('processing time: %.3f s, %.3f frames / s' % (t, q))



if __name__ == '__main__':
    main()