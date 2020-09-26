from selenium import webdriver
from pyautogui import screenshot
import pytesseract as tess
import numpy as np
import cv2
from time import sleep

NUMBER_OF_SOLUTIONS = 2            # amount of boards solved automatically. loop iteration value
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
board_size = 9


class Grid:
    def __init__(self, rows=9, cols=9, width=500, height=500):
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


def filter_clues(possible_values, i, j):
    """ remove values in possible_values that already exist on the board """
    block = get_block(i, j)
    row, col = get_cross(i, j)
    unwanted = block.union(block, row, col)
    possible_values.difference_update(unwanted)


def find_empty(queue_ind):
    i = queue[queue_ind][0][0]
    j = queue[queue_ind][0][1]
    return i, j


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


def process_image():
    """ handles the core OCR processing of the image """
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    # draw lines
    for x_pos in range(0, 297, 33):
        cv2.line(gray_image, (x_pos, 0), (x_pos, 296), BLACK, 3)
    for y_pos in range(0, 297, 33):
        cv2.line(gray_image, (0, y_pos), (296, y_pos), BLACK, 3)

    # apply threshold to make image binary
    ret, final = cv2.threshold(gray_image, 254, 255, cv2.THRESH_BINARY)
    return final


def extract_clues_from_image():
    # get contours of image
    contours, hierarchy = cv2.findContours(processed, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
    list_of_clues = []

    for contour in contours:
        extracted_value = ''

        # create black mask
        mask = np.zeros(processed.shape, dtype=np.uint8)

        # check if contour is a cell
        area = cv2.contourArea(contour)
        if 700 <= area <= 1000:  # contour is a cell
            cv2.drawContours(mask, [contour], -1, WHITE, -1)  # color everything in mask, but the contour- white
            isolated_cell = cv2.bitwise_and(processed, mask)
            isolated_cell[mask == 0] = 255  # invert isolated_cell's mask to WHITE (for tess)

            # extract text from isolated_cell
            text = tess.image_to_string(isolated_cell, config='--psm 10')

            # clean non-numbers:
            for ch in text:
                if ch.isdigit():
                    extracted_value = ch

            # calculate cell coordinates only if extracted_value exist
            if extracted_value:
                [x_pos, y_pos, wid, hei] = cv2.boundingRect(contour)    # get contour's sizes
                x_coord = int(y_pos // (grid_size_pixels / 9))  # get x row-coordinate
                y_coord = int(x_pos // (grid_size_pixels / 9))          # get y col-coordinate
                list_of_clues.append(((x_coord, y_coord), int(extracted_value)))
        else:   # contour isn't a cell
            continue

    if list_of_clues:
        return list_of_clues
    else:
        print("ERROR extracting clues from image")


def extract_answers_from_grid():
    extracted_answers = []
    clues_coordinates = [clue[0] for clue in clues]

    for x in range(board_size):
        for y in range(board_size):
            if not (x, y) in clues_coordinates:
                extracted_answers.append(board.cells[y][x].get_value())
    return extracted_answers


def fill_board():
    for clue in clues:
        board.cells[clue[0][1]][clue[0][0]].set_value(clue[1])


if __name__ == '__main__':
    # using selenium to open the website
    url = 'https://nine.websudoku.com/'
    driver = webdriver.Firefox()
    driver.get(url)

    for _ in range(NUMBER_OF_SOLUTIONS):
        sleep(3)
        # using pyautogui to capture screen, and crop it to get only the sudoku board
        grid_size_pixels = 297                                                                  # grid is always a box, thus size = width = height
        screen_captured = screenshot(region=(644, 443, grid_size_pixels, grid_size_pixels))     # DO NOT MOVE OPENED WINDOW! it is hardcoded to specific place on screen

        if screen_captured:
            screen_captured.save('sudoku_board.png')                                # save cropped image
            original_image = cv2.imread('sudoku_board.png', cv2.IMREAD_COLOR)       # open image in cv
            processed = process_image()                                             # pre-process image

            # get clues from image
            clues = extract_clues_from_image()

            # initialize grid object
            board = Grid()

            # fill board with extracted_values
            fill_board()

            print('Board fetched:')
            print_board()

            print('Solving...')
            queue = get_queue()
            if solve(0):
                print('Solved board:')
                print_board()

                # get list of answers entered after solving board
                answers = extract_answers_from_grid()

                # get all elements of empty cells in web
                empty_cells = driver.find_elements_by_xpath("//input[@class='d0']")

                # for each empty cell, insert its correct answer gathered after solving board
                for index, cell in enumerate(empty_cells):
                    cell.send_keys(answers[index])

                # get confirm button element and click it
                confirm = driver.find_element_by_xpath("//input[@name='submit']")
                confirm.click()
                sleep(1)

                # get next puzzle button element and click it
                next_puzzle = driver.find_element_by_xpath("//input[@name='newgame']")
                next_puzzle.click()

            else:
                print('NO SOLUTION!')

        else:
            print('ERROR capturing screen')
