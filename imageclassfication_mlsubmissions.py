# -*- coding: utf-8 -*-
"""ImageClassfication_MLSubmissions.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mhqRGZuSbb2mvmuYNCBPSRwWG5heDXGj

# Nama : Andifa Naufal R
# Submission : Image Classification

#Intel Image

###Library
"""

import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.applications import MobileNetV2
import matplotlib.pyplot as plt

"""###Load Data"""

from google.colab import drive
drive.mount('/content/drive')

from google.colab import drive

# mounting dataset from gdrive
drive.mount('/content/gdrive', force_remount=True)

# dataset path
root_path = '/content/gdrive/MyDrive/inteldataset.zip'

print("Path root:", root_path)

!unzip /content/gdrive/MyDrive/intel_dataset.zip -d /content/gdrive/MyDrive

dataset = ['/content/gdrive/MyDrive/seg_test','/content/gdrive/MyDrive/seg_train']

import shutil
import os


# Function to create new folder if not exists
def make_new_folder(folder_name, parent_folder):
	
	# Path
	path = os.path.join(parent_folder, folder_name)
	
	# Create the folder
	# 'new_folder' in
	# parent_folder
	try:
		# mode of the folder
		mode = 0o777

		# Create folder
		os.mkdir(path, mode)
	except OSError as error:
		print(error)

# current folder path
current_folder = os.getcwd()

# list of folders to be merged
list_dir = dataset

# enumerate on list_dir to get the
# content of all the folders ans store
# it in a dictionary
content_list = {}
for index, val in enumerate(list_dir):
	path = os.path.join(current_folder, val)
	content_list[ list_dir[index] ] = os.listdir(path)

# folder in which all the content will
# be merged
merge_folder = "merge_folder"

# merge_folder path - current_folder
# + merge_folder
merge_folder_path = os.path.join(current_folder, merge_folder)

# create merge_folder if not exists
make_new_folder(merge_folder, current_folder)

# loop through the list of folders
for sub_dir in content_list:

	# loop through the contents of the
	# list of folders
	for contents in content_list[sub_dir]:

		# make the path of the content to move
		path_to_content = sub_dir + "/" + contents

		# make the path with the current folder
		dir_to_move = os.path.join(current_folder, path_to_content )

		# move the file
		shutil.move(dir_to_move, merge_folder_path)

"""###Preprocessing Data"""

from tensorflow.keras.preprocessing.image import ImageDataGenerator
train_datagenerator = ImageDataGenerator(
    rescale = 1./255,
    validation_split=0.2 #split data 
    
)
train_generator = train_datagenerator.flow_from_directory (
    '/content/merge_folder/seg_train',
    target_size = (150,150),
    shuffle = True,
    batch_size = 32,
    class_mode='categorical',
    subset  = 'training'
)
validation_generator = train_datagenerator.flow_from_directory(
    '/content/merge_folder/seg_train',
    target_size = (150,150),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)

"""###Build Model"""

model = Sequential ([
    Conv2D(16, (3,3), activation='relu', input_shape=(150, 150, 3)),
    MaxPooling2D(2, 2),
    Conv2D(32, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Conv2D(128, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Flatten(),
    Dropout (0.5),
    Dense(512, activation='relu'),
    Dense(6, activation='softmax') # layer output
])
model.summary()

"""###Compile Model"""

model.compile(loss='categorical_crossentropy',
             optimizer= tf.keras.optimizers.Adam(learning_rate=1.0000e-04),
             metrics=['accuracy'])

"""###Callbacks

"""

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('val_accuracy')>=0.85):
      print("\nAkurasi telah mencapai >=85%!")
      self.model.stop_training = True
callbacks = myCallback()

"""###Fit Model

"""

history = model.fit(train_generator,
         batch_size=64,
         epochs=20,
         validation_data=validation_generator,
         verbose=2,
         callbacks=[callbacks])

"""### Plot """

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train','Validation'], loc='upper right')
plt.show()

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train','Validation'], loc='upper right')
plt.show()

"""###Convert Model"""

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

"""###Save Model"""

with tf.io.gfile.GFile('model.tflite', 'wb') as f:
  f.write(tflite_model)