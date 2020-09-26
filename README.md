# Sudoku
a few different approaches to solving sudoku using different modules


1. Sudoku_solver_pygame:
solved a hardcoded sudoku game using pygame module to visualize the recursion process.

2. Sudoku_solver_BeautifulSoup:
used BeautifulSoup4 module to extract, parse and solve sudoku boards from a website

3. Sudoku_solver_automation:
used multiple modules to automate solving sudoku boards in a website:
* used Selenium module to open a website, and after solving the board, to confirm solved board and move to the next one.
* used pyautogui module to take a screenshot of the website and crop only the sudoku board
* used cv2 (python-openCV) module to pre-process the screenshot, recognize and mark numbers in the image.
* used pytesseract (OCR engine) module to extract marked numbers from the image into a string.

then, a Grid and Cells objects are declared and initialized, and the program solves the sudoku recursively, fill the board on the website,
and move to the next board by navigating the site automatically
