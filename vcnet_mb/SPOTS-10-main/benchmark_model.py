import tensorflow as tf
from tensorflow.keras import layers, applications, models
import numpy as np
from utilities.distiller import Distiller
from utilities.spots_10_loader import SPOT10Loader

class TeacherStudentModels:
    @staticmethod
    def create_teacher_model(model_name="MobileNet", input_shape=(32, 32, 3), num_classes=10):
        base_model = getattr(applications, model_name)(
            weights="imagenet",
            include_top=False,
            input_shape=input_shape
        )

        teacher = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(num_classes)
        ])

        return teacher

    @staticmethod
    def create_student_model(input_shape=(32, 32, 3), num_classes=10):
        student = models.Sequential([
            layers.Input(shape=input_shape),
            layers.Conv2D(32, (3, 3), strides=(2, 2), padding="same"),
            layers.LeakyReLU(alpha=0.2),
            layers.MaxPooling2D(pool_size=(2, 2), strides=(1, 1), padding="same"),

            layers.Conv2D(64, (3, 3), strides=(2, 2), padding="same"),
            layers.LeakyReLU(alpha=0.2),
            layers.MaxPooling2D(pool_size=(2, 2), strides=(1, 1), padding="same"),

            layers.Conv2D(64, (3, 3), strides=(2, 2), padding="same"),
            layers.Flatten(),
            layers.Dense(num_classes),
        ], name="student")

        return student

    @staticmethod
    def load_data(dataset_dir="dataset", kind="train", input_shape=(32, 32, 3)):
        x_data, y_label = SPOT10Loader.get_data(dataset_dir=dataset_dir, kind=kind)

        x_data = x_data.astype('float32') / 255.0
        x_data = np.expand_dims(x_data, axis=-1)
        y_label = np.expand_dims(y_label, axis=-1)
        x_data = np.repeat(x_data, 3, axis=-1)

        return x_data, y_label

def main():
    teacher = TeacherStudentModels.create_teacher_model()
    student = TeacherStudentModels.create_student_model()

    x_train, y_train = TeacherStudentModels.load_data(dataset_dir="dataset", kind="train", input_shape=(32, 32, 3))
    x_test, y_test = TeacherStudentModels.load_data(dataset_dir="dataset", kind="test", input_shape=(32, 32, 3))

    distiller = Distiller(student=student, teacher=teacher)
    distiller.compile(
        optimizer=tf.keras.optimizers.Adam(),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy()],
        student_loss_fn=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        distillation_loss_fn=tf.keras.losses.KLDivergence(),
        alpha=0.1,
        temperature=10,
    )

    distiller.fit(x_train, y_train, epochs=3)
    distiller.evaluate(x_test, y_test)

if __name__ == "__main__":
    main()
