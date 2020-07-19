import numpy as np
import cv2
from line_detector import LineDetector
from point_finder import PointsFinder
from corner_finder import CornerFinder


class GridDetector:

    def __init__(self):
        self.line_detector = LineDetector()
        self.thresh_image = None

    def find_grid(self, image, show_img=True):
        self.thresh_image = self.preprocess_image(image)
        filtered_image = self.filter_small_contours(self.thresh_image)

        lines = self.line_detector.find_lines(filtered_image)
        if lines is None:
            return None

        points_finder = PointsFinder(filtered_image, lines)
        points = points_finder.get_points()
        lines_with_points = points_finder.get_lines_with_points()

        corner_finder = CornerFinder()
        final_corners = corner_finder.estimate_corners(lines_with_points)

        if show_img:
            colored_image = self.draw_image(filtered_image, lines, points, corner_finder.get_middle_lines_ids(),
                                            corner_finder.get_border_lines_ids())
            cv2.imshow('Line & points', colored_image)

        return final_corners

    def draw_image(self, thresh, lines, points, middle_lines, border_lines):
        colored_image = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        self.draw_lines(colored_image, lines, middle_lines, border_lines)
        self.draw_points(colored_image, points)

        return colored_image

    @staticmethod
    def preprocess_image(raw_image):
        gray = cv2.cvtColor(raw_image, cv2.COLOR_BGR2GRAY)
        return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 57, 5)

    @staticmethod
    def filter_small_contours(thresh):
        thresh = np.copy(thresh)
        cnts = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            area = cv2.contourArea(c)
            if area < 1500:
                cv2.drawContours(thresh, [c], -1, 255, -1)

        return 255 - thresh

    @staticmethod
    def draw_lines(colored_image, lines, middle_lines_id, border_lines_id):
        line_id = 0
        for line in lines:
            rho = line[0][0]
            theta = line[0][1]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * a))
            pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * a))
            if line_id in middle_lines_id:
                cv2.line(colored_image, pt1, pt2, (255, 0, 255), 1, cv2.LINE_AA)
            elif line_id in border_lines_id:
                cv2.line(colored_image, pt1, pt2, (0, 255, 0), 1, cv2.LINE_AA)
            else:
                cv2.line(colored_image, pt1, pt2, (0, 0, 255), 1, cv2.LINE_AA)
            line_id += 1

    @staticmethod
    def draw_points(img, points):
        for ps, t, l1, l2 in points:
            color = (0, 255, 0)
            if t == PointsFinder.INTERSECTION_CORNER:
                color = (0, 255, 255)
            elif t == PointsFinder.INTERSECTION_CROSS:
                color = (255, 0, 255)

            cv2.circle(img, ps, 5, color, 2)

