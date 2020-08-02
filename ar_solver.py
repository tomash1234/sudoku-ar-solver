from grid_detector import GridDetector
from image_warper import ImageWarper
from sudoku_solver import SudokuSolver
from digit_reader import DigitReader
import cv2
import copy
import numpy as np


class SudokuArSolver:

    MAX_IMG_SIZE = 400

    def __init__(self):
        self.grid_detector = GridDetector()
        self.warper = ImageWarper()
        self.sudoku_solver = SudokuSolver(9)
        self.digit_reader = DigitReader()

    def solve(self, image):
        image = self.scale_too_big_image(image)
        grid_corners = self.grid_detector.find_grid(image, show_img=True)
        if grid_corners is None:
            return image
        warp = self.warper.warp(self.grid_detector.thresh_image, grid_corners)
        table = self.digit_reader.read_numbers(warp)
        self.sudoku_solver.print_grid(table)
        solved_table = self.sudoku_solver.solve(copy.deepcopy(table))
        image_with_numbers = self.warper.write_number_to_image(warp, table, solved_table)
        res = self.warper.draw_warp_to_original(image_with_numbers, image)
        return res

    @staticmethod
    def scale_too_big_image(image):
        mx_size = np.max(image.shape)
        if mx_size > SudokuArSolver.MAX_IMG_SIZE:
            scale = mx_size / SudokuArSolver.MAX_IMG_SIZE
            return cv2.resize(image, (int(image.shape[1] / scale), int(image.shape[0] / scale)))
        return image

    def load_pic(self, path):
        image = cv2.imread(path)
        res = self.solve(image)

        cv2.imshow('frame', res)
        cv2.waitKey()

    def start_camera(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()

            # frame = frame[60:-60, 60:-60]
            frame = frame[60:60 + 360, 180:180 + 360]

            res = self.solve(frame)
            cv2.imshow('Video', res)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    solver = SudokuArSolver()
    solver.load_pic('test_img/6.jpg')
    #solver.start_camera()
