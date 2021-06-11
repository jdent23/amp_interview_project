#! /usr/bin/python3

from tensorflow.keras.applications import * #Efficient Net included here
from tensorflow.keras import models
from tensorflow.keras import layers
from keras.preprocessing.image import ImageDataGenerator
import os
import shutil
import pandas as pd
from tensorflow.keras import optimizers
from keras.callbacks import ModelCheckpoint
import mysql.connector
from mysql.connector.constants import ClientFlag
from google.cloud import storage
import pandas as pd
import shutil

'''
import tensorflow as tf
print(device_lib.list_local_devices())
'''

# Options: EfficientNetB0, EfficientNetB1, EfficientNetB2, EfficientNetB3, ... up to  7
# Higher the number, the more complex the model is. and the larger resolutions it  can handle, but  the more GPU memory it will need# loading pretrained conv base model#input_shape is (height, width, number of channels) for images

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './credentials/google-storage-cred.json'
storage_client = storage.Client()

def download_file_in_row(row):

    bucket = storage_client.bucket('amp_interview_project_images')
    blob = bucket.blob(row['filename'])

    if row['label'] == 1:
        row['location'] = os.path.join('pics/dogs/', row['filename'])
        blob.download_to_filename(row['location'])
    elif row['label'] == 0:
        row['location'] = os.path.join('pics/cats/', row['filename'])
        blob.download_to_filename(row['location'])

    return row

def get_data():

    config = {
        'user': 'root',
        'host': '35.223.194.159',
        'client_flags': [ClientFlag.SSL],
        'ssl_ca': 'credentials/server-ca.pem',
        'ssl_cert': 'credentials/client-cert.pem',
        'ssl_key': 'credentials/client-key.pem',
        'database': 'db'
    }

    cnxn = mysql.connector.connect(**config)

    cursor = cnxn.cursor()

    cursor.execute("SELECT * FROM images")
    out = cursor.fetchall()
    df = pd.DataFrame(out, columns=['filename', 'label'])
    cnxn.close()

    try:
        shutil.rmtree('pics')
    except Exception:
        pass

    os.mkdir('pics')
    os.mkdir('pics/dogs')
    os.mkdir('pics/cats')
    return(df.apply(download_file_in_row, axis=1))

def train(df):

    image_shape = (360, 480, 3)
    conv_base = EfficientNetB0(weights="imagenet", include_top=False, input_shape=image_shape)
    print(image_shape[0:2])

    model = models.Sequential()
    model.add(conv_base)
    model.add(layers.GlobalMaxPooling2D(name="gap"))
    #avoid overfitting
    model.add(layers.Dropout(rate=0.2, name="dropout_out"))
    # Set NUMBER_OF_CLASSES to the number of your final predictions.
    model.add(layers.Dense(2, activation="softmax", name="fc_out"))
    conv_base.trainable = False

    datagen = ImageDataGenerator(
        validation_split=0.2,
        rescale=1.0 / 255,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode="nearest",
    )

    train_generator = datagen.flow_from_directory(
        'pics/',
        target_size=image_shape[0:2],
        batch_size=df.shape[0],
        class_mode="categorical",
        subset='training'
    )
    validation_generator = datagen.flow_from_directory(
        'pics/',
        target_size=image_shape[0:2],
        batch_size=df.shape[0],
        class_mode="categorical",
        subset='validation'
    )

    try:
        shutil.rmtree('checkpoints')
    except Exception:
        pass

    os.mkdir('checkpoints')

    checkpoint_path = 'checkpoints/cp-{epoch:04d}.hdf5'
    checkpoint_dir = os.path.dirname(checkpoint_path)

    checkpoint = ModelCheckpoint(
        'model.hdf5',
        monitor='val_loss',
        verbose=1,
        save_best_only=True,
        mode='auto',
        period=1
    )


    model.compile(
        loss="categorical_crossentropy",
        optimizer=optimizers.RMSprop(learning_rate=2e-5),
        metrics=["acc"],
    )

    return model.fit(
        train_generator,
        steps_per_epoch=1,
        epochs=10,
        validation_data=validation_generator,
        validation_steps=1,
        callbacks=[checkpoint],
        verbose=1,
        use_multiprocessing=True,
        workers=4,
    )

def save_model(name):
    try:
        bucket = storage_client.get_bucket('amp_interview_project_models')
        blob = bucket.blob(name)
        blob.upload_from_filename('model.hdf5')
    except Exception as e:
        print(e)

def main():
    df = get_data()
    print(df)
    history = train(df)
    save_model('model.hdf5')


if __name__ == "__main__":
    main()