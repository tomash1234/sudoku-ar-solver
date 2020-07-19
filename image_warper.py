import cv2
import numpy as np


class ImageWarper:
    WARP_PIC_SIZE = 306

    def __init__(self):
        self.points = None
        self.dst = None

    def warp(self, image, points):
        self.points = points
        dst = np.array([
            [0, 0],
            [self.WARP_PIC_SIZE - 1, 0],
            [self.WARP_PIC_SIZE - 1, self.WARP_PIC_SIZE - 1],
            [0, self.WARP_PIC_SIZE - 1]], dtype="float32")
        self.dst = dst

        M = cv2.getPerspectiveTransform(points, dst)
        warp = cv2.warpPerspective(image, M, (self.WARP_PIC_SIZE, self.WARP_PIC_SIZE))
        return warp

    def unwarp(self, image, orig_shape):
        M = cv2.getPerspectiveTransform(self.dst, self.points)
        width, height, d = orig_shape
        warp = cv2.warpPerspective(image, M, (height, width))
        return warp

    def draw_warp_to_original(self, img_result, original):
        img_numbers = self.unwarp(img_result, original.shape)
        return self.merge_pics(original, img_numbers)

    @staticmethod
    def merge_pics(orig_image, numbers):
        ret, warp = cv2.threshold(numbers, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(warp)
        img1_bg = cv2.bitwise_and(orig_image, orig_image, mask=mask_inv)

        fg = cv2.cvtColor(numbers, cv2.COLOR_GRAY2BGR)
        fg[numbers > 0] = (255, 55, 0)
        dst = cv2.add(img1_bg, fg)
        return dst

    def write_number_to_image(self, image, table, new_table):
        img_with_numbers = np.zeros((image.shape[1], image.shape[0]), np.uint8)
        im = cv2.cvtColor(image,cv2.COLOR_GRAY2RGB)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cell_size = int(self.WARP_PIC_SIZE / 9)
        for i in range(len(table)):
            for j in range(len(table[i])):
                if new_table[i][j] != 0 and table[i][j] == 0:
                    cv2.putText(img_with_numbers, str(new_table[i][j]), (cell_size*j + 8, cell_size*(i+1)-8), font, 0.8, 255, 1, cv2.LINE_AA)
                    cv2.putText(im, str(new_table[i][j]), (cell_size*j + 8, cell_size*(i+1)-8), font, 0.8, (128, 0, 255), 2, cv2.LINE_AA)

        cv2.imshow('nums', im)
        return img_with_numbers
