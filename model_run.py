from PIL import Image
from os import listdir
import imageio as iio
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

datapath = 'C:/홍대/Matrix/Advanced/Conference/test_dataset/padding'
y_path = 'label.txt'
X_path = [f for f in listdir(datapath) if f.endswith('jpg')]
y=[]
X=[]
#target 레이블 저장
with open(f'{datapath}/{y_path}','r') as label_txt:
    y=list(map(lambda x: int(x.split()[0]),label_txt.readlines()))
    le = LabelEncoder()
    y = le.fit_transform(y)
    label_txt.close()
# print(X)
for i in range(len(X_path)):
    img_path = X_path[i]
    img_data=[]
    img = Image.open(f'{datapath}/{img_path}')
    ih, iw = img.size
    pix = img.load()
    # print(iw, ih)
    for py in range(100):
        temp = []
        for px in range(100):
            if py <ih and px < iw :
                temp.append(pix[py,px])
            else :
                temp.append((0,0,0))
        img_data.append(temp)
    X.append(img_data[:])
print(f'{len(X)} datas')



model = models.Sequential()
model.add(layers.Conv2D(100, (3, 3), activation='relu', input_shape=(100, 100, 3)))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.MaxPooling2D((2, 2)))
model.add(layers.Conv2D(64, (3, 3), activation='relu'))
model.add(layers.Flatten())
model.add(layers.Dense(64, activation='relu'))
model.add(layers.Dense(10, activation='softmax'))
model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

X = np.asarray(X)
y= np.asarray(y)
train_images, test_images, train_labels, test_labels = train_test_split(X,y, test_size=0.2,random_state=42)
# print(len(X), y)

history = model.fit(train_images, train_labels, epochs=30, 
                    validation_data=(test_images, test_labels))
# model.save_weights('Saved_padding/model_padding')
plt.plot(history.history['accuracy'], label='accuracy')
plt.plot(history.history['val_accuracy'], label = 'val_accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.ylim([0.5, 1])
plt.legend(loc='lower right')
plt.show()
test_loss, test_acc = model.evaluate(test_images,  test_labels, verbose=2)
y_predict = np.argmax(model.predict(test_images),axis=1)
print('pred$$$$$',np.argmax(y_predict))
confusion = tf.math.confusion_matrix(labels=test_labels, predictions=y_predict, num_classes=10)
from sklearn.metrics import f1_score
print('f1 score is',f1_score(test_labels, y_predict, average=None))