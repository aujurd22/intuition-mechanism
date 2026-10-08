import gzip
import numpy as np
import struct
import os
from array import array

class SPOT10Loader:
    def __init__(self):
        pass

    @staticmethod
    def get_data(dataset_dir, kind='train'):
        """Load custom MNIST data from `path`"""
        labels_path = os.path.join(dataset_dir, f'{kind}-labels-idx1-ubyte.gz')
        images_path = os.path.join(dataset_dir, f'{kind}-images-idx3-ubyte.gz')

        with gzip.open(labels_path, 'rb') as file:
            magic, size = struct.unpack(">II", file.read(8))
            if magic != 2049:
                raise ValueError('Magic number mismatch, expected 2049, got {}'.format(magic))
            labels = array("B", file.read())

        with gzip.open(images_path, 'rb') as file:
            magic, size, rows, cols = struct.unpack(">IIII", file.read(16))
            if magic != 2051:
                raise ValueError('Magic number mismatch, expected 2051, got {}'.format(magic))
            image_data = array("B", file.read())

        images = np.zeros((size, rows, cols), dtype=np.uint8)
        for i in range(size):
            images[i] = np.array(image_data[i * rows * cols:(i + 1) * rows * cols]).reshape(rows, cols)

        return np.array(images), np.array(labels)


# Example implementation
if __name__ == "__main__":
    data_loader = SPOT10Loader()
    images, labels = data_loader.get_data(dataset_dir="../dataset", kind='train')
    print(images.shape, labels.shape)
    print(np.unique(labels, return_counts=True))
    print("\n")
    images, labels = data_loader.get_data(dataset_dir="../dataset", kind='test')
    print(images.shape, labels.shape)
    print(np.unique(labels, return_counts=True))

