import os
import numpy as np
from PIL import Image
import gzip
import struct


class UbyteImageProcessor:
    def __init__(self, base_folder, class_descriptions, image_size=(32, 32)):
        self.base_folder = base_folder
        self.class_descriptions = class_descriptions
        self.image_size = image_size

    def load_images_from_folders(self):
        images = []
        labels = []
        for label, class_name in enumerate(self.class_descriptions):
            folder_path = os.path.join(self.base_folder, class_name)
            print("Processing class: ", class_name)
            if not os.path.exists(folder_path):
                continue
            for filename in os.listdir(folder_path):
                if filename.endswith(".png"):
                    img = Image.open(os.path.join(folder_path, filename)).convert('L')  # Convert image to grayscale
                    img = img.resize(self.image_size)  # Resize image to 32x32 pixels
                    img_np = np.array(img, dtype=np.uint8)
                    images.append(img_np)
                    labels.append(label)
        return np.array(images), np.array(labels)

    def save_idx_images(self, filepath, images):
        if not isinstance(images, (np.ndarray, list)):
            raise TypeError('Unsupported data type.')

        # Ensure images is a numpy array
        images = np.array(images)

        # Ensure the images array has the right shape
        if images.ndim != 3:
            raise ValueError('Images array must be 3-dimensional.')

        magic_number = 2051
        num_images = images.shape[0]
        rows = images.shape[1]
        cols = images.shape[2]

        header = struct.pack(">IIII", magic_number, num_images, rows, cols)

        data_list = [header]
        for image in images:
            data_list.append(struct.pack('>' + 'B' * rows * cols, *image.flatten()))

        data = b''.join(data_list)

        with gzip.open(filepath, 'wb') as f:
            f.write(data)

    def save_idx_labels(self, filepath, labels):
        if not isinstance(labels, (np.ndarray, list)):
            raise TypeError('Unsupported label type.')

        # Ensure labels is a numpy array
        labels = np.array(labels)

        # Ensure the labels array has the right shape
        if labels.ndim != 1:
            raise ValueError('Labels array must be 1-dimensional.')

        magic_number = 2049
        num_labels = len(labels)

        data = struct.pack(">II", magic_number, num_labels)

        data += struct.pack('>' + 'B' * num_labels, *labels)

        with gzip.open(filepath, 'wb') as f:
            f.write(data)


# Example implementation
if __name__ == "__main__":
    class_descriptions = [
        "cheetah", "deer", "giraffe", "hyena", "jaguar",
        "leopard", "tapir", "tiger", "WhaleShark", "zebra"
    ]

    # Instantiate the processor for training and testing data
    train_processor = UbyteImageProcessor('../dataset/train', class_descriptions, image_size=(32,32))
    test_processor = UbyteImageProcessor('../dataset/test', class_descriptions, image_size=(32,32))

    # Load images and labels
    train_images, train_labels = train_processor.load_images_from_folders()
    test_images, test_labels = test_processor.load_images_from_folders()

    print(test_images.shape, test_labels.shape)
    print(train_images.shape, train_labels.shape)

    # Save images and labels in IDX format
    train_processor.save_idx_images('../dataset/train-images-idx3-ubyte.gz', train_images)
    train_processor.save_idx_labels('../dataset/train-labels-idx1-ubyte.gz', train_labels)

    test_processor.save_idx_images('../dataset/test-images-idx3-ubyte.gz', test_images)
    test_processor.save_idx_labels('../dataset/test-labels-idx1-ubyte.gz', test_labels)
