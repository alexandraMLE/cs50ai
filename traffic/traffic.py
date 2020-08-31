import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.
        representing the path to a directory where the data is stored, and 
        return image arrays and labels for each image in the data set.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    # platform-independent to separate path components 
        # e.g. use os.sep or os.path.join, etc instead of '/'
    images = []
    labels = []
    # os.listdir() -- Return a list containing the names of the entries in the directory given by path. 
    # The list is in arbitrary order, and does not include special entries.
    for file in os.listdir(data_dir):
        # os.path.join(path, *paths) -- Join one or more path components intelligently. 
        # The return value is the concatenation of path and any members of *paths with exactly one directory separator (os.sep)
        path_file = os.path.join(data_dir, file)
        if os.path.isdir(path_file):
            for f_file in os.listdir(path_file):
                path_f_file = os.path.join(path_file, f_file)
                # check out OpenCV options
                image = cv2.imread(path_f_file, cv2.IMREAD_COLOR)
                # IMG_WIDTH/HEIGHT defined in the beginning; interpolation is if the image gets zoomed, 
                # 5 choices: INTER_AREA -- average of a set of pixels when zooming or expanding
                image_resize = cv2.resize(image, (IMG_WIDTH, IMG_HEIGHT), interpolation=cv2.INTER_AREA)
                images.append(image_resize)
                labels.append(int(file))

    return images, labels


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    # convolutional neural network -- https://www.tensorflow.org/guide/keras/sequential_model
    model = tf.keras.models.Sequential([

        # Assume that `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`
        # Convolutional layer. Learn 64 filters using a 4x4 kernel
        tf.keras.layers.Conv2D(
            64, (4, 4), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),

        # MaxPooling layer, with a 2x2 pool size
        # tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # Add another convolutional layer, different filters, different kernel
        tf.keras.layers.Conv2D(
            64, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),
        
        # Add another convolutional layer
        tf.keras.layers.Conv2D(
            64, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),

        # MaxPooling layer, with a 2x2 pool size
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # Flatten units
        tf.keras.layers.Flatten(), 

        # Add hidden layer with 128 units
        tf.keras.layers.Dense(128, activation="relu"),

        # Add another hidden layer
        tf.keras.layers.Dense(64, activation="relu"),
        
        # Add another hidden layer
        # tf.keras.layers.Dense(32, activation="relu"),

        # Inplement a Dropout to combat overfitting and eliminate overreliance on any single unit
        tf.keras.layers.Dropout(0.5),

        # Output layer for all catagories, softmax: turns output into probability distribution.
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])

    # Train the model
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


if __name__ == "__main__":
    main()





"""
During the course of this project, I experimented with varying a number of parameters:
                number of convolutional layers
                number of pooling layers
                pool sizes for each pooling layer
                number of hidden layers
                hidden layer sizes
                dropout value


I initially started with baseline conditions, as per shown in the lectures, to classify MNIST images:
    • 1 convolutional layer learning 32 filters with a 3x3 kernel
    • 1 pooling layer with size 2x2
    • 1 hidden layer with 128 neurons
    • 0.5 dropout

With modification, from above, of the parameters one by one to observe effect on accuracy,
I found adding more convolutional layers was most beneficial.

I determined the parameters set:
    • convolutional layer learning 64 filters with a 4x4 kernel
    • convolutional layer learning 64 filters with a 3x3 kernel
    • convolutional layer learning 64 filters with a 3x3 kernel
    • pooling layer with size 2x2
    • hidden layer with 128 neurons
    • hidden layer with 64 neurons
    • 0.5 dropout

resulted in a testing accuracy of 97.6% (averaging 5 independent runs) with the highest testing accuracy of 98.3%.
This was the highest accuracy
I found under my own influence; common ConvNet architectures (found online after research)
resulted in varying testing accuracies.

If you have any suggestions/comments on different parameters or architectures to try,
or any suggestions to improve the efficiency of my code — contact me — a.lee.epstein@gmail.com
"""
