#!/usr/bin/env python3.9
"""game.py - An implementation of conway's game of life in modern python."""
from __future__ import annotations

import argparse
import copy
import os
import random
import signal
import sys
import time
from types import FrameType
from typing import Optional
from typing import Sequence

__author__ = "Joshua Smith (cmyui)"
__email__ = "cmyuiosu@gmail.com"
__discord__ = "cmyui#0425"


""" rules of the game
1. any live cell with fewer than two live neighbours dies, as if by underpopulation
2. any live cell with two or three live neighbours lives on to the next generation
3. any live cell with more than three live neighbours dies, as if by overpopulation
4. any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction
"""

class Life:
    def __init__(
        self,
        start_width: Optional[int] = None,
        start_height: Optional[int] = None,
        clear_screen: bool = False,
    ) -> None:
        if start_width is None or start_height is None:
            term_width, term_height = os.get_terminal_size()
            start_width, start_height = term_width - 1, term_height - 1

        self.width: int = start_width
        self.height: int = start_height
        self.clear_screen = clear_screen

        # store two buffers, swapping between them each pass
        self.cells_table = [[False] * self.width] * self.height
        self.prev_cells_table = [[False] * self.width] * self.height

        self.start_time = time.time()
        self.frame_count = 0

        # used when handling window size changes
        self.should_regenerate_screen = False
        self.new_width = None
        self.new_height = None
        self.setup_sigwinch_handler()

    def setup_sigwinch_handler(self) -> None:
        """Handle window size changes automatically."""
        def sigwinch_handler(signum: int, frame: Optional[FrameType] = None) -> None:
            self.update_window_size(width=None, height=None)

        signal.signal(signal.SIGWINCH, sigwinch_handler)

    def update_window_size(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        """Gracefully handle a window size change (on the next frame)."""
        if width is None or height is None:
            term_width, term_height = os.get_terminal_size()
            width, height = term_width - 1, term_height - 1

        # enqueue a size change on the next frame
        self.should_regenerate_screen = True
        self.new_width = width
        self.new_height = height

    # helper function used to apply the game's rules to each cell
    def get_alive_neighbours(self, row_idx: int, column_idx: int) -> int:
        """Find a given cell's (t) count of living neighbours (x).
        # o o o o o          ^
        # o x x x o          | column
        # o x t x o          v
        # o x x x o
        # o o o o o    <-----> row
        """
        neighbour_indices = (
            # adjacent cells
            (row_idx - 1, column_idx), # top
            (row_idx, column_idx + 1), # right
            (row_idx + 1, column_idx), # bottom
            (row_idx, column_idx - 1), # left

            # diagonal cells
            (row_idx - 1, column_idx - 1), # top left
            (row_idx - 1, column_idx + 1), # top right
            (row_idx + 1, column_idx - 1), # bottom left
            (row_idx + 1, column_idx + 1), # bottom right
        )

        return sum((
            self.prev_cells_table[row_idx][column_idx]
            for row_idx, column_idx in neighbour_indices
            if 0 <= row_idx < self.height and 0 <= column_idx < self.width
        ))

    def should_continue_running(self) -> bool:
        return True # TODO: shutdown once a stable state is reached

    def apply_rules(self) -> None:
        """Iterate through each value in our cells table,
        applying the game's rules to the cells a single time."""
        for row_idx, row in enumerate(self.cells_table):
            for column_idx, is_alive in enumerate(row):
                alive_neighbours_count = self.get_alive_neighbours(row_idx, column_idx)

                if is_alive:  # rules for living cells
                    # each cell with one of no neighbours dies, as if by solitude
                    if alive_neighbours_count <= 1:
                        self.cells_table[row_idx][column_idx] = False

                    # each cell with four or more neighbours dies, as if by overpopulation
                    elif alive_neighbours_count >= 4:
                        self.cells_table[row_idx][column_idx] = False

                else:  # rules for dead cells
                    # each cell with three neighbours becomes populated, as if by reproduction
                    if alive_neighbours_count == 3:
                        self.cells_table[row_idx][column_idx] = True

    def print_cells_table(self) -> None:
        """Print a given table to stdout."""
        if self.clear_screen:
            # TODO: may be able to optimize this further if worth it?
            # http://www.climagic.org/mirrors/VT100_Escape_Codes.html
            print(f"\x1b[{self.width}A\x1b[J", end="") # move to upper left, clear below

        output_rows = [
            [
                "X" if self.cells_table[row_idx][column_idx] else " "
                for column_idx in range(self.width)
            ] for row_idx in range(self.height)
        ]

        # add frame rate & count to top right
        frames_per_sec = self.frame_count / (time.time() - self.start_time)
        frame_info_output = f" FPS: {frames_per_sec:.2f} | Frames: {self.frame_count}"
        output_rows[0][self.width - len(frame_info_output):] = frame_info_output

        print("\n".join("".join(row) for row in output_rows))

    def randomize_table(self) -> None:
        """Replace the current table of cells with a randomized set of the same size."""
        full_table_size = self.width * self.height

        # generate random alive state for each cell in our table
        random_values = random.choices([True, False], k=full_table_size)

        # overwrite our cells table with the new (random) state
        self.cells_table = [
            random_values[i:i+self.width]
            for i in range(0, full_table_size, self.width)
        ]

        self.prev_cells_table = copy.deepcopy(self.cells_table)

    def run(self) -> int:
        """Run the game with the current state."""
        self.randomize_table()

        while self.should_continue_running():
            # handle pending window size changes
            if self.new_width and self.new_height: # TODO: handle 0s?
                self.width = self.new_width
                self.height = self.new_height
                self.randomize_table()

                self.new_width = None
                self.new_height = None

                self.start_time = time.time()
                self.frame_count = 0

            # run a single iteration of the game
            self.apply_rules()

            # save the current buffer
            self.prev_cells_table = copy.deepcopy(self.cells_table)

            # print the table to stdout
            self.print_cells_table()

            self.frame_count += 1

        return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    if argv:
        parser = argparse.ArgumentParser()

        # ./main.py {width} {height}
        parser.add_argument(
            "width",
            help="the width of the game field.",
            type=int,
        )
        parser.add_argument(
            "height",
            help="the height of the game field.",
            type=int,
        )

        args = parser.parse_args(argv)

        width, height = args.width, args.height
    else:  # not argv
        width, height = None, None

    game = Life(width, height, clear_screen=True)

    exit_code = game.run()

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
