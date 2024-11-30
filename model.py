import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, Flatten, Dense, BatchNormalization, MaxPooling2D, Dropout
import pickle
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
import os

directory = 'C:/Users/workstation/Desktop/Computer Vision/image classification'
datagen = ImageDataGenerator(rescale=1./255.)


train = datagen.flow_from_directory(
    directory= os.path.join(directory,'train'),
    class_mode = 'categorical',
    target_size = (256,256),
    batch_size = 32,
    color_mode = 'rgb'
)


test = datagen.flow_from_directory(
    directory = os.path.join(directory,'test'),
    class_mode = 'categorical',
    shuffle = True,
    target_size = (256,256),
    batch_size = 32,
    color_mode = 'rgb'
)

classes = os.listdir(os.path.join(directory, 'train'))


model = Sequential([
    Conv2D(32, (3,3), activation = 'relu', input_shape = (256,256,3)),
    MaxPooling2D((2,2)),
    BatchNormalization(),

    Conv2D(64, (3,3), activation = 'relu'),
    MaxPooling2D((2,2)),
    BatchNormalization(),

    Conv2D(128, (3,3), activation = 'relu'),
    MaxPooling2D((2,2)),
    BatchNormalization(),

    Conv2D(256, (3,3), activation = 'relu'),
    MaxPooling2D((2,2)),
    BatchNormalization(),

    Flatten(),
    Dense(512),
  
    Dropout(0.2),
    Dense(len(classes), activation = 'softmax')
])

model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])

history = model.fit(train, epochs = 50, verbose = 1, batch_size = 32, validation_data = test)

val_acc = history.history['val_accuracy']
train_acc = history.history['accuracy']

epoch_count = range(1, len(val_accacc) + 1)

plt.plot(epoch_count, val_acc, 'b')
plt.plot(epoch_count, train_acc, 'r')

plt.xlabel('Epochs')
plt.ylabel('Acc')
plt.legend('val_accuracy', 'accuracy')
plt.title('Accuracy & Val_accuracy')
plt.show()


loss, acc = model.evaluate(test, batch_size=32, verbose=1)
print(f'Model accuracy is : {acc}')

with open('model.pkl', 'wb') as file:
    pickle.dump(model, file)
