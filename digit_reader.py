import cv2
import numpy as np
from matplotlib import pyplot as plt
import tensorflow as tf

class DigitReader:

    IMG_SIZE = 34

    def __init__(self):
        self.model = tf.keras.models.load_model('tf-digits-model')
        self.input = list()
        self.coords = list()

    def read_numbers(self, warp):
        crop_size = (self.IMG_SIZE, self.IMG_SIZE)
        table = list()
        self.input = list()
        self.coords = list()
        for i in range(9):
            row = list()
            for j in range(9):
                crop = warp[int(crop_size[1] * i): int(crop_size[1] * (i + 1)),
                            int(crop_size[1] * j): int(crop_size[1] * (j + 1))]
                row.append(self.read_field(crop, i, j))
            table.append(row)

        predictions = self.model.predict(np.asarray(self.input))
        index = 0
        for r, c in self.coords:
            table[r][c] = np.argmax(predictions[index])
            index += 1

        return table

    def read_field(self, crop, r, c):
        filter_img = self.filter_borders(crop)
        filter_img = self.cut_img_padding(filter_img)
        filter_img = cv2.threshold(filter_img, 70, 255, cv2.THRESH_TOZERO)[1]
        if np.sum(filter_img) / (len(crop)**2) < 10:
            return 0
        #plt.imshow(filter_img, 'gray')
        #plt.show()

        self.input.append(filter_img * 1.0 / 255)
        self.coords.append((r, c))
        return 0

    @staticmethod
    def cut_img_padding(crop):
        return cv2.resize(crop[4:30, 4:30], (28, 28))

    def filter_borders(self, crop):
        crop = 255 - crop
        num_labels, labels_im, _, centroids = cv2.connectedComponentsWithStats(crop, 4)
        filter_img = np.zeros_like(crop)
        number_label = self.find_center_label(labels_im)
        if number_label == -1:
            return filter_img

        filter_img[labels_im == number_label] = 1
        filter_img = crop * filter_img
        center = centroids[number_label]
        return self.center_pic(filter_img, center)

    @staticmethod
    def find_center_label(label_img):
        for i in range(12, 24):
            for j in range(12, 24):
                if label_img[i, j] != 0:
                    return label_img[i, j]
        return -1

    @staticmethod
    def center_pic(img, center):
        cols, rows = img.shape
        ny = center[1] - rows / 2
        nx = center[0] - cols / 2
        M = np.float32([[1, 0, -nx], [0, 1, -ny]])
        return cv2.warpAffine(img, M, (cols, rows))







