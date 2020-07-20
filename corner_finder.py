from point_finder import PointsFinder
import numpy as np


class CornerFinder:
    BORDER_LINE_THRESHOLD = 70

    def __init__(self):
        self.middle_lines_ids = list()
        self.border_lines_ids = list()
        self.lines = list()

    def estimate_corners(self, lines_with_points):
        self.lines = lines_with_points
        self.middle_lines_ids = self.extract_middle_lines(lines_with_points)
        self.border_lines_ids = self.extract_border_lines(lines_with_points, self.middle_lines_ids)
        corners = self.pick_best_corners()
        sorted_corners = self.sort_points(corners)
        return sorted_corners

    @staticmethod
    def extract_middle_lines(lines):
        lines_ids = list()
        for i in range(len(lines)):
            if CornerFinder.is_middle_line(lines[i]):
                lines_ids.append(i)
        return lines_ids

    @staticmethod
    def is_middle_line(line):
        counts = 0
        for _, t, _ in line:
            if t == PointsFinder.INTERSECTION_T:
                if counts == 0:
                    counts = 1
                elif counts > 6:
                    return True
                elif counts < 3:
                    counts = 1
            elif t == PointsFinder.INTERSECTION_CROSS and counts > 0:
                counts += 1

        return False

    @staticmethod
    def extract_border_lines(lines, middle_lines):
        lines_ids = list()
        for i in range(len(lines)):
            if i in middle_lines:
                continue
            score = CornerFinder.calculate_border_line_score(lines[i], middle_lines)
            if score > CornerFinder.BORDER_LINE_THRESHOLD:
                lines_ids.append(i)
        return lines_ids

    @staticmethod
    def calculate_border_line_score(line, middle_lines):
        counts = 0
        errors = 0
        line_id = -1
        for _, t, line_cross in line:
            line_id += 1
            if t == PointsFinder.INTERSECTION_CORNER:
                if counts == 0:
                    counts = 1
                elif counts > 5:
                    return 100 - errors
                elif counts < 3 and line_cross not in middle_lines:
                    counts = 1
            elif t == PointsFinder.INTERSECTION_T:
                if line_cross not in middle_lines:
                    if counts == 0:
                        counts = 1
                    elif counts > 5:
                        return 100 - errors
                    else:
                        errors += 1
                if line_cross in middle_lines and counts > 0:
                    counts += 1
            elif line_cross in middle_lines and counts > 0:
                counts += 1
                errors += 3

        return 0

    def pick_best_corners(self):
        if len(self.border_lines_ids) < 4:
            return None
        if len(self.middle_lines_ids) < 10:
            return None

        for line_id in self.border_lines_ids:
            start, end = self.find_two_corners_on_line(self.lines[line_id])
            if start is None or start[1] == end[1]:
                continue
            another_points = self.find_neighbours_corners(start, end)
            if another_points is None:
                continue
            return [start[0], end[0], another_points[0], another_points[1]]

    def find_two_corners_on_line(self, line):
        start = None
        count = 0
        for ps, _, line_index in line:
            if line_index in self.border_lines_ids:
                if start is None or count < 3:
                    start = ps, line_index
                elif count > 5:
                    return start, (ps, line_index)
            elif line_index in self.middle_lines_ids and count is not None:
                count += 1
            else:
                count -= 1
        return None, None

    def find_neighbours_corners(self, point1, point2):
        first_line = self.lines[point1[1]]
        second_line = self.lines[point2[1]]

        first_points = self.find_cross_point_with_another_border_line(point1[0], first_line, False) + \
                       self.find_cross_point_with_another_border_line(point1[0], first_line, True)
        second_points = self.find_cross_point_with_another_border_line(point2[0], second_line, False) + \
                       self.find_cross_point_with_another_border_line(point2[0], second_line, True)

        # first_points[0] = self.find_cross_point_with_another_border_line(point1[0], first_line, True)
        # first_points[1] = self.find_cross_point_with_another_border_line(point1[0], first_line, False)
        # second_points = [None, None]
        # second_points[0] = self.find_cross_point_with_another_border_line(point2[0], second_line, True)
        # second_points[1] = self.find_cross_point_with_another_border_line(point2[0], second_line, False)

        for first in first_points:
            if first is None:
                continue
            for second in second_points:
                if second is None:
                    continue
                if first[1] == second [1]:
                    return first_line[first[0]][0], second_line[second[0]][0]

        return None

    def find_cross_point_with_another_border_line(self, point, line, up):
        point_index = self.find_index_of_point(line, point)
        if up:
            return self.find_cross_point_with_another_border_line_helper(line, point_index + 1, len(line), 1)
        else:
            return self.find_cross_point_with_another_border_line_helper(line, point_index - 1, -1, -1)

    def find_cross_point_with_another_border_line_helper(self, line, start, end, inc):
        cross_points = list()
        count = 0
        for i in range(start, end, inc):
            _, _, line_id = line[i]
            if line_id in self.border_lines_ids:
                if count < 5:
                    continue
                cross_points.append((i, line_id))
            else:
                count += 1
        return cross_points

    @staticmethod
    def sort_points(points):
        if points is None:
            return None
        roi = np.zeros((4, 2), dtype="float32")
        points.sort(key=(lambda p: p[0] ** 2 + p[1] ** 2))
        roi[0] = points[0]
        roi[2] = points[3]
        points.pop(-1)
        points.pop(0)
        points.sort(key=(lambda p: p[1] ** 2))
        roi[1] = points[0]
        roi[3] = points[1]
        return roi

    @staticmethod
    def find_index_of_point(line, point):
        for i in range(len(line)):
            p, _, _ = line[i]
            if p == point:
                return i
        return -1

    def get_middle_lines_ids(self):
        return self.middle_lines_ids

    def get_border_lines_ids(self):
        return self.border_lines_ids
