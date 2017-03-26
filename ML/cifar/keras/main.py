#!/usr/bin/env python

import keras
from keras.datasets import cifar10
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Activation
from keras.layers import Convolution2D, MaxPooling2D
from keras import backend as K
from keras.preprocessing.image import ImageDataGenerator
import time

# Data
img_rows, img_cols, img_channels = 32, 32, 1
nb_classes = 10

# training
batch_size = 128
epochs = 1
data_augmentation = False

# The data, shuffled and split between train and test sets:
(x_train, y_train), (x_test, y_test) = cifar10.load_data()

print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# Convert class vectors to binary class matrices.
y_train = keras.utils.to_categorical(y_train, nb_classes)
y_test = keras.utils.to_categorical(y_test, nb_classes)

input_shape = x_train.shape[1:]

model = Sequential()
model.add(Convolution2D(32, (3, 3), padding='same', activation='relu',
                        input_shape=input_shape))
model.add(Convolution2D(32, (3, 3), padding='same', activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Convolution2D(64, (3, 3), padding='same', activation='relu'))
model.add(Convolution2D(64, (3, 3), padding='same', activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Convolution2D(2048, (8, 8),
                        padding='valid', activation='relu'))
model.add(Dropout(0.5))
model.add(Convolution2D(2048, (1, 1), padding='same', activation='relu'))
model.add(Dropout(0.5))
model.add(Convolution2D(nb_classes, (1, 1), padding='same'))
model.add(Activation('softmax'))
model.add(Flatten())

model.compile(loss='categorical_crossentropy', optimizer='rmsprop',
              metrics=['accuracy'])

x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255

if not data_augmentation:
    print('Not using data augmentation.')
    t0 = time.time()
    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=epochs,
              validation_data=(x_test, y_test),
              shuffle=True)
    t1 = time.time()
else:
    print('Using real-time data augmentation.')
    # This will do preprocessing and realtime data augmentation:
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False)  # randomly flip images

    # Compute quantities required for featurewise normalization
    # (std, mean, and principal components if ZCA whitening is applied).
    datagen.fit(x_train)

    # Fit the model on the batches generated by datagen.flow().
    t0 = time.time()
    model.fit_generator(datagen.flow(x_train, y_train,
                                     batch_size=batch_size),
                        steps_per_epoch=x_train.shape[0] // batch_size,
                        epochs=epochs,
                        validation_data=(x_test, y_test))
    t1 = time.time()

print("Fit time: {:0.2f}s (Augment: {})".format(t1 - t0, data_augmentation))
