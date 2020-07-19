import numpy as np


class PointsFinder:

    INTERSECTION_CORNER = 2
    INTERSECTION_T = 3
    INTERSECTION_CROSS = 4

    def __init__(self, thresh, lines):
        self.lines = lines
        self.thresh = thresh
        self.points = list()
        self.lines_with_points = list()
        for _ in lines:
            self.lines_with_points.append(list())
        self.width, self.height = thresh.shape

        self.find_all_intersections( lines, thresh)
        self.sort_points_in_all_lines()

    def get_points(self):
        return self.points

    def get_lines_with_points(self):
        return self.lines_with_points

    @staticmethod
    def is_line_horizontal(line):
        theta = line[0][1]
        return np.pi / 4 < theta < np.pi / 4.0 * 3

    def sort_points_in_all_lines(self):
        for i in range(len(self.lines_with_points)):
            self.sort_points_in_line(i)

    def sort_points_in_line(self, line_index):
        if self.is_line_horizontal(self.lines[line_index]):
            self.lines_with_points[line_index].sort(key=(lambda p: p[0][0] ** 2))
        else:
            self.lines_with_points[line_index].sort(key=(lambda p: p[0][1] ** 2))

    def add_point(self, pos, p_type, line_index, line2_index):
        self.lines_with_points[line_index].append((pos, p_type, line2_index))
        self.lines_with_points[line2_index].append((pos, p_type, line_index))
        self.points.append((pos, p_type, line_index, line2_index))

    def find_all_intersections(self, lines, img):
        for i in range(len(lines)):
            rho, theta = lines[i][0]
            a, b, c, x0, y0 = self.get_line_paramaters(theta, rho)
            for j in range(i + 1, len(lines), 1):
                if i == j:
                    continue
                rho2, theta2 = lines[j][0]
                d, e, f, x1, y1 = self.get_line_paramaters(theta2, rho2)
                p = self.find_intersection(a, b, c, d, e, f)
                if p is None:
                    continue

                if p[0] < 0 or p[0] >= self.height:
                    continue
                if p[1] < 0 or p[1] >= self.width:
                    continue
                t = self.get_type_of_intersection(p, (a, b, c), (d, e, f), img)
                if t is None:
                    continue
                self.add_point(p, t, i, j)

    @staticmethod
    def get_line_paramaters(theta, rho):
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        c = -(x0 * a + y0 * b)
        return a, b, c, x0, y0

    @staticmethod
    def norm_vector(a, b):
        nx = -b
        ny = a
        dist = np.sqrt(a * a + b * b)
        return nx / dist, ny / dist

    @staticmethod
    def is_point_white(img, mx, my):
        mx = int(mx)
        my = int(my)
        if my >= img.shape[0] or my < 0 or mx >= img.shape[1] or mx < 0 \
                or img[my, mx] < 50:
            return False
        return True

    @staticmethod
    def checkpoint(img, space, x, y, na, nb, mul):
        mx = int(x + mul * na * space)
        my = int(y + mul * nb * space)
        if PointsFinder.is_point_white(img, mx, my):
            return True
        elif PointsFinder.check_point_surroundings(img, mx, my, 1):
            return True
        return PointsFinder.check_point_surroundings(img, mx, my, 2)

    @staticmethod
    def get_number_of_line_crossing(img, x, y, a, b):
        space = 8
        line_inter = 0
        na, nb = PointsFinder.norm_vector(a, b)
        if PointsFinder.checkpoint(img, space, x, y, na, nb, 1):
            line_inter += 1
        if PointsFinder.checkpoint(img, space, x, y, na, nb, -1):
            line_inter += 1
        return line_inter

    def check_point_surroundings(img, x, y, r):
        angle = 0
        while angle < 2 * np.pi:
            mx = int(np.cos(angle) * r)
            my = int(np.sin(angle) * r)
            if PointsFinder.is_point_white(img, x + mx, y + my):
                return True
            angle += np.pi / 2
        return False

    @staticmethod
    def is_point_or_surrounding_white(img, x, y):
        if PointsFinder.is_point_white(img, x, y):
            return True
        if PointsFinder.check_point_surroundings(img, x, y, 1):
            return True
        if PointsFinder.check_point_surroundings(img, x, y, 3):
            return True
        return False

    @staticmethod
    def get_type_of_intersection(pos, line1, line2, img):
        x, y = pos
        a, b, c = line1
        d, e, f = line2
        if not PointsFinder.is_point_or_surrounding_white(img, x, y):
            return None
        n = PointsFinder.get_number_of_line_crossing(img, x, y, a, b)
        m = PointsFinder.get_number_of_line_crossing(img, x, y, d, e)
        if (n == 2 and m == 0) or (n == 0 and m == 2):
            return None
        if n == 2 and m == 2:
            return PointsFinder.INTERSECTION_CROSS
        elif n == 1 and m == 1:
            return PointsFinder.INTERSECTION_CORNER
        return PointsFinder.INTERSECTION_T

    @staticmethod
    def find_intersection(a, b, c, d, e, f):
        """
        lines are in this format
        ax + by + c = 0
        dx + ey + f = 0
        """
        if d == 0 and a != 0:
            y = -f / e
            x = (-b * y - c) / a
            return int(x), int(y)

        if d != 0 and a == 0:
            y = -c / b
            x = (-e * y - f) / d
            return int(x), int(y)

        if d == 0 and a == 0:
            return None

        if b == 0 and e != 0:
            x = - c / a
            y = (-d * x - f) / e
            return int(x), int(y)
        if e == 0 and b != 0:
            x = - f / d
            y = (-a * x - c) / b
            return int(x), int(y)
        if e == 0 and b == 0:
            return None
        if abs(d) < 0.1 or abs(a) < 0.1:
            cc = (a - (b * d) / e)
            if cc == 0:
                # liens are parallel
                return None
            x = (b * f / e - c) / cc
            y = (-d * x - f) / e
            return int(x), int(y)
        else:
            cc = (b - a * e / d)
            if cc == 0:
                return None
            y = (a * f / d - c) / cc
            x = (-b * y - c) / a
        return int(x), int(y)
