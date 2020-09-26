# imports:
import time
from bs4 import BeautifulSoup
import requests as re


def extract_cell_coordinates_and_value():
    # each cell's coordinates are under <id> tag, and are in a pattern of "ij"
    # the value in that cell, is a text in the pattern of "\n{val}\n"
    clues = []                      # list of clues given at start of game
    cell_html_info = soup.find_all('input')

    for item in cell_html_info:
        if item.has_attr('readonly') and item.has_attr('value'):        # item is a clue
            i = int(item.get('id')[1])               # get row coordinate
            j = int(item.get('id')[2])               # get col coordinate
            value = int(item.get('value')[0])        # get value
            cell_data = ((i, j), value)              # make tuple of coordinates and value
            clues.append(cell_data)
    return clues


def init_board():
    """ initializes a grid of size <grid_size> """
    for clue in clues:
        board.cells[clue[0][0]][clue[0][1]].set_value(clue[1])



def print_board():
    """prints the current grid to stdout"""
    for i in range(board_size):
        if i % 3 == 0 and i != 0:
            print('—\t' * (board_size + 2))
        for j in range(board_size):
            if j % 3 == 0 and j != 0:
                print('|', end='\t')
            print(board.cells[i][j].get_value(), end='\t')
        print()     # '\n'


def find_empty(queue_ind):
    i = queue[queue_ind][0][0]
    j = queue[queue_ind][0][1]
    return i, j


def filter_clues(possible_values, i, j):
    """ remove values in possible_values that already exist on the board """
    block = get_block(i, j)
    row, col = get_cross(i, j)
    unwanted = block.union(block, row, col)
    possible_values.difference_update(unwanted)


def get_cross(i, j):
    row = set()
    col = set()
    # row:
    for ind in range(board_size):
        if board.cells[i][ind].get_value() != 0:
            row.add(board.cells[i][ind].get_value())
    # column:
    for ind in range(board_size):
        if board.cells[ind][j].get_value() != 0:
            col.add(board.cells[ind][j].get_value())

    return row, col


def is_valid_cross(i, j, pos):
    """ returns True if value of given coordinates appears in its row and column """
    row, col = get_cross(i, j)
    return False if pos in row or pos in col else True


def get_queue():
    temp_queue = []
    for i in range(board_size):
        for j in range(board_size):
            if board.cells[i][j].get_value() == 0:
                row, col = get_cross(i, j)
                block = get_block(i, j)
                num_of_clues = len(row) + len(col) + len(block)
                temp_queue.append(((i, j), num_of_clues))
    temp_queue.sort(key=lambda x: x[1], reverse=True)
    return temp_queue


def get_block(i, j):
    block = set()
    block_row = i // 3
    block_col = j // 3
    for x in range(block_row * 3, block_row * 3 + 3):
        for y in range(block_col * 3, block_col * 3 + 3):
            if board.cells[x][y].get_value() != 0:
                block.add(board.cells[x][y].get_value())
    return block


def is_valid_block(i, j, pos):
    """ returns True if value of given coordinates appears in its block """
    block = get_block(i, j)
    return False if pos in block else True


def solve(queue_ind):
    """ solve given board inplace, using recursion"""
    if queue_ind == -1:
        return False
    if queue_ind >= len(queue):             # no more empty spaces, filled all of the board
        return True
    i, j = find_empty(queue_ind)
    possible_values = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    filter_clues(possible_values, i, j)
    for pos in possible_values:
        if is_valid_block(i, j, pos) and is_valid_cross(i, j, pos):
            board.cells[i][j].set_value(pos)                                             # if poss isn't in the row, col or block, we can
            queue_ind += 1                                                               # add it to current cell. then, we call solve()
            if solve(queue_ind):                                                         # recursively and if at some point the recursion
                return True                                                              # folds, and it returns True (in line 55), it means
            board.cells[i][j].set_value(0)                                               # the folding started from the last cell (condition in line 47)
            queue_ind -= 1
    queue_ind -= 1
    return False


class Grid:
    def __init__(self, rows, cols, width=500, height=500):
        self.rows = rows
        self.cols = cols
        self.grid_size = (width, height)
        self.cells = [[Cell(0, i, j, width, height) for j in range(board_size)] for i in range(board_size)]


class Cell:
    def __init__(self, value, row, col, width, height):     # (x,y) = starting position of cell's dimensions
        self.value = value
        self.row = row
        self.col = col
        self.height = height
        self.width = width

    def get_value(self):
        return self.value

    def set_value(self, val):
        self.value = val

run = 0
board_size = 9
print('Fetching board...')
while run < 10:
    r = re.get('https://nine.websudoku.com/')            # 200=success | 300=serverError | 400=clientError
    soup = BeautifulSoup(r.content, 'lxml')             # convert request object into BeautifulSoup object with lxml parser
    clues = extract_cell_coordinates_and_value()        # parse soup and extract a list with data of all cells (i, j, val)
    board = Grid(board_size, board_size)                # initialize board object filled with cell objects
    init_board()                                        # fill board with extracted clues

    print('Board fetched:')
    print_board()

    print('Solving...')
    queue = get_queue()
    if solve(0):
        print('Solved board:')
        print_board()
    else:
        print('NO SOLUTION!')
    run += 1
    print('=====================================================================')
