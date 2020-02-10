from typing import Tuple, List, Optional
from sys import exit, stdout
from random import getrandbits
from time import sleep

# Rules:
# Any live cell with fewer than two live neighbours dies, as if by underpopulation.
# Any live cell with two or three live neighbours lives on to the next generation.
# Any live cell with more than three live neighbours dies, as if by overpopulation.
# Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

class Cell(object):
    def __init__(self, alive: bool = False) -> None:
        self.alive = alive

class Grid(object):
    def __init__(self, x_size: int = 16, y_size: int = 16) -> None:
        self.x_size = x_size
        self.y_size = y_size

        self.cells: List[List[Cell]] = [[Cell() for i in range(x_size)] for i in range(y_size)] # TODO: test generator ()

    @property
    def get_size(self) -> Tuple[int]:
        return (self.x_size, self.y_size)

    @property # Not sure if this is proper use case?
    def get_cell(self, x: int, y: int) -> Cell:
        return self.cells[x][y]

    def print_grid(self):
        for y in self.cells:
            for x in y:
                stdout.write('X' if x.alive else ' ')
            stdout.write('\n')
        return

    def clear_grid(self) -> None:
        for _ in range(self.y_size):
            for __ in range(self.x_size):
                stdout.write('\b \b') # Clear a single character
            stdout.write('\033[F') # Move up a line
        #stdout.write('\033[F')
        return

    def flip_cell(self, x: int, y: int) -> None:
        self.cells[y][x].alive = not self.cells[y][x].alive
        return

    def get_neighbours(self, _x: int, _y: int) -> Tuple[Optional[bool]]:
        # Return a tuple of all neighbours `alive` status around X.
        #  1 2 3
        #  4 X 5
        #  6 7 8
        # For any out-of zone, return None.
        l: List[Optional[bool]] = []
        for y in range(_y - 1, _y + 2):
            if y < 0 or y == self.y_size:
                l.extend([None, None, None])
                continue
            for x in range(_x - 1, _x + 2):
                if _y == y and _x == x: continue
                if x < 0 or x == self.x_size:
                    l.append(None)
                    continue

                l.append(self.cells[y][x].alive)

        return tuple(l)

    def update_grid_full(self) -> None: # Apply the game's rules to the grid.
        _cells: List[List[Cell]] = [[Cell() for _ in range(self.x_size)] for __ in range(self.y_size)]
        for y in range(self.y_size):
            for x in range(self.x_size):
                neighbours: Tuple[Optional[bool]] = self.get_neighbours(x, y)

                #if (self.get_cell(x, y)).alive: # This cell was alive before
                if self.cells[y][x].alive:
                    # Below 2, die from underpopulation. > 3, die from overpopulation.
                    if sum(i if i is not None else 0 for i in neighbours) in range(2, 4):
                        _cells[y][x].alive = True
                else: # This cell was dead before
                    # Dead but had 3 neighbours, reprodocution life
                    if sum(i if i is not None else 0 for i in neighbours) == 3:
                        _cells[y][x].alive = True

        # Update our cells.
        self.cells = _cells
        return

    def randomize_grid(self) -> None:
        for y in self.cells:
            for x in y:
                x.alive = getrandbits(1) # Probably fastest?
        return

if __name__ == '__main__':
    print("Conway's Game of Life")
    g: Grid = Grid(int(input('X: ')), int(input('Y: ')))
    print_size: int = g.x_size * (g.y_size + 1) # account for newline

    g.randomize_grid()

    while True:
        g.print_grid()
        g.update_grid_full()

        g.clear_grid()
