import numpy as np
import cv2


class LineDetector:
    MAX_THETA_DIFFERENCE = np.pi / 14.0
    MAX_RHO_DIFFERENCE = 9

    @staticmethod
    def combine_lines(line, merge_to_index, merged_lines, lines_count):
        number_of_line_merged = lines_count[merge_to_index]
        merged_lines[merge_to_index][0][0] = (merged_lines[merge_to_index][0][0] * number_of_line_merged
                                              + line[0][0]) / (number_of_line_merged + 1)
        merged_lines[merge_to_index][0][1] = (merged_lines[merge_to_index][0][1] * number_of_line_merged
                                              + line[0][1]) / (number_of_line_merged + 1)
        lines_count[merge_to_index] += 1

    @staticmethod
    def is_line_same(line1, line2):
        rho1 = line1[0][0]
        theta1 = line1[0][1]
        rho2 = line2[0][0]
        theta2 = line2[0][1]
        return abs(rho1 - rho2) < LineDetector.MAX_RHO_DIFFERENCE and\
            abs(theta1 - theta2) < LineDetector.MAX_THETA_DIFFERENCE

    @staticmethod
    def merge_similar_lines(lines):
        merged_lines = list()
        lines_count = list()
        for line in lines:
            need_to_be_added = True
            for i in range(len(merged_lines)):
                if LineDetector.is_line_same(line, merged_lines[i]):
                    need_to_be_added = False
                    LineDetector.combine_lines(line, i, merged_lines, lines_count)
                    break
            if need_to_be_added:
                merged_lines.append(line)
                lines_count.append(1)

        return merged_lines

    def find_lines(self, thresh_image):
        lines = cv2.HoughLines(thresh_image, 1, np.pi / 180, 200, None, 0, 0)
        if lines is None:
            return None
        lines = self.merge_similar_lines(lines)
        return lines


