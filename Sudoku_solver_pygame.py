import pygame as pg
import time
start_time = time.time()
# global variables:
screen_size = (500, 700)
board_size = 9
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
board = [
    [9, 0, 0, 8, 5, 0, 1, 0, 0],
    [2, 6, 0, 0, 0, 4, 7, 0, 0],
    [0, 0, 5, 7, 0, 0, 0, 8, 0],
    [0, 0, 0, 4, 0, 0, 0, 0, 1],
    [0, 8, 9, 0, 7, 0, 0, 4, 0],
    [1, 0, 0, 0, 0, 9, 0, 0, 0],
    [0, 2, 0, 0, 0, 7, 4, 0, 0],
    [0, 0, 1, 2, 0, 0, 0, 0, 3],
    [0, 0, 3, 0, 9, 5, 0, 0, 8]
]


def draw_grid():
    line_num = 0
    inc = screen_size[0] // 9
    rec = pg.Rect(0, 0, 500, 500)
    pg.draw.rect(screen, black, rec, 3)
    for x in range(inc, 500, inc+1):
        line_num += 1
        if line_num % 3 == 0:
            pg.draw.line(screen, black, (x, 0), (x, 499), 3)
        pg.draw.line(screen, black, (x, 0), (x, 499))

    line_num = 0
    for y in range(inc, 500, inc+1):
        line_num += 1
        if line_num % 3 == 0:
            pg.draw.line(screen, black, (0, y), (499, y), 3)
        pg.draw.line(screen, black, (0, y), (499, y))


def draw_button():
    # shape
    x = screen_size[0] / 3 + 1
    y = ((screen_size[1] - screen_size[0]) / 3) + screen_size[0]
    rec = pg.Rect(x, y, x, 100)

    # text
    font = pg.font.Font(None, 35)
    text = font.render('Solve', True, black)

    # draw
    pg.draw.rect(screen, black, rec, 3)
    text_x_pos = x+(x/3) - 7
    text_y_pos = y+40
    screen.blit(text, (text_x_pos, text_y_pos))


def pressed_solve(m_pos):
    solve_x_left = screen_size[0] / 3
    solve_x_right = 2 * solve_x_left
    solve_y_up = (screen_size[1]-screen_size[0]) / 3 + screen_size[0]
    solve_y_down = solve_y_up + 100
    if solve_x_left < m_pos[0] < solve_x_right and solve_y_up < m_pos[1] < solve_y_down:
        return True
    return False


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


def is_valid_cross(i, j, poss):
    """ returns True if value of given coordinates appears in its row and column """
    row, col = get_cross(i, j)
    return False if poss in row or poss in col else True


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


def fill_board():
    for i in range(board_size):
        for j in range(board_size):
            if board.cells[i][j].get_value() != 0:
                fill_cell(i, j)


def fill_cell(i, j, blank=False):
    cell_x_pos = screen_size[0] / 9 * j
    cell_y_pos = screen_size[0] / 9 * i
    if not blank:
        font_x_pos = cell_x_pos + cell_height // 3
        font_y_pos = cell_y_pos + cell_height // 3
        font = pg.font.Font(None, 35)
        text = font.render(str(board.cells[i][j].get_value()), True, black)
        screen.blit(text, (font_x_pos, font_y_pos))
    else:
        rect = pg.Rect(cell_x_pos, cell_y_pos, cell_width, cell_height)
        screen.fill(white, rect)
        pg.display.update()


def refresh_screen():
    screen.fill(white)
    draw_grid()                                     # makes grid on screen window
    fill_board()                                    # fill board with given clues
    draw_button()                                   # makes 'solve' button
    pg.display.update()


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



def solve(queue_ind):
    """ solve given board inplace, using recursion"""
    if queue_ind == -1:
        return False
    if queue_ind >= len(queue):             # no more empty spaces, filled all of the board
        return True

    i, j = find_empty(queue_ind)

    x_pos = screen_size[0] / 9 * j
    y_pos = screen_size[0] / 9 * i
    rect = pg.Rect(x_pos+2, y_pos+2, cell_width, cell_height)

    possible_values = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    filter_clues(possible_values, i, j)
    for pos in possible_values:
        #time.sleep(0.01)                                                # slow process time to actually see what's up
        if is_valid_block(i, j, pos) and is_valid_cross(i, j, pos):
            # draw green rect
            board.cells[i][j].set_value(pos)
            queue_ind += 1
            fill_cell(i, j)
            pg.draw.rect(screen, green, rect, 3)
            pg.display.update()

            if solve(queue_ind):
                return True

            board.cells[i][j].set_value(0)
            queue_ind -= 1
            fill_cell(i, j, True)           # over-write cell with blank color (del current value)
            pg.display.update()
        # draw red rect
        pg.draw.rect(screen, red, rect, 3)
        pg.display.update()
    queue_ind -= 1
    return False


class Grid:
    def __init__(self, rows, cols, width=500, height=500):
        self.rows = rows
        self.cols = cols
        self.grid_size = (width, height)
        self.cells = [[Cell(board[i][j], i, j, width, height) for j in range(board_size)] for i in range(board_size)]


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


def get_queue():
    """ get queue of empty cells to run in the recursion.
     the more numbers in an empty cell row, column and block, the higher priority it will have."""
    temp_queue = []
    for i in range(board_size):
        for j in range(board_size):
            if board.cells[i][j].get_value() == 0:
                # get a set of values in the row, column and block
                row, col = get_cross(i, j)
                block = get_block(i, j)

                # get total number of values around the cell and append its index and number of values around it
                num_of_clues = len(row) + len(col) + len(block)
                temp_queue.append(((i, j), num_of_clues))

    # sort the lists from most values around empty cell to lowest
    temp_queue.sort(key=lambda que: que[1], reverse=True)
    return temp_queue


# initial set up
run = True                                      # while loop condition
is_solved = False                               # end message flag

pg.init()                                       # initialize pygame
screen = pg.display.set_mode(screen_size)       # create window of given size

if pg.image.get_extended():                     # insert window icon
    icon = pg.image.load('Sprites/icon.png')
    icon.convert()
    pg.display.set_icon(icon)

pg.display.set_caption("Sudoku Solver")         # insert window title

board = Grid(board_size, board_size)            # create the board
cell_width = screen_size[0] / 9
cell_height = cell_width
refresh_screen()
queue = get_queue()                             # get order of cells to scan through in the recursion
while run:
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN and pressed_solve(event.pos):   # pressed "solve" button in window
            if solve(0):                                                    # solve sudoku
                is_solved = True
                run = False
            else:
                run = False

        if event.type == pg.QUIT:                                           # exited window
            pg.display.quit()
            pg.quit()
            exit()
        refresh_screen()

# (x, y) coordinates to print end message in
y = ((screen_size[1] - screen_size[0]) / 3) + screen_size[0]
y = y - ((y - screen_size[0]) // 2)
x = screen_size[0] / 3 + 1

# define text size
font = pg.font.Font(None, 35)

# print final message
if is_solved:
    text = font.render('Sudoku solved!', True, green)
    screen.blit(text, (x, y))
else:
    text = font.render('There is no Solution!', True, red)
    screen.blit(text, ((x-35), y))
    
pg.display.update()
time.sleep(3)
pg.display.quit()
pg.quit()
exit()

