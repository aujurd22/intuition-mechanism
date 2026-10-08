import os
import pandas as pd
import tensorflow as tf
from tensorflow.keras.layers import Conv2D, Dense, Dropout, GlobalAveragePooling2D, Input
from tensorflow.keras import applications
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from utilities.spots_10_loader import SPOT10Loader

class ModelTrainer:
    def __init__(self, benchmark_models, dataset_dir="dataset"):
        self.benchmark_models = benchmark_models
        self.dataset_dir = dataset_dir
        self.csv_file = 'test_accuracy.csv'
        self.columns = ['model_name', 'accuracy', 'loss']
        self.df = pd.DataFrame(columns=self.columns)

    def build_model(self, model_name=None, num_classes=10, weights=None, input_shape=(32, 32, 1)):
        input_layer = Input(shape=input_shape)
        x = Conv2D(3, (1, 1), padding='same')(input_layer)

        base_model = None

        if model_name == "ResNet50":
            base_model = applications.ResNet50(input_shape=(x.shape[1], x.shape[2], x.shape[3]), include_top=False, weights=weights)
        elif model_name == "MobileNet":
            base_model = applications.MobileNet(input_shape=(x.shape[1], x.shape[2], x.shape[3]), include_top=False, weights=weights)
        elif model_name == "MobileNetV2":
            base_model = applications.MobileNetV2(input_shape=(x.shape[1], x.shape[2], x.shape[3]), include_top=False, weights=weights)
        elif model_name == "DenseNet121":
            base_model = applications.DenseNet121(input_shape=(x.shape[1], x.shape[2], x.shape[3]), include_top=False, weights=weights)
        elif model_name == "NASNetMobile":
            base_model = applications.NASNetMobile(input_shape=(x.shape[1], x.shape[2], x.shape[3]), include_top=False, weights=weights)
        elif model_name == "EfficientNetB0":
            base_model = applications.EfficientNetB0(input_shape=(x.shape[1], x.shape[2], x.shape[3]), include_top=False, weights=weights)
        elif model_name == "EfficientNetB1":
            base_model = applications.EfficientNetB1(input_shape=(x.shape[1], x.shape[2], x.shape[3]), include_top=False, weights=weights)
        elif model_name == "EfficientNetB2":
            base_model = applications.EfficientNetB2(input_shape=(x.shape[1], x.shape[2], x.shape[3]), include_top=False, weights=weights)
        elif model_name == "EfficientNetB3":
            base_model = applications.EfficientNetB3(input_shape=(x.shape[1], x.shape[2], x.shape[3]), include_top=False, weights=weights)
        elif model_name == "ConvNeXtTiny":
            base_model = applications.ConvNeXtTiny(input_shape=(x.shape[1], x.shape[2], x.shape[3]), include_top=False,
                                                     weights=weights)
        else:
            raise ValueError("Please specify a valid model!")

        x = base_model(x, training=False)
        x = GlobalAveragePooling2D()(x)
        predictions = Dense(num_classes, activation='softmax')(x)

        model = Model(inputs=input_layer, outputs=predictions)
        return model

    def load_data(self, kind="train"):
        X_train, y_train = SPOT10Loader.get_data(dataset_dir=self.dataset_dir, kind=kind)
        X_train = X_train.astype('float32') / 255.0
        X_train = tf.expand_dims(X_train, axis=-1)
        y_train = tf.keras.utils.to_categorical(y_train, num_classes=10)
        return X_train, y_train

    def train_models(self):
        for benchmark_model in self.benchmark_models:
            print(f"Training {benchmark_model} model...")

            # Build model
            model = self.build_model(model_name=benchmark_model)
            model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
            model.summary()

            # Load data
            X_train, y_train = self.load_data(kind="train")
            X_test, y_test = self.load_data(kind="test")

            # Callbacks
            callbacks = [
                EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
                ModelCheckpoint('best_model.h5', monitor='val_loss', save_best_only=True, verbose=1),
                ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=5, min_lr=0.0001, verbose=1)
            ]

            # Train model
            history = model.fit(
                X_train, y_train,
                batch_size=32,
                validation_data=(X_test, y_test),
                epochs=100,
                callbacks=callbacks
            )

            # Evaluate model
            loss, accuracy = model.evaluate(X_test, y_test)
            print(f"Test Loss: {loss}")
            print(f"Test Accuracy: {accuracy}")

            # Save results to DataFrame
            new_data = pd.DataFrame({'model_name': [benchmark_model], 'accuracy': [accuracy], 'loss': [loss]})
            self.df = pd.concat([self.df, new_data], ignore_index=True)

        # Save DataFrame to CSV
        self.df.to_csv(self.csv_file, index=False)
        print(f"Test Accuracy results saved to {self.csv_file}")


if __name__ == "__main__":
    benchmark_models = ["ResNet50", "MobileNet", "MobileNetV2",
                        "DenseNet121", "NASNetMobile", "EfficientNetB0",
                        "EfficientNetB1", "EfficientNetB2", "EfficientNetB3", "ConvNeXtTiny"]

    trainer = ModelTrainer(benchmark_models)

    model = trainer.build_model(model_name="ResNet50")
    #model.summary()
    #trainer.train_models()
